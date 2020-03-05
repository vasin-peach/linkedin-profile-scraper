from selenium import webdriver
from bs4 import BeautifulSoup as BS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from . import config as cfg

import pickle

class Scrap:

  # ! Init
  def __init__(self):

    # Init driver
    OPTIONS = webdriver.ChromeOptions();
    # OPTIONS.add_argument('headless'); # invisible browser
    OPTIONS.add_argument('window-size=1200x600');
    self.DRIVER = webdriver.Chrome(executable_path='C:/chromedriver', chrome_options=OPTIONS)
    self.DRIVER.get('https://www.linkedin.com')
    


  # ! Login
  def Login(self):
    # Direct to linkedin login page
    self.DRIVER.get('https://www.linkedin.com/login')

    # Enter form and submit
    self.DRIVER.find_element_by_id("username").send_keys(cfg.USERNAME)
    self.DRIVER.find_element_by_id("password").send_keys(cfg.PASSWORD)
    self.DRIVER.find_element_by_class_name("from__button--floating").click()

    # Store auth cookie
    all_cookies = self.DRIVER.get_cookies()
    new_cookies = all_cookies

    # Dump cookie to pkl file
    # Use to load when open new session
    pickle.dump(new_cookies , open("./Cookies.pkl","wb"))

  # ! Validate Login
  def Validate(self):

    validateURL = f"https://www.linkedin.com/search/results/people/?keywords=agoda&origin=SUGGESTION&page=1"
    self.DRIVER.get(SearchURL)

    try: # Wait element class name `actor-name` located 
      element = WebDriverWait(self.DRIVER, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "actor-name"))
      )
      break 
    except TimeoutException: # If can't locate `actor-name` element --> login
      


  # ! Find User
  # find user url by linkedin company search
  def Find(self, keyword="agoda", page_start=1 , page_range=10):

    Users = [] # for store user list

    for page in range(page_start, page_range + 1):


      # Open driver by `SearchURL`
      SearchURL = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SUGGESTION&page={page}"
      self.DRIVER.get(SearchURL)


      # ? Validate Login
      try_range = 1
      for _try in range(0, try_range):
        # Wait element class name `actor-name` located 
        try: 
            element = WebDriverWait(self.DRIVER, 5).until(
              EC.presence_of_element_located((By.CLASS_NAME, "actor-name"))
            )
            break 
        # If can't locate `actor-name` element --> login
        except TimeoutException: 

          if try_range == _try: 
            self.DRIVER.quit()
            raise

          print("Timeout --> Try Login", _try + 1)
          self.Login()


    

    

