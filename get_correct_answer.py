from datasets import load_dataset  
import re  

dataset_name='your_dataset_name'

try:  
    gsm8k_dataset = load_dataset(dataset_name, "main", split='test')  
except Exception as e:  
    print(f"load error: {e}")  
    exit()  

answers = gsm8k_dataset['answer']  

with open('your_dataset_name_answer.txt', 'w', encoding='utf-8') as f:  
    for answer in answers:  
        if '####' in answer:  
            answer = answer.split('####')[-1].strip()  
        else:  
            print(f"not find `####` item:{answer}")  
            continue 

        if ',' in answer:  
            answer = answer.replace(',', '')  
        
        answer = str(int(answer))
        f.write(answer+'\n')
        

print("get your_dataset_name_answer.txt!")