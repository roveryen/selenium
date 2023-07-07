from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

from pprint import pprint
import time

from scrappy import scrappy

class scrappyICharging(scrappy):
    def __init__(self):
        
        self.dictTargetUrl = {
            "icharging"  : "https://www.icharging.com.tw/tw/map/p02.aspx",
        }

        self.dictCssSelector = {
            "gmap"    : ".gm-style",
            "marker"  : "[role=\"button\"]",
            "dialog"  : ".gm-style-iw",
            "title"   : ".main-title",
            "address" : ".sub-title",
            "item"    : ".map-info-box .item",
            "plug"    : ".bi-ev-station",
            "fee"     : ".bi-coin",
            "park"    : ".bi-car-front"    
        }

        self.scrapeResults = {
            'source': 'icharging',
            'plug' : 'all',
            'stations': []
        }

        super().__init__()


    def __extractDialogData(self, dialog):

        result = {
            "title"  : "Unknown title",
            "address": "Unknown address",
            "ccs1" : "-",
            "ccs2" : "-",
            "chademo" : "-",
            "fee"  : "",
            "remark" : ""
        }

        try:

            element = dialog.find_element(By.CSS_SELECTOR, self.dictCssSelector["title"])
            if None is element :
                print("extractDialogData => cannot found title element")
                return False

            result["title"] = element.text

            element = dialog.find_element(By.CSS_SELECTOR, self.dictCssSelector["address"])
            if None is element :
                print("extractDialogData => cannot found address element")
                return False
        
            result["address"] = element.text.replace("停車場地址 ", "")

            element = dialog.find_element(By.CSS_SELECTOR, self.dictCssSelector["plug"])
            if None is element :
                print("extractDialogData => cannot found plug element")
                return False

            parent = element.find_element(By.XPATH, "./..")
            if "CCS1" in parent.text:
                result["ccs1"] = "Y"
            if "CCS2" in parent.text:
                result["ccs2"] = "Y"
            if "CHAdeMo" in parent.text:
                result["chademo"] = "Y"

            element = dialog.find_element(By.CSS_SELECTOR, self.dictCssSelector["fee"])
            if None is element :
                print("extractDialogData => cannot found fee element")
            else:
                parent = element.find_element(By.XPATH, "./..")
                result["fee"] = parent.text + "\n"

            element = dialog.find_element(By.CSS_SELECTOR, self.dictCssSelector["park"])
            if None is element :
                print("extractDialogData => cannot found park element")
            else:
                parent = element.find_element(By.XPATH, "./..")
                result["remark"] = parent.text + "\n"


        except NoSuchElementException as e:
            if ".bi-car-front" in e.msg :
                pass
            else:
                print(e.msg)
        finally:
            self.scrapeResults['stations'].append(result)
            pprint(result)        

    def __extractMarkerData(self, element):
        try:        

            self.driver.execute_script("$(arguments[0]).click()", element)

            time.sleep(3)

            dialogs = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["dialog"])
            for index, dialog in enumerate(dialogs):
                if ( dialog.is_displayed() ):
                    self.__extractDialogData(dialog)
                    #driver.save_screenshot('icharging-test' + str(index) + '.png')

        finally:
            pass

    def __extractMapData(self):
        try:
            print("extractMapData => ready to detect gmap")

            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dictCssSelector["gmap"]))
            )

            gmap = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["gmap"])
            if ( len(gmap) > 1 ):
                print("extractTableData => too many maps in this page")
                return False

            gmap = gmap[0]

            #print("gmap is visible")

            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dictCssSelector["marker"]))
            )

            markers = gmap.find_elements(By.CSS_SELECTOR, self.dictCssSelector["marker"])
            #print("get markers of gmap")

            for marker in markers:
                self.__extractMarkerData(marker)            

        finally:
            pass


    def extractSourceData(self):
        try:
            self.__extractMapData()
        finally:
            pass

    def saveScrapeResultToFile(self):
        try:
            super().saveScrapeResultToFile()
        finally:
            pass

def main():
    
    try:
        s = scrappyICharging()
        s.startScrapeData()        

    finally:
        pass


if __name__ == '__main__':
    main()
