import os
import yaml
import re
import logging


class Shortcuts:
    def __init__(self, directory_path: str, logging_level="INFO"):
        self.__shortcuts = {}
        self._placeholder = "{REPLACE}"

        logging.basicConfig(level=getattr(
            logging, logging_level.upper(), logging.INFO))

        for filename in filter(lambda f: f.lower().endswith(('.yaml', '.yml')), os.listdir(directory_path)):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                self._load_shortcut(file_path, filename)

    def _load_shortcut(self, file_path: str, filename: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if isinstance(data, dict) and 'shortcut' in data and 'prompt' in data:
                shortcut_key, prompt_value = data['shortcut'], data['prompt']
                if isinstance(shortcut_key, str) and isinstance(prompt_value, str):
                    if shortcut_key in self.__shortcuts:
                        logging.warning(
                            f"Duplicate shortcut '{shortcut_key}' in '{filename}'. Overwriting.")
                    self.__shortcuts[shortcut_key] = prompt_value
                else:
                    logging.warning(
                        f"Invalid 'shortcut' or 'prompt' format in '{filename}'. Skipping.")
            else:
                logging.warning(
                    f"Invalid format in '{filename}'. Missing 'shortcut' or 'prompt'. Skipping.")
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML file '{filename}': {e}")
        except Exception as e:
            logging.error(f"Error processing file '{filename}': {e}")

    def get_prompt(self, input_string: str) -> str | bool:
        match = re.match(r"^@(\S+)(?:\s+(.*))?$", input_string)
        if match:
            shortcut_key, replacement_text = match.group(1), match.group(2)
            return self.__shortcuts.get(shortcut_key, False).replace(self._placeholder, replacement_text or "")
        return False
