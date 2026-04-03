import os  
import numpy as np  
import json  
import math
import re
from collections import defaultdict, Counter
import nltk
from nltk.corpus import brown, stopwords
from nltk.util import ngrams

nltk.download('brown')
nltk.download('stopwords')
nltk.download('punkt')

UNIGRAM_WEIGHT = 0.6
BIGRAM_WEIGHT = 0.4
MIN_FREQ = 1 
ALPHA = 0.15 

stop_words = set(stopwords.words('english'))

def clean_and_tokenize(sentence, remove_stopwords=True):
    text = re.sub(r"[^a-zA-Z'-]", ' ', sentence.lower())
    text = re.sub(r"(?<!\w)['-]|['-](?!\w)", '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    words = []
    for word in text.split():
        if '-' in word and len(word) > 1:
            words.extend([w for w in word.split('-') if w])
        else:
            words.append(word)
    
    if remove_stopwords:
        words = [w for w in words if w not in stop_words]
    
    return words

def get_ngram_frequencies(custom_path=None):

    brown_tokens = clean_and_tokenize(' '.join(brown.words()))
    brown_uni_counts = Counter(brown_tokens)
    brown_bi_counts = Counter(ngrams(brown_tokens, 2))
    
    custom_uni_counts = Counter()
    custom_bi_counts = Counter()
    if custom_path and os.path.exists(custom_path):
        with open(custom_path, 'r', encoding='utf-8') as f:
            custom_text = f.read()
        custom_tokens = clean_and_tokenize(custom_text)
        custom_uni_counts = Counter(custom_tokens)
        custom_bi_counts = Counter(ngrams(custom_tokens, 2))

        print(len(custom_uni_counts),len(custom_bi_counts))

    brown_total = max(sum(brown_uni_counts.values()), 1)
    custom_total = max(sum(custom_uni_counts.values()), 1)
    scale_factor = math.sqrt(brown_total / custom_total)
    
    final_uni = defaultdict(lambda: MIN_FREQ)
    final_bi = defaultdict(lambda: MIN_FREQ)
    
    BOOST_FACTOR = 4.0 
    COMMON_FACTOR = 1.2

    all_words = set(brown_uni_counts) | set(custom_uni_counts)
    for word in all_words:
        brown_prob = brown_uni_counts[word] / brown_total
        custom_base = custom_uni_counts[word] / custom_total
        
        if word not in brown_uni_counts:
            custom_prob = custom_base * scale_factor * BOOST_FACTOR
        else:
            custom_prob = custom_base * scale_factor * COMMON_FACTOR
        
        final_uni[word] = ALPHA * brown_prob + (1-ALPHA) * custom_prob
    
    all_bigrams = set(brown_bi_counts) | set(custom_bi_counts)
    brown_bi_total = max(sum(brown_bi_counts.values()), 1)
    custom_bi_total = max(sum(custom_bi_counts.values()), 1)
    bi_scale = math.sqrt(brown_bi_total / custom_bi_total)
    
    for bigram in all_bigrams:
        brown_bi_prob = brown_bi_counts[bigram] / brown_bi_total
        custom_base = custom_bi_counts[bigram] / custom_bi_total
        
        if bigram not in brown_bi_counts:
            custom_bi_prob = custom_base * bi_scale * BOOST_FACTOR
        else:
            custom_bi_prob = custom_base * bi_scale * COMMON_FACTOR
        
        final_bi[bigram] = ALPHA * brown_bi_prob + (1-ALPHA) * custom_bi_prob
    
    base_freq = 10000
    return {
        'unigram': {k: int(v * base_freq) + MIN_FREQ for k, v in final_uni.items()},
        'bigram': {k: int(v * base_freq) + MIN_FREQ for k, v in final_bi.items()}
    }

def geometric_mean(frequencies):
    if not frequencies:
        return MIN_FREQ
    try:
        sum_logs = sum(math.log(f) for f in frequencies)
        return math.exp(sum_logs / len(frequencies))
    except:
        return MIN_FREQ

def calculate_weighted_score_new(sentence, freq_dict):
    words = clean_and_tokenize(sentence)
    if not words:
        return 0.0
    
    unigrams = words
    bigrams = list(ngrams(words, 2)) if len(words) >= 2 else []
    
    uni_freq = [freq_dict['unigram'].get(w, MIN_FREQ) for w in unigrams]
    bi_freq = [freq_dict['bigram'].get(b, MIN_FREQ) for b in bigrams]
    
    uni_score = geometric_mean(uni_freq)
    bi_score = geometric_mean(bi_freq) if bi_freq else MIN_FREQ
    
    combined_score = (uni_score ** UNIGRAM_WEIGHT) * (bi_score ** BIGRAM_WEIGHT)
    return combined_score

def main():  
    langs = ["kea_Latn", "lvs_Latn", "pag_Latn", "kik_Latn"]  
    
    for lang in langs:  
        with open(f'low_{lang}.json', 'r', encoding='utf-8') as f1, \
             open(f'high_{lang}.json', 'r', encoding='utf-8') as f2:  
            data1 = json.load(f1)  
            data2 = json.load(f2)  

        input_data_low = [entry['input'] for entry in data1]  
        input_data_high = [entry['input'] for entry in data2]  

        freq_dict = get_ngram_frequencies("your_generate_file.txt")  

        scored_entries_low = [(entry, calculate_weighted_score_new(entry['input'], freq_dict)) for entry in data1]  
        scored_entries_high = [(entry, calculate_weighted_score_new(entry['input'], freq_dict)) for entry in data2]  
 
        scored_entries_low.sort(key=lambda x: x[1])
        scored_entries_high.sort(key=lambda x: x[1], reverse=True)  
        
        lowest_entries = [entry[0] for entry in scored_entries_low[:]]  
        highest_entries = [entry[0] for entry in scored_entries_high[:]]  

        merged_top_entries = lowest_entries + highest_entries  

        final_scored_entries = []  
        for entry in merged_top_entries:  
            score = calculate_weighted_score_new(entry['input'], freq_dict_low)
            final_scored_entries.append((entry, score))  
        
        final_scored_entries.sort(key=lambda x: x[1], reverse=True)  
        
        final_entries = [entry[0] for entry in final_scored_entries]  
        
        with open(f'{lang}_highTolow_all.json', 'w', encoding='utf-8') as output_file:  
            json.dump(final_entries, output_file, ensure_ascii=False, indent=4)  

if __name__ == "__main__":  
    main()  