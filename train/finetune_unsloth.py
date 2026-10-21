"""
Fine-tuning script for Qwen 2.5 7B Instruct using Unsloth (QLoRA 4-bit)
Optimized for NVIDIA GeForce RTX 5080 (16GB VRAM).
Estimated training time for 10,000 decisions: ~12-15 minutes.
"""
import torch

def train():
    try:
        from unsloth import FastLanguageModel
        from datasets import load_dataset
        from trl import SFTTrainer
        from transformers import TrainingArguments
    except ImportError:
        print("Please install training dependencies: pip install -r requirements-train.txt")
        return

    max_seq_length = 1024
    dtype = None # Auto detect: Float16 for Tesla/Turing, Bfloat16 for Ampere/Ada/Blackwell
    load_in_4bit = True

    print("Loading base model: Qwen/Qwen2.5-7B-Instruct...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="Qwen/Qwen2.5-7B-Instruct",
        max_seq_length=max_seq_length,
        dtype=dtype,
        load_in_4bit=load_in_4bit,
    )

    # Set up LoRA configuration
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )

    # Load prepared dataset
    dataset = load_dataset("json", data_files="data/train.jsonl", split="train")

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="messages",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            warmup_steps=20,
            max_steps=200,
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir="outputs",
        ),
    )

    print("Starting fine-tuning on RTX 5080...")
    trainer.train()

    # Save fine-tuned LoRA
    model.save_pretrained_merged("outputs/finetuned_model", tokenizer, save_method="merged_16bit")
    print("Saved merged 16-bit model to outputs/finetuned_model")
    
    # Save directly to GGUF for instant Ollama serving
    print("Exporting GGUF for Ollama...")
    model.save_pretrained_gguf("outputs/gguf", tokenizer, quantization_method="q4_k_m")
    print("GGUF exported successfully to outputs/gguf/unsloth.Q4_K_M.gguf")

if __name__ == "__main__":
    train()
