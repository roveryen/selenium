from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

from pprint import pprint
import re

from scrappy import scrappy

class scrappy8891(scrappy):

    def __init__(self):
        
        self.dictTargetUrl = {
            "8891"  : "https://c.8891.com.tw/Models/ev/search/x-x-x-x-x-x-x",
        }

        # url + "/spec#car-trim-nav"
        self.dictCssSelector = {
            "search-result" : 'div[class*="list-container-"]',
            "config-button" : 'div[class*="list-item-"] a[class*="item-msg-"]',
            'next-page' : '[class*="pagination-"] .ant-pagination-next > button',
            'item'      : '.cp-comp-col.comp-item-unit',
            'item-title' : '.comp-col-list-nm',
            'cell'     : '.comp-item dd[id^="cell-"]',
        }        


        # ○ / ●

        self.scrapeResults = {
            'source': '8891',
            'evs': []
        }


        super().__init__()

    def __appendMoreSpecs(self, result, dictSpecification):
        try:
            if dictSpecification["key"] == "brake" :
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

        finally:
            return result


    def __extractTableData(self, element):
        try:
            result = {
                "title"  : "Unknown title",
                "slug"   : "-",
                "specs"  : [],
                "remark" : ""
            }            
            

            title = element.find_element(By.CSS_SELECTOR, self.dictCssSelector["item-title"])
            brand = re.sub(r"https://[^/]+/([^/]+)/.+", r"\1", title.get_attribute('href'))
            result["title"] = brand + ' ' + title.text
            result["slug"] = self.parseTitleToSlug(result['title'])


            cells = element.find_elements(By.CSS_SELECTOR, self.dictCssSelector["cell"])
            for index, cell in enumerate(cells):

                label = re.sub(r"cell-\d+-\d+-(.+)", r"\1", cell.get_attribute('id'))
                label = re.sub(r"\(.+\)", "", label)                

                dictSpecification = {
                    "label" : label,
                    "key"  : "",
                    "value" : "N/A"
                }


                if label in self.dictLabelTextMap.keys():
                    key = self.dictLabelTextMap[label]
                    dictSpecification["key"] = key
                        
                dictSpecification["value"] = cell.text

                if len(dictSpecification["label"]) > 0 :
                    result["specs"].append(dictSpecification)

                result = self.__appendMoreSpecs(result, dictSpecification)

                
            #pprint(result)
            self.scrapeResults['evs'].append(result)

        finally:
            pass
    
    
    def __extractSourceData(self):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dictCssSelector["item"]))
            )


            items = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["item"])
            for item in items :
                self.__extractTableData(item)


        finally:
            pass

    def __extractDetailData(self):
        try:
            for slug in self.dictTargetUrl:
                targetUrl = self.dictTargetUrl[slug]                

                print("Scraping ... " + slug)
                self.driver.get(targetUrl)
                
                self.__extractSourceData()                
                
                
        finally:
            pass

    def __extractSearchResultData(self):
        try:        

            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.dictCssSelector["search-result"]))
            )

            searchResult = self.driver.find_elements(By.CSS_SELECTOR, self.dictCssSelector["search-result"])
            if ( len(searchResult) > 1 ):
                print("extractSearchResultData => too many result in this page")
                return False
            
            d = scrappy8891()
            d.scrapeResults = {
                "source": self.scrapeResults["source"],
                "evs"   : []
            }

            d.dictTargetUrl = {}
            d.dictCssSelector = self.dictCssSelector.copy()
            del d.dictCssSelector['search-result']
            del d.dictCssSelector['next-page']
            del d.dictCssSelector['config-button']

            buttons = searchResult[0].find_elements(By.CSS_SELECTOR, self.dictCssSelector['config-button'])
            for button in buttons :
                href = button.get_attribute('href')
                if ( None is href ):
                    continue
                                
                if re.search("Summary.html", href) :
                    slug = re.sub(r"^.+/(.+/.+)/Summary.html$", r"\1", href)
                    slug = slug.replace('/', '-')                    

                    if slug in d.dictTargetUrl.keys():
                        pass
                    else:
                        d.dictTargetUrl[slug] = href.replace("Summary.html", "Specification.html")

            
            d.__extractDetailData()
            self.scrapeResults["evs"] = self.scrapeResults["evs"] + d.scrapeResults["evs"]

            
            nextPage = self.driver.find_element(By.CSS_SELECTOR, self.dictCssSelector["next-page"])
            if None is nextPage :
                pass
            elif None is nextPage.get_attribute('disabled') :
                nextPage.click()
                return self.__extractSearchResultData()

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
        s = scrappy8891()
        s.startScrapeData()

    finally:
        pass


if __name__ == '__main__':
    main()
