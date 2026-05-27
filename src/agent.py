import os
import sys
import io
import json
import re
import yaml
import logging
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    if hasattr(sys.stdin, 'buffer'):
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "src" / "prompts"
CONFIG_PATH = BASE_DIR / "config.yaml"
LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "agent.log"
API_KEY_FILE = BASE_DIR / "api_key.txt"

def _load_api_key() -> str:
    """Сначала ищет ключ в переменной окружения OPENROUTER_API_KEY,
        затем в файле api_key.txt в корне проекта."""
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        return key.strip()
    if API_KEY_FILE.exists():
        return API_KEY_FILE.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        "API-ключ не найден"
    )

LOGS_DIR.mkdir(exist_ok=True) 

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),        
        logging.FileHandler(LOG_FILE, encoding='utf-8')  # запись в файл
    ]
)

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    else:
        config = {
            "model": {"default": "openai/gpt-4o-mini"},
            "generation": {"temperature": 0.2, "max_tokens": 1024}
        }

    return config

def run_agent(user_input:str, user_mode:str, config:dict) -> str: 
    def build_prompt() -> str: 
        if user_mode == "grammar":
            prompt = f"""
Ты — профессиональный репетитор китайского языка (уровни HSK 1–5). 
Твоя задача — объяснять грамматику четко, с примерами и контрастами.

ИНСТРУКЦИЯ (рассуждай по шагам внутри):
1. Определи грамматическую структуру.
2. Сформулируй правило на русском (1–2 предложения).
3. Дай 2 примера: с конструкцией и без неё.
4. Укажи типичную ошибку русскоговорящих.
5. Определи уровень HSK.

Запрос: {user_input}
Ответ: 
            """
            return prompt    
        elif user_mode == "dialog":
            prompt = f"""
Ты — профессиональный репетитор китайского языка (уровни HSK 1–5). 
Твоя задача — вести диалог с пользователем определив уровень и подстроиться под контекст.

ИНСТРУКЦИЯ (рассуждай по шагам внутри):
1. Определи контекст.
2. Определи уровень.
3. Сформулируй ответ на русском (1–2 предложения).
4. Не указывай на ошибки, если не понятен смысл, пробуй понять по контексту.

Запрос: {user_input}
Ответ:
            """
            return prompt    
        else:
            logging.error(f"Неизвестный режим: {user_mode}")
            return f"Неизвестный режим: {user_mode}. Используйте /grammar или /dialog."
    
    client = OpenAI(
        api_key=_load_api_key(),
        base_url="https://openrouter.ai/api/v1",
        timeout=60,
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "AI Chinese Tutor"
        }
    )
    model = config["model"]["default"]
    gen = config["generation"]

    try:
        prompt = build_prompt()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=gen["temperature"],
            max_tokens=gen["max_tokens"]
        )
        result = response.choices[0].message.content
        return result
    except Exception as e: 
        logging.error(f"Ошибка в run_agent: {e}")
        return "Не удалось получить ответ"

def main():
    config = load_config()
    user_mode = "grammar" #default
    user_message = "введите /grammar или /dialog"
    print(user_message)
    
    while True:
        
        user_input = input(f"[{user_mode}] > ").strip()
    
        if user_input.startswith("/"):
            if user_input in ["/grammar", "/dialog"]:
                user_mode = user_input.lstrip("/")
                print(f"Режим: {user_mode}")
            continue
    
        result = run_agent(user_input, user_mode, config)
        print(result)
        logging.info(f"Ответ от модели: {result}")

if __name__ == "__main__":
    main()
