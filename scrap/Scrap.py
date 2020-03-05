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
      


  # ! Scrap User URL
  # Find user url by linkedin keyword search
  def ScrapUserURL(self, keyword="agoda", page_start=1 , page_range=2):

    # ? Validate driver is logged in
    if not self.Validate(): return self.DRIVER.quit()

    saveURL = 'data/url/' + cfg.BASE_DATE + '.json'


    # ? Scrap each page in keyword
    for page in range(page_start, page_range + 1):

      # open driver by `SearchURL`
      SearchURL = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SUGGESTION&page={page}"
      self.DRIVER.get(SearchURL)

      # scrapt page
      bs_obj = BS(self.DRIVER.page_source, 'html.parser')

      # find `a` and get href
      user_list = bs_obj.select("div.search-result__info a.search-result__result-link")
      user_href = [user['href'] for user in user_list]
      user_href = list(filter(lambda user: user != "#", user_href))

      # display and save
      print(f"scraping {keyword} page {page} finish.")
      
      
      if os.path.exists(saveURL):
        with open(saveURL) as json_file:
          data = json.load(json_file) 
          temp = data
          temp.extend(user_href)
          self.writeJson(data, saveURL)
      else:
        data = user_href
        self.writeJson(data, saveURL)

    # close browser
    self.DRIVER.quit()

    # return save file
    return saveURL

  # ! Scrap User Data
  # by useing user url in url directory to scrap user profile
  def ScrapUserData(self, file, check=True):

    print(check)
    # ? Validate driver is logged in
    if check: 
      if not self.Validate(): return self.DRIVER.quit()

    # ? Read user url csv file
    saveURL = 'data/user/' + cfg.BASE_DATE + '.json'
    userURL = json.load(open(file, "r"))
    userURL = list(filter(lambda user: user != "#", userURL))
    user_raw = []
    time = 1

    # ? Scrap each user
    for user in userURL:

      # skip if user is `#`

      # display 
      print(str(time) + "/" + str(len(userURL)) + " " + cfg.BASE_URL + user)
      time += 1
      self.DRIVER.get(cfg.BASE_URL + user)

      try:
        scheight = .1
        while scheight < 9.9:
          self.DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
          scheight += .1
        
        element = WebDriverWait(self.DRIVER, 10).until(
          EC.presence_of_element_located((By.CLASS_NAME, "experience-section"))
        )

      except TimeoutException:
        print("Timed out waiting for page to load")
        self.DRIVER.quit()
        return False

      
      # ? Parse Page
      # Use BeatufulSoup parser page
      bs_obj = BS(self.DRIVER.page_source, 'html.parser')

      # Common scrap
      artdeco_card = bs_obj.select_one("section.artdeco-card")
      userImage = artdeco_card.select_one("div.pv-top-card--photo img")['src']
      userName = artdeco_card.select_one("ul.pv-top-card--list li").getText().strip()
      userPositionHead = artdeco_card.select_one("h2.t-18.t-black.t-normal").getText().strip()
      userLocation = artdeco_card.select_one("ul.pv-top-card--list-bullet li").getText().strip()
      userAbout = bs_obj.select_one("section.pv-about-section span")
      userAbout = userAbout.getText().strip() if userAbout else ""


      
      profile_section = bs_obj.select("section.pv-profile-section--reorder-enabled .pv-profile-section__section-info")
  


      # ! Experience
      user_experience = [] 
      if bs_obj.select_one(".experience-section"):
        profile_experience_item = profile_section[0].select("div.pv-entity__summary-info")
        for item in profile_experience_item:
          position = {}
          position['name'] = item.h3.getText()
          position['company'] = item.select_one("p.pv-entity__secondary-title").getText()
          position['date_range'] = item.select_one("h4.pv-entity__date-range").getText().strip() if item.select_one("h4.pv-entity__date-range") else ""
          user_experience.append(position)



      # ! Education
      user_education = []
      if bs_obj.select_one(".education-section"):
        profile_education_item = profile_section[1].select("div.pv-entity__summary-info")
        for item in profile_education_item:
          user_education.append(item.select_one("h3.pv-entity__school-name").getText())



      # ! Skill
      user_skill = []
      if bs_obj.select_one(".pv-skills-section__additional-skills"):
        self.DRIVER.find_element_by_class_name("pv-skills-section__additional-skills").click() # find showmore button and click
        bs_obj = BS(self.DRIVER.page_source, 'html.parser') # new parser
        profile_skill_section = bs_obj.select_one("section.pv-skill-categories-section")

        try:
          element = WebDriverWait(self.DRIVER, 10).until(
              EC.presence_of_element_located((By.CLASS_NAME, "pv-skill-category-list"))
          )
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.DRIVER.quit()
            return False  

        # scrap skill
        profile_skill_item = profile_skill_section.select("span.pv-skill-category-entity__name-text")
        user_skill = [skill.getText().strip() for skill in profile_skill_item]
      

      # ! Interests
      user_interest = []
      if bs_obj.select_one("section.pv-interests-section "):
        interest_item = bs_obj.select("section.pv-interests-section .pv-entity__summary-info h3 span")
        user_interest = [item.getText().strip() for item in interest_item]


      # ? Create user data set
      user_data = {}
      user_data['image'] = userImage
      user_data['name'] = userName
      user_data['position'] = userPositionHead
      user_data['location'] = userLocation
      user_data['experience'] = user_experience
      user_data['about'] = userAbout
      user_data['education'] = user_education
      user_data['skill'] = user_skill
      user_data['interest'] = user_interest

      print(user_data)

      user_raw.append(user_data)

      if os.path.exists(saveURL):
        with open(saveURL) as json_file:
          data = json.load(json_file) 
          temp = data['data']
          temp.append(user_data) 
          self.writeJson(data, saveURL)
      else:
        data = user_data
        self.writeJson({'data': [data]}, saveURL)

    self.DRIVER.quit()
    return saveURL
    

    

