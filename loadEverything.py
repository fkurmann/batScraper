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


class LoadEverything():
  def __init__(self, model):
    self.model = model
    print ("Creating object for: ", self.model)
    self.name_array = []
    self.year_array = []
    self.spec_array = []
    self.transmission_array = []
    self.price_array = []
    self.date_array = []
    self.sold_array = []
    self.mileage_array = []
    self.color_array = []
    self.interior_array = []

    self.array_length = 0

  def setup_method(self): 
    self.driver = driver
    self.vars = {}
  
  def teardown_method(self): 
    self.driver.quit()

  # Method open the page for a specific model, not loading everything (good for quicker testing)
  def open(self):
    self.driver.get("https://bringatrailer.com/porsche/987-boxster/")
  
  # Method to load all auctions of a specific model
  def loadEverything(self):
    self.driver.get("https://bringatrailer.com/porsche/987-boxster/")
    while (True):
      try:
        button = self.driver.find_element(By.CSS_SELECTOR, ".auctions-footer span:nth-child(1)")
        button.click()
        self.driver.implicitly_wait(10)
      except:
        break
      

  # Method to get initial information on all loaded cars
  def get_cars(self):
    names = self.driver.find_elements(by=By.XPATH, value='//*[contains(concat( " ", @class, " " ), concat( " ", "title", " " ))]//a')
    
    # Extract year, model, transmission, data from name
    for name in names: 
      self.name_array.append(name.text)
      
      year = re.search("\d\d\d\d", name.text)
      self.year_array.append(year.group())
      
      model = "Base"
      if (re.search(" S", name.text)):
        model = "S"
      if (re.search("Spyder", name.text) and re.search("RS", name.text)):
        model = "S"
      if (re.search("Spyder", name.text) and not re.search("RS", name.text)):
        model = "Spyder"
      self.spec_array.append(model)

      transmission = "Automatic"
      if (re.search("-Speed", name.text)):
        transmission = "Manual"
      self.transmission_array.append(transmission)
    
    # Extract price and sales data from subtitle
    finishes = self.driver.find_elements(by=By.XPATH, value='//*[contains(concat( " ", @class, " " ), concat( " ", "subtitle", " " ))]')
    
    self.array_length = len(names)
    counter = 0
    
    for finish in finishes:
      if (counter == self.array_length):
        break
      
      price = re.search("\$\d+[,]\d{3}", finish.text)
      self.price_array.append(price.group())

      date = re.search("1*\d/\d*\d/\d\d", finish.text)
      self.date_array.append(date.group())

      status = "Sold"
      if (re.search("Bid", finish.text)):
        status = "Reserve Not Met"
      self.sold_array.append(status)

      counter += 1

    

  # Method to get mileage, color, and interior data on each car, this must be done by opening the car's own auction page
  def get_page_info(self):
    links = self.driver.find_elements(by=By.XPATH, value='//*[contains(concat( " ", @class, " " ), concat( " ", "title", " " ))]//a')
    counter = 0
    
    # Open each car's page in a new tab
    for link in links:
      
      if (counter == 20 or counter == self.array_length):
        break
      
      # Open page in new tab
      link = link.get_attribute("href")
      self.driver.execute_script("window.open('');")
      self.driver.implicitly_wait(10)
      self.driver.switch_to.window(driver.window_handles[counter + 1])
      self.driver.get(link)
      self.driver.implicitly_wait(10)
      
      # Extract data
      data = self.driver.find_elements(by=By.XPATH, value='/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul')
      mileage = 'missing'
      mileage_formatted = 'N/A'
      color = 'missing'
      color_formatted = 'N/A'
      interior = 'missing'
      interior_formatted = 'N/A'
      for item in data:
          mileage = re.search(".*Miles.*", item.text)
          color = re.search(".*Paint.*", item.text)
          if (color == None):
            color = re.search (".* Metallic.*", item.text)
          interior = re.search(".*Upholstery.*", item.text)
          if (interior == None):
            interior = re.search (".* Leather.*", item.text)

      # Format data
      if (mileage != None):
        mileage_formatted = re.sub(" Miles", "", mileage.group())
      if (color != None):
        try:
          color_formatted = re.sub(" Paint", "", color.group())
        except:
          pass
      if (interior != None):
        try:
          interior_formatted = re.sub(" Upholstery", "", interior.group())
        except:
          try:
            interior_formatted = re.sub(" Leather", "", interior.group())
          except:
            pass

      counter +=1
      print (color_formatted, interior_formatted, mileage_formatted)

      # Return data
      self.mileage_array.append(mileage_formatted)
      self.color_array.append(color_formatted)
      self.interior_array.append(interior_formatted)

      # Prepare for next iteration
      self.driver.switch_to.window(driver.window_handles[0])
      self.driver.implicitly_wait(10)

    # Make sure arrays are all equal length
    while (len(self.mileage_array) < len(self.name_array)):
      self.mileage_array.append("BLANK")
      self.color_array.append("BLANK")
      self.interior_array.append("BLANK")
    

  # Method to compine all data lists into a single CSV file
  def info_to_csv(self):
    # Create a data frame containing all the information
    boxsters_dict = {'Year' : self.year_array, 'Spec' : self.spec_array, 'Transmission' : self.transmission_array, 'Price' : self.price_array, 'Date' : self.date_array, 'Status' : self.sold_array, 'Mileage' : self.mileage_array, 'Color': self.color_array, 'Interior' : self.interior_array}
    boxsters = pd.DataFrame(boxsters_dict)
    print(boxsters)
    boxsters.to_csv('boxsters.csv')

# DEBUG Method to get mileage, color, and interior data on specific car
  def get_page_info_DEBUG(self):
    link = 'https://bringatrailer.com/listing/2006-porsche-boxster-22/'
      
    # Open page in new tab
    self.driver.get(link)
    self.driver.implicitly_wait(10)
    
    # Extract data
    data = self.driver.find_elements(by=By.XPATH, value='/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul')
    mileage = 'missing'
    mileage_formatted = 'N/A'
    color = 'missing'
    color_formatted = 'N/A'
    interior = 'missing'
    interior_formatted = 'N/A'
    for item in data:
        mileage = re.search(".*Miles.*", item.text)
        color = re.search(".*Paint.*", item.text)
        interior = re.search(".*Upholstery.*", item.text)
        print(interior)
        if (interior == None):
          interior = re.search (".* Leather.*", item.text)
    
    # Format data
    if (mileage != 'missing'):
      mileage_formatted = re.sub(" Miles", "", mileage.group())
    if (color != 'missing'):
      color_formatted = re.sub(" Paint", "", color.group())
    if (interior != 'missing'):
      try:
        interior_formatted = re.sub(" Upholstery", "", interior.group())
      except:
        try:
          interior_formatted = re.sub(" Leather", "", interior.group())
        except:
          pass

    print (color_formatted, interior_formatted, mileage_formatted)



batBoxsters = LoadEverything("boxster") 
batBoxsters.setup_method()

#batBoxsters.loadEverything()
batBoxsters.open()
batBoxsters.get_cars()
print(batBoxsters.array_length)
batBoxsters.get_page_info()

# batBoxsters.get_page_info_DEBUG()

batBoxsters.teardown_method()

batBoxsters.info_to_csv()


