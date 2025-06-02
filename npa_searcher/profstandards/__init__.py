"""
Подмодуль для работы с профессиональными стандартами РФ
Интегрирован в NPA_Processor для расширения функциональности
"""

from .downloader import ProfstandardDownloader
from .parser import ProfstandardParser
from .analyzer import ProfstandardAnalyzer
from .integration import NPAProfstandardsIntegration

__version__ = "1.0.0"
__author__ = "NPA_Processor Team"

__all__ = [
    'ProfstandardDownloader',
    'ProfstandardParser', 
    'ProfstandardAnalyzer',
    'NPAProfstandardsIntegration'
]
