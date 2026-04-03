
import json

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


def process_sentences_from_file(sen1, sen2, max_attempts):

    prompt = (
        'Judge whether the following two sentences express the same mathematical meaning and coverd the same mathematical information?\n'
        f'sentence1: {sen1}\n'
        f'sentence2: {sen2}\n'
        'Reply with "yes" if they are the same, or "no" if they are different.\n'
    )
    
    response = make_requests_GPT(system, prompt.strip(), token=api_key)  
    answer = response.choices[0].message.content.strip()
    
    return answer

def compare_and_write_results(sen1_file, sen2_file, output_file):

    with open(sen1_file, 'r', encoding='utf-8') as f1, open(sen2_file, 'r', encoding='utf-8') as f2:
        sen1_data = [json.loads(line.strip()) for line in f1]
        sen2_data = [json.loads(line.strip()) for line in f2]
    
    all_results = []

    assert len(sen1_data) == len(sen2_data), "The number of lines in the two files do not match!"

    for index, (sen1_entry, sen2_entry) in enumerate(zip(sen1_data, sen2_data)):

        sen1 = sen1_entry.get('instruction', '').strip()
        sen2 = sen2_entry.get('instruction', '').strip()

        comparison_result = process_sentences_from_file(sen1, sen2)
        cleaned_result = comparison_result.replace("\n", "").strip()

        all_results.append(cleaned_result)

    with open(output_file, 'w', encoding='utf-8') as f:
        for result in all_results:
            f.write(result+ '\n')

    print(f"Comparison results have been saved to {output_file}")


api_key=''
sen1_file = "lowfrequency.."  
sen2_file = "highfrequency.."   
output_file = ""

compare_and_write_results(sen1_file, sen2_file, output_file)