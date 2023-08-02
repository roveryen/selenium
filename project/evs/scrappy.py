from selenium import webdriver
from django.conf import settings
from pathlib import Path

import paramiko

import os
import json
import re
import logging

class Scrappy:

    dict_target_url = {}
    dict_specification_url = {}

    dict_css_selectors = {}

    name = None

    SFTP = {}

    logger = None

    scrape_results = {
        'source': 'scrappy',        
        'evs': []
    }

    dict_label_text_map = {
        '馬達出力' : '_power',
        'Total Power *' : 'power',
        'Total Power' : 'power',

        '馬達最大扭力' : 'torque',        
        'Total Torque *' : 'torque',
        'Total Torque' : 'torque',
        
        '電池容量' : 'battery_usable',
        'Useable Capacity*' : 'battery_usable',
        'Useable Capacity' : 'battery_usable',

        '驅動型式' : 'powertrain',
        'Drive'   : 'powertrain',

        '變速系統' : 'transmission',

        '前輪懸吊' : 'front_suspension',
        '後輪懸吊' : 'rear_suspension',

        '煞車型式' : 'brake',
        '輪胎尺碼' : 'wheels',
        '車門數'   : 'doors',

        '座位數'   : 'seats',
        '乘客數'   : 'seats',
        'Seats'   : 'seats',

        '車長'     : 'length',
        'Length'  : 'length',
        
        '車寬'     : 'width',
        'Width'   : 'width',
        
        '車高'     : 'height',
        'Height'  : 'height',
        
        '車重'     : 'curb_weight',
        'Weight Unladen (EU)' : 'curb_weight',
        
        '軸距'     : 'axis_wheelbase',
        'Wheelbase' : 'axis_wheelbase',
        
        '標準行李箱容量' : 'luggage',
        '行李容積' : 'luggage',
        'Cargo Volume' : 'luggage',

        '滿電可續航里程' :'range',
        'Range'        : 'range',

        '快速充電站'    : 'charging_80',
        '新車售價'  : 'base_price',
        
        '官方0-100km/h加速' : 'accelerate_0_100',
        'Acceleration 0 - 100 km/h' : 'accelerate_0_100',

        '能源局公布能耗值' : 'efficiency',
        'Rated Consumption' : 'efficiency',

        '前輪距'    : 'front_wheelbase',
        '後輪距'    : 'rear_wheelbase',
        '最小離地高度' : 'ground_clearance',
        '馬達最大馬力' : 'horsepower',
        '原廠公布純電里程' : 'range',
        '前輪尺碼'   : 'front_wheel',
        '後輪尺碼'   : 'rear_wheel',
        '極速'      : 'top_speed',
        'DC充電規格' : 'charge_port',
        'Top Speed' : 'top_speed',
        'Fastcharge Power (max)' : 'super_charge',
        'Charge Power' : 'standard_charge',

    }

    driver = None
    counter = 0

    JSON_RESULT_DIR = str(Path(__file__).resolve().parent) + "/results"
    

    def __init__(self):

        self.init_logger()

        self.SFTP = settings.SFTP
        self.SFTP["remote_file_path"] = "./www.ddcar.com.tw/storage/app/evs"

    
    def parse_data_to_number_format(self, s):
        return re.sub(r"[^\d]*([\d\.]+).*[\r\n]*", r"\1", s)
        
    def parse_title_to_slug(self, s):
        return re.sub(r"\s+", r"-", s.lower())

    def parse_power_to_horse_power(self, s):
        return re.sub(r"([0-9\.]+)hp.*", r"\1", s)

    def parse_power_to_torque(self, s):
        return re.sub(r"[^/]+/?(.*)kgm.*", r"\1", s)

    def init_logger(self):

        self.logger = logging.getLogger('evs')
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            fileHandler = logging.FileHandler('/project/logs/log-evs.txt')
            fileHandler.setFormatter( logging.Formatter('%(asctime)s - %(levelname)s : %(message)s') )
            self.logger.addHandler(fileHandler)


    def logging(self, d):
        self.logger.info(d)


    def init_webdriver(self):
        self.close_webdriver()

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox') # An error will occur without this line
        #options.add_argument('lang=zh_TW.UTF-8')
        #options.add_argument('--user-data-dir=/Users/roveryen/Library/Application Support/Google/Chrome/Default')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=options)

    def close_webdriver(self):
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()

        self.driver = None


    def get_result_file_name(self):
        return "result-" + self.scrape_results['source'] + ".json"

    def save_scrape_result_to_file(self):
        try:
            result_file_name = self.get_result_file_name()
            self.logging("Saving data to ... => " + self.JSON_RESULT_DIR + "/" + result_file_name)
            f = open(self.JSON_RESULT_DIR + "/" + result_file_name, "w")
            f.write( json.dumps(self.scrape_results) )
            f.close()
        finally:
            pass

    def rcsv_make_directory(self, sftp, path):
        try:
            self.logging("Checking and create remote directory => " + path)
            sftp.stat(path)
        except FileNotFoundError:
            dirpath = path.rsplit("/", 1)[0]
            self.rcsv_make_directory(sftp, dirpath)
            sftp.mkdir(path)

        finally:
            pass

    def upload_result_file_to_sftp(self):
    
        try:

            SFTP = self.SFTP

            result_file_name = self.get_result_file_name()

            host = SFTP["hostname"]
            port = SFTP["port"]

            transport = paramiko.Transport((host, port))
            transport.connect(username = SFTP["username"], password = SFTP["password"])

            sftp = paramiko.SFTPClient.from_transport(transport)

            self.rcsv_make_directory(sftp, SFTP["remote_file_path"])

            # Upload file to root FTP folder
            self.logging("Upload " + result_file_name + " to ...\n=> " + SFTP["remote_file_path"] + "/" + result_file_name)
            sftp.put(self.JSON_RESULT_DIR + "/" + result_file_name, SFTP["remote_file_path"] + "/" + result_file_name)
                    
            self.logging("File " + self.JSON_RESULT_DIR + "/" + result_file_name + " uploaded successfully.")

    
        except Exception as e:
            self.logging(f"Error: {str(e)}")
    
        finally:
            # Close the SFTP session and SSH connection            
            sftp.close()
            transport.close()
            

    
    def start_scrape_data(self):

        try:

            for source in self.dict_target_url:

                self.init_webdriver()

                target_url = self.dict_target_url[source]

                self.logging("Scraping from ... => " + target_url)

                self.driver.get(target_url)

                self.scrape_results['source'] = source
                self.scrape_results['evs'] = []
                self.extract_source_data()
                self.save_scrape_result_to_file()
                self.upload_result_file_to_sftp()

                self.close_webdriver()

        finally:
            self.close_webdriver()


