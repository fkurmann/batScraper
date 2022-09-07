# Import Stuff

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
  
  # Load all auctions of a specific model
  def test_loadEverything(self):
    self.driver.get("https://bringatrailer.com/porsche/987-boxster/")
    while (True):
      try:
        button = self.driver.find_element(By.CSS_SELECTOR, ".auctions-footer span:nth-child(1)")
        button.click()
        self.driver.implicitly_wait(10)
      except:
        break
      

  # Get initial information on all loaded cars
  def get_cars(self):
    name_array = []
    year_array = []
    spec_array = []
    transmission_array = []
    price_array = []
    date_array = []
    sold_array = []
    mileage_array = []
    color_array = []
    names = self.driver.find_elements(by=By.XPATH, value='//*[contains(concat( " ", @class, " " ), concat( " ", "title", " " ))]//a')
    for name in names: 
      name_array.append(name.text)
      
      year = re.search("\d\d\d\d", name.text)
      year_array.append(year.group())
      
      model = "Base"
      if (re.search(" S", name.text)):
        model = "S"
      if (re.search("Spyder", name.text) and re.search("RS", name.text)):
        model = "S"
      if (re.search("Spyder", name.text) and not re.search("RS", name.text)):
        model = "Spyder"
      spec_array.append(model)

      transmission = "Automatic"
      if (re.search("-Speed", name.text)):
        transmission = "Manual"
      transmission_array.append(transmission)
    
    finishes = self.driver.find_elements(by=By.XPATH, value='//*[contains(concat( " ", @class, " " ), concat( " ", "subtitle", " " ))]')
    
    num_cars = len(names)
    counter = 0
    
    for finish in finishes:
      if (counter == num_cars):
        break
      
      price = re.search("\$\d+[,]\d{3}", finish.text)
      price_array.append(price.group())

      date = re.search("1*\d/\d*\d/\d\d", finish.text)
      date_array.append(date.group())

      status = "Sold"
      if (re.search("Bid", finish.text)):
        status = "Reserve Not Met"
      sold_array.append(status)

      counter += 1

    # Create a data frame containing all the information
    boxsters_dict = {'Year' : year_array, 'Spec' : spec_array, 'Transmission' : transmission_array, 'Price' : price_array, 'Date' : date_array, 'Status' : sold_array}
    boxsters = pd.DataFrame(boxsters_dict)
    print(boxsters)
    boxsters.to_csv('boxsters.csv')



batBoxsters = TestLoadEverything("boxster") 
batBoxsters.setup_method()

batBoxsters.test_loadEverything()
batBoxsters.get_cars()

batBoxsters.teardown_method()
