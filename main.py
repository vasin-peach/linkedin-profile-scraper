from scrap.Scrap import Scrap
Scrap = Scrap()

def Main():

  # Scrap User URL
  Scrap.ScrapUserURL(keyword="Web Developer", size=80) # size is number of user

  # Manual Call Funciton
  # url = "data/url/" + "02-25-24-06-03-20.json"   # file name from use ScrapUserURL
  # Scrap User Data
  # Scrap.ScrapUserData('data/url/08-25-17-14-05-20.json', 'Help Desk Technician')


if __name__ == "__main__":
  Main()