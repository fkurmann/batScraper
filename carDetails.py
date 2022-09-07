# Import Stuff

from cgi import MiniFieldStorage
from xml.etree.ElementPath import xpath_tokenizer
import pytest
import time
import json
import pandas as pd
import os
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

# Resources
# https://www.selenium.dev/selenium/docs/api/rb/Selenium/WebDriver/Chrome/Options.html
# https://www.lambdatest.com/blog/selenium-wait-for-page-to-load/



#object of ChromeOptions
op = webdriver.ChromeOptions()
#add option
op.add_argument('--enable-extensions')
op.add_argument("--start-maximized")
op.add_argument("--enable-strict-powerful-feature-restrictions")
op.add_argument('--disable-notifications')


#pass option to webdriver object
driver = webdriver.Chrome(options=op)


class TestLoadEverything():
    def __init__(self, model):
        self.model = model
        print ("Creating object for: ", self.model)

    def setup_method(self): #, method
        self.driver = driver
        self.vars = {}

    def teardown_method(self): #, method
        self.driver.quit()

    def get_page_info(self):
        self.driver.get("https://bringatrailer.com/listing/2007-porsche-boxster-s-24/")
        data = self.driver.find_elements(by=By.XPATH, value='/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul')
        
        # mileage = self.driver.find_element(by=By.XPATH, value='/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[2]')
        # color = self.driver.find_element(by=By.XPATH, value='/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[5]')
        # interior = self.driver.find_element(by=By.XPATH, value='/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[6]')

        mileage = 'missing'
        color = 'missing'
        interior = 'missing'
        print (len(data))
        for item in data:
            
            mileage = re.search(".*Miles.*", item.text)
            color = re.search(".*Paint.*", item.text)
            interior = re.search(".*Upholstery.*", item.text)
      
        print (color.group(), interior.group(), mileage.group())
        mileage_formatted = re.sub(" Miles", "", mileage.group())
        color_formatted = re.sub(" Paint", "", color.group())
        interior_formatted = re.sub(" Uphostery", "", interior.group())
        print (color_formatted, interior_formatted, mileage_formatted)


batBoxsters = TestLoadEverything("boxster") 
batBoxsters.setup_method()

batBoxsters.get_page_info()

batBoxsters.teardown_method()