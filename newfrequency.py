import numpy as np
from nltk.corpus import brown, stopwords
from collections import defaultdict
import re

stop_words = set(stopwords.words('english'))

def clean_and_tokenize(text):
    text = re.sub(r'[^a-zA-Z\'\s]', '', text.lower()) 
    words = [word for word in text.split() if word and word not in stop_words]
    return words

def load_and_normalize_corpus(file_path=None):
    """
    :param file_path: 
    :return:  {word: prob}
    """
    if file_path is None:
        word_counts = defaultdict(int)
        for sentence in brown.sents():
            words = clean_and_tokenize(' '.join(sentence))
            for word in words:
                word_counts[word] += 1
    else:
        word_counts = defaultdict(int)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                words = clean_and_tokenize(line.strip())
                for word in words:
                    word_counts[word] += 1

    total = max(sum(word_counts.values()), 1)
    return {word: count/total for word, count in word_counts.items()}

def align_and_merge(old_probs, new_probs, beta=0.5, epsilon=1e-8):
    """
    :param beta: (0.0~1.0)
    :param epsilon: 
    :return:  {word: prob}
    """
    common_words = set(old_probs.keys()) & set(new_probs.keys())
    if len(common_words) > 10:
        ratios = [
            (old_probs[w] + epsilon) / (new_probs[w] + epsilon)
            for w in common_words
            if new_probs[w] > 1e-10 and old_probs[w] > 1e-10
        ]
        gamma = np.median(ratios) if ratios else 1.0
    else:
        gamma = 1.0
    
    new_probs_aligned = {w: p * gamma for w, p in new_probs.items()}
    
    combined_vocab = set(old_probs.keys()) | set(new_probs.keys())
    merged_probs = {}
    for word in combined_vocab:
        p_old = old_probs.get(word, epsilon)
        p_new = new_probs_aligned.get(word, epsilon)

        #merged_probs[word] = beta * p_old + (1 - beta) * p_new
        merged_probs[word] = p_old * p_new
    
    total = sum(merged_probs.values()) or 1
    return {word: p/total for word, p in merged_probs.items()}

def compute_sentence_score(sentence, prob_dict, epsilon=1e-8):
    words = clean_and_tokenize(sentence)
    if not words:
        return 0.0
    
    probs = [prob_dict.get(word, epsilon) for word in words]
    
    log_sum = np.sum(np.log(1 / np.array(probs)))
    return np.exp(log_sum / len(words))


stop_words = set(stopwords.words('english'))  

def load_probabilities(file_path):  
    '''
    file_path:your_combined_probs.txt
    '''
    prob_dict = {} 
    with open(file_path, 'r', encoding='utf-8') as f:  
        for line in f:  
            word, prob = line.strip().split('\t')  
            prob_dict[word] = float(prob)  
    return prob_dict  

def compute_zipf_frequency(sentence, prob_dict, epsilon=1e-8):  
    words = clean_and_tokenize(sentence)  
    if not words:  
        return 0.0  
     
    probs = [prob_dict.get(word, epsilon) for word in words]  
    
    log_sum = np.sum(np.log(1 / np.array(probs)))  
    return np.exp(log_sum / len(words))  

if __name__ == "__main__":

    old_probs = load_and_normalize_corpus()
    new_probs = load_and_normalize_corpus('your_new_generate_file.txt')
    
    merged_probs = align_and_merge(old_probs, new_probs, beta=0.6)
    
    with open('your_combined_probs.txt', 'w', encoding='utf-8') as f:
        for word, prob in sorted(merged_probs.items(), key=lambda x: -x[1]):
            f.write(f"{word}\t{prob:.10f}\n")
    
    test_sentence = "Business formal attire typically consists of suits, and colleagues habitually address one another either by their surnames or professional designations."
    score = compute_sentence_score(test_sentence, merged_probs)
    print(f"Sentence Frequency Score: {score:.4f} (Higher means less common)")