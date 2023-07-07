from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

from pprint import pprint
import time

from scrappy import scrappy

"""
CCS1 快充地圖：https://bit.ly/TeslaHereCCS1
CCS2 快充地圖：https://bit.ly/TeslaHereCCS2
Tesla 超充地圖：https://bit.ly/TeslaHereSC（Tesla 車輛適用）
"""

class scrappyTeslaHere(scrappy):
    def __init__(self):
        
        self.dictTargetUrl = {
            "ccs1"  : "https://www.google.com/maps/d/viewer?mid=19OGC8E8JMvUgHOEJkpkBUXnqiYgfwEcZ",
            "ccs2"  : "https://www.google.com/maps/d/viewer?mid=1K8SBziyQK5fogutH3cvxfAnX4TrWvP0",
            #"tesla" : "https://www.google.com/maps/d/viewer?mid=1-kwJpQRM_xTh1fWb8JESCOz9hxyIphkc"
        }

        self.dictCssSelector = {
            "expandItem" : ".uVccjd.HzV7m-pbTTYe-KoToPc-ornU0b-hFsbo",
            "listItem"   : ".HzV7m-pbTTYe-ibnC6b-V67aGc",
            "labelItem"  : ".qqvbed-p83tee-lTBxed",
            "closeButton": ".HzV7m-tJHJj-LgbsSe-Bz112c",
            "detailLayer": ".dzWwaf-qqvbed",
        }

        self.dictClassName = {
            "parentItem" : "pbTTYe-ibnC6b-d6wfac",
        }

        self.scrapeResults = {
            'source': 'teslahere',
            'plug' : 'all',
            'stations': []
        }

        super().__init__()


    def __isListItemClickable(self, element):
        try:
            parentElement = element.find_element(By.XPATH, "./..")
            className = parentElement.get_attribute('class')
        
            if self.dictClassName["parentItem"] in className:
                #print("isListItemClickable => " + self.dictClassName["parentItem"] + " in " + className)            
                return True

            return False

        finally:
            pass

    def __showDetail(self, element):
        try:        

            if ( False == element.is_enabled() ):
                print("showDetail => element is not enabled")
                return False

            if ( False == element.is_displayed() ):
                print("showDetail => element is not displayed")
                return False

            isClickable = self.__isListItemClickable(element)

            if False == isClickable :
                print("showDetail => element is not clickable")
                return False

            element.click()

            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dictCssSelector["detailLayer"]))
            )
        

            time.sleep(1)

            result = {
                "title"  : "Unknown title",
                "address": "Unknown address",
                "remark" : ""
            }

            selector = self.dictCssSelector["detailLayer"] + " " + self.dictCssSelector["labelItem"]
            labelItems = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for index, labelItem in enumerate(labelItems):
                if index == 0 :
                    result["title"] = labelItem.text
                elif index == 1 :
                    result["address"] = labelItem.text
                else :
                    result["remark"] = labelItem.text

            self.scrapeResults['stations'].append(result)
            pprint(result)

            #self.driver.save_screenshot(screenShotFileName + ".png")

            selector = self.dictCssSelector["detailLayer"] + " " + self.dictCssSelector["closeButton"]
            button = self.driver.find_element(By.CSS_SELECTOR, selector)
            button.click()

            time.sleep(1)

        finally:
            pass



    def __showList(self):
        try:        

            #element.click()
                
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.dictCssSelector["listItem"]))
            )
        
            listItems = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["listItem"])
            for index, listItem in enumerate(listItems):
                self.__showDetail(listItem)

            #self.driver.save_screenshot('search.png')
        finally:
            pass        

    def __expandList(self):
        try:        

            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.dictCssSelector["expandItem"]))
            )

            expandItems = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["expandItem"])
        

            for element in expandItems:
                element.click()
                time.sleep(300/1000)

                #for index, expandItem in enumerate(expandItems):
                #    showList(self.driver, screenShotFileName + '-' + str(index), expandItem)
                self.__showList()

        finally:
            pass


    def extractSourceData(self):
        try:
            self.__expandList()
        finally:
            pass

    def saveScrapeResultToFile(self):
        try:
            super().saveScrapeResultToFile()
        finally:
            pass

def main():
    
    try:
        s = scrappyTeslaHere()
        s.startScrapeData()        

    finally:
        pass


if __name__ == '__main__':
    main()
