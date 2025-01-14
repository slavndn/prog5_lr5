import pytest
from unittest.mock import patch
import time
from io import BytesIO
from main import CurrencyFetcher


@pytest.fixture 
@patch('requests.get')
def fetcher(mock_get):
    mock_get.return_value.content = mock_xml_response()
    return CurrencyFetcher(cooldown=1)


def mock_xml_response():
    xml_content = '''
    <ValCurs Date="11.01.2025" name="Foreign Currency Market">
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
    </ValCurs>
    '''
    return BytesIO(xml_content.encode('utf-8'))


def test_singleton(fetcher):
    fetcher1 = CurrencyFetcher()
    fetcher2 = CurrencyFetcher()
    assert fetcher1 is fetcher2, "CurrencyFetcher должен быть синглтоном"


@patch('requests.get')
def test_fetch_currencies(mock_get, fetcher):
    mock_get.return_value.content = mock_xml_response()
    result = fetcher.fetch_currencies(['R01035', 'R01335'])
    expected = [
        {'GBP': ('Фунт стерлингов', ('100', '25'))},
        {'PLN': ('Польский злотый', ('25', '50'))}
    ]
    assert result == expected, "Данные валют не соответствуют ожидаемым"


def test_get_currency_info(fetcher):
    fetcher.fetch_currencies(['R01035'])
    currency_info = fetcher.get_currency_info('GBP')
    assert currency_info == ('Фунт стерлингов', ('100', '25'), 1), "Некорректная информация о валюте"


def test_cooldown(fetcher):
    fetcher.fetch_currencies(['R01035'])
    
    with pytest.raises(Exception, match="Запросы можно делать не чаще"):
        fetcher.fetch_currencies(['R01035'])

    time.sleep(1)
    try:
        fetcher.fetch_currencies(['R01035'])
    except Exception:
        pytest.fail("Cooldown ограничение не сброшено после задержки")


@patch('matplotlib.pyplot.show')
def test_visualize_currencies(mock_show, fetcher):
    fetcher.fetch_currencies(['R01035', 'R01335'])
    try:
        fetcher.visualize_currencies()
        mock_show.assert_called_once()  # Проверяем, что график был показан
    except Exception as e:
        pytest.fail(f"Не удалось построить график: {e}")
