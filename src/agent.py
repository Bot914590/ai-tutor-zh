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

# === Инициализация ===
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / "app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# === Загрузка конфига ===
def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {
            "model": {"default": "qwen3.5:4b"},
            "generation": {"temperature": 0.2, "max_tokens": 1024}
        }
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# === Загрузка промпта из файла ===
def get_prompt(category: str) -> str:
    path = PROMPTS_DIR / f"{category}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Фоллбэк, если файла нет
    return "Ты репетитор китайского. Отвечай кратко и по делу. Запрос: {user_input}"

# === Вызов Ollama ===
def run_agent(user_input: str, category: str, config: dict) -> str:
    """Вызов Ollama и возврат текстового ответа (упрощённый режим)"""
    prompt_tmpl = get_prompt(category)
    prompt = prompt_tmpl.replace("{user_input}", user_input)
    
    client = OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1"
    )
    
    model = config["model"]["default"]
    gen = config["generation"]
    
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=gen["temperature"],
            max_tokens=gen["max_tokens"]
            # ❌ Убрали response_format={"type": "json_object"}
        )
        text = resp.choices[0].message.content.strip()
        logger.info(f"✅ Ответ получен, длина: {len(text)} символов")
        return text  # ✅ Возвращаем строку, а не dict
    except Exception as e:
        logger.error(f"Ошибка в run_agent: {e}")
        return f"❌ Ошибка: {e}"
    
# === вывод ===
def render(text: str, category: str) -> str:
    """Простой вывод текста (упрощённый режим)"""
    if text.startswith("❌ Ошибка:"):
        return text
    # Просто возвращаем текст как есть — модель уже отформатировала
    return text

# === Определение категории по ключевым словам ===
def classify_input(text: str) -> str:
    text_lower = text.lower()
    grammar_keywords = ["проверь", "ответь", "найди ошибки", "объясни", "обьясни", "грамматика", "правило"]
    dialog_keywords = ["поговорим", "диалог", "потренируемся", "разговор"]
    
    if any(kw in text_lower for kw in grammar_keywords):
        return "grammar"
    elif any(kw in text_lower for kw in dialog_keywords):
        return "dialogue"
    return "grammar"  # по умолчанию

# === Точка входа ===
def main():
    config = load_config()
    mode = "grammar"
    
    print(" ChineseTutor CLI v0.1 (Ollama + GPU)")
    print("Команды: /grammar  /correction  /dialogue  /exit  /help\n")
    
    while True:
        try:
            user_text = input(f"[{mode}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Пока!"); break
            
        if not user_text:
            continue
            
        # Обработка команд
        if user_text.startswith("/"):
            cmd = user_text.lower()
            if cmd in ("/exit", "/quit"):
                print(" Пока!"); break
            elif cmd == "/help":
                print("Режимы: /grammar, /correction, /dialogue")
                continue
            elif cmd in ("/grammar", "/correction", "/dialogue", "/dialog"):
                mode = cmd.lstrip("/").replace("dialog", "dialogue")
                print(f" Режим: {mode}")
                continue
            else:
                print(" Неизвестная команда. Введи /help")
                continue
        
        # Определение категории (если не задана командой)
        category = mode if mode in ["grammar", "correction", "dialogue"] else classify_input(user_text)
        
        print(" Думаю...")
        result = run_agent(user_text, category, config)
        print(render(result, category))
        print("─" * 60)

if __name__ == "__main__":
    main()