from pathlib import Path
import yaml
import re
import logging
from typing import Dict, Union


class Shortcuts:
    def __init__(self, directory_path: str, logging_level: str = "INFO") -> None:
        """Initializes the Shortcuts class and loads all shortcut definitions.

        Scans the specified directory for .yaml or .yml files, parses them,
        and stores the defined shortcuts.

        Args:
            directory_path: The path to the directory containing shortcut files.
            logging_level: The logging level string (e.g., "INFO", "DEBUG").
                           (Note: logging is now centralized, this parameter is for compatibility).
        """
        self.__shortcuts: Dict[str, str] = {}
        self._placeholder: str = "{REPLACE}"

        # logging.basicConfig is already centralized in assistant.py
        # logging_level parameter is kept for compatibility during refactor, but not used.

        dir_path_obj = Path(directory_path)
        if not dir_path_obj.is_dir():
            logging.error(f"Shortcuts directory not found or is not a directory: {directory_path}")
            return

        for file_path_obj in dir_path_obj.iterdir():
            if file_path_obj.is_file() and file_path_obj.suffix.lower() in ('.yaml', '.yml'):
                self._load_shortcut(file_path_obj)

    def _load_shortcut(self, file_path: Path) -> None:
        """Loads shortcuts from a single YAML file.

        Parses the YAML file, validates its structure, and stores valid
        shortcuts. Logs warnings for duplicates or invalid formats and
        errors for parsing issues.

        Args:
            file_path: The path to the .yaml or .yml shortcut file.
        """
        filename_for_logging: str = file_path.name
        try:
            # Path object can be used directly with open
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if isinstance(data, dict) and 'shortcut' in data and 'prompt' in data:
                shortcut_key, prompt_value = data['shortcut'], data['prompt']
                if isinstance(shortcut_key, str) and isinstance(prompt_value, str):
                    if shortcut_key in self.__shortcuts:
                        logging.warning(
                            f"Duplicate shortcut '{shortcut_key}' in '{filename_for_logging}'. Overwriting.")
                    self.__shortcuts[shortcut_key] = prompt_value
                else:
                    logging.warning(
                        f"Invalid 'shortcut' or 'prompt' format in '{filename_for_logging}'. Skipping.")
            else:
                logging.warning(
                    f"Invalid format in '{filename_for_logging}'. Missing 'shortcut' or 'prompt'. Skipping.")
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML file '{filename_for_logging}': {e}")
        except Exception as e:
            logging.error(f"Error processing file '{filename_for_logging}': {e}")

    def get_prompt(self, input_string: str) -> Union[str, bool]:
        """Resolves an input string into a prompt using loaded shortcuts.

        If the input string starts with '@' followed by a known shortcut key,
        it replaces the key (and optionally a placeholder within the prompt)
        with the corresponding prompt template.

        Args:
            input_string: The user input string, potentially a shortcut command
                          (e.g., "@shortcut_key some text").

        Returns:
            The resolved prompt string if a shortcut is matched and found,
            otherwise False.
        """
        match = re.match(r"^@(\S+)(?:\s+(.*))?$", input_string)
        if match:
            shortcut_key: str = match.group(1)
            replacement_text: Union[str, None] = match.group(2)
            prompt_template = self.__shortcuts.get(shortcut_key)
            if prompt_template:
                return prompt_template.replace(self._placeholder, replacement_text or "")
            return False
        return False
