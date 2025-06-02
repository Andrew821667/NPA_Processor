"""
Загрузчик профессиональных стандартов
Интегрирован с архитектурой NPA_Processor
"""

import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import logging
from typing import Dict, List, Optional
import re

# Простое логирование без сложных зависимостей
logger = logging.getLogger(__name__)

# Безопасные импорты из родительского модуля
try:
    from ..exceptions import NPAError
except ImportError:
    # Fallback если NPAError не найден
    class NPAError(Exception):
        pass

try:
    from ..utils import validate_response
except ImportError:
    # Fallback для валидации ответов
    def validate_response(response):
        response.raise_for_status()

class ProfstandardDownloadError(NPAError):
    """Ошибка загрузки профстандарта"""
    pass

class ProfstandardDownloader:
    """
    Загрузчик профессиональных стандартов из официальных источников
    Интегрирован с конфигурацией NPA_Processor
    """
    
    def __init__(self, config=None):
        self.config = config
        self.output_dir = Path('data/profstandards')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Проверенные рабочие источники
        self.sources = {
            'fgosvo': 'https://fgosvo.ru/uploadfiles/profstandart/{code}.pdf',
            'registry': 'http://classinform.ru/profstandarty/reestr_professionalnyh_standartov.xls'
        }
        
        # Настройка сессии
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf,text/html,application/xhtml+xml,*/*'
        })
        
        self.timeout = 30
        self.delay = 2.0
    
    def get_registry(self) -> List[Dict]:
        """Получить реестр профстандартов"""
        logger.info("Загружаем реестр профстандартов...")
        
        try:
            response = self.session.get(self.sources['registry'], timeout=self.timeout)
            validate_response(response)
            
            # Сохраняем Excel
            excel_path = self.output_dir / f"registry_{datetime.now().strftime('%Y%m%d')}.xls"
            with open(excel_path, 'wb') as f:
                f.write(response.content)
            
            # Читаем данные
            df = pd.read_excel(excel_path, engine='xlrd')
            
            profstandards = []
            for _, row in df.iterrows():
                ps = {
                    'code': str(row.get('Код', '')).strip(),
                    'name': str(row.get('Наименование', '')).strip(),
                    'area': str(row.get('Область', '')).strip(),
                    'status': str(row.get('Статус', '')).strip(),
                    'order': str(row.get('Приказ', '')).strip(),
                    'date': str(row.get('Дата', '')).strip()
                }
                if ps['code'] and ps['name'] and self._validate_code(ps['code']):
                    profstandards.append(ps)
            
            logger.info(f"Загружен реестр: {len(profstandards)} профстандартов")
            return profstandards
            
        except Exception as e:
            logger.error(f"Ошибка загрузки реестра: {e}")
            raise ProfstandardDownloadError(f"Не удалось загрузить реестр: {e}")
    
    def download_pdf(self, code: str) -> Optional[bytes]:
        """Скачать PDF профстандарта"""
        if not self._validate_code(code):
            raise ProfstandardDownloadError(f"Некорректный код профстандарта: {code}")
        
        url = self.sources['fgosvo'].format(code=code)
        logger.info(f"Скачиваем профстандарт {code} из {url}")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Проверяем что это PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type or len(response.content) > 10000:
                    logger.info(f"Профстандарт {code} загружен ({len(response.content):,} байт)")
                    return response.content
                else:
                    logger.warning(f"Получен файл неподходящего формата для {code}")
            elif response.status_code == 404:
                logger.warning(f"Профстандарт {code} не найден (HTTP 404)")
            else:
                logger.warning(f"Ошибка загрузки {code}: HTTP {response.status_code}")
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка скачивания {code}: {e}")
            return None
    
    def save_profstandard(self, code: str, content: bytes) -> str:
        """Сохранить профстандарт"""
        filename = f"PS_{code.replace('.', '_')}.pdf"
        filepath = self.output_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        logger.info(f"Профстандарт {code} сохранен: {filename}")
        return str(filepath)
    
    def download_multiple(self, codes: List[str]) -> Dict[str, str]:
        """Скачать несколько профстандартов"""
        results = {}
        
        for i, code in enumerate(codes, 1):
            logger.info(f"[{i}/{len(codes)}] Обрабатываем {code}")
            
            try:
                pdf_content = self.download_pdf(code)
                
                if pdf_content:
                    filepath = self.save_profstandard(code, pdf_content)
                    results[code] = {'status': 'success', 'file': filepath}
                else:
                    results[code] = {'status': 'not_found', 'file': None}
                    
            except Exception as e:
                logger.error(f"Ошибка обработки {code}: {e}")
                results[code] = {'status': 'error', 'error': str(e)}
            
            # Задержка между запросами
            if i < len(codes):
                time.sleep(self.delay)
        
        return results
    
    def _validate_code(self, code: str) -> bool:
        """Валидация кода профстандарта"""
        pattern = r'^\d{2}\.\d{3}$'
        return bool(re.match(pattern, code))
    
    def get_statistics(self) -> Dict:
        """Получить статистику загруженных профстандартов"""
        pdf_files = list(self.output_dir.glob('PS_*.pdf'))
        
        return {
            'total_files': len(pdf_files),
            'total_size': sum(f.stat().st_size for f in pdf_files),
            'latest_file': max(pdf_files, key=lambda f: f.stat().st_mtime).name if pdf_files else None,
            'output_dir': str(self.output_dir)
        }
