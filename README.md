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


# Тесты 

```python
import pytest
from unittest.mock import patch
from main import CurrencyFetcher
import time
```

*   **`import pytest`**: Импортирует библиотеку `pytest`, которая используется для написания и запуска тестов.
*   **`from unittest.mock import patch`**: Импортирует `patch` из `unittest.mock`. Это используется для замены (мокирования) объектов и функций во время тестов.
*   **`from main import CurrencyFetcher`**: Импортирует класс `CurrencyFetcher` из файла `main.py`, который мы хотим протестировать.
*   **`import time`**: Импортирует модуль `time`, который может быть использован в тестах.

```python
@pytest.fixture(scope="module")
def fetcher():
    """Создает экземпляр CurrencyFetcher для использования в тестах."""
    return CurrencyFetcher(cooldown=1)
```

*   **`@pytest.fixture(scope="module")`**: Это декоратор `pytest`, который определяет фикстуру (fixture). Фикстуры - это функции, которые предоставляют данные или ресурсы для тестов. `scope="module"` означает, что фикстура создается один раз для всего модуля тестов (то есть для всего файла `test.py`).
*   **`def fetcher():`**:  Это определение функции-фикстуры. Она возвращает объект `CurrencyFetcher` с `cooldown` равным `1`. Теперь все тесты в этом файле могут использовать этот объект.

```python
def mock_xml_response():
    """Возвращает фальшивый XML-ответ для тестирования."""
    return '''<ValCurs Date="17.01.2025" name="Foreign Currency Market">
                <Valute ID="R01035">
                    <CharCode>GBP</CharCode>
                    <Name>Фунт стерлингов</Name>
                    <Value>100,25</Value>
                    <Nominal>1</Nominal>
                </Valute>
                <Valute ID="R01335">
                    <CharCode>PLN</CharCode>
                    <Name>Польский злотый</Name>
                    <Value>25,50</Value>
                    <Nominal>10</Nominal>
                </Valute>
              </ValCurs>'''
```

*   **`def mock_xml_response():`**: Это функция, которая возвращает строку с фальшивым XML-ответом от сайта ЦБ РФ. Этот XML используется для мокирования запроса к сайту, чтобы тесты не зависели от реального сервера и данных.

```python
def test_singleton_behavior():
    """Тестирует, что CurrencyFetcher является синглтоном."""
    instance1 = CurrencyFetcher()
    instance2 = CurrencyFetcher()
    assert instance1 is instance2, "Экземпляры CurrencyFetcher должны быть одинаковыми (синглтон)"
```

*   **`def test_singleton_behavior():`**: Это тестовая функция, которая проверяет, что `CurrencyFetcher` работает как синглтон (то есть создается только один экземпляр).
*   **`instance1 = CurrencyFetcher()`**: Создает первый экземпляр `CurrencyFetcher`.
*   **`instance2 = CurrencyFetcher()`**: Создает второй экземпляр `CurrencyFetcher`.
*   **`assert instance1 is instance2, ...`**: Использует оператор `assert`, чтобы проверить, что `instance1` и `instance2` — это один и тот же объект. Если это не так, то тест упадет.

```python
@patch('requests.get')
def test_fetch_currencies(mock_get, fetcher):
    """Тестирует получение и сохранение валютных данных."""
    mock_get.return_value.content = mock_xml_response()
    result = fetcher.fetch_currencies(['R01035', 'R01335'])
    assert len(result) == 2, "Должно вернуться две валюты"
    assert 'GBP' in fetcher._currencies, "GBP должна быть в сохраненных валютах"
    assert fetcher._currencies['GBP'] == ('Фунт стерлингов', ('100', '25'), 1)
```

