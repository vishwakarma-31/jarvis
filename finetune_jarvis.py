import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, PeftModel
from datasets import load_dataset
import json

# Model and tokenizer
model_name = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# Load model on CPU for low VRAM setup
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map={"": "cpu"},
    trust_remote_code=True,
    attn_implementation="eager",
)

# LoRA config
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Load dataset
dataset = load_dataset("json", data_files="jarvis_finetune_dataset.jsonl")

# Preprocess function
def preprocess_function(examples):
    inputs = []
    for instruction, response in zip(examples["instruction"], examples["response"]):
        text = f"Instruct: {instruction}\nOutput: {response}"
        inputs.append(text)
    tokenized = tokenizer(inputs, truncation=True, padding=True, max_length=512)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

tokenized_dataset = dataset.map(preprocess_function, batched=True, remove_columns=dataset["train"].column_names)

# Training arguments for low VRAM
training_args = TrainingArguments(
    output_dir="./jarvis_lora",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-4,
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
    train_dataset=tokenized_dataset["train"],
)

# Fine-tune
trainer.train()

# Save LoRA adapters
trainer.save_model("./jarvis_lora")

# Test the model
print("Testing the fine-tuned model...")

# Load base model and merge LoRA
base_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map={"": "cpu"},
    trust_remote_code=True,
)
model_with_lora = PeftModel.from_pretrained(base_model, "./jarvis_lora")

test_prompts = [
    "Jarvis, what's the weather today?",
    "Jarvis, open my email.",
    "Jarvis, is my system secure?",
]

for prompt in test_prompts:
    input_text = f"Instruct: {prompt}\nOutput:"
    inputs = tokenizer(input_text, return_tensors="pt").to("cpu")
    with torch.no_grad():
        outputs = model_with_lora.generate(**inputs, max_new_tokens=100, do_sample=True, temperature=0.7)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print("-" * 50)