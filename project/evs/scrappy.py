from selenium import webdriver

import paramiko

import config

from pprint import pprint

import os
import json
import re

class scrappy():

    dictTargetUrl = {}

    dictCssSelector = {}

    scrapeResults = {
        'source': 'scrappy',        
        'evs': []
    }

    dictLabelTextMap = {
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

    currentWorkingDirectory = ""
    

    def __init__(self):

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox') # An error will occur without this line
        #options.add_argument('lang=zh_TW.UTF-8')
        #options.add_argument('--user-data-dir=/Users/roveryen/Library/Application Support/Google/Chrome/Default')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=options)

        self.currentWorkingDirectory = os.path.dirname(os.path.realpath(__file__))
        #print(self.currentWorkingDirectory)

    
    def parseDataToNumberFormat(self, s):
        return re.sub(r"[^\d]*([\d\.]+).*[\r\n]*", r"\1", s)
        
    def parseTitleToSlug(self, s):
        return re.sub(r"\s+", r"-", s.lower())

    def parsePowerToHorsePower(self, s):
        return re.sub(r"([0-9\.]+)hp.*", r"\1", s)

    def parsePowerToTorque(self, s):        
        return re.sub(r"[^/]+/?(.*)kgm.*", r"\1", s)

    def getResultFileName(self):
        return "result-" + self.scrapeResults['source'] + ".json"

    def saveScrapeResultToFile(self):
        try:
            resultFileName = self.getResultFileName()
            print("Saving data to ... => " + self.currentWorkingDirectory + "/" + resultFileName)
            f = open(self.currentWorkingDirectory + "/" + resultFileName, "w")
            f.write( json.dumps(self.scrapeResults) )
            f.close()
        finally:
            pass

    def rcsvMakeDirectory(self, sftp, path):
        try:
            print("Checking and create remote directory => " + path)
            sftp.stat(path)
        except FileNotFoundError:
            dirpath = path.rsplit("/", 1)[0]
            self.rcsvMakeDirectory(sftp, dirpath)
            sftp.mkdir(path)

        finally:
            pass

    def uploadResultFileToSFtp(self):        
    
        try:

            resultFileName = self.getResultFileName()            

            host = config.sftp["hostname"]
            port = config.sftp["port"]

            transport = paramiko.Transport((host, port))
            transport.connect(username = config.sftp["username"], password = config.sftp["password"])

            sftp = paramiko.SFTPClient.from_transport(transport)

            self.rcsvMakeDirectory(sftp, config.sftp["remoteFilePath"])

            # Upload file to root FTP folder
            print("Upload " + resultFileName + " to ...\n=> " + config.sftp["remoteFilePath"] + "/" + resultFileName)
            sftp.put(self.currentWorkingDirectory + "/" + resultFileName, config.sftp["remoteFilePath"] + "/" + resultFileName)
                    
            print("File " + self.currentWorkingDirectory + "/" + resultFileName + " uploaded successfully.")

    
        except Exception as e:
            print(f"Error: {str(e)}")
    
        finally:
            # Close the SFTP session and SSH connection            
            sftp.close()
            transport.close()
            

    
    def startScrapeData(self):

        try:            

            for source in self.dictTargetUrl:
                targerUrl = self.dictTargetUrl[source]

                print("Scraping from ...\n=> " + targerUrl)
                self.driver.get(targerUrl)

                self.scrapeResults['source'] = source
                self.scrapeResults['evs'] = []
                self.extractSourceData()
                self.saveScrapeResultToFile()
                self.uploadResultFileToSFtp()
        
        finally:
            self.driver.close()
            self.driver.quit()

    
