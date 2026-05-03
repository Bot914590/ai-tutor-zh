import os
import json
import re
import yaml
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
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    else:
        config = {
            "model": {"default": "qwen3.5:4b"},
            "generation": {"temperature": 0.2, "max_tokens": 1024}
}

    return config

def run_agent(user_input:str, user_mode:str, config:dict) -> str: 
    def build_prompt(): #версия пока без json
        if user_mode == "/grammar":
            prompt = """
Ты — профессиональный репетитор китайского языка (уровни HSK 1–5). 
Твоя задача — объяснять грамматику четко, с примерами и контрастами.

ИНСТРУКЦИЯ (рассуждай по шагам внутри):
1. Определи грамматическую структуру.
2. Сформулируй правило на русском (1–2 предложения).
3. Дай 2 примера: с конструкцией и без неё.
4. Укажи типичную ошибку русскоговорящих.
5. Определи уровень HSK.

ПРИМЕР:
Запрос: {user_input}
Ответ: ###ДОБАВТЬ ПРИМЕРЫ НУЖНО###

                    """
        elif user_mode == "/dialog":
            prompt = """
Ты — профессиональный репетитор китайского языка (уровни HSK 1–5). 
Твоя задача — вести диалог с пользователем определив уровень и подстроиться под контекст.

ИНСТРУКЦИЯ (рассуждай по шагам внутри):
1. Определи контекст.
2. определи уровень.
3. Сформулируй ответ на русском (1–2 предложения).
4. Не указывай на ошибки, если не понятен смысл пробуй понять по контексту.


ПРИМЕР:
Запрос: ""
Ответ: 
                    """
            
        return prompt
    
    client = OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1"
    )
    model = config["model"]["default"]
    gen = config["generation"]

    try:
        response = client.chat.completions.create(
            model=config["model"],  # "qwen3.5:4b"
            messages=[{"role": "user", "content": build_prompt()}],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"]
        )
        result = response.choices[0].message.content
        return result
    except Exception as e: 
        logging.error(f"Ошибка в run_agent: {e}")
        return "Не удалось получить ответ. Проверьте, запущен ли Ollama."


def main():
    config = load_config()
    user_mode = "/grammar" #default
    user_massage = "введите /grammar или /dialog"
    
    while True:
        print(user_massage)
        user_input = input(f"[{user_mode}] > ").strip()
    
        if user_input.startswith("/"):
            if user_input in ["/grammar", "/dialog"]:
                user_mode = user_input.lstrip("/")
                print(f"Режим: {user_mode}")
            continue
    

        result = run_agent(user_input, user_mode, config)
        print(result)

if __name__ == "__main__":
    main()