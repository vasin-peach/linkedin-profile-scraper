# https://medium.com/@winston.smith.spb/python-selenium-speed-scraping-45bda525e42
# https://github.com/TheDancerCodes/Selenium-Webscraping-Example/blob/master/webscraping_example.py

#Import modules
from selenium import webdriver
from bs4 import BeautifulSoup as BS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import time
import pandas as pd
import csv
import os
import pickle
import re
import time 
import json


class ScrapActor:

  def __init__(self):
    self.baseURL = "https://www.linkedin.com"
    self.date_now = time.strftime("%I-%M-%S-%d-%m-%y")
    # username = input("enter linkedin username: ")
    # password = input("enter linkedin password: ")
    # keywords = input("enter linkedin keywords: ")
    # pages_start = int(input("page start at: "))
    # pages_range = int(input("page range: "))

    # url = "https://www.linkedin.com/search/results/people/?keywords=" + keywords + "&origin=SUGGESTION&page="

    options = webdriver.ChromeOptions();
    options.add_argument('headless');
    options.add_argument('window-size=1200x600');
    self.driver = webdriver.Chrome(executable_path='C:/chromedriver', chrome_options=options)
    # self.login(username, password)
    # actors = self.getActorByPage(url, pages_start, pages_range)
    # self.saveData('./data/actorsURL-' + date_now + '.csv', pd.Series(actors))



    # open default page
    self.driver.get('https://www.linkedin.com')


    # load cookie
    if os.path.exists("QuoraCookies.pkl"):
      for cookie in pickle.load(open("QuoraCookies.pkl", "rb")):
        cookie_new = cookie
        if cookie.get('expiry') != None: del cookie['expiry']
        self.driver.add_cookie(cookie)
    # if cookie not exist than login


    # get actor data by csv file
    self.getActorData("data/actorsURL-11-48-41-21-02-20.csv")


  # ? LOGIN
  def login(self, username, password):
    # To Linkedin Login
    self.driver.get('https://www.linkedin.com/login')

    # Login
    self.driver.find_element_by_id("username").send_keys(username)
    self.driver.find_element_by_id("password").send_keys(password)
    self.driver.find_element_by_class_name("from__button--floating").click()

    all_cookies = self.driver.get_cookies()
    new_cookies = all_cookies
    # for index in range(len(all_cookies)):
    #   new_cookies[index]['domain'] = 'https://www.linkedin.com'

    pickle.dump(new_cookies , open("./QuoraCookies.pkl","wb"))


  # ? GET SEARCH PAGE
  def getActorByPage(self, url, pages_start, pages_range):
    actors = []
    for page in range(pages_start, pages_range + 1):

      # create url by page number
      url_page = url + str(page)

      try:
        # get actor
        actors.append(self.getActorURL(url_page))
      except:
        print("Can not get actor url in page " + str(page))
        return actors

    actors = sum(actors, [])
    return actors
  
  # ? SAVE TO CSV
  def saveData(self, filename, data):
    try:
      data.to_csv(filename, index = None, header=False)
    except Exception as e:
      print(e)
      return False


  # ? GET ACTOR URL
  def getActorURL(self, url):
    # Open page
    self.driver.get(url)

    # Wait element class name `actor-name` located 
    try:
        element = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located((By.CLASS_NAME, "actor-name"))
        )
    except TimeoutException:
        print("Timed out waiting for page to load")
        self.driver.quit()
        return False

    # Use BeatufulSoup parser page
    bs_obj = BS(self.driver.page_source, 'html.parser')

    # Find `a` and get href
    actor_list = bs_obj.select("div.search-result__info a.search-result__result-link")
    actor_href = [actor['href'] for actor in actor_list]

    # display scrap finish
    print("Scraping url  " + url + " finish.")
    return actor_href

  def getActorData(self, file):

    # read actorsURL csv file
    saveURL = 'data/actors/' + self.date_now + '.json'
    actorURL = list(csv.reader(open(file, "r")))
    actors_raw = []

    time = 1
    for actor in actorURL:
    # for actor in [['/in/panthasit-techawattanagan-009058140/']]:
      print(str(time) + "/" + str(len(actorURL)) + " " + self.baseURL + actor[0])
      time += 1

      self.driver.get(self.baseURL + actor[0])

      try:
          # scroll to bottom of page
          # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2)") 
          # wait element class name `pv-interest-entity"` located 

          scheight = .1
          while scheight < 9.9:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
            scheight += .1

          # element = WebDriverWait(self.driver, 10).until(
          #     EC.presence_of_element_located((By.CLASS_NAME, "education-section"))
          # )

          element = WebDriverWait(self.driver, 10).until(
              EC.presence_of_element_located((By.CLASS_NAME, "experience-section"))
          )
      except TimeoutException:
          print("Timed out waiting for page to load")
          self.driver.quit()
          return False

      # Use BeatufulSoup parser page
      bs_obj = BS(self.driver.page_source, 'html.parser')

      # Common scrap
      artdeco_card = bs_obj.select_one("section.artdeco-card")
      actorImage = artdeco_card.select_one("div.pv-top-card--photo img")['src']
      actorName = artdeco_card.select_one("ul.pv-top-card--list li").getText().strip()
      actorPositionHead = artdeco_card.select_one("h2.t-18.t-black.t-normal").getText().strip()
      actorLocation = artdeco_card.select_one("ul.pv-top-card--list-bullet li").getText().strip()
      actorAbout = bs_obj.select_one("section.pv-about-section span")
      actorAbout = actorAbout.getText().strip() if actorAbout else ""

      
      profile_section = bs_obj.select("section.pv-profile-section--reorder-enabled .pv-profile-section__section-info")
  


      # ! Experience
      actor_experience = [] 
      if bs_obj.select_one(".experience-section"):
        profile_experience_item = profile_section[0].select("div.pv-entity__summary-info")
        for item in profile_experience_item:
          position = {}
          position['name'] = item.h3.getText()
          position['company'] = item.select_one("p.pv-entity__secondary-title").getText()
          position['date_range'] = item.select_one("h4.pv-entity__date-range").getText().strip() if item.select_one("h4.pv-entity__date-range") else ""
          actor_experience.append(position)



      # ! Education
      actor_education = []
      if bs_obj.select_one(".education-section"):
        profile_education_item = profile_section[1].select("div.pv-entity__summary-info")
        for item in profile_education_item:
          actor_education.append(item.select_one("h3.pv-entity__school-name").getText())



      # ! Skill
      actor_skill = []
      if bs_obj.select_one(".pv-skills-section__additional-skills"):
        self.driver.find_element_by_class_name("pv-skills-section__additional-skills").click() # find showmore button and click
        bs_obj = BS(self.driver.page_source, 'html.parser') # new parser
        profile_skill_section = bs_obj.select_one("section.pv-skill-categories-section")

        try:
          element = WebDriverWait(self.driver, 10).until(
              EC.presence_of_element_located((By.CLASS_NAME, "pv-skill-category-list"))
          )
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.driver.quit()
            return False  

        # scrap skill
        profile_skill_item = profile_skill_section.select("span.pv-skill-category-entity__name-text")
        actor_skill = [skill.getText().strip() for skill in profile_skill_item]
      

      # ! Interests
      actor_interest = []
      if bs_obj.select_one("section.pv-interests-section "):
        interest_item = bs_obj.select("section.pv-interests-section .pv-entity__summary-info h3 span")
        actor_interest = [item.getText().strip() for item in interest_item]


      # ! Create actor data set
      actor_data = {}
      actor_data['image'] = actorImage
      actor_data['name'] = actorName
      actor_data['position'] = actorPositionHead
      actor_data['location'] = actorLocation
      actor_data['experience'] = actor_experience
      actor_data['about'] = actorAbout
      actor_data['education'] = actor_education
      actor_data['skill'] = actor_skill
      actor_data['interest'] = actor_interest

      print(actor_data)
      actors_raw.append(actor_data)

      if os.path.exists(saveURL):
        with open(saveURL) as json_file:
          data = json.load(json_file) 
          temp = data['data']
          temp.append(actor_data) 
          self.writeJson(data, saveURL)
      else:
        data = actor_data
        self.writeJson({'data': [data]}, saveURL)


    # # dict to json
    # with open('data/actors/' + self.date_now + ".json", 'w') as f:
    #   json.dump(actors_raw, f)  

  def writeJson(self, data, filename):
    with open(filename, 'w') as f:
      json.dump(data, f, indent=4)


