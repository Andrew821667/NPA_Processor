"""
Интеграция профстандартов с основным функционалом NPA_Processor
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class NPAProfstandardsIntegration:
    """
    Интеграция профстандартов с основным функционалом NPA_Processor
    Упрощенная версия для демонстрации
    """
    
    def __init__(self, npa_searcher=None):
        self.npa_searcher = npa_searcher
        
        # Инициализируем загрузчик
        from .downloader import ProfstandardDownloader
        self.downloader = ProfstandardDownloader()
    
    def search_profstandards_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """Поиск профстандартов по ключевым словам (упрощенная версия)"""
        
        # Заглушка для демонстрации
        mock_profstandards = [
            {
                'code': '01.001',
                'name': 'Педагог (педагогическая деятельность в сфере дошкольного, начального общего, основного общего, среднего общего образования)',
                'area': 'Образование и наука',
                'status': 'действует'
            },
            {
                'code': '06.015', 
                'name': 'Специалист по информационным системам',
                'area': 'Связь, информационные и коммуникационные технологии',
                'status': 'действует'
            },
            {
                'code': '07.003',
                'name': 'Специалист по управлению персоналом', 
                'area': 'Административно-управленческая и офисная деятельность',
                'status': 'действует'
            }
        ]
        
        # Простая фильтрация по ключевым словам
        results = []
        for ps in mock_profstandards:
            for keyword in keywords:
                if keyword.lower() in ps['name'].lower() or keyword.lower() in ps['area'].lower():
                    # Добавляем релевантность
                    relevance = 0.5
                    if keyword.lower() in ps['name'].lower():
                        relevance += 0.4
                    if keyword.lower() in ps['area'].lower():
                        relevance += 0.1
                    
                    ps_copy = ps.copy()
                    ps_copy['relevance'] = relevance
                    ps_copy['matched_keywords'] = [kw for kw in keywords 
                                                  if kw.lower() in ps['name'].lower() or kw.lower() in ps['area'].lower()]
                    
                    if ps_copy not in results:
                        results.append(ps_copy)
                    break
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results
