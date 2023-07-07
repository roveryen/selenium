from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

from pprint import pprint
import urllib.parse
import re
import time

from scrappy import scrappy

class scrappyEVDatabase(scrappy):

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
        
        
        self.dictTargetUrl = {
            "ev-database"  : "https://ev-database.org/",            
        }

        # url + "/spec#car-trim-nav"
        self.dictCssSelector = {
            "search-result" : ".content.jplist .list",
            'href-button' : '.list-item h2 a.title',
            'next-page'   : '.pagination-wrapper .jplist-next',
            'photo' : '.img-main img.fotorama__img',
            'title': '.sub-header > h1',            
            'spec' : '#main-data .data-table table > tbody > tr',            
        }

        self.scrapeResults = {
            'source': 'ev-database',
            'evs': []
        }


        super().__init__()

    def __appendMoreSpecs(self, result, dictSpecification):
        try:
            if dictSpecification["key"] == "_power" :
                result["specs"].append({
                    "label" : "等效馬力",
                    "key"  : "horsepower",
                    "value" : self.parsePowerToHorsePower(dictSpecification['value'])
                })

                result["specs"].append({
                    "label" : "扭力",
                    "key"  : "torque",
                    "value" : self.parsePowerToTorque(dictSpecification['value'])
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
    
    
    def __extractSourceData(self, slug):
        returnValue = True
        try:
            element = WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dictCssSelector["title"]))
            )

            result = {
                "title"  : "Unknown title",
                "slug"   : slug,
                "specs"  : [],
                "photos" : [],
                "remark" : ""
            }

            title = self.driver.find_element(By.CSS_SELECTOR, self.dictCssSelector["title"])
            result["title"] = title.text

            photos = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["photo"])            
            for photo in photos:
                src = photo.get_attribute('src')
                src = src.replace("-thumb.jpg", ".jpg")                
                result["photos"].append(src)

            specs = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["spec"])
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

                        if cell.text in self.dictLabelTextMap.keys():
                            key = self.dictLabelTextMap[cell.text]
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

                #result = self.__appendMoreSpecs(result, dictSpecification)


            #pprint(result)
            if "blocked" in result["title"]:                
                print("Request blocked, will try again later...")
                returnValue = False
                return returnValue

            self.scrapeResults['evs'].append(result)

        finally:
            return returnValue

    def __extractDetailData(self):
        try:

            seconds = 5
            for slug in self.dictTargetUrl:
                targetUrl = self.dictTargetUrl[slug]
                
                for x in range(6):

                    print("Scraping ... " + slug)
                    self.driver.get(targetUrl)

                    if False is self.__extractSourceData(slug) :
                        print("Waiting for " + str(20*seconds) + " seconds")
                        time.sleep(20*seconds)
                    else:
                        break

                print("Waiting for " + str(seconds) + " seconds")
                time.sleep(seconds)

                #print( len(self.scrapeResults['evs']) % 5 )
                """
                if len(self.scrapeResults['evs']) % 5 == 0 :
                    print("Waiting another " + str(3*seconds) + " seconds")
                    time.sleep(3*seconds)
                """
                
        finally:
            pass

    def __extractSearchResultData(self):
        try:

            element = WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dictCssSelector["search-result"]))
            )

            searchResult = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["search-result"])
            if ( len(searchResult) > 1 ):
                print("extractSearchResultData => too many result in this page")
                return False
            
            d = scrappyEVDatabase()
            d.scrapeResults = {
                "source": self.scrapeResults["source"],
                "evs"   : []
            }

            d.dictTargetUrl = {}
            d.dictCssSelector = self.dictCssSelector.copy()
            del d.dictCssSelector['search-result']
            del d.dictCssSelector['href-button']
            del d.dictCssSelector['next-page']

            buttons = searchResult[0].find_elements(By.CSS_SELECTOR, self.dictCssSelector['href-button'])
            for index, button in enumerate(buttons):
                href = button.get_attribute('href')
                if ( None is href ):
                    continue

                if ( re.search("ev-database", href) and re.search("/car/", href) ):
                    slug = re.sub(r"^.+car\/\d+\/(.+)$", r"\1", href)
                    slug = urllib.parse.unquote(slug)
                    slug = slug.lower()
                    if slug in d.dictTargetUrl.keys():
                        pass
                    else:
                        for prefix in self.brands:
                            if prefix+'-' in slug:
                                d.dictTargetUrl[slug] = href
                                break

             
            #pprint(d.dictTargetUrl)
            d.__extractDetailData()
            self.scrapeResults["evs"] = self.scrapeResults["evs"] + d.scrapeResults["evs"]
            
            try:
                nextPage = self.driver.find_element(By.CSS_SELECTOR, self.dictCssSelector["next-page"])
                if None is nextPage :
                    pass
                else:
                    parent = nextPage.find_element(By.XPATH, "./..");
                    if "not-active" in parent.get_attribute('class') :                        
                        pass
                    else:
                        nextPage.click()
                        #print("scrape next page")
                        return self.__extractSearchResultData()

            except NoSuchElementException :
                pass
            finally:
                pass            

            #print ("=> Total " + str(len(self.scrapeResults['evs'])) + " results")


        finally:
            pass


    def extractSourceData(self):
        try:
            self.__extractSearchResultData()
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
        s = scrappyEVDatabase()
        s.startScrapeData()
        

    finally:
        pass


if __name__ == '__main__':
    main()
