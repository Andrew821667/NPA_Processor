"""
Модуль для поиска нормативно-правовых актов (НПА)
Использует официальный API publication.pravo.gov.ru и GPT для извлечения документов
"""

# Импортируем основные классы из соответствующих модулей
from npa_searcher.processor import NPAProcessor
from npa_searcher.npa_searcher import NPASearcher
from npa_searcher.gpt_helper import GPTHelper
from npa_searcher.config import Config
from npa_searcher.exceptions import NPASearchError, APIError

# Версия модуля
__version__ = "1.0.0"

# Автор
__author__ = "Andrew_Popov"

# Описание
__description__ = "Модуль для поиска российских нормативно-правовых актов"

# Что доступно при импорте модуля (import *)
__all__ = [
    "NPAProcessor",    # Главный класс для пользователей
    "NPASearcher",     # Поисковик НПА через API
    "GPTHelper",       # GPT помощник для извлечения документов
    "Config",          # Конфигурация модуля
    "NPASearchError",  # Базовая ошибка модуля
    "APIError",        # Ошибка API
]
