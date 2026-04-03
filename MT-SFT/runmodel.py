import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

# ============== configs ==============
BASE_MODEL_PATH = "Qwen2.5-7B-Instruct"
LORA_ADAPTER_PATH = "./saves/qwen-7b/lora/sft_kea_Latn_hightolow"
INPUT_FILE = "eng_Latn.txt"
OUTPUT_FILE = "kea_Latn-hightolow.txt"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_HISTORY = 0
# ===================================

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    torch_dtype=torch.bfloat16,
    device_map=DEVICE,
    trust_remote_code=True,
    use_flash_attention_2=False
)
model = PeftModel.from_pretrained(model, LORA_ADAPTER_PATH)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

class BatchChatBot:
    def __init__(self):
        self.system_prompt = "you are an expert in translation."
        
    def generate(self, query):
        prompt = f"<|im_start|>system\n{self.system_prompt}<|im_end|>\n"
        prompt += f"<|im_start|>user\n{query}<|im_end|>\n<|im_start|>assistant\n"
        
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            max_length=2048,
            truncation=True
        ).to(DEVICE)
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id
        )
        
        response = tokenizer.decode(
            outputs[0][inputs.input_ids.shape[-1]:],
            skip_special_tokens=True
        )
        return response.strip()

def process_batch():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        queries = [line.strip() for line in f if line.strip()]
    
    bot = BatchChatBot()
    
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f_out:
        for idx, query in enumerate(tqdm(queries, desc="Processing")):
            try:
                query_merge = f'Translate the following sentence from English to Kabuverdianu.Note:Only response me the final translation.'+ query
                #print(query_merge)
                response = bot.generate(query_merge)
                response = response.replace("\n", " ") 
                if ':' in response:  
                    response = response.split(':', 1)[-1].strip()  
                response = response.replace('\n', '')  
                #f_out.write(f"Input {idx+1}: {query}\n")
                #print(response)
                f_out.write(f"{response}\n")
                #f_out.flush()  
            except Exception as e:
                f_out.write(f"Error processing input.\n")

if __name__ == "__main__":
    process_batch()
    print(f"success! {OUTPUT_FILE}")