from typing import List, Dict, Any

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


class DBManager:
    """Класс для управления базой данных PostgreSQL"""

    def __init__(self, dbname: str, user: str, password: str, host: str = 'localhost', port: str = '5432'):
        """
        Инициализация менеджера БД

        :param dbname: Имя базы данных
        :param user: Имя пользователя
        :param password: Пароль
        :param host: Хост
        :param port: Порт
        """
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.conn.autocommit = True

    def __del__(self):
        """Закрытие соединения при удалении объекта"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании

        :return: Список словарей с информацией о компаниях и количестве вакансий
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT e.name, COUNT(v.id) as vacancies_count
                FROM employers e
                LEFT JOIN vacancies v ON e.id = v.employer_id
                GROUP BY e.id
                ORDER BY vacancies_count DESC
            """
            cur.execute(query)
            return cur.fetchall()

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию

        :return: Список словарей с информацией о вакансиях
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT e.name as company, v.title, 
                       v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                ORDER BY e.name, v.salary_from DESC NULLS LAST
            """
            cur.execute(query)
            return cur.fetchall()

    def get_avg_salary(self) -> Dict[str, Any]:
        """
        Получает среднюю зарплату по вакансиям

        :return: Словарь с информацией о средней зарплате
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT 
                    AVG(salary_from) as avg_salary_from,
                    AVG(salary_to) as avg_salary_to
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """
            cur.execute(query)
            return cur.fetchone()

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям

        :return: Список словарей с информацией о вакансиях
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT e.name as company, v.title, 
                       v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE v.salary_from > (
                    SELECT AVG(salary_from) 
                    FROM vacancies 
                    WHERE salary_from IS NOT NULL
                ) OR v.salary_to > (
                    SELECT AVG(salary_to) 
                    FROM vacancies 
                    WHERE salary_to IS NOT NULL
                )
                ORDER BY COALESCE(v.salary_from, v.salary_to) DESC
            """
            cur.execute(query)
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные слова

        :param keyword: Ключевое слово для поиска
        :return: Список словарей с информацией о вакансиях
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = sql.SQL("""
                SELECT e.name as company, v.title, 
                       v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE v.title ILIKE %s
                ORDER BY e.name, v.title
            """)
            cur.execute(query, (f'%{keyword}%',))
            return cur.fetchall()

    def get_vacancies_by_city(self, city: str) -> List[Dict[str, Any]]:
        """
        Получает список вакансий в указанном городе

        :param city: Название города
        :return: Список словарей с информацией о вакансиях
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT e.name as company, v.title, 
                       v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE v.city ILIKE %s
                ORDER BY e.name, v.title
            """
            cur.execute(query, (f'%{city}%',))
            return cur.fetchall()

    def get_cities_with_counts(self) -> List[Dict[str, Any]]:
        """
        Получает список городов с количеством вакансий

        :return: Список словарей с информацией о городах
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT city, COUNT(*) as vacancies_count
                FROM vacancies
                WHERE city IS NOT NULL
                GROUP BY city
                ORDER BY vacancies_count DESC
            """
            cur.execute(query)
            return cur.fetchall()

    def insert_employer(self, employer: Dict[str, Any]) -> None:
        """
        Добавляет работодателя в БД

        :param employer: Словарь с информацией о работодателе
        """
        with self.conn.cursor() as cur:
            query = """
                INSERT INTO employers (id, name, url, open_vacancies)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """
            cur.execute(query, (
                employer['id'],
                employer['name'],
                employer['url'],
                employer['open_vacancies']
            ))

    def insert_vacancy(self, vacancy: Dict[str, Any]) -> None:
        """
        Добавляет вакансию в БД

        :param vacancy: Словарь с информацией о вакансии
        """
        with self.conn.cursor() as cur:
            query = """
                INSERT INTO vacancies (
                    id, employer_id, title, 
                    salary_from, salary_to, currency, 
                    url, description
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """
            cur.execute(query, (
                vacancy['id'],
                vacancy['employer_id'],
                vacancy['title'],
                vacancy['salary_from'],
                vacancy['salary_to'],
                vacancy['currency'],
                vacancy['url'],
                vacancy['description']
            ))
