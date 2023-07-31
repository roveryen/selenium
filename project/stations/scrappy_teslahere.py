from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

from .scrappy import Scrappy

import time

"""
CCS1 快充地圖：https://bit.ly/TeslaHereCCS1
CCS2 快充地圖：https://bit.ly/TeslaHereCCS2
"""

class ScrappyTeslaHere(Scrappy):
    def __init__(self):
        
        self.dict_target_url = {
            "ccs1"  : "https://www.google.com/maps/d/viewer?mid=19OGC8E8JMvUgHOEJkpkBUXnqiYgfwEcZ",
            "ccs2"  : "https://www.google.com/maps/d/viewer?mid=1K8SBziyQK5fogutH3cvxfAnX4TrWvP0",
            #"tesla" : "https://www.google.com/maps/d/viewer?mid=1-kwJpQRM_xTh1fWb8JESCOz9hxyIphkc"
        }

        self.dict_css_selectors = {
            "expandItem" : ".uVccjd.HzV7m-pbTTYe-KoToPc-ornU0b-hFsbo",
            "listItem"   : ".HzV7m-pbTTYe-ibnC6b-V67aGc",
            "labelItem"  : ".qqvbed-p83tee-lTBxed",
            "closeButton": ".HzV7m-tJHJj-LgbsSe-Bz112c",
            "detailLayer": ".dzWwaf-qqvbed",
        }

        self.dict_class_names = {
            "parent_item" : "pbTTYe-ibnC6b-d6wfac",
        }

        self.scrape_results = {
            'source': 'teslahere',
            'plug' : 'all',
            'stations': []
        }

        super().__init__()


    def __is_list_item_clickable(self, element):
        try:
            parentElement = element.find_element(By.XPATH, "./..")
            className = parentElement.get_attribute('class')
        
            if self.dict_class_names["parent_item"] in className:
                #self.logging("isListItemClickable => " + self.dict_class_names["parent_item"] + " in " + className)
                return True

            return False

        finally:
            pass

    def __show_detail(self, element):
        try:        

            if ( False == element.is_enabled() ):
                self.logging("showDetail => element is not enabled")
                return False

            if ( False == element.is_displayed() ):
                self.logging("showDetail => element is not displayed")
                return False

            isClickable = self.__is_list_item_clickable(element)

            if False == isClickable :
                self.logging("showDetail => element is not clickable")
                return False

            element.click()

            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dict_css_selectors["detailLayer"]))
            )
        

            time.sleep(1)

            result = {
                "title"  : "Unknown title",
                "address": "Unknown address",
                "remark" : ""
            }

            selector = self.dict_css_selectors["detailLayer"] + " " + self.dict_css_selectors["labelItem"]
            labelItems = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for index, labelItem in enumerate(labelItems):
                if index == 0 :
                    result["title"] = labelItem.text
                elif index == 1 :
                    result["address"] = labelItem.text
                else :
                    result["remark"] = labelItem.text

            self.scrape_results['stations'].append(result)
            self.logging(result)

            #self.driver.save_screenshot(screenShotFileName + ".png")

            selector = self.dict_css_selectors["detailLayer"] + " " + self.dict_css_selectors["closeButton"]
            button = self.driver.find_element(By.CSS_SELECTOR, selector)
            button.click()

            time.sleep(1)

        finally:
            pass



    def __show_list(self):
        try:        

            #element.click()
                
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.dict_css_selectors["listItem"]))
            )
        
            listItems = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["listItem"])
            for index, listItem in enumerate(listItems):
                self.__show_detail(listItem)

            #self.driver.save_screenshot('search.png')
        finally:
            pass        

    def __expand_list(self):
        try:        

            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.dict_css_selectors["expandItem"]))
            )

            expandItems = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["expandItem"])
        

            for element in expandItems:
                element.click()
                time.sleep(300/1000)

                #for index, expandItem in enumerate(expandItems):
                #    showList(self.driver, screenShotFileName + '-' + str(index), expandItem)
                self.__show_list()

        finally:
            pass


    def extract_source_data(self):
        try:
            self.__expand_list()
        finally:
            pass

