import re
import json
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel
import torch


class ReceiptExtractor:
    """
    A class to extract information from receipts using the Donut model.

    The model is loaded during initialization to avoid reloading it
    for every extraction.
    """

    def __init__(self, model_name: str = "naver-clova-ix/donut-base-finetuned-cord-v2"):
        """
        Initializes the ReceiptExtractor by loading the model and processor.

        Args:
            model_name (str): The name of the pre-trained Donut model to use.
        """
        print(f"Loading model '{model_name}'...")
        self.processor = DonutProcessor.from_pretrained(model_name)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"Using device: {self.device}")
        print("Model loaded successfully.")

    def process_receipt(self, receipt_path: str):
        """
        Extracts information from a given receipt image.

        Args:
            receipt_path (str): The file path to the receipt image.

        Returns:
            dict: A dictionary containing the parsed receipt data, or None if an error occurs.
        """
        # 1. Load the image
        try:
            image = Image.open(receipt_path).convert("RGB")
        except FileNotFoundError:
            print(f"Error: Image file not found at {receipt_path}")
            return None

        # 2. Prepare for the model
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        task_prompt = "<s_cord-v2>"
        decoder_input_ids = self.processor.tokenizer(
            task_prompt, add_special_tokens=False, return_tensors="pt"
        ).input_ids

        # Move inputs to the correct device
        pixel_values = pixel_values.to(self.device)
        decoder_input_ids = decoder_input_ids.to(self.device)

        # 3. Generate the output
        outputs = self.model.generate(
            pixel_values,
            decoder_input_ids=decoder_input_ids,
            max_length=self.model.decoder.config.max_position_embeddings,
            early_stopping=True,
            pad_token_id=self.processor.tokenizer.pad_token_id,
            eos_token_id=self.processor.tokenizer.eos_token_id,
            use_cache=True,
            num_beams=1,
            bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,
        )

        # 4. Decode and Parse the Output
        sequence = self.processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(self.processor.tokenizer.pad_token,
                                                                                    "")
        sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # Remove first token

        print("\n--- Raw Model Output ---")
        print(sequence)

        # Use the static parsing method
        parsed_data = self._parse_model_output(sequence)
        return parsed_data

    @staticmethod
    def _parse_model_output(output_string: str):
        """
        Parses the custom tagged string output from the Donut model into a dictionary.
        """
        result = {}

        # 1. Parse the menu items
        menu_match = re.search(r"<s_menu>(.*?)</s_menu>", output_string, re.DOTALL)
        if menu_match:
            result['menu'] = []
            menu_content = menu_match.group(1)

            items = menu_content.split("<sep/>")

            for item_string in items:
                if not item_string.strip():
                    continue

                item_dict = {}
                tags = re.findall(r"<s_(\w+)>(.*?)</s_\1>", item_string)

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
                result['sub_total'][tag] = value

        # 3. Parse the total
        total_match = re.search(r"<s_total>(.*?)</s_total>", output_string, re.DOTALL)
        if total_match:
            result['total'] = {}
            total_content = total_match.group(1)
            tags = re.findall(r"<s_(\w+)>(.*?)</s_\1>", total_content)
            for tag, value in tags:
                result['total'][tag] = value

        return result


# --- How to use the class ---
if __name__ == "__main__":

    # 1. Create an instance of the extractor.
    #    (This will load the model, which might take a moment)
    extractor = ReceiptExtractor()

    # 2. Define the path to your receipt
    receipt_path = 'receipt_2.png'

    # 3. Process the receipt
    extracted_data = extractor.process_receipt(receipt_path)

    # 4. Print the results
    if extracted_data:
        print("\n--- Extracted Data (as JSON) ---")
        print(json.dumps(extracted_data, indent=2))
    else:
        print(f"Could not process the receipt at {receipt_path}")