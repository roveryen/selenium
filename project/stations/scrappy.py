from selenium import webdriver
from django.conf import settings
from pathlib import Path

import paramiko

import os
import json
import re
import logging

class Scrappy():

    dict_target_url = {}

    dict_css_selectors = {}

    SFTP = {}

    logger = None

    scrape_results = {
        'source': 'scrappy',
        'plug' : 'all',
        'stations': []
    }    

    driver = None

    JSON_RESULT_DIR = str(Path(__file__).resolve().parent) + "/results"

    def __init__(self):

        self.init_logger()

        self.SFTP = settings.SFTP
        self.SFTP["remote_file_path"] = "./www.ddcar.com.tw/storage/app/stations"

        #self.JSON_RESULT_DIR = os.path.dirname(os.path.realpath(__file__))
        #self.logging(self.JSON_RESULT_DIR)

    
    def parse_data_to_number_format(self, s):
        return re.sub(r"[^\d]*([\d\.]+).*[\r\n]*", r"\1", s)
    
    def parse_data_to_title(self, s):
        return re.sub(r"^([^]+).*", r"\1", s)
    
    def parse_data_to_address(self, s):
        return re.sub(r".*\((.+)\).*", r"\1", s)

    def init_logger(self):
        self.logger = logging.getLogger('stations')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            fileHandler = logging.FileHandler('/project/logs/log-stations.txt')
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

    def getresult_filename(self):
        return "result-" + self.scrape_results['plug'] + ".json"

    def save_scrape_result_to_file(self):
        try:
            result_filename = self.getresult_filename()
            f = open(self.JSON_RESULT_DIR + "/" + result_filename, "w")
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

            result_filename = self.getresult_filename()

            host = SFTP["hostname"]
            port = SFTP["port"]

            transport = paramiko.Transport((host, port))
            transport.connect(username = SFTP["username"], password = SFTP["password"])

            sftp = paramiko.SFTPClient.from_transport(transport)

            self.rcsv_make_directory(sftp, SFTP["remote_file_path"])

            # Upload file to root FTP folder
            sftp.put(self.JSON_RESULT_DIR + "/" + result_filename, SFTP["remote_file_path"] + "/" + result_filename)
                    
            self.logging("File " + self.JSON_RESULT_DIR + "/" + result_filename + " uploaded successfully.")

    
        except Exception as e:
            self.logging(f"Error: {str(e)}")
    
        finally:
            # Close the SFTP session and SSH connection            
            sftp.close()
            transport.close()
            

    
    def start_scrape_data(self):

        try:

            for plug in self.dict_target_url:

                self.init_webdriver()

                target_url = self.dict_target_url[plug]

                self.logging("Scraping from ... => " + target_url)
                self.driver.get(target_url)

                self.scrape_results['plug'] = plug
                self.scrape_results['stations'] = []
                self.extract_source_data()
                self.save_scrape_result_to_file()
                self.upload_result_file_to_sftp()

                self.close_webdriver()

        finally:
            self.close_webdriver()

    
