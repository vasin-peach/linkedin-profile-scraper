from scrap.scrap import Scrap
Scrap = Scrap()

def Main():

  # Scrap User URL
  Scrap.ScrapUserURL(keyword="agoda", page_start=1, page_range=5)

  # Manual Call Funciton
  # url = "data/url/" + "02-25-24-06-03-20.json"   # file name from use ScrapUserURL
  # Scrap User Data
  # Scrap.ScrapUserData(url)


if __name__ == "__main__":
  Main()