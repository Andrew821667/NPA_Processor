"""
GPT помощник для извлечения документов из неструктурированного текста
Использует OpenAI API для анализа текста и извлечения списка НПА
"""

import json
import time
from typing import List, Dict, Any
import openai

class GPTHelper:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Инициализация GPTHelper с улучшениями
        
        Args:
            api_key: OpenAI API ключ
            model: Модель GPT (по умолчанию gpt-4o-mini для лучшего качества)
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def extract_documents(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Извлечение документов из текста с улучшениями
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с извлеченными документами по категориям
        """
        # Увеличиваем размер чанка для лучшей обработки
        max_chunk_size = 5000
        text_chunks = self._split_text(text, max_chunk_size)
        all_documents = []

        # КРИТИЧЕСКОЕ УЛУЧШЕНИЕ: обрабатываем ВСЕ чанки, а не только первые 3
        print(f"📄 Обрабатываем {len(text_chunks)} чанков (все)")
        
        for i, chunk in enumerate(text_chunks, 1):
            try:
                print(f"🔄 Чанк {i}/{len(text_chunks)}", end=" ")
                chunk_docs = self._process_chunk(chunk)
                all_documents.extend(chunk_docs)
                print(f"✅({len(chunk_docs)})")
                
                # Пауза между запросами для избежания rate limits
                time.sleep(0.5)
            except Exception as e:
                print(f"❌({str(e)[:20]})")
                continue

        # Удаляем дубликаты
        unique_documents = self._remove_duplicates(all_documents)

        # Разделяем на категории
        npa_docs = []
        letter_docs = []

        for doc in unique_documents:
            doc_type = doc.get('type', '').lower()
            if 'письмо' in doc_type or doc.get('category') == 'ПИСЬМО':
                letter_docs.append(doc)
            else:
                npa_docs.append(doc)

        return {
            'all_documents': unique_documents,
            'npa_documents': npa_docs,
            'letters': letter_docs
        }

    def _process_chunk(self, chunk: str) -> List[Dict[str, Any]]:
        """
        Обработка одного чанка текста с улучшенным промптом
        
        Args:
            chunk: Фрагмент текста для обработки
            
        Returns:
            Список найденных документов
        """
        # УЛУЧШЕННЫЙ ПРОМПТ: более точные инструкции и примеры
        prompt = f"""
        Найди в тексте ВСЕ российские правовые документы. Будь максимально внимательным!

        ТИПЫ ДОКУМЕНТОВ ДЛЯ ПОИСКА:
        - Федеральные законы (примеры: №273-ФЗ, 323-ФЗ, 426-ФЗ, 477н)
        - Постановления Правительства (примеры: №1490, 825, 580, 719)
        - Приказы министерств (примеры: №709н, 816, 477н, 205, 947н)
        - ПИСЬМА всех видов (примеры: АК-1879/06, 14-0/10/В-2253, 06-735)
        - Указы, положения, регламенты, стандарты

        ВАЖНЫЕ ПРАВИЛА:
        - Включай ВСЕ документы с номерами (даже 477н, 205, 806)
        - НЕ пропускай документы без указания ведомства
        - Ищи в списках, таблицах, сплошном тексте
        - Извлекай точные номера и полные названия

        ИГНОРИРУЙ только:
        - HTTP ссылки и URL
        - Телефоны и почтовые адреса
        - Номера страниц и разделов

        Верни JSON со ВСЕМИ найденными документами:
        {{
            "documents": [
                {{
                    "type": "точный тип документа",
                    "number": "точный номер",
                    "title": "полное название документа",
                    "category": "НПА" или "ПИСЬМО"
                }}
            ]
        }}

        Текст для анализа:
        {chunk[:4500]}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # низкая температура для точности
                max_tokens=2000   # увеличено для большего количества документов
            )

            result = response.choices[0].message.content
            
            # Более надежный парсинг JSON
            json_start = result.find('{')
            json_end = result.rfind('}') + 1

            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                try:
                    chunk_data = json.loads(json_str)
                    documents = chunk_data.get('documents', [])
                    
                    # Базовая фильтрация от мусора
                    valid_docs = []
                    for doc in documents:
                        if self._is_valid_document(doc):
                            valid_docs.append(doc)
                    
                    return valid_docs
                except json.JSONDecodeError:
                    # Попытка исправить JSON
                    try:
                        # Убираем возможные проблемы с кавычками
                        fixed_json = json_str.replace('\\"', '"').replace('\\n', ' ')
                        chunk_data = json.loads(fixed_json)
                        return chunk_data.get('documents', [])
                    except:
                        return []

        except Exception as e:
            print(f"Ошибка обработки чанка: {e}")
            return []

        return []

    def _is_valid_document(self, doc: Dict[str, Any]) -> bool:
        """
        Проверка валидности документа
        
        Args:
            doc: Документ для проверки
            
        Returns:
            True если документ валиден
        """
        number = str(doc.get('number', '')).strip()
        title = str(doc.get('title', '')).strip().lower()
        
        # Исключаем только очевидный мусор
        if (not number or 
            number in ['', 'nan', 'none', 'нет', 'н/а'] or
            len(number) > 30 or
            'http' in title or
            'www' in title or
            '@' in title or
            len(title) < 5):
            return False
        
        # Все остальное считаем валидным
        return True

    def _split_text(self, text: str, max_size: int) -> List[str]:
        """
        Разбивка текста на чанки с улучшенной логикой
        
        Args:
            text: Исходный текст
            max_size: Максимальный размер чанка
            
        Returns:
            Список чанков текста
        """
        if len(text) <= max_size:
            return [text]

        chunks = []
        start = 0
        overlap = 500  # перекрытие между чанками

        while start < len(text):
            end = start + max_size
            
            if end >= len(text):
                # Последний чанк
                chunks.append(text[start:])
                break
            
            # Ищем удобное место для разрыва
            chunk = text[start:end]
            
            # Приоритет разрыва: двойной перенос > одинарный > точка > пробел
            break_points = [
                chunk.rfind('\n\n'),
                chunk.rfind('\n'),
                chunk.rfind('. '),
                chunk.rfind(' ')
            ]
            
            best_break = -1
            for bp in break_points:
                if bp > max_size - 300:  # не слишком близко к концу
                    best_break = bp
                    break
            
            if best_break > 0:
                actual_end = start + best_break + 1
                chunks.append(text[start:actual_end])
                start = actual_end - overlap  # с перекрытием
            else:
                # Если не нашли хорошее место, разрываем по размеру
                chunks.append(chunk)
                start = end - overlap

        return chunks

    def _remove_duplicates(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Удаление дубликатов документов с улучшенной логикой
        
        Args:
            documents: Список документов
            
        Returns:
            Список уникальных документов
        """
        seen = {}
        unique_docs = []

        for doc in documents:
            # Создаем ключ для дедупликации
            doc_type = doc.get('type', '').lower().strip()
            doc_number = str(doc.get('number', '')).lower().strip()
            
            # Нормализуем номер для сравнения
            import re
            clean_number = re.sub(r'[№n°#\s\-_]+', '', doc_number)
            
            key = f"{doc_type}_{clean_number}"
            
            if key not in seen:
                seen[key] = doc
                unique_docs.append(doc)
            else:
                # Если дубликат, выбираем документ с более полным названием
                existing_doc = seen[key]
                current_title_len = len(doc.get('title', ''))
                existing_title_len = len(existing_doc.get('title', ''))
                
                if current_title_len > existing_title_len:
                    # Заменяем в списке
                    for i, item in enumerate(unique_docs):
                        if item == existing_doc:
                            unique_docs[i] = doc
                            seen[key] = doc
                            break

        return unique_docs
