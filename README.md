# NPA Processor

Модуль для поиска российских нормативно-правовых актов (НПА) с использованием официального API publication.pravo.gov.ru и GPT для извлечения документов из текста.

## Автор
**Andrew_Popov**

## Возможности

- 🔍 **Извлечение НПА из текста**: Использует GPT для автоматического извлечения упоминаний документов
- 📋 **Поиск в официальной базе**: Ищет документы через API publication.pravo.gov.ru
- 🎯 **Умная оценка релевантности**: Сложный алгоритм скоринга для точных результатов
- 📊 **Экспорт в Excel**: Создание подробных отчетов с результатами поиска
- 🚀 **Множественные стратегии поиска**: Поиск по номеру, названию, базе знаний

## Установка

```bash
pip install -r requirements.txt
```

## Быстрый старт

```python
from npa_searcher import NPAProcessor

# Инициализация (требуется OpenAI API ключ)
processor = NPAProcessor(openai_api_key="your-api-key")

# Обработка текста
text = """
В соответствии с Федеральным законом №273-ФЗ "Об образовании в РФ" 
и Постановлением Правительства №1490...
"""

results = processor.process_text(text)

# Экспорт в Excel
filename = processor.export_to_excel(results)
print(f"Результаты сохранены в {filename}")
```

## Структура результатов

```python
{
    'successful': [],     # Найденные основные НПА
    'amendments': [],     # Найденные изменения к НПА
    'failed': [],        # Не найденные документы
    'errors': [],        # Ошибки поиска
    'extraction_info': {
        'total_extracted': 0,
        'npa_extracted': 0,
        'letters_extracted': 0
    }
}
```

## Поддерживаемые типы документов

- Федеральные законы (ФЗ)
- Постановления Правительства РФ
- Приказы министерств и ведомств
- Указы Президента РФ
- Письма и разъяснения
- Кодексы (ГК РФ, УК РФ и т.д.)
- Положения, регламенты, стандарты

## Компоненты модуля

### NPAProcessor
Главный класс для пользователей. Объединяет извлечение и поиск в простом интерфейсе.

### NPASearcher
Поисковик НПА через официальный API. Реализует множественные стратегии поиска.

### GPTHelper
GPT помощник для извлечения документов из неструктурированного текста.

## Примеры использования

### Поиск конкретного документа

```python
from npa_searcher import NPASearcher

searcher = NPASearcher()

document = {
    'type': 'Федеральный закон',
    'number': '273-ФЗ',
    'title': 'Об образовании в Российской Федерации'
}

results = searcher.search_document(document)
for result in results:
    print(f"Найден: {result['name']}")
    print(f"EO номер: {result['eoNumber']}")
    print(f"Score: {result['score']}")
```

### Только извлечение документов

```python
from npa_searcher import GPTHelper

gpt = GPTHelper(api_key="your-key")

text = "Согласно ФЗ №44 и постановлению №1490..."
extracted = gpt.extract_documents(text)

print(f"Найдено документов: {len(extracted['all_documents'])}")
```

## Настройки

Все настройки находятся в `npa_searcher/config.py`:

- API endpoints
- Параметры скоринга
- Настройки GPT
- База знаний известных документов

## Требования

- Python 3.8+
- OpenAI API ключ
- Интернет-соединение для доступа к API

## Лицензия

MIT License

## Поддержка

Для вопросов и предложений создавайте issues в GitHub репозитории.
