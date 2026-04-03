import os
os.environ['HF_HOME'] = '/data/.cache'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from PIL import Image


import huggingface_hub
huggingface_hub.login("####")

data_name='your_dataset_name'
from datasets import load_dataset  
try:  
    your_dataset = load_dataset(data_name, split='validation') 
    print('success')  

except Exception as e:  
    print(f"load error: {e}")  
    exit()  

questions = your_dataset['question']  


with open('dataset_name.txt', 'w', encoding='utf-8') as f:  
    for question in questions:  
        question_cleaned = question.replace('\n', ' ').strip()  
        f.write(question_cleaned + '\n')  

print("save success!")  