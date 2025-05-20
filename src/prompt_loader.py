import logging

import yaml

logger = logging.getLogger(__name__)

def load_prompt(prompt_name: str, file_path: str = "prompts.yaml") -> dict:
    """
    Loads prompts from a YAML file.

    Args:
        file_path (str): The path to the YAML file containing prompts.

    Returns:
        str: The prompt for the given prompt name.
    """
    prompts = {}
    try:
        with open(file_path, 'r') as f:
            loaded_yaml_prompts = yaml.safe_load(f)
            if isinstance(loaded_yaml_prompts, dict):
                prompts.update(loaded_yaml_prompts)
            else:
                logger.warning(f"YAML file '{file_path}' did not load as a dictionary.")
    except FileNotFoundError:
        logger.warning(f"Prompt file '{file_path}' not found.")
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file '{file_path}': {e}.")

    return prompts[prompt_name]

