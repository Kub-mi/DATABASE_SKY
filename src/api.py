import requests
from typing import List, Dict


class HHApi:
    """
    Класс для работы с API hh.ru
    """

    BASE_URL = "https://api.hh.ru"

    @staticmethod
    def get_employer_vacancies(employer_id: str, per_page=100) -> List[Dict]:
        """
        Получить список вакансий по id работодателя.
        """
        url = f"{HHApi.BASE_URL}/vacancies"
        params = {"employer_id": employer_id, "per_page": per_page}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("items", [])

    @staticmethod
    def get_employer_info(employer_id: str) -> Dict:
        """
        Получить информацию о работодателе по id.
        """
        url = f"{HHApi.BASE_URL}/employers/{employer_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
