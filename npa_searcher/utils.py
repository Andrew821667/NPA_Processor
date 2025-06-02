"""
Утилиты для модуля поиска НПА
Вспомогательные функции общего назначения
"""

import re
import time
import logging
from typing import List, Dict, Any, Callable, Optional
from npa_searcher.config import Config
from npa_searcher.exceptions import APIError

# Настройка логирования
logger = logging.getLogger(__name__)

def clean_number(number: str) -> str:
    """
    Очистка номера документа от лишних символов
    
    Args:
        number: исходный номер документа
        
    Returns:
        str: очищенный номер
        
    Example:
        >>> clean_number("№ 273-ФЗ")
        "273-ФЗ"
        >>> clean_number("N 1490")
        "1490"
    """
    if not number:
        return ""
    
    # Убираем символы номера и пробелы
    clean = re.sub(r'[№N\s]+', '', number)
    # Убираем дефисы в начале
    clean = re.sub(r'^-+', '', clean)
    # Убираем лишние пробелы
    return clean.strip()

def is_amendment(text: str, keywords: List[str] = None) -> bool:
    """
    Проверка, является ли документ изменением к основному НПА
    
    Args:
        text: название документа
        keywords: ключевые слова для поиска (по умолчанию из конфига)
        
    Returns:
        bool: True если документ является изменением
        
    Example:
        >>> is_amendment("О внесении изменений в ФЗ №273")
        True
        >>> is_amendment("О образовании в РФ")
        False
    """
    if not text:
        return False
    
    if keywords is None:
        keywords = Config.AMENDMENT_KEYWORDS
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)

def retry_request(func: Callable, max_retries: int = None, 
                 base_delay: float = None, backoff_factor: float = None) -> Any:
    """
    Механизм повторных попыток для HTTP запросов
    
    Args:
        func: функция для выполнения
        max_retries: максимальное количество попыток
        base_delay: базовая задержка между попытками
        backoff_factor: множитель увеличения задержки
        
    Returns:
        результат выполнения функции
        
    Raises:
        последнее исключение если все попытки неудачны
    """
    # Используем настройки из конфига если не переданы
    config = Config.RETRY_CONFIG
    max_retries = max_retries or config['max_retries']
    base_delay = base_delay or config['base_delay']
    backoff_factor = backoff_factor or config['backoff_factor']
    max_delay = config['max_delay']
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Попытка {attempt + 1}/{max_retries}")
            return func()
            
        except Exception as e:
            last_exception = e
            
            # Если это последняя попытка - поднимаем исключение
            if attempt == max_retries - 1:
                logger.error(f"Все {max_retries} попыток неудачны. Последняя ошибка: {e}")
                break
            
            # Вычисляем задержку с экспоненциальным backoff
            delay = min(base_delay * (backoff_factor ** attempt), max_delay)
            
            logger.warning(f"Попытка {attempt + 1} неудачна: {e}. Повтор через {delay:.1f}с")
            time.sleep(delay)
    
    # Поднимаем последнее исключение
    raise last_exception

def validate_document_data(document: Dict[str, Any]) -> bool:
    """
    Валидация данных документа
    
    Args:
        document: словарь с данными документа
        
    Returns:
        bool: True если данные корректны
        
    Raises:
        InvalidDocumentError: если данные некорректны
    """
    from npa_searcher.exceptions import InvalidDocumentError
    
    if not isinstance(document, dict):
        raise InvalidDocumentError("Документ должен быть словарем")
    
    required_fields = ['type', 'number']
    for field in required_fields:
        if field not in document:
            raise InvalidDocumentError(f"Отсутствует обязательное поле: {field}")
        if not document[field]:
            raise InvalidDocumentError(f"Поле {field} не может быть пустым")
    
    # Проверяем, что номер не слишком общий
    number = document['number']
    if len(clean_number(number)) <= 1:
        raise InvalidDocumentError(f"Номер документа слишком короткий: {number}")
    
    return True

def format_score_explanation(score: int, details: Dict[str, Any]) -> str:
    """
    Форматирование объяснения оценки релевантности
    
    Args:
        score: итоговая оценка
        details: детали расчета оценки
        
    Returns:
        str: человекочитаемое объяснение оценки
    """
    explanation = f"Итоговая оценка: {score}\n"
    
    if details.get('exact_match'):
        explanation += "✓ Точное совпадение номера (+8000)\n"
    elif details.get('clean_match'):
        explanation += "✓ Совпадение очищенного номера (+7000)\n"
    elif details.get('partial_match'):
        explanation += "✓ Частичное совпадение номера (+6000)\n"
    
    title_matches = details.get('title_matches', 0)
    if title_matches >= 3:
        explanation += f"✓ Отличное совпадение названия ({title_matches} слов, +3000)\n"
    elif title_matches >= 2:
        explanation += f"✓ Хорошее совпадение названия ({title_matches} слов, +1500)\n"
    elif title_matches >= 1:
        explanation += f"✓ Частичное совпадение названия ({title_matches} слов, +500)\n"
    
    if details.get('is_amendment'):
        explanation += "⚠ Документ является изменением (штраф)\n"
    
    if details.get('year_bonus'):
        explanation += f"✓ Бонус за актуальность (+{details['year_bonus']})\n"
    
    return explanation

def setup_logging(level: str = "INFO") -> None:
    """
    Настройка логирования для модуля
    
    Args:
        level: уровень логирования (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
