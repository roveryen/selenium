
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from .scrappy import Scrappy

import re

class ScrappyTeslaGuru(Scrappy):

    def __init__(self):
        
        self.dict_target_url = {
            "tesla"  : "https://teslagu.ru/supercharger/",
        }

        self.dict_css_selectors = {
            "table" : ".page-content .wp-block-table",
        }

        self.scrape_results = {
            'source': 'teslaguru',
            'plug' : 'all',
            'stations': []
        }

        super().__init__()


    def __parse_data_to_lat_and_lng(self, href):
        return re.findall(r'\d+\.\d+', href)

    def __extract_row_data(self, element):
        try:

            if ( False == element.is_enabled() ):
                self.logging("showDetail => element is not enabled")
                return False

            if ( False == element.is_displayed() ):
                self.logging("showDetail => element is not displayed")
                return False

            result = {
                "title"    : "Unknown title",
                "address"  : {
                    "lat"  : 0.0,
                    "lng"  : 0.0
                },
                "tpc"      : 0,
                "ccs2"     : 0,
                "type"     : "",
                "floor"    : 1,
                "business" : "",
                "fee"      : "",
                "park_fee" : "",
                "remark"   : ""
            }
        

            link = element.find_element(By.CSS_SELECTOR, "td a[href]")
            if None is link:
                return False

            cells = element.find_elements(By.CSS_SELECTOR, "td")
            for index, cell in enumerate(cells):
                if index == 0 :                
                    href = link.get_attribute('href')
                    matches = self.__parse_data_to_lat_and_lng(href)

                    for index, value in enumerate(matches):
                        if index == 0 :
                            result["address"]["lat"] = value
                        if index == 1 :
                            result["address"]["lng"] = value

                elif index == 2 :
                    result["title"] = cell.text                    
                elif index == 3 :
                    result["tpc"] = self.parse_data_to_number_format(cell.text)
                elif index == 4 :
                    result["ccs2"] = self.parse_data_to_number_format(cell.text)
                elif index == 5 :
                    result["floor"] = cell.text
                elif index == 6 :
                    result["business"] = "開放時間：" + cell.text
                elif index == 7 :
                    result["fee"] = self.parse_data_to_number_format(cell.text)
                elif index == 8 :
                    result["park_fee"] = "停車收費：" + cell.text
                elif index == 9 :
                    result["type"] = cell.text
                else :
                    result["remark"] += cell.text + "\n"

            self.scrape_results['stations'].append(result)
            self.logging(result)
        
        except NoSuchElementException as e:
            if "a[href]" in e.msg :
                pass
            else:
                self.logging(e.msg)

        finally:
            pass


    def __extract_table_data(self):
        try:        

            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.dict_css_selectors["table"]))
            )

            table = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["table"])
            if ( len(table) > 1 ):
                self.logging("extractTableData => too many tables in this page")
                return False

            table = table[0]
            tbody = table.find_element(By.CSS_SELECTOR, "tbody")
            if None is tbody:
                self.logging("extractTableData => tbody not found")
                return False

            rows = tbody.find_elements(By.CSS_SELECTOR, "tr")
            for row in rows:
                self.__extract_row_data(row)
                
        finally:
            pass



    def extract_source_data(self):
        try:
            self.__extract_table_data()
        finally:
            pass

