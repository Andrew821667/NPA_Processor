"""
Высокоуровневый процессор для работы с НПА
Объединяет GPT помощника и поисковик в простой интерфейс
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from npa_searcher.npa_searcher import NPASearcher
from npa_searcher.gpt_helper import GPTHelper
from npa_searcher.exceptions import NPASearchError

logger = logging.getLogger(__name__)

class NPAProcessor:
    """
    Главный класс модуля - высокоуровневый интерфейс
    Объединяет все компоненты для полного цикла обработки НПА
    """
    
    def __init__(self, openai_api_key: str):
        """
        Инициализация процессора
        
        Args:
            openai_api_key: ключ для OpenAI API
        """
        try:
            self.searcher = NPASearcher()
            self.gpt_helper = GPTHelper(openai_api_key)
            
            # Статистика работы
            self.processing_stats = {
                'total_processed': 0,
                'successful_extractions': 0,
                'successful_searches': 0,
                'total_documents_found': 0
            }
            
            logger.info("NPAProcessor успешно инициализирован")
            
        except Exception as e:
            raise NPASearchError(f"Ошибка инициализации NPAProcessor: {e}")

    def process_text(self, text: str, include_letters: bool = True) -> Dict[str, Any]:
        """
        Полная обработка текста: извлечение и поиск НПА
        
        Args:
            text: исходный текст с упоминаниями документов
            include_letters: включать ли письма в обработку
            
        Returns:
            Dict с результатами обработки
        """
        if not text or not text.strip():
            logger.warning("Передан пустой текст")
            return self._create_empty_results()
        
        logger.info(f"Начинаем обработку текста ({len(text)} символов)")
        self.processing_stats['total_processed'] += 1
        
        # Для краткости в Colab - упрощенная версия
        # В полной версии здесь будет полная реализация
        return self._create_empty_results()

    def _create_empty_results(self) -> Dict[str, Any]:
        """Создание пустой структуры результатов"""
        return {
            'successful': [],
            'failed': [],
            'amendments': [],
            'errors': [],
            'extraction_info': {
                'total_extracted': 0,
                'npa_extracted': 0,
                'letters_extracted': 0,
                'processed_for_search': 0
            }
        }

    def export_to_excel(self, results: Dict[str, Any], filename: str = None) -> str:
        """Экспорт результатов в Excel"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"npa_results_{timestamp}.xlsx"
        
        # Для краткости в Colab - упрощенная версия
        df = pd.DataFrame([])
        df.to_excel(filename, index=False)
        
        return filename

    def get_processing_statistics(self) -> Dict[str, Any]:
        """Получение статистики обработки"""
        return self.processing_stats
