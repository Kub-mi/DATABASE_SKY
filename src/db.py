from typing import List, Tuple

import psycopg2
from .postgres import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def create_database():
    """
    Создает БД, если не существует.
    """
    # Подключение к postgres (не к самой БД, а к серверу)
    conn = psycopg2.connect(
        dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}';")
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {DB_NAME};")
    cur.close()
    conn.close()


def create_tables():
    """
    Создает таблицы работодателей и вакансий.
    """
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employers (
            id SERIAL PRIMARY KEY,
            hh_id VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL
        );
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            hh_id VARCHAR(20) UNIQUE NOT NULL,
            employer_id INTEGER REFERENCES employers(id),
            name VARCHAR(255) NOT NULL,
            salary INTEGER,
            url TEXT
        );
    """
    )
    conn.commit()
    cur.close()
    conn.close()


class DBManager:
    """
    Класс для управления вакансиями в БД PostgreSQL.
    """

    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        self.conn.autocommit = True

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Список всех компаний и количества вакансий у каждой.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, COUNT(v.id)
                FROM employers e
                LEFT JOIN vacancies v ON e.id = v.employer_id
                GROUP BY e.name
            """
            )
            return cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, int, str]]:
        """
        Список всех вакансий с указанием названия компании, вакансии, зарплаты и ссылки.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, v.name, v.salary, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
            """
            )
            return cur.fetchall()

    def get_avg_salary(self) -> float:
        """
        Средняя зарплата по вакансиям.
        """
        with self.conn.cursor() as cur:
            cur.execute("SELECT AVG(salary) FROM vacancies WHERE salary IS NOT NULL;")
            return cur.fetchone()[0] or 0

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, int, str]]:
        """
        Вакансии с зарплатой выше средней.
        """
        avg_salary = self.get_avg_salary()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, v.name, v.salary, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE v.salary > %s
            """,
                (avg_salary,),
            )
            return cur.fetchall()

    def get_vacancies_with_keyword(
        self, keyword: str
    ) -> List[Tuple[str, str, int, str]]:
        """
        Вакансии, в названии которых есть keyword.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, v.name, v.salary, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE v.name ILIKE %s
            """,
                (f"%{keyword}%",),
            )
            return cur.fetchall()
