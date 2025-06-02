"""
Исключения для модуля поиска НПА
Иерархия ошибок для точной обработки различных ситуаций
"""

class NPASearchError(Exception):
    """
    Базовый класс исключений для модуля поиска НПА
    Все остальные исключения наследуются от него
    """
    
    def __init__(self, message: str, details: dict = None):
        """
        Инициализация исключения
        
        Args:
            message: описание ошибки
            details: дополнительные детали ошибки
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message

class APIError(NPASearchError):
    """
    Ошибки при работе с API pravo.gov.ru
    """
    
    def __init__(self, message: str, status_code: int = None, url: str = None):
        """
        Инициализация API ошибки
        
        Args:
            message: описание ошибки
            status_code: HTTP код ответа
            url: URL запроса
        """
        details = {}
        if status_code:
            details['status_code'] = status_code
        if url:
            details['url'] = url
            
        super().__init__(message, details)
        self.status_code = status_code
        self.url = url

class GPTError(NPASearchError):
    """
    Ошибки при работе с GPT API
    """
    pass

class ConfigError(NPASearchError):
    """
    Ошибки конфигурации модуля
    """
    pass

class DocumentNotFoundError(NPASearchError):
    """
    Документ не найден в системе
    """
    pass

class InvalidDocumentError(NPASearchError):
    """
    Некорректные данные документа
    """
    pass


# Добавлено для интеграции с профстандартами
class NPAError(Exception):
    """Базовый класс исключений для NPA модуля"""
    pass
