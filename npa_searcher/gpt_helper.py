"""
GPT помощник для извлечения документов из неструктурированного текста
Использует OpenAI API для анализа текста и извлечения списка НПА
"""

import json
import time
import logging
from typing import List, Dict, Any
import openai
from npa_searcher.config import Config
from npa_searcher.exceptions import GPTError
from npa_searcher.utils import retry_request

logger = logging.getLogger(__name__)

class GPTHelper:
    """
    Класс для работы с GPT API
    Извлекает структурированную информацию о НПА из текста
    """
    
    def __init__(self, api_key: str, model: str = None):
        """
        Инициализация GPT помощника
        
        Args:
            api_key: ключ для OpenAI API
            model: модель GPT для использования
        """
        if not api_key:
            raise GPTError("OpenAI API ключ не может быть пустым")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model or Config.GPT_CONFIG['model']
        self.temperature = Config.GPT_CONFIG['temperature']
        self.max_tokens = Config.GPT_CONFIG['max_tokens']
        self.chunk_size = Config.GPT_CONFIG['chunk_size']
        
        logger.info(f"GPT Helper инициализирован с моделью {self.model}")

    def extract_documents(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Основная функция извлечения документов из текста
        
        Args:
            text: исходный текст с упоминаниями документов
            
        Returns:
            Dict с найденными документами по категориям
            
        Raises:
            GPTError: при ошибках работы с GPT API
        """
        if not text or not text.strip():
            logger.warning("Передан пустой текст")
            return {
                'all_documents': [],
                'npa_documents': [],
                'letters': []
            }
        
        logger.info(f"Начинаем извлечение документов из текста ({len(text)} символов)")
        
        # Для краткости в Colab - упрощенная версия
        # В полной версии здесь будет полная реализация
        return {
            'all_documents': [],
            'npa_documents': [],
            'letters': []
        }

    # Остальные методы для краткости опущены в Colab версии
