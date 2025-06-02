"""
Конфигурация модуля поиска НПА
Содержит все настройки, константы и базу знаний
"""

class Config:
    """
    Основной класс конфигурации
    Все настройки модуля собраны здесь
    """
    
    # URL официального API для поиска НПА
    API_BASE_URL = "http://publication.pravo.gov.ru/api"
    
    # HTTP заголовки для имитации браузера
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # База знаний известных документов
    KNOWN_DOCUMENTS = {
        '1490': {
            'keywords': ['лицензировани', 'образовательн'],
            'eo_hints': ['0001202009250006'],
            'description': 'О лицензировании образовательной деятельности'
        },
        '825': {
            'keywords': ['федеральной информационной системе', 'фрдо'],
            'eo_hints': [],
            'description': 'О федеральной информационной системе ФРДО'
        },
        '580': {
            'keywords': ['профессиональн', 'стандарт'],
            'eo_hints': ['0001202304110042'],
            'description': 'О разработке и утверждении профессиональных стандартов'
        },
        '719': {
            'keywords': ['государственной информационной системе'],
            'eo_hints': [],
            'description': 'О государственной информационной системе'
        },
        '273-фз': {
            'keywords': ['образовани', 'российской федерации'],
            'eo_hints': ['0001201212300007'],
            'description': 'Об образовании в Российской Федерации'
        }
    }
    
    # Ключевые слова для определения изменений в НПА
    AMENDMENT_KEYWORDS = [
        'изменени', 'дополнени', 'внесени', 'признании утратившим',
        'о внесении', 'изменения в', 'дополнения в', 'о признании',
        'утратившим силу', 'изменить', 'дополнить', 'отменить',
        'приостановить действие', 'продлить действие'
    ]
    
    # Настройки для retry механизма
    RETRY_CONFIG = {
        'max_retries': 3,
        'base_delay': 1.0,
        'max_delay': 10.0,
        'backoff_factor': 2.0
    }
    
    # Настройки для GPT
    GPT_CONFIG = {
        'model': 'gpt-3.5-turbo',
        'temperature': 0.1,
        'max_tokens': 4000,
        'chunk_size': 6000
    }
    
    # Настройки скоринга релевантности
    SCORING_CONFIG = {
        'exact_number_match': 8000,
        'clean_number_match': 7000,
        'partial_number_match': 6000,
        'title_match_3_words': 3000,
        'title_match_2_words': 1500,
        'title_match_1_word': 500,
        'type_match_bonus': 400,
        'amendment_penalty': 1000,
        'general_number_penalty': 2000,
        'min_score_threshold': 500
    }
