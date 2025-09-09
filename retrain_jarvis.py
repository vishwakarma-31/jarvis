import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, PeftModel
from datasets import load_dataset, Dataset
import json
import os
from feedback_logger import load_feedback, clear_feedback

# Model and tokenizer
model_name = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# Load base model
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map={"": "cpu"},
    trust_remote_code=True,
    attn_implementation="eager",
)

# Load existing LoRA if available
lora_path = "./jarvis_lora"
if os.path.exists(lora_path):
    model = PeftModel.from_pretrained(model, lora_path)
    print("Loaded existing LoRA adapters.")
else:
    # Apply new LoRA
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

model.print_trainable_parameters()

# Load original dataset
original_dataset = load_dataset("json", data_files="jarvis_finetune_dataset.jsonl")

# Load feedback and convert to dataset format
feedback_data = load_feedback()
if not feedback_data:
    print("No feedback data available for retraining.")
    exit(0)

feedback_entries = []
for entry in feedback_data:
    feedback_entries.append({
        "instruction": entry["original_instruction"],
        "response": entry["correction"]
    })

# Create feedback dataset
feedback_dataset = Dataset.from_list(feedback_entries)

# Combine datasets
combined_dataset = original_dataset["train"].concatenate(feedback_dataset)

# Preprocess function
def preprocess_function(examples):
    inputs = []
    for instruction, response in zip(examples["instruction"], examples["response"]):
        text = f"Instruct: {instruction}\nOutput: {response}"
        inputs.append(text)
    tokenized = tokenizer(inputs, truncation=True, padding=True, max_length=512)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

tokenized_dataset = combined_dataset.map(preprocess_function, batched=True, remove_columns=combined_dataset.column_names)

# Training arguments
training_args = TrainingArguments(
    output_dir="./jarvis_lora",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=1,  # Fewer epochs for incremental learning
    learning_rate=1e-4,  # Lower learning rate for fine-tuning
    fp16=True,
    save_steps=10,
    logging_steps=10,
    save_total_limit=2,
    push_to_hub=False,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

# Retrain
print("Starting retraining with feedback data...")
trainer.train()

# Save updated LoRA
trainer.save_model("./jarvis_lora")
print("Retraining complete. LoRA adapters updated.")

# Clear feedback after successful retraining
clear_feedback()

# Test the updated model
print("Testing the updated model...")
test_prompts = [
    "Jarvis, what's the weather today?",
    feedback_data[0]["original_instruction"] if feedback_data else "Jarvis, test correction."
]

for prompt in test_prompts:
    input_text = f"Instruct: {prompt}\nOutput:"
    inputs = tokenizer(input_text, return_tensors="pt").to("cpu")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100, do_sample=True, temperature=0.7)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print("-" * 50)