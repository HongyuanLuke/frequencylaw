import json  


def read_data_from_jsonl(file_path):  
    data = []  
    with open(file_path, 'r') as f:  
        for line in f:  
            data.append(json.loads(line))  
    return data  


answers = []  

with open('your_dataset_name_answer.txt', 'r', encoding='utf-8') as file:  
    for line in file:  
        answers.append(line.strip()) 

file_name = 'reply_your_dataset_name.jsonl'  
all_results = []  


data = read_data_from_jsonl(file_name)  

judge = [[] for _ in range(len(data))]  


def compare_numbers(num1, num2):  
    return float(num1) == float(num2)  


for index, entry in enumerate(data):  
    instruction = entry['instruction']  

    instruction_str = str(instruction)  

    if compare_numbers(instruction_str, answers[index]):  
        judge[index].append(1)  
    else:  
        judge[index].append(0)  

    paraphrases = entry['paraphrases']  
    for p in paraphrases:  
        p_str = str(p)  
        if compare_numbers(p_str, answers[index]):  
            judge[index].append(1)  
            break  
    else:  
        judge[index].append(0)  

with open('judge_results_your_dataset_name.txt', 'w', encoding='utf-8') as results_file:  
    for j in judge:  
        correct_count = sum(j) 
        total_count = len(j)  
        results_file.write(f"{correct_count}/{total_count}\n")  


total_correct = sum(sum(j) for j in judge)  
total_entries = len(judge)  

print(f"total correct answer: {total_correct}/{total_entries}")  

with open('total_correct_results_your_dataset_name.txt', 'w', encoding='utf-8') as total_results_file:  
    total_results_file.write(f"{total_correct}/{total_entries}\n")