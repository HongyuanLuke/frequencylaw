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


def process_questions(question, token, system):  
    prompt = (  
        f'Your task is to generate 10 unique paraphrases for the given query, ensuring that the meaning of '  
        f'each paraphrase remains consistent, and the structure is significantly altered. Do not introduce any '  
        f'new information that isn’t present in the original query, and avoid omitting any crucial information '  
        f'from the original query, particularly any specific requirements about the output content, style, format, '  
        f'options, or any numbers or data. The responses to your paraphrases and the original query should be '  
        f'identical. Your task is not to answer the query, but solely to rephrase it. Please provide unique and creative rephrasing. '  
        f'Please note that you should provide exactly 10 paraphrases, not less. Output each paraphrase separated by "||||".\nquery: {question}'  
    )  
    response = make_requests_GPT(system, prompt.strip(), token=token)  

    # 提取冒号后面的部分，并根据 "||||" 分割成列表  
    if ':' in response:  
        response = response.split(':', 1)[1].strip()  
    paraphrases = response.split('||||')  
    
    # 确保返回的列表正好有10个释义  
    return paraphrases[:10] if len(paraphrases) >= 10 else paraphrases  


# 处理每个问题并保存结果  
def process_file():  
    token = 'your_api_key'  
    system = ""  

    file_name = 'your_dataset_name.txt'
    all_results = []

    max_lines = MAXLINE

    with open(file_name, 'r', encoding='utf-8') as file:
        for index, line in enumerate(file):
            if index >= max_lines:
                break
            
            question = line.strip()
            paraphrases = process_questions(question, token, system)

            result = {
                "instruction": question,
                "paraphrases": paraphrases,
                "index": index
            }
            all_results.append(result)


    with open('rephrase_your_dataset_name.jsonl', 'w', encoding='utf-8') as f:  
        for result in all_results:  
            f.write(json.dumps(result, ensure_ascii=False) + '\n')  


if __name__ == "__main__":  
    process_file()