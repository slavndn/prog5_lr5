import pytest
from unittest.mock import patch
from main import CurrencyFetcher
import time


@pytest.fixture(scope="module")
def fetcher():
    """Создает экземпляр CurrencyFetcher для использования в тестах."""
    return CurrencyFetcher(cooldown=1)


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


def test_singleton_behavior():
    """Тестирует, что CurrencyFetcher является синглтоном."""
    instance1 = CurrencyFetcher()
    instance2 = CurrencyFetcher()
    assert instance1 is instance2, "Экземпляры CurrencyFetcher должны быть одинаковыми (синглтон)"


@patch('requests.get')
def test_fetch_currencies(mock_get, fetcher):
    """Тестирует получение и сохранение валютных данных."""
    mock_get.return_value.content = mock_xml_response()
    result = fetcher.fetch_currencies(['R01035', 'R01335'])
    assert len(result) == 2, "Должно вернуться две валюты"
    assert 'GBP' in fetcher._currencies, "GBP должна быть в сохраненных валютах"
    assert fetcher._currencies['GBP'] == ('Фунт стерлингов', ('100', '25'), 1)


@patch('time.time', side_effect=[0, 1.5, 3])
@patch('requests.get')
def test_cooldown(mock_get, mock_time, fetcher):
    """Тестирует соблюдение периода ожидания между запросами."""
    mock_get.return_value.content = mock_xml_response()
    fetcher.fetch_currencies(['R01035'])  # Первый вызов успешен
    with pytest.raises(Exception, match="Запросы можно делать не чаще"):
        fetcher.fetch_currencies(['R01035'])  # Второй вызов слишком рано
    fetcher.fetch_currencies(['R01035'])  # Третий вызов должен быть успешен


@patch('matplotlib.pyplot.show')
def test_visualize_currencies(mock_show, fetcher):
    """Тестирует построение и отображение графика."""
    fetcher._currencies = {
        'GBP': ('Фунт стерлингов', ('100', '25'), 1),
        'PLN': ('Польский злотый', ('25', '50'), 10)
    }
    fetcher.visualize_currencies()
    mock_show.assert_called_once()