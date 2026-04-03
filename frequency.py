
import nltk
from collections import Counter
import numpy as np
import re
import json

nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('english'))

def get_word_frequencies():
    # for example 'brown'
    from nltk.corpus import brown
    words = [word.lower() for word in brown.words()]
    word_counts = Counter(words)
    return word_counts

def clean_and_tokenize(sentence):
    sentence = re.sub(r'\d+', '', sentence)
    sentence = re.sub(r'[^\w\s]', '', sentence)
    words = word_tokenize(sentence.lower())
    return [word for word in words if word not in stop_words]

def compute_zipf_frequency(sentence, word_frequencies):
    words = clean_and_tokenize(sentence)
    word_count = len(words)

    if word_count == 0:
        return 0

    frequencies = []
    for word in words:
        word_freq = word_frequencies.get(word, 1)
        frequencies.append(word_freq)
        print(word,word_freq)

    zipf_product = np.prod([1 / f for f in frequencies])
    zipf_normalized = zipf_product / word_count

    return zipf_normalized


def process_jsonl(jsonl_file):
    word_frequencies = get_word_frequencies()
    
    with open(jsonl_file, 'rb') as file:
        lines = file.readlines()

    with open('your_dataset_name_lowfrequency.txt', 'w',encoding='utf-8') as low_file, open('your_dataset_name_highfrequency.txt', 'w',encoding='utf-8') as high_file:
        for line in lines:
            data = json.loads(line)
            paraphrases = data.get("paraphrases", [])
            
            if not paraphrases:
                continue
            zipf_scores = [(sentence, compute_zipf_frequency(sentence, word_frequencies)) for sentence in paraphrases]  

            zipf_scores.sort(key=lambda x: x[1]) 
            max_zipf_sentence = zipf_scores[-1]
            min_zipf_sentence = zipf_scores[0]

            if len(max_zipf_sentence[0]) < 10:  
                max_zipf_sentence = zipf_scores[-2] 

            if len(min_zipf_sentence[0]) < 10:  
                min_zipf_sentence = zipf_scores[1]
            
            max_zipf_sentence_cleaned = max_zipf_sentence[0].replace('\n', ' ').strip()  # 先处理句子  
            min_zipf_sentence_cleaned = min_zipf_sentence[0].replace('\n', ' ').strip()  # 先处理句子


            low_file.write(f"{max_zipf_sentence_cleaned}\n")  
            high_file.write(f"{min_zipf_sentence_cleaned}\n")

if __name__ == "__main__":
    process_jsonl('rephrase_your_dataset_name.jsonl')
