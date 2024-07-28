from multiprocessing.pool import ThreadPool

from requests import get
from bs4 import BeautifulSoup


class Parser:
    _host = "https://www.farpost.ru/"
    _source = ("vladivostok/service/construction/guard/"
               "%D0%A1%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D1%8B+"
               "%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE%D0%BD%D0%B0%D0%B1%D0%BB%D1%8E%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F/")

    @classmethod
    def _fetch_page(cls, address: str, timeout: int | None = None):
        page_source = get(cls._host + address, timeout=timeout).text
        if "Мы зарегистрировали подозрительный траффик, исходящий из вашей сети." in page_source:
            return
        return page_source

    @classmethod
    def _parse(cls, position, data):
        declaration_data = {
            "position": position,
            "id": data.get("data-doc-id")
        }
        author_data = {}

        header_tag = data.find('a', class_='bulletinLink bull-item__self-link auto-shy',
                               attrs={"data-role": "bulletin-link"})
        if header_tag:
            declaration_data["header"] = header_tag.text.strip()
            link = header_tag.get("href")
        else:
            declaration_data["header"] = "No header"
            link = ""

        views_tag = data.find('span', class_="views nano-eye-text", attrs={"title": "Количество просмотров"})
        if views_tag:
            declaration_data["views"] = int(views_tag.text.strip())

        if link:
            declaration_detail_source = cls._fetch_page(link)
            if declaration_detail_source is not None:
                declaration_detail_soup = BeautifulSoup(declaration_detail_source, 'html.parser')

                user_nick_tag = declaration_detail_soup.find('span', class_="userNick auto-shy")
                if user_nick_tag:
                    author_link = user_nick_tag.find("a").get("href")

                    author_detail_source = cls._fetch_page(author_link)
                    if author_detail_source is not None:
                        author_detail_soup = BeautifulSoup(author_detail_source, 'html.parser')

                        nick_tag = author_detail_soup.find('span', class_="userNick auto-shy")
                        phone_tag = author_detail_soup.find("div", class_="separated-list__item phoneItem")
                        address_tag = author_detail_soup.find("a", class_="company-places__item")

                        author_data["name"] = nick_tag.text.strip() if nick_tag else None
                        author_data["phone"] = phone_tag.text.strip() if phone_tag else None
                        author_data["address"] = address_tag.text.strip() if address_tag else None

        return declaration_data, author_data

    @classmethod
    def _run_parse(cls, timeout, total_declarations):
        declaration_list_source = cls._fetch_page(cls._source, timeout)
        if declaration_list_source is None:
            return
        root_soup = BeautifulSoup(declaration_list_source, 'html.parser')
        declarations = root_soup.find_all("tr", class_="bull-list-item-js -exact", attrs={"data-doc-id": True, "data-source": "actual"})[:total_declarations]
        for position, data in enumerate(declarations, start=1):
            yield cls._parse(position, data)

    @classmethod
    def run(cls, timeout: int | None = None, total_declarations: int = 10):
        yield from cls._run_parse(timeout, total_declarations)
