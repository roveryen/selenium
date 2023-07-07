from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

from pprint import pprint
import urllib.parse
import re

from scrappy import scrappy

class scrappyYahoo(scrappy):

    def __init__(self):
        
        self.dictTargetUrl = {
            "yahoo-100-600"  : "https://autos.yahoo.com.tw/car-search?price_range=60-600&power_type=%E9%9B%BB%E5%8B%95&p=1",            
            "yahoo-600"  : "https://autos.yahoo.com.tw/car-search?price_range=600&power_type=%E9%9B%BB%E5%8B%95&p=1",            
        }

        # url + "/spec#car-trim-nav"
        self.dictCssSelector = {
            "search-result" : ".search-result",
            'href-button' : '.gabtn',
            'next-page'   : '.paginations .gabtn[title="下一頁"]',
            'section' : '.trim-spec-detail .spec-wrapper .gabtn[data-ga], .trim-spec-detail .spec-wrapper.spec-right > label',
            'gallery-photos' : '.slick-slide .gabtn',
            'title': '.trim-main > .title',
            'spec' : '.spec-wrapper ul>li',
        }

        self.scrapeResults = {
            'source': 'yahoo',
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
        try:
            element = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dictCssSelector["title"]))
            )

            result = {
                "title"  : "Unknown title",
                "slug"   : slug,
                "specs"  : [],
                "remark" : ""
            }

            title = self.driver.find_element(By.CSS_SELECTOR, self.dictCssSelector["title"])
            result["title"] = title.text

            sections = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["section"])
            for section in sections:
                nextSibling = section.find_element(By.XPATH, "following-sibling::*[1]")
                if nextSibling.is_displayed():
                    pass
                else:
                    section.click()

            specs = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["spec"])
            for index, spec in enumerate(specs):
                dictSpecification = {
                    "label" : "Unknown",
                    "key"  : "",
                    "value" : "N/A"
                }

                spans = spec.find_elements(By.CSS_SELECTOR, "span")
                for index, span in enumerate(spans):
                    if index == 0:
                        dictSpecification["label"] = span.text

                        if span.text in self.dictLabelTextMap.keys():
                            key = self.dictLabelTextMap[span.text]
                            dictSpecification["key"] = key
                        
                    elif index == 1:
                        dictSpecification["value"] = span.text
                    else:
                        dictSpecification["value"] += "/" + span.text

                if len(dictSpecification["label"]) > 0 :
                    result["specs"].append(dictSpecification)

                result = self.__appendMoreSpecs(result, dictSpecification)


            #pprint(result)
            self.scrapeResults['evs'].append(result)


        finally:
            pass

    def __extractDetailData(self):
        try:
            for slug in self.dictTargetUrl:
                targetUrl = self.dictTargetUrl[slug]
                targetUrl += "/spec#car-trim-nav"

                print("Scraping ... " + slug)
                self.driver.get(targetUrl)
                
                self.__extractSourceData(slug)
                
                
        finally:
            pass

    def __extractSearchResultData(self):
        try:

            element = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dictCssSelector["search-result"]))
            )

            searchResult = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["search-result"])
            if ( len(searchResult) > 1 ):
                print("extractSearchResultData => too many result in this page")
                return False
            
            d = scrappyYahoo()
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

                if ( re.search("autos.yahoo.com.tw", href) and re.search("/trim/", href) ):
                    slug = re.sub(r"^.+trim\/(.+)$", r"\1", href)
                    slug = urllib.parse.unquote(slug)

                    if slug in d.dictTargetUrl.keys():
                        pass
                    else:
                        d.dictTargetUrl[slug] = href

             
            #pprint(d.dictTargetUrl)
            d.__extractDetailData()
            self.scrapeResults["evs"] = self.scrapeResults["evs"] + d.scrapeResults["evs"]

            try:
                nextPage = self.driver.find_element(By.CSS_SELECTOR, self.dictCssSelector["next-page"])
                if None is nextPage :
                    pass
                else:
                    href = nextPage.get_attribute('href')
                    if len(href) > 0 :                        
                        self.driver.get(href)
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
        s = scrappyYahoo()
        s.startScrapeData()

        #print( s.parsePowerToTorque("517hp/86.7kgm(Boost模式598hp)") )

    finally:
        pass


if __name__ == '__main__':
    main()
