import os

import pytest
from dotenv import load_dotenv

from src.db_creator import DBCreator
from src.db_manager import DBManager
from src.hh_api import HeadHunterAPI

load_dotenv()


@pytest.fixture(scope="session")
def test_db():
    """Создаем тестовую БД и таблицы один раз для всех тестов"""
    creator = DBCreator(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST')
    )

    # Создаем тестовую БД
    creator.create_database(os.getenv('TEST_DB_NAME', 'hh_vacancies_test'))

    # Создаем таблицы в тестовой БД
    creator.create_tables(os.getenv('TEST_DB_NAME', 'hh_vacancies_test'))

    yield


@pytest.fixture
def db_manager(test_db):
    """Фикстура для DBManager с подключением к тестовой БД"""
    db = DBManager(
        dbname=os.getenv('TEST_DB_NAME', 'hh_vacancies_test'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST')
    )
    yield db
    # Очистка таблиц после каждого теста
    with db.conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE vacancies, employers RESTART IDENTITY CASCADE")
    db.conn.commit()


@pytest.fixture
def hh_api():
    return HeadHunterAPI()


@pytest.fixture
def sample_employer():
    return {
        'id': '12345',
        'name': 'Test Company',
        'url': 'http://test.com',
        'open_vacancies': 10
    }


@pytest.fixture
def sample_vacancy():
    return {
        'id': '54321',
        'employer_id': '12345',
        'title': 'Test Vacancy',
        'salary_from': 100000,
        'salary_to': 150000,
        'currency': 'RUB',
        'url': 'http://test.com/vacancy',
        'description': 'Test description',
        'city': 'Москва'
    }
