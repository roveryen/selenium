from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

from pprint import pprint
import re

from scrappy import scrappy

class scrappyUPower(scrappy):
    def __init__(self):
        
        self.dictTargetUrl = {
            "upower"  : "https://www.u-power.com.tw/",
        }

        self.dictCssSelector = {
            "table" : "table.table",
        }

        self.scrapeResults = {
            'source': 'u-power',
            'plug' : 'all',
            'stations': []
        }

        super().__init__()
    
    
    def parseDataToAddress(self, s):
        return re.sub(r"[（）]+", "", s)


    def __extractRowData(self, element):
        try:        

            if ( False == element.is_enabled() ):
                print("showDetail => element is not enabled")
                return False

            if ( False == element.is_displayed() ):
                print("showDetail => element is not displayed")
                return False

            result = {
                "title"  : "Unknown title",
                "address": "Unknown address",
                "ccs1" : {
                    "_500a" : "-", 
                    "_200a" : "-"
                },
                "ccs2" : {
                    "_500a" : "-",
                    "_200a" : "-"
                },
                "remark" : ""
            }

            cells = element.find_elements(By.CSS_SELECTOR, "td")
            for index, cell in enumerate(cells):
                if index == 0 :

                    tempAddress = cell.find_element(By.XPATH, "./small").text                    
                    result["title"] = cell.text.replace(tempAddress, "")                    
                    result["address"] = self.parseDataToAddress(tempAddress)                    
                elif index == 1 :
                    result["max"] = cell.text
                elif index == 2 :
                    result["ccs1"]["_500a"] = self.parseDataToNumberFormat(cell.text)
                elif index == 3 :
                    result["ccs1"]["_200a"] = self.parseDataToNumberFormat(cell.text)
                elif index == 4 :
                    result["ccs2"]["_500a"] = self.parseDataToNumberFormat(cell.text)
                elif index == 5 :
                    result["ccs2"]["_200a"] = self.parseDataToNumberFormat(cell.text)
                else :
                    result["remark"] = cell.text

            self.scrapeResults['stations'].append(result)
            pprint(result)
        
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
            if ( None == tbody ):
                print("extractTableData => tbody not found")
                return False

            rows = tbody.find_elements(By.CSS_SELECTOR, "tr")
            for index, row in enumerate(rows):
                if index > 1:
                    self.__extractRowData(row)
                

        finally:
            pass


    def extractSourceData(self):
        try:
            self.__extractTableData()
        finally:
            pass

    """
    def saveScrapeResultToFile(self):
        try:
            super().saveScrapeResultToFile()
        finally:
            pass
    """

def main():
    
    try:
        s = scrappyUPower()
        s.startScrapeData()        

    finally:
        pass


if __name__ == '__main__':
    main()
