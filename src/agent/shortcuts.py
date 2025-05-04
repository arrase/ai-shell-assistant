import os
import yaml
import re


class Shortcuts:
    def __init__(self, directory_path: str):
        self.__shortcuts = {}
        self._placeholder = "{REPLACE}"

        for filename in os.listdir(directory_path):
            if filename.lower().endswith(('.yaml', '.yml')):
                file_path = os.path.join(directory_path, filename)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = yaml.safe_load(f)

                            if isinstance(data, dict) and 'shortcut' in data and 'prompt' in data:
                                shortcut_key = data['shortcut']
                                prompt_value = data['prompt']

                                if isinstance(shortcut_key, str) and isinstance(prompt_value, str):
                                    if shortcut_key in self.__shortcuts:
                                        print(f"Warning: Duplicate shortcut '{shortcut_key}' "
                                              f"(found in '{filename}'). It will be overwritten.")
                                    self.__shortcuts[shortcut_key] = prompt_value
                                else:
                                    print(f"Warning: The format of 'shortcut' or 'prompt' is not a string "
                                          f"in the file '{filename}'. Skipping.")
                            else:
                                print(f"Warning: Invalid format in the file '{filename}'. "
                                      f"It must contain 'shortcut' and 'prompt'. Skipping.")
                    except yaml.YAMLError as e:
                        print(
                            f"Error parsing the YAML file '{filename}': {e}")
                    except Exception as e:
                        print(
                            f"Error processing the file '{filename}': {e}")

    def get_prompt(self, input_string: str) -> str | bool:
        match = re.match(r"^@(\S+)(?:\s+(.*))?$", input_string)

        if match:
            shortcut_key = match.group(1)
            replacement_text = match.group(2)
            if shortcut_key in self.__shortcuts:
                return self.__shortcuts[shortcut_key].replace(self._placeholder, replacement_text)
            else:
                return False
        else:
            return False
