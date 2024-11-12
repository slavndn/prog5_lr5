# Славный Даниил Михайлович - Лабораторная работа 5

1. Создаю класс CurrencyFetcher, реализующий шаблон "Одиночка" с помощью метаклассов.
2. Класс будет получать курсы валют, хранить значения с целой и дробной частью, а также ограничивать частоту запросов.
3. Добавляю метод для визуализации данных и сохраняю график в виде файла.

* Класс CurrencyFetcher использует метакласс Singleton, что гарантирует, что будет создан только один экземпляр этого класса.
* Метод fetch_currencies:
  1. Получает курсы валют с сайта ЦБ РФ.
  2. Разделяет значение на целую и дробную части.
  3. Сохраняет данные в виде словаря.

* Метод visualize_currencies:
  1. Строит график курсов валют с помощью matplotlib и сохраняет его в файл currencies.jpg.

* Контроль частоты запросов:
  1. Если попытаться вызвать fetch_currencies слишком часто, будет выброшено исключение.

## Программа: 

```
import requests
import time
from xml.etree import ElementTree as ET
import matplotlib.pyplot as plt
from collections import defaultdict
from decimal import Decimal


class Singleton(type):
    """Метакласс для реализации шаблона проектирования 'Одиночка'."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CurrencyFetcher(metaclass=Singleton):
    """Класс для получения и обработки курсов валют с сайта ЦБ РФ."""

    def __init__(self, cooldown: int = 1):
        self._cooldown = cooldown
        self._last_request_time = 0
        self._currencies = defaultdict(lambda: (None, None))
    
    def _request_data(self):
        """Запрашивает данные с сайта ЦБ РФ."""
        cur_res_str = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
        root = ET.fromstring(cur_res_str.content)
        return root.findall("Valute")

    def fetch_currencies(self, currencies_ids: list):
        """Получает курсы валют и возвращает их в заданном формате."""
        current_time = time.time()
        if current_time - self._last_request_time < self._cooldown:
            raise Exception(f"Запросы можно делать не чаще, чем раз в {self._cooldown} секунд")

        self._last_request_time = current_time
        valutes = self._request_data()
        result = []

        for _v in valutes:
            valute_id = _v.get('ID')
            if valute_id in currencies_ids:
                char_code = _v.find('CharCode').text
                name = _v.find('Name').text
                value = _v.find('Value').text
                nominal = int(_v.find('Nominal').text)

                integer_part, fractional_part = value.split(',')
                formatted_value = (integer_part, fractional_part)
                
                self._currencies[char_code] = (name, formatted_value, nominal)
                result.append({char_code: (name, formatted_value)})
        
        return result

    def get_currency_info(self, code: str):
        """Возвращает информацию о валюте по её коду."""
        return self._currencies.get(code, None)

    def visualize_currencies(self):
        """Визуализирует курсы валют и сохраняет график в файл."""
        if not self._currencies:
            print("Нет данных для визуализации.")
            return

        labels = []
        values = []
        for code, (name, (integer_part, fractional_part), _) in self._currencies.items():
            labels.append(f"{name} ({code})")
            values.append(float(f"{integer_part}.{fractional_part}"))

        # Построение графика
        plt.figure(figsize=(10, 5))
        plt.bar(labels, values, color='skyblue')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Курс к рублю')
        plt.title('Курсы валют')
        plt.tight_layout()
        plt.savefig('currencies.jpg')
        plt.show()


if __name__ == '__main__':
    fetcher = CurrencyFetcher(cooldown=1)
    
    try:
        result = fetcher.fetch_currencies(['R01035', 'R01335', 'R01700J'])
        print(result)
    except Exception as e:
        print(f"Ошибка: {e}")

    print(fetcher.get_currency_info('GBP'))
    
    fetcher.visualize_currencies()
```

1. Установил необходимые библиотеки

```
pip install requests matplotlib
```

Эти библиотеки нужны для:
  * **requests** — для получения данных с сайта ЦБ РФ.
  * **matplotlib** — для построения и сохранения графиков.

2. Я подключаюсь к сайту ЦБ РФ и получаю курсы валют для указанных ID.
3. Строю график на основе полученных данных и сохраняю его в файл currencies.jpg.

4. По умолчанию между запросами должна проходить как минимум 1 секунда. Если я хочу изменить этот параметр, мне нужно изменить значение тут:

```
fetcher = CurrencyFetcher(cooldown=2)
```
