from scrap.scrap import Scrap

Scrap = Scrap()

def Main():
  # print(Scrap.ScrapUserURL(keyword="kbtg", page_start=1, page_range=10))
  print(Scrap.ScrapUserData(f"data/url/02-11-40-06-03-20.json"))
  # Scrap.Find()

if __name__ == "__main__":
  Main()