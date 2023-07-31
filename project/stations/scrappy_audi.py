from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .scrappy import Scrappy

class ScrappyAudi(Scrappy):

    def __init__(self):
        
        self.dict_target_url = {
            "audi"  : "https://charging-map.audi-service.com.tw/",
        }

        self.dict_css_selectors = {
            "gmap"    : ".gm-style",
        }

        self.scrape_results = {
            'source': 'audi',
            'plug' : 'all',
            'stations': []
        }

        super().__init__()


    def __extract_station_data(self, element):
        try:
        
            """
            {"v":"AUDI","n":"Audi 內湖","m":"180kW, 每度電12元","a":"台北市內湖區新湖三路 288 號","lat":25.06681,"lng":121.58269,"p":"02-27939191","ps":0,"fp":2,"ac":0,"dc":2},
            {"v":"NOODOE","n":"KUN Hotel","m":"依現場公告為準","a":"台中市西屯區福星北三街33巷56號","lat":24.183642,"lng":120.645712,"p":null,"ps":4,"fp":0,"ac":4,"dc":0},
            """
            if "dc" in element and element["dc"] > 0:
                result = {
                    "title"  : "Unknown title",
                    "address": "Unknown address",
                    "ccs1" : 0,                     
                    "remark" : ""
                }

                result["title"] = element["v"] + "|" + element["n"] + "|" + str(element["dc"]) + "槍"            
                result["address"] = element["a"]
                result["ccs1"] = element["dc"]
                result["lat'"] = element["lat"]
                result["lng"] = element["lng"]
                result["remark"] = element["m"]

                self.scrape_results['stations'].append(result)
                self.logging(result)

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

            stations = self.driver.execute_script('return window.stations')
            for station in stations:
                self.__extract_station_data(station)
        

        finally:
            pass


    def extract_source_data(self):
        try:
            self.__extract_map_data()
        finally:
            pass

    def save_scrape_result_to_file(self):
        try:
            super().save_scrape_result_to_file()
        finally:
            pass
