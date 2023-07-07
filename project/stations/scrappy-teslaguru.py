
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

from pprint import pprint
#import pprint
import re

from scrappy import scrappy

class scrappyTeslaGuru(scrappy):

    def __init__(self):
        
        self.dictTargetUrl = {
            "tesla"  : "https://teslagu.ru/supercharger/",
        }

        self.dictCssSelector = {
            "table" : ".page-content .wp-block-table",
        }

        self.scrapeResults = {
            'source': 'teslaguru',
            'plug' : 'all',
            'stations': []
        }

        super().__init__()


    def __parseDataToLatLng(self, href):        
        return re.findall(r'\d+\.\d+', href)

    def __extractRowData(self, element):
        try:

            if ( False == element.is_enabled() ):
                print("showDetail => element is not enabled")
                return False

            if ( False == element.is_displayed() ):
                print("showDetail => element is not displayed")
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
                    matches = self.__parseDataToLatLng(href)

                    for index, value in enumerate(matches):
                        if index == 0 :
                            result["address"]["lat"] = value
                        if index == 1 :
                            result["address"]["lng"] = value

                elif index == 2 :
                    result["title"] = cell.text                    
                elif index == 3 :
                    result["tpc"] = self.parseDataToNumberFormat(cell.text)
                elif index == 4 :
                    result["ccs2"] = self.parseDataToNumberFormat(cell.text)
                elif index == 5 :
                    result["floor"] = cell.text
                elif index == 6 :
                    result["business"] = "開放時間：" + cell.text
                elif index == 7 :
                    result["fee"] = self.parseDataToNumberFormat(cell.text)
                elif index == 8 :
                    result["park_fee"] = "停車收費：" + cell.text
                elif index == 9 :
                    result["type"] = cell.text
                else :
                    result["remark"] += cell.text + "\n"

            self.scrapeResults['stations'].append(result)
            pprint(result)
        
        except NoSuchElementException as e:
            if "a[href]" in e.msg :
                pass
            else:
                print(e.msg)

        finally:
            pass


    def __extractTableData(self):
        try:        

            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.dictCssSelector["table"]))
            )

            table = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["table"])
            if ( len(table) > 1 ):
                print("extractTableData => too many tables in this page")
                return False

            table = table[0]
            tbody = table.find_element(By.CSS_SELECTOR, "tbody")
            if None is tbody:
                print("extractTableData => tbody not found")
                return False

            rows = tbody.find_elements(By.CSS_SELECTOR, "tr")
            for row in rows:
                self.__extractRowData(row)
                
        finally:
            pass



    def extractSourceData(self):
        try:
            self.__extractTableData()
        finally:
            pass

    def saveScrapeResultToFile(self):
        try:
            super().saveScrapeResultToFile()
        finally:
            pass

def main():
    
    try:
        s = scrappyTeslaGuru()
        s.startScrapeData()

    finally:
        pass


if __name__ == '__main__':
    main()