*   **`@patch('requests.get')`**: Декоратор `patch` заменяет функцию `requests.get` на объект-заглушку `mock_get`. Это позволяет контролировать поведение запроса к сайту ЦБ РФ.
*   **`def test_fetch_currencies(mock_get, fetcher):`**: Тестовая функция, которая проверяет корректность работы метода `fetch_currencies` класса `CurrencyFetcher`.
*   **`mock_get.return_value.content = mock_xml_response()`**: Устанавливает ответ `mock_get` так, чтобы он возвращал фальшивый XML-ответ.
*   **`result = fetcher.fetch_currencies(['R01035', 'R01335'])`**: Вызывает `fetch_currencies` с двумя ID валют и сохраняет результат.
*   **`assert len(result) == 2, ...`**: Проверяет, что было возвращено два объекта в списке `result` (т.е., что были получены данные для двух валют).
*   **`assert 'GBP' in fetcher._currencies, ...`**: Проверяет, что код валюты 'GBP' присутствует в словаре `fetcher._currencies` (то есть, что данные о валюте были сохранены).
*   **`assert fetcher._currencies['GBP'] == ('Фунт стерлингов', ('100', '25'), 1)`**: Проверяет, что сохраненные данные для GBP соответствуют ожидаемым значениям.

```python
@patch('time.time', side_effect=[0, 1.5, 3])
@patch('requests.get')
def test_cooldown(mock_get, mock_time, fetcher):
    """Тестирует соблюдение периода ожидания между запросами."""
    mock_get.return_value.content = mock_xml_response()
    fetcher.fetch_currencies(['R01035'])  # Первый вызов успешен
    with pytest.raises(Exception, match="Запросы можно делать не чаще"):
        fetcher.fetch_currencies(['R01035'])  # Второй вызов слишком рано
    fetcher.fetch_currencies(['R01035'])  # Третий вызов должен быть успешен
```

*   **`@patch('time.time', side_effect=[0, 1.5, 3])`**:  `patch` заменяет `time.time` на мок, который будет возвращать значения `0`, `1.5` и `3` по очереди при каждом вызове.
*   **`@patch('requests.get')`**: Аналогично, заменяем `requests.get`.
*   **`def test_cooldown(mock_get, mock_time, fetcher):`**:  Тестовая функция, которая проверяет, что `fetch_currencies` соблюдает `cooldown`.
*   **`mock_get.return_value.content = mock_xml_response()`**: Устанавливает `mock_get` для возврата фальшивого ответа.
*   **`fetcher.fetch_currencies(['R01035'])`**:  Первый вызов `fetch_currencies`, должен пройти успешно.
*   **`with pytest.raises(Exception, match="Запросы можно делать не чаще"):`**: Ожидает, что следующий вызов `fetch_currencies` вызовет исключение.
*   **`fetcher.fetch_currencies(['R01035'])`**:  Второй вызов, должен вызвать ошибку.
*   **`fetcher.fetch_currencies(['R01035'])`**: Третий вызов `fetch_currencies`, должен пройти успешно (так как прошло достаточно времени).

```python
@patch('matplotlib.pyplot.show')
def test_visualize_currencies(mock_show, fetcher):
    """Тестирует построение и отображение графика."""
    fetcher._currencies = {
        'GBP': ('Фунт стерлингов', ('100', '25'), 1),
        'PLN': ('Польский злотый', ('25', '50'), 10)
    }
    fetcher.visualize_currencies()
    mock_show.assert_called_once()
```
*   **`@patch('matplotlib.pyplot.show')`**: Заменяет `plt.show` моком `mock_show`.
*   **`def test_visualize_currencies(mock_show, fetcher):`**: Тест для проверки отрисовки графика.
*   **`fetcher._currencies = {...}`**: Создаем тестовые данные для отрисовки.
*   **`fetcher.visualize_currencies()`**:  Вызываем функцию отрисовки.
*   **`mock_show.assert_called_once()`**: Проверяем, что метод `plt.show()` был вызван один раз.


![image](https://github.com/user-attachments/assets/44d37382-9962-4a35-9ca7-3d69a9397a3a)
![image](https://github.com/user-attachments/assets/3f91165d-1c93-45a5-a0ed-6b53ee8f3e18)

