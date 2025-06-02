"""
Конфигурация для подмодуля профстандартов
"""

# Настройки по умолчанию для профстандартов
PROFSTANDARDS_CONFIG = {
    # Директории
    'profstandards.data_dir': 'data/profstandards',
    'profstandards.cache_dir': 'cache/profstandards',
    
    # Источники данных
    'profstandards.sources.fgosvo': 'https://fgosvo.ru/uploadfiles/profstandart/{code}.pdf',
    'profstandards.sources.registry': 'http://classinform.ru/profstandarty/reestr_professionalnyh_standartov.xls',
    
    # Настройки загрузки
    'profstandards.timeout': 30,
    'profstandards.retry_count': 3,
    'profstandards.delay_between_requests': 2.0,
    
    # Настройки парсинга
    'profstandards.extract_images': False,
    'profstandards.extract_tables': True,
    'profstandards.min_text_length': 1000,
    
    # GPT настройки для профстандартов
    'profstandards.gpt.model': 'gpt-3.5-turbo',
    'profstandards.gpt.max_tokens': 2000,
    'profstandards.gpt.temperature': 0.1,
}

def update_config_with_profstandards(config):
    """Обновить основной конфиг настройками профстандартов"""
    for key, value in PROFSTANDARDS_CONFIG.items():
        if not config.get(key):
            config.set(key, value)
    return config
