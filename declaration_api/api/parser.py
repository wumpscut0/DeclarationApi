from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from .models import Declaration


class Parser:
    _host = "https://www.farpost.ru/"
    _source = ("vladivostok/service/construction/guard/"
               "%D0%A1%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D1%8B+"
               "%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE%D0%BD%D0%B0%D0%B1%D0%BB%D1%8E%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F/")
    _total_declarations = 10

    _options = webdriver.ChromeOptions()
    _options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    _options.add_argument("--disable-blink-features=AutomationControlled")
    _options.add_argument('--headless')
    _options.add_argument('--no-sandbox')
    _options.add_argument('--disable-dev-shm-usage')
    _options.add_argument('--disable-cache')
    _options.add_argument('--incognito')

    _chromedriver_path = '/usr/bin/chromedriver'
    _service = Service(_chromedriver_path)
    _cookies = None

    @classmethod
    def _fetch_page(cls, address: str, driver, timeout: int = 10):
        try:
            driver.delete_all_cookies()
            driver.get(cls._host + address)
            WebDriverWait(driver, timeout).until(
                lambda x: x.execute_script("return document.readyState") == "complete"
            )
            return driver.page_source
        except TimeoutException:
            return None

    @classmethod
    def _parse(cls, driver: WebDriver):
        declaration_list_source = cls._fetch_page(cls._source, driver)
        root_soup = BeautifulSoup(declaration_list_source, 'html.parser')
        declarations = root_soup.find_all("tr", class_="bull-list-item-js -exact", attrs={"data-doc-id": True, "data-source": "actual"})[:cls._total_declarations]
        for position, data in enumerate(declarations, start=1):
            jsonify_data = {
                "position": position,
                "id": data.get("data-doc-id")
            }

            header_tag = data.find('a', class_='bulletinLink bull-item__self-link auto-shy', attrs={"data-role": "bulletin-link"})
            if header_tag:
                jsonify_data["header"] = header_tag.text.strip()
                link = header_tag.get("href")
            else:
                jsonify_data["header"] = "No header"
                link = ""

            views_tag = data.find('span', class_="views nano-eye-text", attrs={"title": "Количество просмотров"})
            if views_tag:
                jsonify_data["views"] = int(views_tag.text.strip())
            else:
                jsonify_data["views"] = 0

            if link:
                declaration_detail_source = cls._fetch_page(link, driver)
                declaration_detail_soup = BeautifulSoup(declaration_detail_source, 'html.parser')

                user_nick_tag = declaration_detail_soup.find('span', class_="userNick auto-shy")
                if user_nick_tag:
                    author_link = user_nick_tag.find("a").get("href")

                    author_detail_source = cls._fetch_page(author_link, driver)
                    author_detail_soup = BeautifulSoup(author_detail_source, 'html.parser')

                    nick_tag = author_detail_soup.find('span', class_="userNick auto-shy")
                    phone_tag = author_detail_soup.find("div", class_="separated-list__item phoneItem")
                    address_tag = author_detail_soup.find("a", class_="company-places__item")

                    nick = nick_tag.text.strip() if nick_tag else "No Nick"
                    phone = phone_tag.text.strip() if phone_tag else "No Phone"
                    address = address_tag.text.strip() if address_tag else "No Address"

                    jsonify_data["author"] = f"{nick}\n{phone}\n{address}"
                else:
                    jsonify_data["author"] = "No Author Info"
            else:
                jsonify_data["author"] = "No Author Info"

            yield jsonify_data

    @classmethod
    def run(cls):
        driver = webdriver.Chrome(service=cls._service, options=cls._options)
        yield from cls._parse(driver)
        driver.quit()


if __name__ == '__main__':
    for declaration in Parser.run():
        Declaration.objects.create(**declaration)
