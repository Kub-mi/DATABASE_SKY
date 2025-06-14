from src.api import HHApi
from src.db import create_database, create_tables
from src.db import DBManager

def main():
    # 1. Создание БД и таблиц
    create_database()
    create_tables()
    print("База данных и таблицы созданы.")

    # 2. Сбор и заполнение данных о работодателях и вакансиях
    employer_ids = ['3529', '1740', '78638']  # Сюда свои id работодателей
    # --- код для получения и вставки данных в БД ---
    # В этом месте реализуй заполнение БД данными

    # 3. Взаимодействие с пользователем через CLI
    dbm = DBManager()
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