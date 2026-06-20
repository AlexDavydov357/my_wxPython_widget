# setup.py
from setuptools import setup, find_packages

setup(
    name="my_wxpython_widget",               # имя пакета, будет использоваться в import
    version="0.1.0",
    packages=find_packages(),        # найдёт папку my_wxpython_widget
    python_requires=">=3.8",         # при необходимости
    # Если нужны зависимости, укажи их здесь:
    # install_requires=["numpy>=1.20", ...],
)
