
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
from typing import Dict, List, Optional, Any

class ConsolidatedVersionParser:
    """
    Парсер для поиска консолидированных версий НПА в различных СПС
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Известные источники консолидированных версий
        self.sps_sources = [
            {
                'name': 'СПС Законодательство России',
                'base_url': 'https://pravo.gov.ru/ips/',
                'search_url': 'https://pravo.gov.ru/ips/ext_search.html',
                'parser_method': self._parse_pravo_gov
            },
            {
                'name': 'Гарант (backup)',
                'base_url': 'http://base.garant.ru/',
                'search_url': 'http://www.garant.ru/search/',
                'parser_method': self._parse_garant
            }
        ]
    
    def find_consolidated_version(self, document_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Поиск консолидированной версии документа
        
        Args:
            document_info: информация о документе (number, name, eoNumber)
            
        Returns:
            Dict с информацией о консолидированной версии
        """
        doc_number = document_info.get('number', '')
        doc_name = document_info.get('name', '')
        
        print(f"🔍 Ищем консолидированную версию: {doc_number}")
        
        # Пробуем каждый источник
        for source in self.sps_sources:
            try:
                print(f"   📡 Проверяем {source['name']}...")
                result = source['parser_method'](doc_number, doc_name)
                
                if result:
                    result['source'] = source['name']
                    result['search_term'] = doc_number
                    print(f"   ✅ Найдено в {source['name']}")
                    return result
                else:
                    print(f"   ❌ Не найдено в {source['name']}")
                    
            except Exception as e:
                print(f"   ⚠️ Ошибка в {source['name']}: {e}")
                continue
        
        # Если автоматический поиск не удался, возвращаем инструкции для ручного поиска
        return self._create_manual_search_instructions(doc_number, doc_name)
    
    def _parse_pravo_gov(self, doc_number: str, doc_name: str) -> Optional[Dict[str, Any]]:
        """Парсинг СПС Законодательство России"""
        try:
            # Пытаемся найти прямую ссылку через поиск
            search_urls = [
                f"https://pravo.gov.ru/ips/?search_base=LAW&search_text={doc_number}",
                f"https://pravo.gov.ru/ips/?docbody=&nd={doc_number}",
                f"https://pravo.gov.ru/ips/?docbody=&text={doc_number}"
            ]
            
            for search_url in search_urls:
                try:
                    response = self.session.get(search_url, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Ищем ссылки на документы
                        links = soup.find_all('a', href=True)
                        
                        for link in links:
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            # Проверяем, что это ссылка на наш документ
                            if (doc_number.lower() in text.lower() or 
                                doc_number.lower() in href.lower()):
                                
                                full_url = urljoin(search_url, href)
                                
                                return {
                                    'url': full_url,
                                    'title': text,
                                    'type': 'consolidated_version',
                                    'format': 'html',
                                    'pdf_available': self._check_pdf_availability(full_url)
                                }
                
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Ошибка парсинга pravo.gov.ru: {e}")
            return None
    
    def _parse_garant(self, doc_number: str, doc_name: str) -> Optional[Dict[str, Any]]:
        """Парсинг Гарант (backup источник)"""
        try:
            # Формируем URL для поиска в Гаранте
            # Примеры известных документов в Гаранте
            known_garant_urls = {
                '273-ФЗ': 'http://base.garant.ru/70291362/',
                '44-ФЗ': 'http://base.garant.ru/70353464/',
                '223-ФЗ': 'http://base.garant.ru/12177967/'
            }
            
            # Проверяем известные документы
            clean_number = doc_number.replace('-ФЗ', '').replace('№', '').strip()
            
            if f"{clean_number}-ФЗ" in known_garant_urls:
                garant_url = known_garant_urls[f"{clean_number}-ФЗ"]
                
                # Проверяем доступность
                response = self.session.get(garant_url, timeout=10)
                if response.status_code == 200:
                    return {
                        'url': garant_url,
                        'title': f'Консолидированная версия {doc_number}',
                        'type': 'consolidated_version',
                        'format': 'html',
                        'pdf_available': False,
                        'note': 'Доступен в Гаранте (backup источник)'
                    }
            
            return None
            
        except Exception as e:
            print(f"Ошибка парсинга Гарант: {e}")
            return None
    
    def _check_pdf_availability(self, url: str) -> bool:
        """Проверка доступности PDF версии на странице"""
        try:
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                content = response.text.lower()
                return ('pdf' in content or 
                       'скачать' in content or
                       'download' in content)
        except:
            pass
        return False
    
    def _create_manual_search_instructions(self, doc_number: str, doc_name: str) -> Dict[str, Any]:
        """Создание инструкций для ручного поиска"""
        return {
            'type': 'manual_search_required',
            'instructions': [
                f"1. Откройте СПС 'Законодательство России': https://pravo.gov.ru/ips/",
                f"2. В поле поиска введите: {doc_number}",
                f"3. Найдите консолидированную версию (со всеми изменениями)",
                f"4. Скачайте PDF версию актуального текста"
            ],
            'search_terms': [doc_number, doc_name],
            'backup_sources': [
                {
                    'name': 'КонсультантПлюс',
                    'url': 'http://www.consultant.ru/',
                    'search_term': doc_number
                },
                {
                    'name': 'Гарант',
                    'url': 'http://www.garant.ru/',
                    'search_term': doc_number
                }
            ]
        }
    
    def extract_pdf_links(self, page_url: str) -> List[str]:
        """Извлечение ссылок на PDF файлы со страницы"""
        try:
            response = self.session.get(page_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_links = []
            
            # Ищем ссылки на PDF
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                
                if ('.pdf' in href.lower() or 
                    'pdf' in link.get_text(strip=True).lower() or
                    'скачать' in link.get_text(strip=True).lower()):
                    
                    full_url = urljoin(page_url, href)
                    pdf_links.append(full_url)
            
            return pdf_links
            
        except Exception as e:
            print(f"Ошибка извлечения PDF ссылок: {e}")
            return []
