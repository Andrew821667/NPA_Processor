"""
NPA Searcher - Модуль для поиска российских нормативно-правовых актов
Расширен поддержкой профессиональных стандартов
"""

# Основные импорты
from .npa_searcher import NPASearcher
from .processor import NPAProcessor
from .gpt_helper import GPTHelper
from .config import Config

# Безопасный импорт исключений
try:
    from .exceptions import NPAError
except ImportError:
    class NPAError(Exception):
        pass

# Безопасный импорт утилит
try:
    from .utils import setup_logging
except ImportError:
    import logging
    def setup_logging(name):
        return logging.getLogger(name)

# Импорт подмодуля профстандартов
try:
    from . import profstandards
    from .profstandards import (
        ProfstandardDownloader,
        ProfstandardParser,
        ProfstandardAnalyzer
    )
    PROFSTANDARDS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Профстандарты недоступны: {e}")
    PROFSTANDARDS_AVAILABLE = False

__version__ = "1.1.0"
__author__ = "Andrew_Popov"

# Основные классы
__all__ = [
    'NPASearcher',
    'NPAProcessor', 
    'GPTHelper',
    'Config',
    'NPAError',
    'setup_logging'
]

if PROFSTANDARDS_AVAILABLE:
    __all__.extend([
        'ProfstandardDownloader',
        'ProfstandardParser',
        'ProfstandardAnalyzer',
        'profstandards'
    ])

# Упрощенная функция для создания загрузчика профстандартов
def create_profstandard_downloader():
    """Создать загрузчик профстандартов"""
    if not PROFSTANDARDS_AVAILABLE:
        raise ImportError("Модуль профстандартов недоступен")
    
    return ProfstandardDownloader()

# Быстрая функция для поиска профстандартов
def quick_profstandard_search(keywords):
    """
    Быстрый поиск профстандартов по ключевым словам (заглушка)
    """
    if not PROFSTANDARDS_AVAILABLE:
        return []
    
    # Пока возвращаем заглушку
    if isinstance(keywords, str):
        keywords = [keywords]
    
    # Имитация результатов поиска
    mock_results = [
        {
            'code': '01.001',
            'name': 'Педагог (педагогическая деятельность в сфере дошкольного, начального общего, основного общего, среднего общего образования)',
            'area': 'Образование и наука',
            'status': 'действует',
            'relevance': 0.9,
            'matched_keywords': [kw for kw in keywords if kw.lower() in 'педагог учитель']
        },
        {
            'code': '06.015',
            'name': 'Специалист по информационным системам',
            'area': 'Связь, информационные и коммуникационные технологии',
            'status': 'действует',
            'relevance': 0.8,
            'matched_keywords': [kw for kw in keywords if kw.lower() in 'программист информационные системы']
        }
    ]
    
    # Фильтруем результаты по ключевым словам
    filtered_results = []
    for result in mock_results:
        for keyword in keywords:
            if keyword.lower() in result['name'].lower() or keyword.lower() in result['area'].lower():
                if result not in filtered_results:
                    filtered_results.append(result)
                break
    
    return filtered_results
