from scrap.scrap import Scrap

Scrap = Scrap()

def Main():
  url = Scrap.ScrapUserURL(keyword="scb", page_start=1, page_range=5)
  print(Scrap.ScrapUserData(url, check=False))
  # Scrap.Find()

if __name__ == "__main__":
  Main()