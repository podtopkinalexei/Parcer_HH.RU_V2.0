from config import DB_NAME, DB_USER, DB_PASSWORD
from src.db_creator import DBCreator
from src.db_manager import DBManager
from src.hh_api import HeadHunterAPI


def main():
    # Список интересующих компаний
    companies = [
        'Яндекс',
        'Тинькофф',
        'Сбер',
        'ВКонтакте',
        'Ростелеком',
        'Лаборатория Касперского',
        '1С',
        'МТС',
        'Газпром нефть',
        'Ozon'
    ]

    # Создаем базу данных и таблицы
    db_creator = DBCreator(DB_USER, DB_PASSWORD)
    db_creator.create_database(DB_NAME)
    db_creator.create_tables(DB_NAME)

    # Получаем данные от API
    hh_api = HeadHunterAPI()
    hh_api.connect()

    # Получаем информацию о компаниях
    employers = hh_api.get_employers(companies)
    print(f"Получено {len(employers)} компаний")

    # Создаем менеджер БД
    db_manager = DBManager(DB_NAME, DB_USER, DB_PASSWORD)

    # Заполняем таблицу employers
    for employer in employers:
        db_manager.insert_employer(employer)

    # Запрашиваем у пользователя город для фильтрации
    city_filter = input("Хотите фильтровать вакансии по городу? (y/n): ").lower()
    city_id = None

    if city_filter == 'y':
        city_name = input("Введите название города: ")
        areas = hh_api.get_areas(city_name)
        if areas:
            print(f"Найдены следующие локации: {', '.join([a['name'] for a in areas])}")
            if len(areas) == 1:
                city_id = areas[0]['id']
            else:
                print("Выберите нужную локацию:")
                for i, area in enumerate(areas, 1):
                    print(f"{i}. {area['name']}")
                choice = int(input("> ")) - 1
                city_id = areas[choice]['id']

    # Получаем и сохраняем вакансии для каждой компании
    for employer in employers:
        vacancies = hh_api.get_vacancies(employer['id'], city_id)
        print(f"Получено {len(vacancies)} вакансий для компании {employer['name']}")

        for vacancy in vacancies:
            db_manager.insert_vacancy(vacancy)

    # Взаимодействие с пользователем
    while True:
        print("\nВыберите действие:")
        print("1. Получить список всех компаний и количество вакансий")
        print("2. Получить список всех вакансий")
        print("3. Получить среднюю зарплату по вакансиям")
        print("4. Получить список вакансий с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("6. Получить список вакансий по городу")
        print("7. Получить список городов с количеством вакансий")
        print("0. Выход")

        choice = input("> ")

        if choice == '1':
            companies = db_manager.get_companies_and_vacancies_count()
            for company in companies:
                print(f"{company['name']}: {company['vacancies_count']} вакансий")

        elif choice == '2':
            vacancies = db_manager.get_all_vacancies()
            for vacancy in vacancies:
                salary = ""
                if vacancy['salary_from'] or vacancy['salary_to']:
                    salary = f"Зарплата: {vacancy['salary_from'] or '?'}-{vacancy['salary_to'] or '?'} {vacancy['currency'] or ''}"
                print(f"{vacancy['company']}: {vacancy['title']}. {salary}. Ссылка: {vacancy['url']}")

        elif choice == '3':
            avg_salary = db_manager.get_avg_salary()
            print(f"Средняя зарплата от: {avg_salary['avg_salary_from']:.2f}")
            print(f"Средняя зарплата до: {avg_salary['avg_salary_to']:.2f}")

        elif choice == '4':
            vacancies = db_manager.get_vacancies_with_higher_salary()
            for vacancy in vacancies:
                salary = f"Зарплата: {vacancy['salary_from'] or '?'}-{vacancy['salary_to'] or '?'} {vacancy['currency'] or ''}"
                print(f"{vacancy['company']}: {vacancy['title']}. {salary}. Ссылка: {vacancy['url']}")


        elif choice == '5':

            keyword = input("Введите ключевое слово для поиска: ")
            vacancies = db_manager.get_vacancies_with_keyword(keyword)

            if vacancies:
                print(f"\nНайдено {len(vacancies)} вакансий по ключевому слову '{keyword}':")

                for vacancy in vacancies:
                    salary = f"Зарплата: {vacancy['salary_from'] or '?'}-{vacancy['salary_to'] or '?'} {vacancy['currency'] or ''}"
                    print(f"\n{vacancy['company']}: {vacancy['title']}")
                    print(f"{salary}")
                    print(f"Ссылка: {vacancy['url']}")

            else:
                print(f"\nПо вашему запросу '{keyword}' вакансий не найдено.")
                print("Попробуйте изменить ключевое слово или использовать менее строгий фильтр.")


        elif choice == '6':

            city = input("Введите название города: ")
            vacancies = db_manager.get_vacancies_by_city(city)

            if vacancies:
                print(f"\nНайдено {len(vacancies)} вакансий в городе {city}:")

                for vacancy in vacancies:
                    salary = f"Зарплата: {vacancy['salary_from'] or '?'}-{vacancy['salary_to'] or '?'} {vacancy['currency'] or ''}"
                    print(f"\n{vacancy['company']}: {vacancy['title']}")
                    print(f"{salary}")
                    print(f"Ссылка: {vacancy['url']}")

            else:

                print(f"\nВ городе {city} вакансий не найдено.")

                print("Попробуйте уточнить название города или посмотрите список доступных городов (пункт 7).")

        elif choice == '7':
            cities = db_manager.get_cities_with_counts()
            if cities:
                print("\nГорода с количеством вакансий:")
                for city in cities:
                    print(f"{city['city']}: {city['vacancies_count']} вакансий")
            else:
                print("Информация о городах отсутствует")

        elif choice == '0':
            break

        else:
            print("Неверный ввод. Попробуйте еще раз.")


if __name__ == '__main__':
    main()
