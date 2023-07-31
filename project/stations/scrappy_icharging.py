from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

import time

from .scrappy import Scrappy

class ScrappyICharging(Scrappy):
    def __init__(self):
        
        self.dict_target_url = {
            "icharging"  : "https://www.icharging.com.tw/tw/map/p02.aspx",
        }

        self.dict_css_selectors = {
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

        self.scrape_results = {
            'source': 'icharging',
            'plug' : 'all',
            'stations': []
        }

        super().__init__()


    def __extract_dialog_data(self, dialog):

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

            element = dialog.find_element(By.CSS_SELECTOR, self.dict_css_selectors["title"])
            if None is element :
                self.logging("extractDialogData => cannot found title element")
                return False

            result["title"] = element.text

            element = dialog.find_element(By.CSS_SELECTOR, self.dict_css_selectors["address"])
            if None is element :
                self.logging("extractDialogData => cannot found address element")
                return False
        
            result["address"] = element.text.replace("停車場地址 ", "")

            element = dialog.find_element(By.CSS_SELECTOR, self.dict_css_selectors["plug"])
            if None is element :
                self.logging("extractDialogData => cannot found plug element")
                return False

            parent = element.find_element(By.XPATH, "./..")
            if "CCS1" in parent.text:
                result["ccs1"] = "Y"
            if "CCS2" in parent.text:
                result["ccs2"] = "Y"
            if "CHAdeMo" in parent.text:
                result["chademo"] = "Y"

            element = dialog.find_element(By.CSS_SELECTOR, self.dict_css_selectors["fee"])
            if None is element :
                self.logging("extractDialogData => cannot found fee element")
            else:
                parent = element.find_element(By.XPATH, "./..")
                result["fee"] = parent.text + "\n"

            element = dialog.find_element(By.CSS_SELECTOR, self.dict_css_selectors["park"])
            if None is element :
                self.logging("extractDialogData => cannot found park element")
            else:
                parent = element.find_element(By.XPATH, "./..")
                result["remark"] = parent.text + "\n"


        except NoSuchElementException as e:
            if ".bi-car-front" in e.msg :
                pass
            else:
                self.logging(e.msg)
        finally:
            self.scrape_results['stations'].append(result)
            self.logging(result)

    def __extract_marker_data(self, element):
        try:        

            self.driver.execute_script("$(arguments[0]).click()", element)

            time.sleep(3)

            dialogs = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["dialog"])
            for index, dialog in enumerate(dialogs):
                if ( dialog.is_displayed() ):
                    self.__extract_dialog_data(dialog)
                    #driver.save_screenshot('icharging-test' + str(index) + '.png')

        finally:
            pass

    def __extract_map_data(self):
        try:
            self.logging("extractMapData => ready to detect gmap")

            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dict_css_selectors["gmap"]))
            )

            gmap = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["gmap"])
            if ( len(gmap) > 1 ):
                self.logging("extractTableData => too many maps in this page")
                return False

            gmap = gmap[0]

            #self.logging("gmap is visible")

            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dict_css_selectors["marker"]))
            )

            markers = gmap.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["marker"])
            #self.logging("get markers of gmap")

            for marker in markers:
                self.__extract_marker_data(marker)

        finally:
            pass


    def extract_source_data(self):
        try:
            self.__extract_map_data()
        finally:
            pass

