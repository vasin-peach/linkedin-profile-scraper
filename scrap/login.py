
class Login():
  
  # ! Login
  def __init__(self):
    
    # Direct to linkedin login page
    self.driver.get('https://www.linkedin.com/login')

    # Enter form and submit
    self.driver.find_element_by_id("username").send_keys(username)
    self.driver.find_element_by_id("password").send_keys(password)
    self.driver.find_element_by_class_name("from__button--floating").click()

    # Store auth cookie
    all_cookies = self.driver.get_cookies()
    new_cookies = all_cookies

    # Dump cookie to pkl file
    # Use to load when open new session
    pickle.dump(new_cookies , open("./Cookies.pkl","wb"))

