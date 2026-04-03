### README.md
# FrequencyLaw: Textual Frequency Law on Large Language Models
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Project Introduction
This project is the official code repository accompanying the paper **Textual Frequency Law on Large Language Models**. It implements the three core methods proposed in the paper: **Textual Frequency Law (TFL)**, **Textual Frequency Distillation (TFD)**, and **Curriculum Textual Frequency Training (CTFT)**, verifying the optimization effect of textual frequency on Large Language Models (LLMs) in Mathematical Reasoning (MR) and Machine Translation (MT) tasks.

Based on GSM8K (Mathematical Reasoning) and FLORES-200 (Machine Translation), the project constructs the **Textual Frequency Paired Dataset (TFPD)**. It provides end-to-end code for frequency calculation, dataset processing, model fine-tuning and evaluation, enabling the reproduction of the experimental conclusions in the paper.

## Environment Setup
### Dependency Installation
```bash
pip install -r requirements.txt
```
If `requirements.txt` is not generated, run the following command to create it:
```bash
pip freeze > requirements.txt
```

### Core Dependencies
- Python 3.9+
- PyTorch 2.0+
- Hugging Face Transformers/Datasets/Accelerate
- NumPy/Pandas (Data Processing)
- LoRA (peft): For lightweight model fine-tuning

## Project Structure
```
frequencyclaw/
├── datasets/                # Textual Frequency Paired Dataset (TFPD)
│   ├── csqa-highfrequency.txt  # CSQA high-frequency math problems
│   ├── csqa-lowfrequency.txt   # CSQA low-frequency math problems
│   ├── gsm8k-highfrequency.txt # GSM8K high-frequency math problems
│   └── gsm8k-lowfrequency.txt  # GSM8K low-frequency math problems
├── MT-SFT/                  # Machine Translation (MT) Fine-tuning Module (CTFT)
│   ├── data/                # MT task data storage directory
│   ├── merge.py             # Data merging script
│   └── sort_frequency.py    # Frequency sorting tool
│   └── runmodel.py          # Run the fine-tuned model weights

├── frequency.py             # Core script for textual frequency calculation (TFL implementation)
├── newfrequency.py          # Re-calculate frequency after TFD distillation
├── get_correct_answer.py    # Mathematical reasoning answer verification
├── issame.py                # Semantic consistency check (dataset construction)
├── judge.py                 # Automatic evaluation of model outputs
├── readdata.py              # Dataset loading utility
├── rephrase.py              # Text paraphrasing generation (high/low frequency)
├── reply_mr.py              # Mathematical Reasoning (MR) model inference
├── reply_mt.py              # Machine Translation (MT) model inference
└── README.md                # Project documentation
```