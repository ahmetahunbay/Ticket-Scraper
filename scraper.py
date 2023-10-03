from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime


# this represents an individual game.
# store the two teams, first one will be home team
# store date of game.
# store the volume aka "{volume} students looking for tickets!"
class Game:
    def __init__(self, team1, team2, date, volume):
        self.team1 = team1
        self.team2 = team2
        self.date = date
        self.volume = volume

# represents individual ticket listings. rank is the rank of the ticket in the list of tickets
class Ticket:
    def __init__(self, userName, price, rank):
        self.userName = userName
        self.price = price
        self.rank = rank


#this function retrieves one scrape. In the future, this will be ran every x minutes to get continuous data in a DB
def scrapeTickets():
    #url of ticket website
    url = "https://studentseats.com/"   
    chrome_options = Options()
    chrome_options.add_argument('--headless')           
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    #list of upcoming games
    gamecard_elements = driver.find_elements(By.CLASS_NAME, 'upcomingGameCard')

    scrapeKey = datetime.now()
    gameList = []

    #iterate through upcoming game pages
    ticketSites = []
    for element in gamecard_elements:
        ticketSites.append(element.get_attribute('href'))    
    for site in ticketSites:

        driver.get(site)

        # Game Name
        title = driver.find_element(By.CSS_SELECTOR, 'h1').text
        teams = [sub.strip() for sub in title.split("vs.")]
        team1 = teams[0]
        team2 = teams[1]

        #TODO: Get ticket volume, aka how many students are interested in ticket
        #volume = driver.find_elements(By.CLASS_NAME, 'card-element-interior-dark')
        volume = 0

        #TODO: Get date of game from website
        date = datetime.now()
        game = Game(team1, team2, date, volume)

        users = driver.find_elements(By.CLASS_NAME, 'ticket-username')
        posts = []
        for user in users:
           posts.append(user.text + ' Post')

        #fills ticket postings
        tickets = []
        for i, post in enumerate(posts):    
            listing = driver.find_element(By.ID, post)
            tup = listing.find_elements(By.CLASS_NAME, 'fa-2x')

            userName = tup[0].text
            ticketPrice = tup[1].text
            rank = i

            tickets.append(Ticket(userName, ticketPrice, rank))
        gameList.append((game, tickets))
        
    return (scrapeKey, gameList)
    

if __name__ == '__main__':
    scrapeTime, gameList = scrapeTickets()


