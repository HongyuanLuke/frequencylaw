import json  

langs= []

dict={"kea_Latn":"Kabuverdianu",
      "lvs_Latn":"Standard Latvian",
      "pag_Latn":"Pangasinan",
      "kik_Latn":"Kikuyu"
      # choose your language
      }

examples={"kea_Latn":"Riportajen di tilivizon mostra fumu branku ta sai di fábrika.",
      "lvs_Latn":"Televīzijas pārraidēs redzams, ka no rūpnīcas nāk balti dūmi.",
      "pag_Latn":"Base ed saray report ed TV, walay amputin asewek ya manlalapud tanaman.",
      "kik_Latn":"Roboti kuumana na Televisheni cironania ndogo njerũ Ĩkiuma kuuma mũtambo-inĨ."
      
      }
for lang in langs:

    with open('your_dataset_name_frequency.txt', 'r', encoding='utf-8') as f1, open(f'your_target_lang_name.txt', 'r', encoding='utf-8') as f2:  
        lines1 = f1.readlines()  
        lines2 = f2.readlines()  

    if len(lines1) != len(lines2):  
        raise ValueError("lines error!")  

    merged_data = []  
    assit= f'''  
        You are an expert in translation. Translate the following sentence from English to {dict[lang]}.\n For example:\n sentence:Television reports show white smoke coming from the plant. \ntranslation:  {examples[lang]} 
    '''  

    for line1, line2 in zip(lines1, lines2):  
        if 1:
            merged_data.append({  
                "instruction": assit,  
                "input": line1.strip(),   
                "output": line2.strip() 
            })  

    with open(f'your_lang_dataset_name.json', 'w', encoding='utf-8') as json_file:  
        json.dump(merged_data, json_file, ensure_ascii=False, indent=2)  

    print("success merge!")