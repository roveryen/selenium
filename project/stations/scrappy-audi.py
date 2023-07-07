
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pprint import pprint


from scrappy import scrappy

class scrappyAudi(scrappy):

    def __init__(self):
        
        self.dictTargetUrl = {
            "audi"  : "https://charging-map.audi-service.com.tw/",
        }

        self.dictCssSelector = {
            "gmap"    : ".gm-style",
        }

        self.scrapeResults = {
            'source': 'audi',
            'plug' : 'all',
            'stations': []
        }

        super().__init__()


    def __extractStationData(self, element):
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

                self.scrapeResults['stations'].append(result)
                pprint(result)

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
            stations = self.driver.execute_script('return window.stations')
            for station in stations:
                self.__extractStationData(station)
        

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
        s = scrappyAudi()
        s.startScrapeData()

    finally:
        pass


if __name__ == '__main__':
    main()
