# from multiprocessing.pool import ThreadPool
#
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.webdriver import WebDriver
# from selenium.webdriver.support.ui import WebDriverWait
#
#
# class SeleniumParser:
#     _host = "https://www.farpost.ru/"
#     _source = ("vladivostok/service/construction/guard/"
#                "%D0%A1%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D1%8B+"
#                "%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE%D0%BD%D0%B0%D0%B1%D0%BB%D1%8E%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F/")
#     _user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"]
#     _chromedriver_path = '/usr/bin/chromedriver'
#
#     # @staticmethod
#     # def _random_sleep():
#     #     time.sleep(uniform(1, 2))
#
#     # @classmethod
#     # def _simulate_user_actions(cls, driver):
#     #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     #     cls._random_sleep()
#     #     driver.execute_script("window.scrollTo(0, 0);")
#     #     cls._random_sleep()
#
#     # @classmethod
#     # def _masking(cls, driver):
#     #     cls._random_sleep()
#         # cls._simulate_user_actions(driver)
#
#     @classmethod
#     def _fetch_page(cls, address: str, driver, timeout: int | None = None):
#         driver.get(cls._host + address)
#         WebDriverWait(driver, timeout).until(
#             lambda x: x.execute_script("return document.readyState") == "complete"
#         )
#         # cls._masking(driver)
#         if "Мы зарегистрировали подозрительный траффик, исходящий из вашей сети." in driver.page_source:
#             return
#         return driver.page_source
#
#     @classmethod
#     def _parse(cls, position, data, driver):
#         declaration_data = {
#             "position": position,
#             "id": data.get("data-doc-id")
#         }
#         author_data = {}
#
#         header_tag = data.find('a', class_='bulletinLink bull-item__self-link auto-shy',
#                                attrs={"data-role": "bulletin-link"})
#         if header_tag:
#             declaration_data["header"] = header_tag.text.strip()
#             link = header_tag.get("href")
#         else:
#             declaration_data["header"] = "No header"
#             link = ""
#
#         views_tag = data.find('span', class_="views nano-eye-text", attrs={"title": "Количество просмотров"})
#         if views_tag:
#             declaration_data["views"] = int(views_tag.text.strip())
#         else:
#             declaration_data["views"] = -1
#
#         if link:
#             declaration_detail_source = cls._fetch_page(link, driver)
#             declaration_detail_soup = BeautifulSoup(declaration_detail_source, 'html.parser')
#
#             user_nick_tag = declaration_detail_soup.find('span', class_="userNick auto-shy")
#             if user_nick_tag:
#                 author_link = user_nick_tag.find("a").get("href")
#
#                 author_detail_source = cls._fetch_page(author_link, driver)
#                 author_detail_soup = BeautifulSoup(author_detail_source, 'html.parser')
#
#                 nick_tag = author_detail_soup.find('span', class_="userNick auto-shy")
#                 phone_tag = author_detail_soup.find("div", class_="separated-list__item phoneItem")
#                 address_tag = author_detail_soup.find("a", class_="company-places__item")
#
#                 author_data["name"] = nick_tag.text.strip() if nick_tag else "No Nick"
#                 author_data["phone"] = phone_tag.text.strip() if phone_tag else "No Phone"
#                 author_data["address"] = address_tag.text.strip() if address_tag else "No Address"
#
#         return declaration_data, author_data
#
#     @classmethod
#     def _run_parse(cls, driver: WebDriver, timeout, total_declarations):
#         declaration_list_source = cls._fetch_page(cls._source, driver, timeout)
#         if declaration_list_source is None:
#             return
#         root_soup = BeautifulSoup(declaration_list_source, 'html.parser')
#         declarations = root_soup.find_all("tr", class_="bull-list-item-js -exact", attrs={"data-doc-id": True, "data-source": "actual"})[:total_declarations]
#         args = [(position, data, driver) for position, data in enumerate(declarations, start=1)]
#         pool = ThreadPool(processes=total_declarations)
#         result = pool.starmap(cls._parse, args)
#         pool.close()
#         pool.join()
#         return result
#
#     @classmethod
#     def _build_driver(cls):
#         options = webdriver.ChromeOptions()
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_argument('--headless')
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#         options.add_argument('--disable-cache')
#         options.add_argument('--incognito')
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument('--disable-blink-features=AutomationControlled')
#         options.add_argument("--window-size=1920,1080")
#         options.add_argument("--start-maximized")
#
#         service = Service(cls._chromedriver_path)
#
#         return webdriver.Chrome(service=service, options=options)
#
#     @classmethod
#     def run(cls, timeout: int | None = None, total_declarations: int = 10):
#         driver = cls._build_driver()
#         data = cls._run_parse(driver, timeout, total_declarations)
#         driver.quit()
#         return data
