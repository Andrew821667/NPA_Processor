
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from typing import Dict, List, Optional, Any

class OfficialPravoGovParser:
    """
    Парсер ТОЛЬКО для официального pravo.gov.ru
    Поиск актуальных версий НПА в СПС "Законодательство России"
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Только официальные endpoints
        self.base_urls = [
            "http://publication.pravo.gov.ru/",
            "http://pravo.gov.ru/",
            "https://pravo.gov.ru/"
        ]
        
        # Известные структуры URL для СПС
        self.ips_patterns = [
            "/ips/",
            "/ips/ext_search.html",
            "/ips/?search=",
            "/ips/?docbody=&nd=",
            "/ips/?search_base=LAW&search_text="
        ]
    
    def find_official_consolidated_version(self, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Поиск консолидированной версии ТОЛЬКО в официальном pravo.gov.ru
        """
        doc_number = document_info.get('number', '')
        doc_name = document_info.get('name', '')
        eo_number = document_info.get('eoNumber', '')
        
        print(f"🏛️ Поиск в ОФИЦИАЛЬНОМ pravo.gov.ru для: {doc_number}")
        
        # Известные документы и их местоположение в СПС
        known_documents = {
            '273-ФЗ': {
                'sps_id': '70291362',  # ID в СПС для закона об образовании
                'full_name': 'Федеральный закон "Об образовании в Российской Федерации"',
                'year': '2012'
            },
            '44-ФЗ': {
                'sps_id': '70353464',
                'full_name': 'Федеральный закон "О контрактной системе"',
                'year': '2013'
            },
            '223-ФЗ': {
                'sps_id': '12177967',
                'full_name': 'Федеральный закон "О закупках товаров, работ, услуг"',
                'year': '2011'
            }
        }
        
        # Проверяем известные документы
        clean_number = doc_number.replace('№', '').strip()
        
        if clean_number in known_documents:
            known_doc = known_documents[clean_number]
            
            return {
                'type': 'official_consolidated_version',
                'source': 'СПС "Законодательство России" (pravo.gov.ru)',
                'document_id': known_doc['sps_id'],
                'search_instructions': {
                    'method_1': {
                        'name': 'Прямой поиск в СПС',
                        'url': 'http://pravo.gov.ru/ips/',
                        'steps': [
                            f"1. Откройте СПС: http://pravo.gov.ru/ips/",
                            f"2. В поле поиска введите: {clean_number}",
                            f"3. Найдите: {known_doc['full_name']}",
                            f"4. Выберите 'Действующая редакция'",
                            f"5. Скачайте PDF актуальной версии"
                        ]
                    },
                    'method_2': {
                        'name': 'Поиск через publication.pravo.gov.ru',
                        'url': 'http://publication.pravo.gov.ru/',
                        'steps': [
                            f"1. Откройте: http://publication.pravo.gov.ru/",
                            f"2. Найдите ссылку на 'Законодательство России'",
                            f"3. Перейдите в СПС",
                            f"4. Найдите документ {clean_number}",
                            f"5. Скачайте консолидированную версию"
                        ]
                    }
                },
                'api_document': {
                    'eo_number': eo_number,
                    'pdf_url': f"http://publication.pravo.gov.ru/file/pdf?eoNumber={eo_number}",
                    'note': 'Оригинальная версия без изменений'
                },
                'recommendations': [
                    'Для изучения структуры используйте оригинальный PDF из API',
                    'Для работы с актуальным текстом используйте СПС "Законодательство России"',
                    'В СПС доступна версия со всеми внесенными изменениями'
                ]
            }
        
        # Для неизвестных документов - общие инструкции
        return self._create_general_search_instructions(doc_number, doc_name, eo_number)
    
    def _create_general_search_instructions(self, doc_number: str, doc_name: str, eo_number: str) -> Dict[str, Any]:
        """Создание общих инструкций для поиска в СПС"""
        return {
            'type': 'manual_search_required',
            'source': 'СПС "Законодательство России" (pravo.gov.ru)',
            'search_instructions': {
                'primary_method': {
                    'name': 'Поиск в СПС Законодательство России',
                    'url': 'http://pravo.gov.ru/ips/',
                    'steps': [
                        f"1. Откройте СПС: http://pravo.gov.ru/ips/",
                        f"2. В поле поиска введите номер: {doc_number}",
                        f"3. Или введите название: {doc_name[:50]}...",
                        f"4. Найдите нужный документ в результатах",
                        f"5. Выберите 'Действующая редакция' или 'Актуальная версия'",
                        f"6. Скачайте PDF консолидированной версии"
                    ]
                },
                'alternative_method': {
                    'name': 'Поиск через главную страницу',
                    'url': 'http://pravo.gov.ru/',
                    'steps': [
                        f"1. Откройте: http://pravo.gov.ru/",
                        f"2. Найдите раздел 'Законодательство России'",
                        f"3. Используйте расширенный поиск",
                        f"4. Укажите номер документа: {doc_number}",
                        f"5. Скачайте актуальную редакцию"
                    ]
                }
            },
            'api_fallback': {
                'eo_number': eo_number,
                'pdf_url': f"http://publication.pravo.gov.ru/file/pdf?eoNumber={eo_number}",
                'note': 'Резервный вариант: оригинальная версия из API (без изменений)'
            },
            'important_note': [
                f"⚠️ API publication.pravo.gov.ru содержит только ОРИГИНАЛЬНЫЕ версии",
                f"📚 Для АКТУАЛЬНОГО текста обязательно используйте СПС pravo.gov.ru/ips",
                f"🔄 В СПС доступны консолидированные версии со всеми изменениями"
            ]
        }
    
    def get_sps_access_status(self) -> Dict[str, Any]:
        """Проверка доступности СПС"""
        sps_status = {
            'accessible': False,
            'tested_urls': [],
            'working_urls': [],
            'error_message': None
        }
        
        test_urls = [
            'http://pravo.gov.ru/ips/',
            'http://pravo.gov.ru/',
            'http://publication.pravo.gov.ru/'
        ]
        
        for url in test_urls:
            try:
                response = self.session.get(url, timeout=5)
                sps_status['tested_urls'].append({
                    'url': url,
                    'status': response.status_code,
                    'accessible': response.status_code == 200
                })
                
                if response.status_code == 200:
                    sps_status['working_urls'].append(url)
                    sps_status['accessible'] = True
                    
            except Exception as e:
                sps_status['tested_urls'].append({
                    'url': url,
                    'status': 'error',
                    'error': str(e),
                    'accessible': False
                })
        
        if not sps_status['accessible']:
            sps_status['error_message'] = (
                "СПС недоступен из текущего окружения (Google Colab). "
                "Это не означает, что СПС не работает - возможны ограничения сети."
            )
        
        return sps_status
