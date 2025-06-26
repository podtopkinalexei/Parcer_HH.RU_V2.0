import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DBCreator:
    """Класс для создания базы данных и таблиц"""

    def __init__(self, user: str, password: str, host: str = 'localhost', port: str = '5432'):
        """
        Инициализация создателя БД

        :param user: Имя пользователя
        :param password: Пароль
        :param host: Хост
        :param port: Порт
        """
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None

    def create_database(self, dbname: str) -> None:
        """
        Создание базы данных

        :param dbname: Имя базы данных
        """
        try:
            # Подключаемся к postgres для создания новой БД
            conn = psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            with conn.cursor() as cur:
                # Проверяем, существует ли БД
                cur.execute(sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s"), [dbname])
                exists = cur.fetchone()

                if not exists:
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
                    print(f"База данных {dbname} успешно создана")
                else:
                    print(f"База данных {dbname} уже существует")

            conn.close()
        except Exception as e:
            print(f"Ошибка при создании базы данных: {e}")
            raise

    def create_tables(self, dbname: str) -> None:
        """
        Создание таблиц в базе данных

        :param dbname: Имя базы данных
        """
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )

            with self.conn.cursor() as cur:
                # Создаем таблицу employers
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS employers (
                        id VARCHAR(20) PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        url VARCHAR(100),
                        open_vacancies INTEGER
                    )
                """)

                # Создаем таблицу vacancies
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id VARCHAR(20) PRIMARY KEY,
                        employer_id VARCHAR(20) REFERENCES employers(id),
                        title VARCHAR(100) NOT NULL,
                        salary_from INTEGER,
                        salary_to INTEGER,
                        currency VARCHAR(10),
                        url VARCHAR(100),
                        description TEXT,
                        city VARCHAR(50)
                    )
                """)

                print("Таблицы успешно созданы")

            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()
