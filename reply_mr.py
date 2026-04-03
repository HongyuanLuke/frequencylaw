# -*- coding: utf-8 -*-  
import json  
import http.client  
import argparse  
import openai  
import random  
import re  
import time  
import subprocess  
import multiprocessing as mp  

def make_requests_GPT(  
        system, user, model='gpt-4o-mini', max_tokens=1024, temperature=1.0, retries=10, presence_penalty=0.0, frequency_penalty=0.0,  
        n=1, organization=None, token=None  
):  
    if organization is not None:  
        openai.organization = organization  

    if model in ['llama-3.1-8b', 'gpt-3.5-turbo', 'gpt-4', 'gpt-4-0613', 'gpt-4-1106-preview', 'gpt-4-32k', 'gpt-4o', 'gpt-4o-mini']:  
        is_chat_or_instruct = 'chat'  
    elif model in ['text-davinci-003', 'text-davinci-004']:  
        is_chat_or_instruct = 'instruct'  
    else:  
        return "Unsupported Model"  
    
    retry_cnt = 0  
    backoff_time = 5  

    while retry_cnt <= retries:  
        try:  
            if is_chat_or_instruct == 'chat':  
                conn = http.client.HTTPSConnection('aigc456.top')  
                payload = json.dumps({  
                    "model": model,  
                    "messages": [  
                        {"role": "system", "content": system},  
                        {"role": "user", "content": user}  
                    ],  
                    "max_tokens": max_tokens,  
                    "temperature": temperature,  
                    "frequency_penalty": frequency_penalty,  
                    "presence_penalty": presence_penalty,  
                    "n": n  
                })  
                headers = {  
                    'Accept': 'application/json',  
                    'Authorization': 'Bearer ' + token,  
                    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',  
                    'Content-Type': 'application/json'  
                }  

                conn.request('POST', '/v1/chat/completions', payload, headers)  
                tmp = conn.getresponse()  
                response = json.loads(tmp.read().decode('utf-8'))  

                return response['choices'][0]['message']['content'].strip()  

            else:  
                raise NotImplementedError  
                response = openai.Completion.create(  
                    engine=model,  
                    prompt=f'{system} {user}',  
                    max_tokens=max_tokens,  
                    temperature=temperature,  
                    frequency_penalty=frequency_penalty,  
                    presence_penalty=presence_penalty,  
                    n=n  
                )  
                return response['choices'][0]['text'].strip()  
        except Exception as e:  
            print(f'Error: {e}.')  
            if 'Please reduce your prompt' in str(e):  
                max_tokens = int(max_tokens * 0.8)  
                print(f'Reducing target length to {max_tokens}, retrying...')  
            elif "Rate limit reached" in str(e):  
                print("Reached rate limit, waiting for rolling window (8m).")  
                time.sleep(8 * 60)  
                retry_cnt = 0  
            else:  
                print(f"Retry in {backoff_time} seconds...")  
                time.sleep(backoff_time)  

            retry_cnt += 1  
 
def extract_number_from_response(response):  
    if response is None:  
        return 'None'  
    match = re.search(r'\d+\.?\d*', response)  
    if match:  
        number = float(match.group(0)) 
        return str(int(number))
    return 'None'

def process_questions(question, token, system):  
    prompt = f'Solve math problems.Question:{question}\nAnswer:'
    response = make_requests_GPT(system, prompt.strip(), token=token)  

    if ':' in response:  
        response = response.split(':', 1)[1].strip()  
    
    answer= extract_number_from_response(response)
    
    return answer

def read_data_from_jsonl(file_path):
    data = []
    with open(file_path, 'r') as f:
        for idx, line in enumerate(f):
            data.append(json.loads(line))
    return data

def process_file():  
    token = 'your_api_key'  
    system = ""  

    file_name = 'rephrase_your_dataset_name.jsonl'
    all_results = []

    data = read_data_from_jsonl(file_name)

    for index, entry in enumerate(data):
        instruction = entry['instruction']
        paraphrases = entry['paraphrases']
        

        tgt_instruction = process_questions(instruction, token, system)


        tgt_paraphrases = []
        for para in paraphrases:
            para_answer = process_questions(para, token, system)
            tgt_paraphrases.append(para_answer)

        result = {
            "instruction": tgt_instruction,
            "paraphrases": tgt_paraphrases,
            "index": index
        }

        all_results.append(result)

    with open('reply_your_dataset_name.jsonl', 'w', encoding='utf-8') as f:  
        for result in all_results:  
            f.write(json.dumps(result, ensure_ascii=False) + '\n')  


# 主函数  
if __name__ == "__main__":  
    process_file()