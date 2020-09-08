from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from os import path
import time
from tools import log_tools
from tools.file import pickle_objects, get_pickled_objects

obj_data_path = '.\\data\\shopping_list.pkl'
products_list = list()
class Price_and_location:
    def __init__(self, site_name: str, page_address: str) -> None:
        self.__site_name = site_name
        self.__page_address = page_address
        self.__price = 0.0

    def __eq__(self, other):
        return self.__site_name == other.site_name and self.__page_address == other.page_address

    def __repr__(self) -> str:
        return f'<Page {self.__site_name,}, {self.__page_address}>'

    @property
    def site_name(self) -> str:
        return self.__site_name

    @property
    def page_address(self) -> str:
        return self.__page_address

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, num: float) -> None:
        print(num)
        self.__price = num

class Product:
    def __init__(self, name) -> None:
        self.__product_name = name
        self.__price_location = dict()
        self.__size = None
        self.__lowest_price = float()
        self.__lowest_chain = str()

    def __repr__(self) -> str:
        return f'<Product {self.__product_name}, {self.__size}>'

    def __eq__(self, other):
        return self.__product_name == other.product_name and self.__size == other.quantity

    @property
    def product_name(self) -> str:
        return self.__product_name

    @property
    def quantity(self) -> float:
        return self.__size

    @quantity.setter
    def quantity(self, size: float):
        self.__size = size

    @property
    def prices(self) -> dict():
        return self.__price_location

    @property
    def lowest_price(self) -> float:
        return self.__lowest_price

    @lowest_price.setter
    def lowest_price(self, num: float):
        self.__lowest_price = num

    @property
    def lowest_chain(self) -> str:
        return self.__lowest_chain

    @lowest_chain.setter
    def lowest_chain(self, a_name: str):
        self.__lowest_chain = a_name

    def add_location(self, chain_name: str, page_address: str) -> None:
        self.__price_location[chain_name] = Price_and_location(chain_name, page_address)

    def add_price(self, chain_name: str, price: float):
        self.__price_location[chain_name].price = price

    def available_at(self) -> list:
        return [*self.__price_location.keys()]

    def price_check(self):
        for val in self.__price_location.values():
            temp = val.price
            tmp_name = val.site_name
            break
        for page_price in self.prices.values():
            if page_price.price < temp:
                temp = page_price.price
                tmp_name = page_price.site_name
        self.lowest_price = temp
        self.lowest_chain = tmp_name


driver = webdriver.Chrome('C:\\Project venv\\chrome_driver\\chromedriver.exe')
waiter = WebDriverWait(driver, 20)

def display_product_list():
    length = len(products_list)
    p = 0
    while p < length:
        print(f'{p} {products_list[p]}')
        p += 1
    return p

def validate_selector(a_string: str, num: int) -> bool:
    if a_string.isnumeric():
        a = int(a_string)
        if 0 <= a < num:
            return True
        else:
            print(a_string + " is not a valid option")
            return False

def get_price_frm_countdown() -> float:
    elem = waiter.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="product-details"]/div[2]/div[2]/product-price/h3')))
    return float(elem.get_attribute('aria-label').strip('$ '))

def get_price_from_foodstuffs() -> float:
    driver.implicitly_wait(5)
    waiter.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/section")))
    try:
        waiter.until(EC.element_to_be_clickable((By.XPATH, '/html/body/header/div/div[2]/div/div[1]/div/div/div/div/div[2]/div/div/input')))
    except exceptions.StaleElementReferenceException:
        waiter.until(EC.element_to_be_clickable((By.XPATH, '/html/body/header/div/div[2]/div/div[1]/div/div/div/div/div[2]/div/div/input')))
    try:
        elem = waiter.until(EC.visibility_of_element_located((By.CLASS_NAME, 'fs-price-lockup__cents')))
        cents = int(elem.text.strip())
    except exceptions.StaleElementReferenceException:
        driver.implicitly_wait(5)
        elem = waiter.until(EC.visibility_of_element_located((By.CLASS_NAME, 'fs-price-lockup__cents')))
        cents = int(elem.text.strip())
    try:
        elem = driver.find_element_by_class_name('fs-price-lockup__dollars')
        dollars = int(elem.text.strip())
    except exceptions.StaleElementReferenceException:
        elem = driver.find_element_by_class_name('fs-price-lockup__dollars')
        dollars = int(elem.text.strip())
    return round(dollars + cents / 100, 2)

