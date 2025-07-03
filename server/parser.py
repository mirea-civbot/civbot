import os
import re
import wikipediaapi


PAGE_TITLE = "Sid Meier’s Civilization VI"
WIKI_LANGUAGE = 'ru'

OUTPUT_DIR = "data_civ6_ru"

def setup_wiki_api(language):
    """Настраивает wikipedia-api для работы с нужным языком."""
    user_agent = "MyKnowledgeBaseBuilder/1.0"
    wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language=language)
    return wiki

def clean_content(text):
    text = re.sub(r'\{\{.*?\}\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[(Файл|Изображение|File|Image):.*?\]\]', '', text, flags=re.IGNORECASE)
    text = re.split(r'==\s*(Примечания|См. также|Литература|Ссылки)\s*==', text, 1)[0]
    text = re.sub(r'\[\[[^|\]]*?\|(.*?)\]\]', r'\1', text)
    text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)
    text = text.replace("'''", "").replace("''", "")
    text = re.sub(r'<.*?>', '', text, flags=re.DOTALL)
    text = re.sub(r'==+\s*(.*?)\s*==+', r'\n\n\\1\n', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

def main():
    wiki = setup_wiki_api(WIKI_LANGUAGE)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Создана директория: {OUTPUT_DIR}")

    try:
        page = wiki.page(PAGE_TITLE)
        
        if not page.exists():
            print(f"ОШИБКА: Страница '{PAGE_TITLE}' не найдена на {WIKI_LANGUAGE}.wikipedia.org")
            return

        print("-> Страница найдена. Скачиваю и очищаю контент...")
        
        cleaned_text = clean_content(page.text)
        
        if not cleaned_text or len(cleaned_text) < 100:
            print("-> ОШИБКА: Не удалось извлечь достаточно контента после очистки.")
            return

        safe_filename = re.sub(r'[\\/*?:"<>|]', "", PAGE_TITLE) + ".txt"
        filepath = os.path.join(OUTPUT_DIR, safe_filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
            
        print(f"УСПЕХ! Статья сохранена в файл: {filepath}")

    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")

if __name__ == "__main__":
    main()