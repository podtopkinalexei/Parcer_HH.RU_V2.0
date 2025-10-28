from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

import requests


class JobAPI(ABC):
    """Абстрактный класс для работы с API вакансий"""

    @abstractmethod
    def connect(self) -> None:
        """Метод подключения к API"""
        pass

    @abstractmethod
    def get_vacancies(self, keyword: str) -> List[Dict[str, Any]]:
        """Метод получения вакансий"""
        pass


class HeadHunterAPI(JobAPI):
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.__base_url = "https://api.hh.ru/"
        self.__headers = {'User-Agent': 'HHVacancyParser/1.0'}
        self.__connected = False

    def connect(self) -> None:
        """Подключение к API"""
        try:
            response = requests.get(f"{self.__base_url}vacancies", headers=self.__headers)
            response.raise_for_status()
            self.__connected = True
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ошибка подключения к API HH: {e}")

    def get_employers(self, employer_names: List[str]) -> List[Dict[str, Any]]:
        """
        Получение информации о работодателях по их названиям

        :param employer_names: Список названий компаний
        :return: Список словарей с информацией о компаниях
        """
        if not self.__connected:
            self.connect()

        employers = []
        for name in employer_names:
            params = {'text': name, 'only_with_vacancies': True, 'per_page': 1}
            try:
                response = requests.get(f"{self.__base_url}employers", params=params, headers=self.__headers)
                response.raise_for_status()
                data = response.json()
                if data['items']:
                    employer = data['items'][0]
                    employers.append({
                        'id': employer['id'],
                        'name': employer['name'],
                        'url': employer['alternate_url'],
                        'open_vacancies': employer['open_vacancies']
                    })
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении данных работодателя {name}: {e}")

        return employers

    def get_vacancies(self, employer_id: str, city_id: Optional[str] = None, per_page: int = 100) -> List[
        Dict[str, Any]]:
        """
        Получение вакансий по ID работодателя с возможностью фильтрации по городу

        :param employer_id: ID работодателя
        :param city_id: ID города для фильтрации (опционально)
        :param per_page: Количество вакансий на странице
        :return: Список вакансий
        """
        if not self.__connected:
            self.connect()

        params = {
            'employer_id': employer_id,
            'per_page': min(per_page, 100),
            'locale': 'RU'
        }

        if city_id:
            params['area'] = city_id  # Добавляем фильтр по городу

        try:
            response = requests.get(f"{self.__base_url}vacancies", params=params, headers=self.__headers)
            response.raise_for_status()
            data = response.json()
            return self._parse_vacancies(data.get('items', []))
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ошибка при запросе вакансий: {e}")

    def _parse_vacancies(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Приватный метод парсинга вакансий"""
        parsed_vacancies = []
        for item in items:
            salary = item.get('salary')
            address = item.get('address')
            city = address.get('city') if address else None

            vacancy = {
                'id': item.get('id'),
                'employer_id': item.get('employer', {}).get('id'),
                'title': item.get('name'),
                'salary_from': salary.get('from') if salary else None,
                'salary_to': salary.get('to') if salary else None,
                'currency': salary.get('currency') if salary else None,
                'url': item.get('alternate_url'),
                'description': item.get('snippet', {}).get('requirement', ''),
                'city': city
            }
            parsed_vacancies.append(vacancy)
        return parsed_vacancies

    def get_areas(self, city_name: str) -> List[Dict[str, Any]]:
        """
        Получение ID области/города по названию

        :param city_name: Название города
        :return: Список подходящих локаций
        """
        if not self.__connected:
            self.connect()

        try:
            response = requests.get(f"{self.__base_url}areas", headers=self.__headers)
            response.raise_for_status()
            areas = response.json()
            return self._find_city_id(areas, city_name)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ошибка при запросе регионов: {e}")

    def _find_city_id(self, areas: List[Dict[str, Any]], city_name: str) -> List[Dict[str, Any]]:
        """
        Рекурсивный поиск ID города по названию

        :param areas: Список регионов
        :param city_name: Название города
        :return: Список подходящих локаций
        """
        result = []
        for area in areas:
            if area['name'].lower() == city_name.lower():
                result.append({'id': area['id'], 'name': area['name']})
            if area['areas']:
                result.extend(self._find_city_id(area['areas'], city_name))
        return result
