import pytest
from unittest.mock import patch, Mock
from requests.exceptions import RequestException


def test_connect_success(hh_api):
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        hh_api.connect()
        assert hh_api._HeadHunterAPI__connected is True


def test_connect_failure(hh_api):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = RequestException("Connection error")

        with pytest.raises(ConnectionError):
            hh_api.connect()
        assert hh_api._HeadHunterAPI__connected is False


def test_get_employers(hh_api):
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            'items': [{
                'id': '123',
                'name': 'Test Company',
                'alternate_url': 'http://test.com',
                'open_vacancies': 5
            }]
        }
        mock_get.return_value = mock_response

        employers = hh_api.get_employers(['Test Company'])
        assert len(employers) == 1
        assert employers[0]['name'] == 'Test Company'


def test_parse_vacancies(hh_api):
    test_data = [{
        'id': '123',
        'name': 'Python Developer',
        'employer': {'id': '456'},
        'salary': {'from': 100000, 'to': 150000, 'currency': 'RUB'},
        'alternate_url': 'http://test.com',
        'snippet': {'requirement': 'Test requirements'},
        'address': {'city': 'Moscow'}
    }]

    parsed = hh_api._parse_vacancies(test_data)
    assert len(parsed) == 1
    assert parsed[0]['title'] == 'Python Developer'
    assert parsed[0]['city'] == 'Moscow'
    