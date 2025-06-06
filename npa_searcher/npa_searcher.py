"""
Основной поисковик НПА через официальный API publication.pravo.gov.ru
Реализует множественные стратегии поиска и систему скоринга релевантности
"""

import requests
import time
import logging
from typing import List, Dict, Any, Optional
from npa_searcher.config import Config
from npa_searcher.utils import clean_number, is_amendment, retry_request, validate_document_data
from npa_searcher.exceptions import APIError, DocumentNotFoundError
from typing import Optional
import os

logger = logging.getLogger(__name__)

class NPASearcher:
    """
    Класс для поиска НПА через официальный API
    Использует множественные стратегии поиска для максимальной эффективности
    """
    
    def __init__(self):
        """Инициализация поисковика"""
        self.api_url = Config.API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update(Config.DEFAULT_HEADERS)
        
        # Статистика поиска
        self.search_stats = {
            'total_searches': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'api_calls': 0
        }
        
        logger.info("NPA Searcher инициализирован")

    def search_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Главная функция поиска документа с множественными стратегиями
        
        Args:
            document: словарь с информацией о документе (type, number, title)
            
        Returns:
            List отсортированных по релевантности результатов
        """
        # Валидация входных данных
        validate_document_data(document)
        
        # Статистика
        self.search_stats['total_searches'] += 1
        
        doc_type = document.get('type', '')
        doc_number = document.get('number', '')
        doc_title = document.get('title', '')
        
        logger.info(f"Поиск документа: {doc_type} №{doc_number}")
        
        all_results = []
        
        # Стратегия 1: Поиск по номеру
        if doc_number:
            results = self._search_by_number(doc_number)
            all_results.extend(results)
        
        # Стратегия 2: Поиск по названию  
        if doc_title:
            results = self._search_by_title(doc_title)
            all_results.extend(results)
        
        # Стратегия 3: Известные документы
        clean_num = clean_number(doc_number)
        if clean_num in Config.KNOWN_DOCUMENTS:
            results = self._search_known_document(clean_num)
            all_results.extend(results)
        
        # Фильтрация и скоринг
        filtered_results = self._filter_relevant_items(all_results, document)
        scored_results = self._score_results(filtered_results, document)
        
        # Удаление дубликатов и сортировка
        unique_results = self._remove_duplicates(scored_results)
        final_results = sorted(unique_results, key=lambda x: x.get('score', 0), reverse=True)
        
        if final_results:
            self.search_stats['successful_searches'] += 1
        
        logger.info(f"Найдено результатов: {len(final_results)}")
        return final_results[:10]  # Топ 10 результатов
    def get_search_statistics(self) -> Dict[str, Any]:
        """Получение статистики поиска"""
        stats = self.search_stats.copy()
        if stats['total_searches'] > 0:
            stats['success_rate'] = (stats['successful_searches'] / stats['total_searches']) * 100
        else:
            stats['success_rate'] = 0
            
        return stats

    def _search_by_number(self, doc_number: str) -> List[Dict[str, Any]]:
        """Поиск по номеру документа"""
        clean_num = clean_number(doc_number)
        results = []
        
        # Различные варианты поиска по номеру
        search_queries = [
            {"Number": doc_number, "NumberSearchType": 0, "PageSize": 30, "Index": 1},
            {"Number": clean_num, "NumberSearchType": 0, "PageSize": 30, "Index": 1},
            {"Number": clean_num, "NumberSearchType": 1, "PageSize": 20, "Index": 1},  # Начинается с
            {"ComplexName": clean_num, "PageSize": 20, "Index": 1}
        ]
        
        for query in search_queries:
            try:
                response = self.session.get(f"{self.api_url}/Documents", params=query, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    results.extend(items)
                    logger.debug(f"Поиск по номеру '{doc_number}': найдено {len(items)}")
                time.sleep(0.5)  # Задержка между запросами
            except Exception as e:
                logger.warning(f"Ошибка поиска по номеру: {e}")
                continue
        
        return results
    
    def _search_by_title(self, doc_title: str) -> List[Dict[str, Any]]:
        """Поиск по названию документа"""
        # Извлекаем ключевые слова (длина > 4, максимум 3 слова)
        words = [w for w in doc_title.split() if len(w) > 4][:3]
        if not words:
            return []
        
        results = []
        
        for word in words:
            try:
                query = {"Name": word, "PageSize": 20, "Index": 1}
                response = self.session.get(f"{self.api_url}/Documents", params=query, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    results.extend(items)
                    logger.debug(f"Поиск по слову '{word}': найдено {len(items)}")
                
                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"Ошибка поиска по названию: {e}")
                continue
        
        return results
    
    def _search_known_document(self, clean_number: str) -> List[Dict[str, Any]]:
        """Поиск известных документов по EO номерам"""
        known_info = Config.KNOWN_DOCUMENTS.get(clean_number, {})
        results = []
        
        # Поиск по известным EO номерам
        for eo_number in known_info.get('eo_hints', []):
            try:
                response = self.session.get(f"{self.api_url}/Document", 
                                         params={"eoNumber": eo_number}, timeout=10)
                if response.status_code == 200:
                    doc_data = response.json()
                    if doc_data:
                        results.append(doc_data)
                        logger.debug(f"Найден известный документ: {eo_number}")
                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"Ошибка поиска известного документа: {e}")
                continue
        
        return results
    
    def _filter_relevant_items(self, items: List[Dict[str, Any]], document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Фильтрация релевантных элементов"""
        doc_number = document.get('number', '').lower()
        clean_num = clean_number(doc_number).lower()
        
        relevant = []
        
        for item in items:
            item_number = item.get('number', '').lower()
            item_name = item.get('name', '').lower()
            complex_name = item.get('complexName', '').lower()
            
            # Проверка совпадения номера
            is_number_match = (
                doc_number == item_number or
                clean_num == item_number or
                clean_num in item_number or
                item_number in clean_num or
                clean_num in complex_name
            )
            
            if is_number_match:
                relevant.append(item)
        
        return relevant
    
    def _score_results(self, results: List[Dict[str, Any]], document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Система скоринга результатов"""
        doc_number = document.get('number', '').lower()
        doc_title = document.get('title', '').lower()
        clean_num = clean_number(doc_number).lower()
        
        scored_results = []
        
        for result in results:
            score = 0
            item_number = result.get('number', '').lower()
            item_name = result.get('name', '').lower()
            complex_name = result.get('complexName', '').lower()
            
            # Оценка номера документа
            if doc_number == item_number:
                score += 8000
            elif clean_num == item_number:
                score += 7000
            elif clean_num in item_number:
                number_ratio = len(clean_num) / max(len(item_number), 1)
                score += 6000 if number_ratio > 0.5 else 3000
            elif item_number in clean_num:
                score += 4000
            
            # Оценка названия
            title_words = [w for w in doc_title.split() if len(w) > 3][:5]
            name_matches = sum(1 for word in title_words if word in item_name)
            complex_matches = sum(1 for word in title_words if word in complex_name)
            total_matches = max(name_matches, complex_matches)
            
            if total_matches >= 3:
                score += 3000
            elif total_matches >= 2:
                score += 1500
            elif total_matches >= 1:
                score += 500
            
            # Бонус за актуальность
            publish_date = result.get('viewDate', '')
            year_bonuses = {
                '2024': 250, '2023': 200, '2022': 150,
                '2021': 100, '2020': 50
            }
            for year, bonus in year_bonuses.items():
                if year in publish_date:
                    score += bonus
                    break
            
            # Штрафы за изменения
            is_amendment_doc = is_amendment(complex_name)
            if is_amendment_doc:
                score = min(score, 1000)
            
            # Добавляем результат если score достаточно высокий
            if score >= 500:
                result['score'] = score
                result['is_amendment'] = is_amendment_doc
                scored_results.append(result)
        
        return scored_results
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Удаление дубликатов результатов"""
        seen_keys = set()
        unique_results = []
        
        for result in results:
            # Создаем уникальные ключи
            eo_number = result.get('eoNumber', '')
            doc_id = result.get('id', '')
            number = result.get('number', '')
            name_part = result.get('name', '')[:30]
            
            keys = [eo_number, doc_id, f"{number}_{name_part}"]
            
            # Проверяем дубликаты
            duplicate_found = False
            for key in keys:
                if key and key in seen_keys:
                    duplicate_found = True
                    break
            
            if not duplicate_found:
                for key in keys:
                    if key:
                        seen_keys.add(key)
                unique_results.append(result)
        
        return unique_results

    def search_consolidated_version(self, document_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Поиск консолидированной (актуальной) версии НПА в СПС 'Законодательство России'
        
        Args:
            document_info: информация о документе из основного поиска
            
        Returns:
            Dict с информацией о консолидированной версии или None
        """
        doc_number = document_info.get('number', '')
        doc_name = document_info.get('name', '')
        
        logger.info(f"Поиск консолидированной версии: {doc_number}")
        
        # Пытаемся найти в СПС через различные подходы
        sps_search_strategies = [
            self._search_sps_by_number,
            self._search_sps_by_name,
            self._search_sps_by_eo_number
        ]
        
        for strategy in sps_search_strategies:
            try:
                result = strategy(document_info)
                if result:
                    logger.info(f"Консолидированная версия найдена через {strategy.__name__}")
                    return result
            except Exception as e:
                logger.warning(f"Ошибка стратегии {strategy.__name__}: {e}")
                continue
        
        logger.warning(f"Консолидированная версия не найдена для {doc_number}")
        return None
    
    def _search_sps_by_number(self, document_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Поиск в СПС по номеру документа"""
        doc_number = document_info.get('number', '')
        
        # Формируем URL для поиска в СПС
        # На основе анализа нужно будет найти правильный endpoint
        sps_base = "http://pravo.gov.ru/ips"
        
        # Заглушка пока не найдем правильный API
        # TODO: Найти правильный endpoint СПС для поиска
        return {
            'source': 'СПС Законодательство России',
            'number': doc_number,
            'url': f"{sps_base}/?search={doc_number}",
            'status': 'Требуется ручной поиск',
            'note': 'Автоматический поиск в СПС пока не реализован'
        }
    
    def _search_sps_by_name(self, document_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Поиск в СПС по названию документа"""
        # Аналогично, заглушка
        return None
    
    def _search_sps_by_eo_number(self, document_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Поиск в СПС по EO номеру"""
        # Аналогично, заглушка  
        return None
    
    def get_document_with_consolidated_version(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Полный поиск: основной документ + консолидированная версия
        
        Returns:
            Dict с основным документом и ссылкой на консолидированную версию
        """
        # Ищем основной документ через API
        search_results = self.search_document(document)
        
        result = {
            'original_search_results': search_results,
            'consolidated_version': None,
            'recommendations': []
        }
        
        if search_results:
            best_match = search_results[0]
            
            # Ищем консолидированную версию
            consolidated = self.search_consolidated_version(best_match)
            result['consolidated_version'] = consolidated
            
            # Формируем рекомендации
            if consolidated:
                result['recommendations'].append({
                    'type': 'consolidated',
                    'description': 'Используйте консолидированную версию для актуального текста',
                    'url': consolidated.get('url'),
                    'source': consolidated.get('source')
                })
            else:
                result['recommendations'].append({
                    'type': 'manual_search',
                    'description': f'Найдите актуальную версию {best_match.get("number", "")} в СПС "Законодательство России"',
                    'url': 'http://pravo.gov.ru/ips/',
                    'search_term': best_match.get('number', '')
                })
        
        return result

    def find_official_consolidated_version(self, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Поиск консолидированной версии ТОЛЬКО в официальном pravo.gov.ru
        """
        # Импортируем парсер
        from official_pravo_parser import OfficialPravoGovParser
        
        parser = OfficialPravoGovParser()
        
        # Получаем инструкции для официального поиска
        official_result = parser.find_official_consolidated_version(document_info)
        
        # Формируем полный ответ пользователю
        return {
            'api_document': {
                'source': 'API publication.pravo.gov.ru',
                'eo_number': document_info.get('eoNumber', ''),
                'pdf_url': f"http://publication.pravo.gov.ru/file/pdf?eoNumber={document_info.get('eoNumber', '')}",
                'name': document_info.get('name', ''),
                'number': document_info.get('number', ''),
                'publish_date': document_info.get('viewDate', ''),
                'is_amendment': document_info.get('is_amendment', False),
                'score': document_info.get('score', 0),
                'purpose': 'Оригинальная версия без изменений'
            },
            'consolidated_search': official_result,
            'final_recommendations': self._create_final_recommendations(document_info, official_result),
            'summary': {
                'api_document_found': True,
                'official_instructions_available': True,
                'source': 'Только официальный pravo.gov.ru',
                'next_steps': 'Следуйте инструкциям для поиска актуальной версии в СПС'
            }
        }
    
    def _create_final_recommendations(self, document_info: Dict[str, Any], official_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Создание финальных рекомендаций пользователю"""
        recommendations = []
        
        # Предупреждение об изменениях
        if document_info.get('is_amendment', False):
            recommendations.append({
                'type': 'warning',
                'icon': '⚠️',
                'message': 'Найденный документ является ИЗМЕНЕНИЕМ к основному НПА',
                'action': 'Найдите основной документ для полного понимания'
            })
        
        # API документ
        recommendations.append({
            'type': 'api_document',
            'icon': '📄',
            'message': 'Оригинальный документ из официального API',
            'url': f"http://publication.pravo.gov.ru/file/pdf?eoNumber={document_info.get('eoNumber', '')}",
            'purpose': 'Для изучения структуры и оригинальной версии',
            'date': document_info.get('viewDate', ''),
            'action': 'Скачать PDF из API'
        })
        
        # Консолидированная версия
        result_type = official_result.get('type', '')
        
        if result_type == 'official_consolidated_version':
            recommendations.append({
                'type': 'consolidated_available',
                'icon': '🏛️',
                'message': 'Консолидированная версия доступна в СПС',
                'url': 'http://pravo.gov.ru/ips/',
                'purpose': 'Актуальная версия со всеми изменениями',
                'action': 'Следуйте инструкциям для поиска в СПС',
                'document_id': official_result.get('document_id', ''),
                'search_term': document_info.get('number', '')
            })
        else:
            recommendations.append({
                'type': 'manual_search_required',
                'icon': '🔍',
                'message': 'Требуется ручной поиск консолидированной версии',
                'url': 'http://pravo.gov.ru/ips/',
                'purpose': 'Актуальная версия со всеми изменениями',
                'action': 'Выполните поиск по инструкциям',
                'search_term': document_info.get('number', '')
            })
        
        # Важное напоминание
        recommendations.append({
            'type': 'important_note',
            'icon': '💡',
            'message': 'Для работы используйте ТОЛЬКО консолидированную версию из СПС',
            'reason': 'API содержит только оригинальные документы без изменений',
            'action': 'Обязательно найдите актуальную версию в pravo.gov.ru/ips'
        })
        
        return recommendations


    def download_pdf(self, eo_number: str, filename: str = None) -> Optional[str]:
        """
        Скачивание PDF документа по EO номеру
        
        Args:
            eo_number: номер электронного опубликования
            filename: имя файла для сохранения (опционально)
            
        Returns:
            str: путь к скачанному файлу или None при ошибке
        """
        if not eo_number:
            logger.warning("EO номер не указан")
            return None
        
        if filename is None:
            filename = f"npa_{eo_number}.pdf"
        
        # URL для скачивания PDF
        pdf_url = f"http://publication.pravo.gov.ru/file/pdf?eoNumber={eo_number}"
        
        try:
            logger.info(f"Скачивание PDF: {eo_number}")
            
            # Выполняем запрос на скачивание
            response = self.session.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            # Проверяем, что это действительно PDF
            if (len(response.content) > 1000 and 
                response.content[:8].startswith(b'%PDF')):
                
                # Сохраняем файл
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"PDF сохранен: {filename} ({len(response.content)} байт)")
                return filename
            else:
                logger.error(f"Получен некорректный PDF файл для {eo_number}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка скачивания PDF {eo_number}: {e}")
            return None
    
    def download_multiple_pdfs(self, documents_list: List[Dict[str, Any]], 
                              folder_name: str = None) -> Dict[str, Any]:
        """
        Скачивание нескольких PDF документов
        
        Args:
            documents_list: список документов с eoNumber
            folder_name: имя папки для сохранения
            
        Returns:
            Dict со статистикой скачивания
        """
        import re
        import os
        from datetime import datetime
        
        if folder_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"npa_downloads_{timestamp}"
        
        # Создаем папку
        os.makedirs(folder_name, exist_ok=True)
        
        successful_downloads = []
        failed_downloads = []
        
        print(f"📥 Скачивание {len(documents_list)} документов в папку {folder_name}...")
        
        for i, doc in enumerate(documents_list, 1):
            eo_number = doc.get('eoNumber', '')
            doc_name = doc.get('name', f'document_{i}')
            
            if not eo_number:
                failed_downloads.append({
                    'document': doc_name,
                    'reason': 'Отсутствует EO номер'
                })
                continue
            
            # Создаем безопасное имя файла
            safe_name = doc_name.replace('<', '_').replace('>', '_').replace(':', '_').replace('"', '_').replace('/', '_').replace('\\', '_').replace('|', '_').replace('?', '_').replace('*', '_')
            safe_name = safe_name[:80]  # Ограничиваем длину
            filename = f"{safe_name}_{eo_number}.pdf"
            filepath = os.path.join(folder_name, filename)
            
            print(f"  📄 {i}/{len(documents_list)}: {doc_name[:50]}...")
            
            # Скачиваем файл
            result = self.download_pdf(eo_number, filepath)
            
            if result:
                successful_downloads.append({
                    'eo_number': eo_number,
                    'filename': filename,
                    'document_name': doc_name,
                    'file_path': filepath
                })
                print(f"    ✅ Скачан: {filename}")
            else:
                failed_downloads.append({
                    'eo_number': eo_number,
                    'document': doc_name,
                    'reason': 'Ошибка скачивания'
                })
                print(f"    ❌ Ошибка: {eo_number}")
            
            # Небольшая задержка между скачиваниями
            time.sleep(0.5)
        
        stats = {
            'total_attempted': len(documents_list),
            'successful': len(successful_downloads),
            'failed': len(failed_downloads),
            'success_rate': len(successful_downloads) / len(documents_list) * 100 if documents_list else 0,
            'folder_path': folder_name,
            'successful_downloads': successful_downloads,
            'failed_downloads': failed_downloads
        }
        
        print(f"\n📊 Статистика скачивания:")
        print(f"  ✅ Успешно: {stats['successful']}")
        print(f"  ❌ Ошибки: {stats['failed']}")
        print(f"  📈 Успешность: {stats['success_rate']:.1f}%")
        print(f"  📁 Папка: {stats['folder_path']}")
        
        return stats
