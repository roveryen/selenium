from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException, TimeoutException

import time
import re

from .scrappy import Scrappy

class Scrappy8891(Scrappy):

    def __init__(self):
        
        self.dict_target_url = {
            "8891"  : "https://c.8891.com.tw/Models/ev/search/x-x-x-x-x-x-x",
        }

        # url + "/spec#car-trim-nav"
        self.dict_css_selectors = {
            "search-result" : 'div[class*="list-container-"]',
            "config-button" : 'div[class*="list-item-"] a[class*="item-msg-"]',
            'next-page' : '[class*="pagination-"] .ant-pagination-next > button',
            'item'      : '.cp-comp-col.comp-item-unit',
            'item-title' : '[href$="Summary.html"]',
            'cell'     : '.comp-item dd[id^="cell-"]',
        }        


        # ○ / ●

        self.scrape_results = {
            'source': '8891',
            'evs': []
        }


        super().__init__()

    def __append_more_specs(self, result, dictSpecification):
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


    def __extract_table_data(self, element):
        try:
            result = {
                "title"  : "Unknown title",
                "slug"   : "-",
                "specs"  : [],
                "remark" : ""
            }            
            

            title = element.find_element(By.CSS_SELECTOR, self.dict_css_selectors["item-title"])
            brand = re.sub(r"https://[^/]+/([^/]+)/.+", r"\1", title.get_attribute('href'))
            result["title"] = brand + ' ' + title.text
            result["slug"] = self.parse_title_to_slug(result['title'])


            cells = element.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["cell"])
            for index, cell in enumerate(cells):

                label = re.sub(r"cell-\d+-\d+-(.+)", r"\1", cell.get_attribute('id'))
                label = re.sub(r"\(.+\)", "", label)                

                dictSpecification = {
                    "label" : label,
                    "key"  : "",
                    "value" : "N/A"
                }


                if label in self.dict_label_text_map.keys():
                    key = self.dict_label_text_map[label]
                    dictSpecification["key"] = key
                        
                dictSpecification["value"] = cell.text

                if len(dictSpecification["label"]) > 0 :
                    result["specs"].append(dictSpecification)

                result = self.__append_more_specs(result, dictSpecification)

            #self.logging(result)

        except NoSuchElementException as e:
            pass
        finally:
            self.scrape_results['evs'].append(result)

    
    def __extract_source_data(self):
        try:
            safe_counter = 0
            while True:

                try:
                    safe_counter+=1

                    if safe_counter>10:
                        self.logging("try too many times, give it up")
                        break

                    element = WebDriverWait(self.driver, 15).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, self.dict_css_selectors["item"]))
                    )

                    items = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["item"])
                    for item in items :
                        self.__extract_table_data(item)

                    break

                except TimeoutException as e:
                    self.logging("WebDriverWait try " + str(safe_counter) + " times")

        finally:
            time.sleep(5)

    def __extract_detail_data(self):
        try:

            for slug in self.dict_specification_url:
                target_url = self.dict_specification_url[slug]

                self.logging("Scraping ... " + slug)
                self.logging("=> " + target_url)

                self.driver.get(target_url)
                
                self.__extract_source_data()

        finally:
            pass

    def __extract_search_result_data(self):
        try:
            self.dict_specification_url = {}
            safe_counter = 0;

            while True :
                element = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, self.dict_css_selectors["search-result"]))
                )

                searchResult = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["search-result"])
                if len(searchResult) > 1:
                    self.logging("extractSearchResultData => too many result in this page")
                    return False

                buttons = searchResult[0].find_elements(By.CSS_SELECTOR, self.dict_css_selectors['config-button'])
                for button in buttons:
                    href = button.get_attribute('href')
                    if None is href:
                        self.logging(button)
                        continue

                    if re.search("Summary.html", href) :
                        slug = re.sub(r"^.+/(.+/.+)/Summary.html$", r"\1", href)
                        slug = slug.replace('/', '-')

                        if slug in self.dict_specification_url.keys():
                            pass
                        else:
                            self.logging("add " + slug)
                            self.dict_specification_url[slug] = href.replace("Summary.html", "Specification.html")

                safe_counter+=1
                nextPage = self.driver.find_element(By.CSS_SELECTOR, self.dict_css_selectors["next-page"])
                if None is nextPage or safe_counter > 99:
                    self.logging("No more pages")
                    break
                elif None is nextPage.get_attribute('disabled') :
                    nextPage.click()
                    self.logging("To next page, sleep 15 sec.")
                    time.sleep(15)
                    #return self.__extract_search_result_data()

            self.__extract_detail_data()
            #self.scrape_results["evs"] = self.scrape_results["evs"] + d.scrape_results["evs"]

        finally:
            pass


    def extract_source_data(self):
        try:
            self.__extract_search_result_data()
        finally:
            pass
