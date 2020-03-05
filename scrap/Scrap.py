from selenium import webdriver
from bs4 import BeautifulSoup as BS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from . import config as cfg

import time
import pandas as pd
import csv
import os
import pickle
import re
import time 
import json

class Scrap:

  # ! Init
  def __init__(self):

    # Init driver
    OPTIONS = webdriver.ChromeOptions();
    # OPTIONS.add_argument('headless'); # invisible browser
    OPTIONS.add_argument('window-size=1200x600');
    self.DRIVER = webdriver.Chrome(executable_path='C:/chromedriver', chrome_options=OPTIONS)
    self.DRIVER.get('https://www.linkedin.com')
    

  def writeJson(self, data, filename):
    with open(filename, 'w') as f:
      json.dump(data, f, indent=4)


  # ! Login
  def Login(self):
    # Direct to linkedin login page
    self.DRIVER.get('https://www.linkedin.com/login')

    # Enter form and submit
    self.DRIVER.find_element_by_id("username").send_keys(cfg.USERNAME)
    self.DRIVER.find_element_by_id("password").send_keys(cfg.PASSWORD)
    self.DRIVER.find_element_by_class_name("from__button--floating").click()

    
    # ? Validate linkedin is logged in
    validateURL = f"https://www.linkedin.com/search/results/people/?keywords=agoda&origin=SUGGESTION&page=1"
    self.DRIVER.get(validateURL)

    try: # Wait element class name `actor-name` located 
      element = WebDriverWait(self.DRIVER, 2).until(
        EC.presence_of_element_located((By.CLASS_NAME, "actor-name"))
      )

      # Store auth cookie
      all_cookies = self.DRIVER.get_cookies()
      new_cookies = all_cookies

      # Dump cookie to pkl file
      # Use to load when open new session
      if not os.path.exists("Cookies.pkl"):
        pickle.dump(new_cookies , open("./Cookies.pkl","wb"))

      return True


    except TimeoutException: # If can't locate `actor-name` element --> login
      print("Cannot Login")
      return False



  # ! Validate Login
  def Validate(self):

    # ? Assign cookie to driver, auth cookie
    if os.path.exists("Cookies.pkl"):
      for cookie in pickle.load(open("Cookies.pkl", "rb")):
        cookie_new = cookie
        if cookie.get('expiry') != None: del cookie['expiry']
        self.DRIVER.add_cookie(cookie)

    validateURL = f"https://www.linkedin.com/search/results/people/?keywords=agoda&origin=SUGGESTION&page=1"
    self.DRIVER.get(validateURL)

    # ? Validate Login Page
    try: # Wait element class name `actor-name` located 
      element = WebDriverWait(self.DRIVER, 2).until(
        EC.presence_of_element_located((By.CLASS_NAME, "actor-name"))
      )
      return True
    except TimeoutException: # If can't locate `actor-name` element --> login

      # Cookie expire --> delete
      if os.path.exists("Cookies.pkl"):
        os.remove("Cookies.pkl")

      # Login
      if self.Login(): 
        return True 
      else: 
        return False
      


  # ! Find User
  # Find user url by linkedin company search
  def Find(self, keyword="agoda", page_start=1 , page_range=2):

    # ? Validate driver is logged in
    if not self.Validate(): return self.DRIVER.quit()


    # ? Scrap each page in keyword
    for page in range(page_start, page_range + 1):

      # open driver by `SearchURL`
      SearchURL = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SUGGESTION&page={page}"
      self.DRIVER.get(SearchURL)

      # scrapt page
      bs_obj = BS(self.DRIVER.page_source, 'html.parser')

      # find `a` and get href
      user_list = bs_obj.select("div.search-result__info a.search-result__result-link")
      user_href = [actor['href'] for actor in user_list]

      # display and save
      print(f"scraping {keyword} page {page} finish.")
      
      saveURL = 'data/url/' + cfg.BASE_DATE + '.json'
      if os.path.exists(saveURL):
        with open(saveURL) as json_file:
          data = json.load(json_file) 
          temp = data['data']
          temp.append(user_href) 
          self.writeJson(data, saveURL)
      else:
        data = user_href
        self.writeJson({'data': [data]}, saveURL)


    

    