if __name__ == "__main__":
  ScrapActor()

# #Get MovieNames
# movienames=driver.find_elements_by_class_name('titleColumn')
# Movienames=[name.text for name in movienames] 

# #Get Ratings
# ratings = driver.find_elements_by_class_name('ratingColumn.imdbRating')
# Ratings=[rating.text for rating in ratings]
# DF_IMDb=pd.DataFrame({'MovieNames':Movienames , 'Ratings':Ratings})

# #Get links
# links=driver.find_elements_by_xpath("//td[@class='titleColumn']/a")
# Links = [link.get_attribute('href') for link in links]
# DF_IMDb['Links']=Links

# #Set List to keep data in each link
# Director=[]
# ActorNames =[]
# CharacterNames =[]
# Storyline=[]
# Runtime=[]
# Genres=[]
# Releasedate=[]
# Budget=[]
# Worldwidegross=[]
# #Loop Links
# for link in range(0,len(Links)):
#     driver.get(Links[link])
#     #Get Director
#     director = driver.find_element_by_xpath("//div[@class='credit_summary_item']/a").text
#     #Get casts (ActorNames,CharactorNames)
#     casts = driver.find_elements_by_xpath("//table[@class='cast_list']/tbody/tr")
#     Actornames =[cast.text.split('...')[0] for cast in casts if str(cast.text.find('...')).isnumeric()]
#     Characternames =[cast.text.split('...')[1] for cast in casts if str(cast.text.find('...')).isnumeric()]
#     #Get storyline
#     storyline = driver.find_element_by_xpath("//div[@class='inline canwrap']/p/span").text
#     genres = driver.find_elements_by_xpath("//div[@id='titleStoryLine']/div[@class='see-more inline canwrap']")[1].text
#     genres2 =  genres[genres.find(" ")+1:]
#     Detail = driver.find_element_by_id("titleDetails").text
#     #Get releasedate
#     releasedate=Detail[Detail.find("Release Date:")+14:]
#     releasedate2=releasedate[0:releasedate.find("See more")-1]
#     #Get worldwidegross
#     worldwidegross=Detail[Detail.find("Cumulative Worldwide Gross:")+28:]
#     worldwidegross2=worldwidegross[0:worldwidegross.find("\n")]
#     #Get runtime
#     runtime=Detail[Detail.find("Runtime:")+9:]
#     runtime2=runtime[0:runtime.find("min")-1]    
#     Director.append(director)
#     ActorNames.append(Actornames)
#     CharacterNames.append(Characternames)
#     Storyline.append(storyline)
#     Runtime.append(runtime2)
#     Genres.append(genres2)
#     Releasedate.append(releasedate)
#     Worldwidegross.append(worldwidegross2)
# #Collect all data and Export to excel
# DF_IMDb2=pd.DataFrame({'Director':Director,'ActorNames':ActorNames,'CharacterNames':CharacterNames,'Storyline':Storyline,'Runtime':Runtime,'Genres':Genres,'Releasedate':Releasedate,'Worldwidegross':Worldwidegross})
# DF_IMDb=pd.concat([DF_IMDb, DF_IMDb2], axis=1)
# DF_IMDb.to_excel('DF_IMDb_Data.xlsx')