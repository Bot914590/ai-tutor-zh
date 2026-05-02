import os
import json
import re
from lxml import etree
import logging
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# === Настройка путей ===
BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "src" / "prompts"
CONFIG_PATH = BASE_DIR / "config.yaml"

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        tree = etree.parse('file.xml')
        root = tree.getroot()
        model = root.xpath("//model/default")
        generation = 

def build_ptompt():
    pass

def main():
    config = load_config()
    user_mode = ""

    while True:
        user_input = input()

        if user_input == "/grammar":
            user_mode == "grammar"
        elif user_input == "/dialog":
            user_mode = "dialog"
        elif user_input != "/dialog" & "/grammar":
            user_mode = "none"
            user_massage = "Неверно, введите /grammar или /dialog"

        result = run_agent(user_input, user_mode, config)
        print(render(result["response"])) # рендер будет выводить в json и сдесь выводится только ответ остальное в логи

if __name__ == "__main__":
    main()