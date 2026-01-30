import re
import json
import torch
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel, pipeline


class ReceiptExtractor:
    """
    A class to extract information from receipts using the Donut model
    and categorize items using a Zero-Shot classifier.
    """

    def __init__(self, model_name: str = "naver-clova-ix/donut-base-finetuned-cord-v2"):
        """
        Initializes the ReceiptExtractor by loading:
        1. The Donut model for text extraction.
        2. The Zero-Shot Classification model for item categorization.
        """
        # --- 1. Load Donut Model (Extraction) ---
        print(f"Loading extraction model '{model_name}'...")
        self.processor = DonutProcessor.from_pretrained(model_name)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)

        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

        self.model.to(self.device)
        print(f"Extraction model loaded on device: {self.device}")

        # --- 2. Load Zero-Shot Model (Categorization) ---
        print("Loading categorization model 'facebook/bart-large-mnli'...")
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

        # Define categories with keywords for better classification
        self.candidate_labels = ["Groceries", "Entertainment", "Lifestyle", "Transportation", "Utilities"]

        # Keyword mapping for improved categorization
        self.category_keywords = {
            "Groceries": ["food", "drink", "grocery", "market", "vegetable", "fruit", "meat", "dairy",
                         "bread", "snack", "beverage", "milk", "eggs", "chicken", "beef", "fish",
                         "coffee", "tea", "water", "juice", "supermarket", "store", "cheese", "yogurt",
                         "banana", "apple", "orange", "grape", "strawberry", "berry", "blueberry",
                         "raspberry", "lemon", "lime", "pear", "peach", "kiwi", "watermelon", "melon"],
            "Entertainment": ["movie", "cinema", "game", "concert", "ticket", "show", "theater",
                            "music", "streaming", "netflix", "spotify", "xbox", "playstation",
                            "entertainment", "fun", "park", "museum"],
            "Lifestyle": ["clothing", "clothes", "shoes", "fashion", "beauty", "cosmetic", "salon",
                         "gym", "fitness", "sport", "book", "magazine", "furniture", "home",
                         "restaurant", "dining", "cafe", "bar", "hotel", "travel"],
            "Transportation": ["gas", "fuel", "petrol", "diesel", "uber", "taxi", "bus", "train",
                             "metro", "subway", "parking", "toll", "car", "vehicle", "transport"],
            "Utilities": ["electric", "electricity", "water", "bill", "phone", "internet", "wifi",
                         "utility", "gas", "heating", "cooling", "service", "subscription"]
        }
        print("All models loaded successfully.")

    def process_receipt(self, receipt_path: str):
        """
        Extracts information from a receipt image and categorizes the items.
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

        # Move inputs to device
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

        # 4. Decode and Parse
        sequence = self.processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(self.processor.tokenizer.pad_token,
                                                                                    "")
        sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()

        print("\n--- Raw Model Output ---")
        print(sequence)

        # 5. Parse into JSON
        parsed_data = self._parse_model_output(sequence)

        # 6. Categorize the Data
        if parsed_data:
            print("Categorizing extracted items...")
            print(f"DEBUG: Found {len(parsed_data.get('menu', []))} menu items")
            if 'total' in parsed_data:
                print(f"DEBUG: Total section: {parsed_data['total']}")
            parsed_data = self._categorize_data(parsed_data)

        return parsed_data

    def _categorize_data(self, json_data):
        """
        Internal method to apply zero-shot classification to the extracted menu items.
        Uses keyword matching first, then falls back to zero-shot classification.
        """
        items = json_data.get("menu", [])

        for item in items:
            # Extract name
            raw_name = item.get("nm", [""])[0]
            clean_name = raw_name.strip().lower()

            # Skip metadata/empty
            if not clean_name or "DATE:" in raw_name:
                item["category"] = "Metadata"
                continue

            # First try keyword matching for faster and more accurate results
            keyword_match = self._match_by_keywords(clean_name)
            if keyword_match:
                item["category"] = keyword_match
                continue

            # Fall back to zero-shot classification
            try:
                result = self.classifier(
                    clean_name,
                    self.candidate_labels,
                    hypothesis_template="This is a purchase of {}."
                )

                top_category = result['labels'][0]
                confidence = result['scores'][0]

                # Use a more lenient threshold since we already tried keyword matching
                if confidence > 0.35:
                    item["category"] = top_category
                else:
                    # If confidence is low, default to Groceries for food-related items
                    item["category"] = "Groceries" if any(word in clean_name for word in ["food", "snack", "drink"]) else "Other"
            except Exception as e:
                print(f"Warning: Could not categorize '{clean_name}': {e}")
                item["category"] = "Other"

        return json_data

    def _match_by_keywords(self, text: str):
        """
        Match text against category keywords for faster and more accurate categorization.

        Args:
            text (str): The text to categorize (should be lowercase)

        Returns:
            str or None: The matched category or None if no match
        """
        text = text.lower()

        # Count matches for each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score

        # Return category with highest score, if any
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]

        return None

    def calculate_category_totals(self, extracted_data):
        """
        Calculate the total spending per category from the extracted receipt data.

        Args:
            extracted_data (dict): The extracted and categorized receipt data

        Returns:
            dict: A dictionary with category names as keys and total amounts as values
        """
        category_totals = {
            "Groceries": 0.0,
            "Entertainment": 0.0,
            "Lifestyle": 0.0,
            "Transportation": 0.0,
            "Utilities": 0.0,
            "Other": 0.0,
            "Metadata": 0.0
        }

        items = extracted_data.get("menu", [])
        total_from_items = 0.0

        for item in items:
            category = item.get("category", "Other")

            # Try multiple fields for price (price, unitprice, etc.)
            price = 0.0
            for price_field in ["price", "unitprice", "total_price"]:
                price_data = item.get(price_field)
                if price_data:
                    if isinstance(price_data, list):
                        price_str = price_data[0] if price_data else "0"
                    else:
                        price_str = str(price_data)

                    # Clean and parse price
                    try:
                        # Remove currency symbols, whitespace, and common separators
                        price_str = price_str.replace("$", "").replace("€", "").replace("£", "")
                        price_str = price_str.replace(",", "").replace(" ", "").strip()

                        # Try to parse as float
                        if price_str and price_str not in ["", "0", "0.0", "0.00"]:
                            price = float(price_str)
                            break  # Found a valid price
                    except (ValueError, AttributeError):
                        continue

            # Add to category total if price is valid
            if price > 0:
                if category in category_totals:
                    category_totals[category] += price
                else:
                    category_totals["Other"] += price
                total_from_items += price

        # If no individual item prices were found, try to use the total from the receipt
        if total_from_items == 0:
            total_price = self._extract_total_price(extracted_data)
            if total_price > 0:
                # If we have a total but no item breakdown, categorize based on items present
                # Default to "Other" if we can't determine category
                dominant_category = self._get_dominant_category(items)
                category_totals[dominant_category] = total_price

        # Remove Metadata and zero categories for cleaner output
        category_totals.pop("Metadata", None)
        category_totals = {k: v for k, v in category_totals.items() if v > 0}

        return category_totals

    def _extract_total_price(self, extracted_data):
        """
        Extract the total price from the receipt's total section.

        Args:
            extracted_data (dict): The extracted receipt data

        Returns:
            float: The total price or 0.0 if not found
        """
        # Check total section
        total_section = extracted_data.get("total", {})
        for field in ["total_price", "cashprice", "changeprice"]:
            if field in total_section:
                try:
                    price_str = str(total_section[field])
                    price_str = price_str.replace("$", "").replace("€", "").replace("£", "")
                    price_str = price_str.replace(",", "").replace(" ", "").strip()
                    if price_str:
                        return float(price_str)
                except (ValueError, AttributeError):
                    continue

        # Check sub_total section
        sub_total_section = extracted_data.get("sub_total", {})
        for field in ["subtotal_price", "total_price"]:
            if field in sub_total_section:
                try:
                    price_str = str(sub_total_section[field])
                    price_str = price_str.replace("$", "").replace("€", "").replace("£", "")
                    price_str = price_str.replace(",", "").replace(" ", "").strip()
                    if price_str:
                        return float(price_str)
                except (ValueError, AttributeError):
                    continue

        return 0.0

    def _get_dominant_category(self, items):
        """
        Get the most common category from a list of items.

        Args:
            items (list): List of item dictionaries

        Returns:
            str: The dominant category or "Other"
        """
        if not items:
            return "Other"

        category_counts = {}
        for item in items:
            category = item.get("category", "Other")
            if category != "Metadata":
                category_counts[category] = category_counts.get(category, 0) + 1

        if category_counts:
            return max(category_counts.items(), key=lambda x: x[1])[0]

        return "Other"

    @staticmethod
    def _parse_model_output(output_string: str):
        """
        Parses the custom tagged string output from Donut into a dictionary.
        """
        result = {}

        # Parse menu
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

        # Parse sub_total
        sub_total_match = re.search(r"<s_sub_total>(.*?)</s_sub_total>", output_string, re.DOTALL)
        if sub_total_match:
            result['sub_total'] = {}
            for tag, value in re.findall(r"<s_(\w+)>(.*?)</s_\1>", sub_total_match.group(1)):
                result['sub_total'][tag] = value

        # Parse total
        total_match = re.search(r"<s_total>(.*?)</s_total>", output_string, re.DOTALL)
        if total_match:
            result['total'] = {}
            for tag, value in re.findall(r"<s_(\w+)>(.*?)</s_\1>", total_match.group(1)):
                result['total'][tag] = value

        return result


# --- Main Execution ---
if __name__ == "__main__":

    # 1. Create an instance (loads both models)
    extractor = ReceiptExtractor()

    # 2. Define path
    receipt_path = 'receipt_2.png'

    # 3. Process
    extracted_data = extractor.process_receipt(receipt_path)

    # 4. Print results
    if extracted_data:
        print("\n--- Extracted & Categorized Data (JSON) ---")
        print(json.dumps(extracted_data, indent=2))

        print("\n--- Summary ---")
        for item in extracted_data.get('menu', []):
            name = item.get('nm', [''])[0].strip()
            cat = item.get('category', 'N/A')
            print(f"Item: {name:<20} | Category: {cat}")
    else:
        print(f"Could not process the receipt at {receipt_path}")