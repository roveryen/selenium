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
        'plug' : 'all',
        'stations': []
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
    
    def parseDataToTitle(self, s):
        return re.sub(r"^([^]+).*", r"\1", s)
    
    def parseDataToAddress(self, s):
        return re.sub(r".*\((.+)\).*", r"\1", s)        

    def getResultFileName(self):
        return "result-" + self.scrapeResults['plug'] + ".json"

    def saveScrapeResultToFile(self):
        try:
            resultFileName = self.getResultFileName()
            f = open(self.currentWorkingDirectory + "/" + resultFileName, "w")
            f.write( json.dumps(self.scrapeResults) )
            f.close()
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

            try:
                sftp.stat(config.sftp["remoteFilePath"])
            except FileNotFoundError:
                sftp.mkdir(config.sftp["remoteFilePath"])
            finally:
                pass

            # Upload file to root FTP folder
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

            for plug in self.dictTargetUrl:
                targerUrl = self.dictTargetUrl[plug]

                print("Scraping from ...\n=> " + targerUrl)
                self.driver.get(targerUrl)

                self.scrapeResults['plug'] = plug
                self.scrapeResults['stations'] = []
                self.extractSourceData()
                self.saveScrapeResultToFile()
                self.uploadResultFileToSFtp()
        
        finally:
            self.driver.close()
            self.driver.quit()

    
