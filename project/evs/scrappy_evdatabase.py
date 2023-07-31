from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

import urllib.parse
import re
import time

from .scrappy import Scrappy

class ScrappyEVDatabase(Scrappy):

    brands = [
        'audi',
        'bmw',
        'citroen',
        'fiat','ford',
        'honda','hyundai',
        'jaguar',
        'kia',
        'lexus',
        'mercedes','mini',
        'nissan',
        'opel',
        'peugeot','porsche',
        'rolls-royce',
        'skoda','smart','ssangyong','subaru',
        'tesla','toyota',
        'volkswagen',
        'volvo',
    ]

    def __init__(self):
        
        
        self.dict_target_url = {
            "ev-database"  : "https://ev-database.org/",            
        }

        # url + "/spec#car-trim-nav"
        self.dict_css_selectors = {
            "search-result" : ".content.jplist .list",
            'href-button' : '.list-item h2 a.title',
            'next-page'   : '.pagination-wrapper .jplist-next',
            'photo' : '.img-main img.fotorama__img',
            'title': '.sub-header > h1',            
            'spec' : '#main-data .data-table table > tbody > tr',            
        }

        self.scrape_results = {
            'source': 'ev-database',
            'evs': []
        }


        super().__init__()

    def __append_more_specs(self, result, dictSpecification):
        try:
            if dictSpecification["key"] == "_power" :
                result["specs"].append({
                    "label" : "等效馬力",
                    "key"  : "horsepower",
                    "value" : self.parse_power_to_horse_power(dictSpecification['value'])
                })

                result["specs"].append({
                    "label" : "扭力",
                    "key"  : "torque",
                    "value" : self.parse_power_to_torque(dictSpecification['value'])
                })
            elif dictSpecification["key"] == "brake" :
                result["specs"].append({
                    "label" : "前制動",
                    "key"  : "front_brake",
                    "value" : dictSpecification['value']
                })

                result["specs"].append({
                    "label" : "後制動",
                    "key"  : "rear_brake",
                    "value" : dictSpecification['value']
                })

            elif dictSpecification["key"] == "wheels" :
                tempArray = dictSpecification['value'].split(" ", 1)
                    
                if len(tempArray) > 0 : 
                    frontWheel = tempArray[0]
                else:
                    frontWheel = "N/A"

                if len(tempArray) > 1 :
                    rearWheel = tempArray[1]
                else:
                    rearWheel = frontWheel

                result["specs"].append({
                    "label" : "前輪尺寸",
                    "key"  : "front_wheel",
                    "value" : frontWheel
                })

                result["specs"].append({
                    "label" : "後輪尺寸",
                    "key"  : "rear_wheel",
                    "value" : rearWheel
                })
        finally:
            return result
    
    
    def __extract_source_data(self, slug):
        returnValue = True
        try:
            element = WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dict_css_selectors["title"]))
            )

            result = {
                "title"  : "Unknown title",
                "slug"   : slug,
                "specs"  : [],
                "photos" : [],
                "remark" : ""
            }

            title = self.driver.find_element(By.CSS_SELECTOR, self.dict_css_selectors["title"])
            result["title"] = title.text

            photos = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["photo"])
            for photo in photos:
                src = photo.get_attribute('src')
                src = src.replace("-thumb.jpg", ".jpg")                
                result["photos"].append(src)

            specs = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["spec"])
            for index, spec in enumerate(specs):

                dictSpecification = {
                    "label" : "Unknown",
                    "key"  : "",
                    "value" : ""
                }

                cells = spec.find_elements(By.CSS_SELECTOR, "td")
                for index, cell in enumerate(cells):
                    if index == 0:
                        dictSpecification["label"] = cell.text

                        if cell.text in self.dict_label_text_map.keys():
                            key = self.dict_label_text_map[cell.text]
                            dictSpecification["key"] = key
                        
                    elif index == 1:
                        if len(dictSpecification["value"]) > 0 : 
                            dictSpecification["value"] += ";" + cell.text
                        else:
                            dictSpecification["value"] = cell.text
                    else:
                        dictSpecification["value"] += ";" + cell.text

                if len(dictSpecification["key"]) > 0 :
                    if len(dictSpecification["value"]) <= 0 :
                        dictSpecification["value"] = "N/A"

                    result["specs"].append(dictSpecification)

                #result = self.__append_more_specs(result, dictSpecification)


            #self.logging(result)
            if "blocked" in result["title"]:                
                self.logging("Request blocked, will try again later...")
                returnValue = False
                return returnValue

            self.scrape_results['evs'].append(result)

        finally:
            return returnValue

    def __extract_detail_data(self):
        try:

            seconds = 5
            for slug in self.dict_target_url:
                targetUrl = self.dict_target_url[slug]
                
                for x in range(6):

                    self.logging("Scraping ... " + slug)
                    self.driver.get(targetUrl)

                    if False is self.__extract_source_data(slug) :
                        self.logging("Waiting for " + str(20*seconds) + " seconds")
                        time.sleep(20*seconds)
                    else:
                        break

                self.logging("Waiting for " + str(seconds) + " seconds")
                time.sleep(seconds)

                #self.logging( len(self.scrape_results['evs']) % 5 )
                """
                if len(self.scrape_results['evs']) % 5 == 0 :
                    self.logging("Waiting another " + str(3*seconds) + " seconds")
                    time.sleep(3*seconds)
                """
                
        finally:
            pass

    def __extract_search_result_data(self):
        try:

            element = WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dict_css_selectors["search-result"]))
            )

            searchResult = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["search-result"])
            if ( len(searchResult) > 1 ):
                self.logging("extractSearchResultData => too many result in this page")
                return False
            
            d = ScrappyEVDatabase()
            d.scrape_results = {
                "source": self.scrape_results["source"],
                "evs"   : []
            }

            d.dict_target_url = {}
            d.dict_css_selectors = self.dict_css_selectors.copy()
            del d.dict_css_selectors['search-result']
            del d.dict_css_selectors['href-button']
            del d.dict_css_selectors['next-page']

            buttons = searchResult[0].find_elements(By.CSS_SELECTOR, self.dict_css_selectors['href-button'])
            for index, button in enumerate(buttons):
                href = button.get_attribute('href')
                if ( None is href ):
                    continue

                if ( re.search("ev-database", href) and re.search("/car/", href) ):
                    slug = re.sub(r"^.+car\/\d+\/(.+)$", r"\1", href)
                    slug = urllib.parse.unquote(slug)
                    slug = slug.lower()
                    if slug in d.dict_target_url.keys():
                        pass
                    else:
                        for prefix in self.brands:
                            if prefix+'-' in slug:
                                d.dict_target_url[slug] = href
                                break

             
            #self.logging(d.dict_target_url)
            d.__extract_detail_data()
            self.scrape_results["evs"] = self.scrape_results["evs"] + d.scrape_results["evs"]
            
            try:
                nextPage = self.driver.find_element(By.CSS_SELECTOR, self.dict_css_selectors["next-page"])
                if None is nextPage :
                    pass
                else:
                    parent = nextPage.find_element(By.XPATH, "./..");
                    if "not-active" in parent.get_attribute('class') :                        
                        pass
                    else:
                        nextPage.click()
                        #self.logging("scrape next page")
                        return self.__extract_search_result_data()

            except NoSuchElementException :
                pass
            finally:
                pass            

            #self.logging ("=> Total " + str(len(self.scrape_results['evs'])) + " results")


        finally:
            pass


    def extract_source_data(self):
        try:
            self.__extract_search_result_data()
        finally:
            pass
