from src.api import HHApi
from src.db import create_database, create_tables, DBManager
from psycopg2.errors import UniqueViolation

def main():
    # 1. Создание БД и таблиц
    create_database()
    create_tables()
    print("База данных и таблицы созданы.")

    # 2. Сбор и заполнение данных о работодателях и вакансиях
    employer_ids = [
        '3529', '1740', '78638', '1006202', '2180',
        '3776', '87021', '1379', '15478', '39305'
    ]
    dbm = DBManager()
    for emp_id in employer_ids:
        emp_info = HHApi.get_employer_info(emp_id)
        try:
            with dbm.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO employers (hh_id, name)
                    VALUES (%s, %s)
                    ON CONFLICT (hh_id) DO NOTHING;
                    """,
                    (emp_id, emp_info.get('name'))
                )
                cur.execute("SELECT id FROM employers WHERE hh_id = %s", (emp_id,))
                employer_db_id = cur.fetchone()[0]
                vacancies = HHApi.get_employer_vacancies(emp_id)
                for v in vacancies:
                    salary = v['salary']['from'] if v.get('salary') and v['salary'].get('from') else None
                    cur.execute(
                        """
                        INSERT INTO vacancies (hh_id, employer_id, name, salary, url)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (hh_id) DO NOTHING;
                        """,
                        (v['id'], employer_db_id, v['name'], salary, v['alternate_url'])
                    )
            print(f"Работодатель и вакансии {emp_info.get('name')} добавлены.")
        except Exception as e:
            print(f"Ошибка при добавлении работодателя {emp_id}: {e}")

    # 3. Взаимодействие с пользователем через CLI
    while True:
        print("\n1. Компании и количество вакансий")
        print("2. Все вакансии")
        print("3. Средняя зарплата")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Вакансии по ключевому слову")
        print("0. Выход")
        choice = input("Выберите действие: ")
        if choice == '1':
            for name, count in dbm.get_companies_and_vacancies_count():
                print(f"Компания: {name} | Вакансий: {count}")
        elif choice == '2':
            for row in dbm.get_all_vacancies():
                print(f"Компания: {row[0]} | Вакансия: {row[1]} | Зарплата: {row[2]} | Ссылка: {row[3]}")
        elif choice == '3':
            print(f"Средняя зарплата: {dbm.get_avg_salary():.2f}")
        elif choice == '4':
            for row in dbm.get_vacancies_with_higher_salary():
                print(f"Компания: {row[0]} | Вакансия: {row[1]} | Зарплата: {row[2]} | Ссылка: {row[3]}")
        elif choice == '5':
            kw = input("Введите ключевое слово: ")
            for row in dbm.get_vacancies_with_keyword(kw):
                print(f"Компания: {row[0]} | Вакансия: {row[1]} | Зарплата: {row[2]} | Ссылка: {row[3]}")
        elif choice == '0':
            print("Выход.")
            break
        else:
            print("Неверный ввод.")

if __name__ == '__main__':
    main()