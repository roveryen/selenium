from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException

import urllib.parse
import re
import time

from .scrappy import Scrappy

class ScrappyYahoo(Scrappy):

    def __init__(self):

        super().__init__()

        self.dict_target_url = {
            "yahoo-100-600"  : "https://autos.yahoo.com.tw/car-search?price_range=60-600&power_type=%E9%9B%BB%E5%8B%95&p=1",            
            "yahoo-600"  : "https://autos.yahoo.com.tw/car-search?price_range=600&power_type=%E9%9B%BB%E5%8B%95&p=1",            
        }

        # url + "/spec#car-trim-nav"
        self.dict_css_selectors = {
            "search-result" : ".search-result",
            'href-button' : '.gabtn',
            'next-page'   : '.paginations .gabtn[title="下一頁"]',
            'section' : '.trim-spec-detail .spec-wrapper .gabtn[data-ga], .trim-spec-detail .spec-wrapper.spec-right > label',
            'gallery-photos' : '.slick-slide .gabtn',
            'title': '.trim-main > .title',
            'price': '.trim-main > .price > span > font',
            'spec' : '.spec-wrapper ul>li',
        }

        self.scrape_results = {
            'source': 'yahoo',
            'evs': []
        }


    def __append_more_specs(self, result, dict_specifications):
        try:
            if dict_specifications["key"] == "_power" :
                result["specs"].append({
                    "label" : "等效馬力",
                    "key"  : "horsepower",
                    "value" : self.parse_power_to_horse_power(dict_specifications['value'])
                })

                result["specs"].append({
                    "label" : "扭力",
                    "key"  : "torque",
                    "value" : self.parse_power_to_torque(dict_specifications['value'])
                })
            elif dict_specifications["key"] == "brake" :
                result["specs"].append({
                    "label" : "前制動",
                    "key"  : "front_brake",
                    "value" : dict_specifications['value']
                })

                result["specs"].append({
                    "label" : "後制動",
                    "key"  : "rear_brake",
                    "value" : dict_specifications['value']
                })

            elif dict_specifications["key"] == "wheels" :
                tempArray = dict_specifications['value'].split(" ", 1)
                    
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
        try:
            safe_counter=0
            while True:
                try:
                    safe_counter+=1

                    if safe_counter>10:
                        self.logging("try too many times, give it up")
                        break

                    element = WebDriverWait(self.driver, 15).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, self.dict_css_selectors["title"]))
                    )

                    result = {
                        "title"  : "Unknown title",
                        "slug"   : slug,
                        "specs"  : [],
                        "remark" : ""
                    }

                    title = self.driver.find_element(By.CSS_SELECTOR, self.dict_css_selectors["title"])
                    result["title"] = title.text

                    price = self.driver.find_element(By.CSS_SELECTOR, self.dict_css_selectors["price"])
                    result["specs"].append({
                        "label" : "售價",
                        "key"  : "base_price",
                        "value" : price.text
                    })

                    sections = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["section"])
                    for section in sections:
                        nextSibling = section.find_element(By.XPATH, "following-sibling::*[1]")
                        if nextSibling.is_displayed():
                            pass
                        else:
                            section.click()
                            time.sleep(1)

                    specs = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["spec"])
                    for index, spec in enumerate(specs):
                        dict_specifications = {
                            "label" : "Unknown",
                            "key"  : "",
                            "value" : "N/A"
                        }

                        spans = spec.find_elements(By.CSS_SELECTOR, "span")
                        for index, span in enumerate(spans):
                            if index == 0:
                                dict_specifications["label"] = span.text

                                if span.text in self.dict_label_text_map.keys():
                                    key = self.dict_label_text_map[span.text]
                                    dict_specifications["key"] = key
                        
                            elif index == 1:
                                dict_specifications["value"] = span.text
                            else:
                                dict_specifications["value"] += "/" + span.text

                        if len(dict_specifications["label"]) > 0 :
                            result["specs"].append(dict_specifications)

                        result = self.__append_more_specs(result, dict_specifications)

                    #self.logging(result)
                    self.scrape_results['evs'].append(result)
                    break

                except TimeoutException as e:
                    self.logging("WebDriverWait try " + str(safe_counter) + " times")

        finally:
            time.sleep(5)

    def __extract_detail_data(self):
        try:
            for slug in self.dict_specification_url:
                target_url = self.dict_specification_url[slug]
                target_url += "/spec#car-trim-nav"

                self.logging("Scraping ... " + slug)
                self.logging("=> " + target_url)

                self.driver.get(target_url)
                
                self.__extract_source_data(slug)
                
                
        finally:
            pass

    def __extract_search_result_data(self):
        try:
            self.dict_specification_url = {}
            safe_counter=0

            while True :
                element = WebDriverWait(self.driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, self.dict_css_selectors["search-result"]))
                )

                searchResult = self.driver.find_elements(By.CSS_SELECTOR, self.dict_css_selectors["search-result"])
                if len(searchResult) > 1:
                    self.logging("extractSearchResultData => too many result in this page")
                    return False
            
                buttons = searchResult[0].find_elements(By.CSS_SELECTOR, self.dict_css_selectors['href-button'])
                for index, button in enumerate(buttons):
                    href = button.get_attribute('href')
                    if None is href:
                        continue

                    if re.search("autos.yahoo.com.tw", href) and re.search("/trim/", href) :
                        slug = re.sub(r"^.+trim\/(.+)$", r"\1", href)
                        slug = urllib.parse.unquote(slug)

                        if slug in self.dict_specification_url.keys():
                            pass
                        else:
                            self.logging("add " + slug)
                            self.dict_specification_url[slug] = href

                try:
                    nextPage = self.driver.find_element(By.CSS_SELECTOR, self.dict_css_selectors["next-page"])
                    if None is nextPage or safe_counter > 999 :
                        self.logging("No more pages")
                        break
                    else:
                        href = nextPage.get_attribute('href')
                        if len(href) > 0 :
                            self.driver.get(href)
                            self.logging("To next page, sleep 15 sec.")
                            time.sleep(15)

                        else:
                            self.logging("No more page href")
                            break

                except NoSuchElementException :
                    break

            self.__extract_detail_data()

        finally:
            pass

    def extract_source_data(self):
        try:
            self.__extract_search_result_data()
        finally:
            pass
