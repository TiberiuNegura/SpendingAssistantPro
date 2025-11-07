import re
import json
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel
import torch


def parse_model_output(output_string: str):
    """
    Parses the custom tagged string output from the Donut model into a dictionary.
    """
    result = {}

    # 1. Parse the menu items
    # Find the content inside <s_menu>...</s_menu>
    menu_match = re.search(r"<s_menu>(.*?)</s_menu>", output_string, re.DOTALL)
    if menu_match:
        result['menu'] = []
        menu_content = menu_match.group(1)

        # Split the menu content by the <sep/> separator
        items = menu_content.split("<sep/>")

        for item_string in items:
            if not item_string.strip():
                continue

            item_dict = {}
            # Find all tags (e.g., <s_nm>...</s_nm>) within this item
            tags = re.findall(r"<s_(\w+)>(.*?)</s_\1>", item_string)

            # The model output can have duplicate tags (like s_num)
            # We'll store values as a list to capture all of them
            for tag, value in tags:
                if tag not in item_dict:
                    item_dict[tag] = []
                item_dict[tag].append(value)

            if item_dict:
                result['menu'].append(item_dict)

    # 2. Parse the sub_total
    sub_total_match = re.search(r"<s_sub_total>(.*?)</s_sub_total>", output_string, re.DOTALL)
    if sub_total_match:
        result['sub_total'] = {}
        sub_total_content = sub_total_match.group(1)
        tags = re.findall(r"<s_(\w+)>(.*?)</s_\1>", sub_total_content)
        for tag, value in tags:
            # Assuming single value for sub_total fields
            result['sub_total'][tag] = value

    # 3. Parse the total
    total_match = re.search(r"<s_total>(.*?)</s_total>", output_string, re.DOTALL)
    if total_match:
        result['total'] = {}
        total_content = total_match.group(1)
        tags = re.findall(r"<s_(\w+)>(.*?)</s_\1>", total_content)
        for tag, value in tags:
            # Assuming single value for total fields
            result['total'][tag] = value

    return result


def extract_receipt_info(receipt_path: str):
    # 1. Load the model and processor from the transformers library
    model_name = "naver-clova-ix/donut-base-finetuned-cord-v2"

    processor = DonutProcessor.from_pretrained(model_name)
    model = VisionEncoderDecoderModel.from_pretrained(model_name)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"Using device: {device}")

    # 2. Load your image
    try:
        image = Image.open(receipt_path).convert("RGB")
    except FileNotFoundError:
        print(f"Error: Image file not found at {receipt_path}")
        return

    pixel_values = processor(image, return_tensors="pt").pixel_values

    # 3. Generate the output
    task_prompt = "<s_cord-v2>"
    decoder_input_ids = processor.tokenizer(
        task_prompt, add_special_tokens=False, return_tensors="pt"
    ).input_ids

    # Move inputs to the correct device
    pixel_values = pixel_values.to(device)
    decoder_input_ids = decoder_input_ids.to(device)

    # Generate the output (sequence of token IDs)
    outputs = model.generate(
        pixel_values,
        decoder_input_ids=decoder_input_ids,
        max_length=model.decoder.config.max_position_embeddings,
        early_stopping=True,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        use_cache=True,
        num_beams=1,
        bad_words_ids=[[processor.tokenizer.unk_token_id]],
        return_dict_in_generate=True,
    )

    # --- 4. Decode and Parse the Output ---
    # Convert the token IDs back into a string
    sequence = processor.batch_decode(outputs.sequences)[0]
    # Remove the special tokens
    sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
    sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # Remove first token

    print("--- Raw Model Output ---")
    print(sequence)

    # --- MODIFIED PART ---
    # Instead of json.loads, use our new custom parser
    parsed_data = parse_model_output(sequence)
    # --- END OF MODIFIED PART ---

    return parsed_data


# --- How to use it ---
# Replace 'path/to/your-receipt.jpg' with the actual path
receipt_path = 'receipt_2.png'
extracted_data = extract_receipt_info(receipt_path)

if extracted_data:
    print("\n--- Extracted Data (as JSON) ---")
    # Pretty-print the dictionary as a JSON string
    print(json.dumps(extracted_data, indent=2))