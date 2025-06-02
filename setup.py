from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="npa-processor",
    version="1.1.0",  # Обновляем версию
    author="Andrew_Popov",
    author_email="andrew@example.com",
    description="Модуль для поиска российских НПА и профессиональных стандартов",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Andrew821667/NPA_Processor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
        ],
        "profstandards": [
            "PyMuPDF>=1.23.0",
            "xlrd>=2.0.0", 
            "beautifulsoup4>=4.12.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "npa-search=npa_searcher.cli:main",
            "profstandards-download=npa_searcher.profstandards.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "npa_searcher": ["*.yaml", "*.yml", "*.json"],
        "npa_searcher.profstandards": ["*.yaml", "*.yml", "*.json"],
    },
)