def get_product_info(page_address, product_loc):
    if page_address[:28] == 'https://shop.countdown.co.nz':
        shopping_chain = 'Countdown'
        price = get_price_frm_countdown()
    elif page_address[:31] == 'https://www.ishopnewworld.co.nz' or page_address[:32] == 'https://www.paknsaveonline.co.nz':
        price = get_price_from_foodstuffs()
        if page_address[:31] == 'https://www.ishopnewworld.co.nz':
            shopping_chain = 'New World'
        else:
            shopping_chain = "PAK'nSAVE"
    products_list[product_loc].add_location(shopping_chain, page_address)
    products_list[product_loc].add_price(shopping_chain, price)

def add_product():
    for product in products_list:
        print(product)
    option = 'o'
    print('--Add Product--')
    while option not in 'YN':
        option = input('Is product in list?:').upper()
    if option == 'Y':
        menu_max = display_product_list()
        option = input('Select product')
        if validate_selector(option, menu_max):
            product_loc = int(option)
            products_list[product_loc]
            page_address = input('URL:').strip()
            driver.get(page_address)
            get_product_info(page_address, product_loc)
    elif option == 'N':
        page_address = input('URL:').strip()
        driver.get(page_address)
        if page_address[:28] == 'https://shop.countdown.co.nz':
            elem = waiter.until(EC.presence_of_element_located((By.CLASS_NAME, "product-title")))
        elif page_address[:31] == 'https://www.ishopnewworld.co.nz' or page_address[
                                                                       :32] == 'https://www.paknsaveonline.co.nz':
            elem = waiter.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/section/div[1]/div/div/div/div/div[1]/div/h1")))
        products_list.append(Product(elem.text))
        get_product_info(page_address, -1)

if __name__ == "__main__":
    log_tools.script_id = "Auto_shopper"
    log_tools.run_date = time.strftime('%d-%m-%Y', time.localtime())
    log_tools.initialize(False)
    del time
    try:
        if path.isfile(obj_data_path):
            for i in get_pickled_objects(obj_data_path):
                products_list.append(i)
            log_tools.tprint(f'{len(products_list)} products loaded\n')
        else:
            print('No shopping list found.')
        option = None
        while option != 'X':
            print('\n\t--MENU--\n\t(A)dd product\n\t(S)ave shopping list\n\t(C)reate Cart\n\te(X)it')
            option = input('Option:').upper()
            if option == 'A':
                add_product()
            elif option == 'S':
                pickle_objects(obj_data_path, products_list)
            elif option == 'C':
                for item in products_list:
                    for name, page in item.prices.items():
                        driver.get(page.page_address)
                        if page.page_address[:28] == 'https://shop.countdown.co.nz':
                            page.price = get_price_frm_countdown()
                        elif page.page_address[:31] == 'https://www.ishopnewworld.co.nz' or page.page_address[:32] == 'https://www.paknsaveonline.co.nz':
                            page.price = get_price_from_foodstuffs()
                    item.price_check()
                print('\nCountdown:')
                for item in products_list:
                    if item.lowest_chain == 'Countdown':
                        print(f'{item} - ${item.lowest_price}')
                print("\nPAK'nSAVE:")
                for item in products_list:
                    if item.lowest_chain == "PAK'nSAVE":
                        print(f'{item} - ${item.lowest_price}')
                print("\nNew World:")
                for item in products_list:
                    if item.lowest_chain == "New World":
                        print(f'{item} - ${item.lowest_price}')
    finally:
        driver.quit()
