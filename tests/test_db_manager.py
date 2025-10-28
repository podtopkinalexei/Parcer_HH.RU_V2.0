def test_insert_employer(db_manager, sample_employer):
    db_manager.insert_employer(sample_employer)

    with db_manager.conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM employers WHERE id = %s", (sample_employer['id'],))
        count = cur.fetchone()[0]
        assert count == 1


def test_insert_vacancy(db_manager, sample_employer, sample_vacancy):
    # Сначала добавляем работодателя
    db_manager.insert_employer(sample_employer)

    # Затем добавляем вакансию
    db_manager.insert_vacancy(sample_vacancy)

    with db_manager.conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM vacancies WHERE id = %s", (sample_vacancy['id'],))
        count = cur.fetchone()[0]
        assert count == 1


def test_get_companies_and_vacancies_count(db_manager, sample_employer, sample_vacancy):
    # Подготовка тестовых данных
    db_manager.insert_employer(sample_employer)
    db_manager.insert_vacancy(sample_vacancy)

    # Тестируемый метод
    result = db_manager.get_companies_and_vacancies_count()

    assert len(result) == 1
    assert result[0]['name'] == sample_employer['name']
    assert result[0]['vacancies_count'] == 1


def test_get_all_vacancies(db_manager, sample_employer, sample_vacancy):
    db_manager.insert_employer(sample_employer)
    db_manager.insert_vacancy(sample_vacancy)

    vacancies = db_manager.get_all_vacancies()

    assert len(vacancies) == 1
    assert vacancies[0]['title'] == sample_vacancy['title']
    assert vacancies[0]['company'] == sample_employer['name']


def test_get_vacancies_with_keyword(db_manager, sample_employer, sample_vacancy):
    db_manager.insert_employer(sample_employer)
    db_manager.insert_vacancy(sample_vacancy)

    # Ищем по ключевому слову из названия вакансии
    vacancies = db_manager.get_vacancies_with_keyword('Test')

    assert len(vacancies) == 1
    assert vacancies[0]['title'] == sample_vacancy['title']
