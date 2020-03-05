# ! Find User
  # find user url by linkedin company search
  def Find(self, keyword="agoda", page_start=1 , page_range=10):

    


    SearchURL = "https://www.linkedin.com/search/results/people/?keywords=" + keyword + "&origin=SUGGESTION&page="
    Users = []

    for page in range(page_start, page_range):
      print(page)