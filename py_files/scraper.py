from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime
from csv_writer import writeGameStatuses
import math
import hashlib
import binascii

# this represents an individual game.
class Game:
    def __init__(self, gameId, team1, team2, date, sport):
        self.gameId = gameId
        self.team1 = team1
        self.team2 = team2
        self.date = date
        self.sport = sport

    def __hash__(self):
        return hash(self.gameId)
    
    def __eq__(self, other):
        return self.gameId == other.gameId

# represents ticket listings.
class Ticket:
    def __init__(self, userName, price, seat_info, bolt, verified, time = None, gameId = None):
        if time is not None and gameId is not None:
            self.userName = userName
            self.price = price
            self.seat_info = seat_info
            self.bolt = bolt
            self.verified = verified
            self.time = time
            self.gameId = gameId
        else:
            self.userName = userName
            self.price = price
            self.seat_info = seat_info
            self.verified = verified
            self.bolt = bolt

    def __hash__(self):
        return hash((self.userName, self.price, self.seat_info["Section"], self.seat_info["Row"], self.seat_info["Seat"]))
    
    def __eq__(self, other):
        if self.userName == other.userName and self.price == other.price and self.seat_info["Section"] == other.seat_info["Section"] and self.seat_info["Row"] == other.seat_info["Row"] and self.seat_info["Seat"] == other.seat_info["Seat"]:
            return True
        return False
    
#represents game status/ game metadata for database comparison
class GameStatus:
    def __init__(self, lowest_price, sold, listed):
        self.lowest_price = lowest_price
        self.sold = sold
        self.listed = listed
    
    def __hash__(self):
        return((self.lowest_price, self.sold, self.listed))
    
    def __eq__(self, other):
        if self.lowest_price == other.lowest_price and self.sold == other.sold and self.listed == other.listed:
            return True
        return False

#represents game status/ game metadata for csv storage
class CSVGameStatus:
    def __init__(self, gameId, volume, sold, listed, scrapeTime):
        self.gameId = gameId
        self.volume = volume
        self.sold = sold
        self.listed = listed
        self.scrapeTime = scrapeTime
    
    def __hash__(self):
        return hash((self.gameId, self.volume, self.sold, self.listed))
    
    def __eq__(self, other):
        if self.gameId == other.gameId and self.volume == other.volume and self.sold == other.sold and self.listed == other.listed:
            return True
        return False

#this function retrieves one scrape. In the future, this will be ran every x minutes to get continuous data in a DB
def scrapeTickets(scrape_time, db_statuses):
    #url of ticket website
    url = "https://studentseats.com/"   
    chrome_options = Options()
    chrome_options.add_argument('--headless')           
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    #list of upcoming games
    gamecard_elements = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, 'upcomingGameCard'))
    )

    csv_statuses = []

    #iterate through upcoming game pages
    gameSites = {}
    snapshot_statuses = {}
    for element in gamecard_elements:
        game, status = get_snapshot(element)
        gameSites[game] = element.get_attribute('href')  
        snapshot_statuses[game.gameId] = status
        
    oldList = []
    newList = []
    changedList = []
    # create 3 lists: new, old, changed
    for game, site in gameSites.items():
        gameId = game.gameId
        if gameId in db_statuses:
            #compare status fields
            if snapshot_statuses[gameId] != db_statuses[gameId]:
                #changed game
                changedList.append((game, site))
            del db_statuses[gameId]
        else:
            #new game
            newList.append((game, site))
        
    for gameId in db_statuses:
        #old game
        oldList.append(gameId)

    newMap = get_game_map(driver, newList, scrape_time, snapshot_statuses, csv_statuses)
    changedMap = get_game_map(driver, changedList, scrape_time, snapshot_statuses, csv_statuses)

    return oldList, newMap, changedMap, csv_statuses, snapshot_statuses

def get_game_map(driver, newList, scrape_time, snapshot_statuses, csv_statuses):
    gameMap = {}

    for game, site in newList:

        driver.get(site)

        #todo: get ticket volume
        volume = 0

        #game = get_game(driver)

        load_tickets(driver)

        posts = get_posts(driver)

        #fills ticket postings
        tickets = {}
        for post in posts:
            ticket = get_ticket(driver, post)

            if ticket not in tickets:
                tickets[ticket] = 0
            
            tickets[ticket] += 1
            
        gameMap[game] = tickets
        sold, listed = snapshot_statuses.get(game.gameId).sold, snapshot_statuses.get(game.gameId).listed
        csv_statuses.append(CSVGameStatus(game.gameId, volume, sold, listed, scrape_time))
        
    return gameMap

def getUserCreds(listing):
    verified = False
    bolt = False
    badge_section = listing.find_element(By.CLASS_NAME, 'ticket-badge-section')
    if badge_section is not None:
        scraped_user_verif = badge_section.find_elements(By.CLASS_NAME, 'material-symbols-outlined')
        for verif in scraped_user_verif:
            if verif.text == "bolt":
                bolt = True
            if verif.text == "verified":
                verified = True
    return verified, bolt

def get_snapshot(element):
    title_price = element.find_elements(By.CLASS_NAME, 'font-weight-bold')
    game_title = title_price[0].text
    price = int(float(title_price[1].text[1:]) * 100)
    teams = [sub.strip() for sub in game_title.split("vs.")]
    team1 = teams[0]
    team2 = teams[1]
    sport = element.find_element(By.CLASS_NAME, "upcomingGameSport").text
    game_date = str(get_game_date(element))
    
    sold_listed = element.find_elements(By.CLASS_NAME, 'm-1')
    sold = int(sold_listed[0].text.split(" ")[0])
    listed = int(sold_listed[1].text.split(" ")[0])

    game_string = ' '.join([team1, team2, game_date, sport])
    game_id = binascii.crc32(game_string.encode()) & 0xffffffff

    return Game(game_id, team1, team2, game_date, sport), GameStatus(price, sold, listed)
    
def get_game(driver):
    # Game Name
    game_title = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1'))
    )
    game_title = game_title.text
    teams = [sub.strip() for sub in game_title.split("vs.")]
    team1 = teams[0]
    team2 = teams[1]

    #Get date of game from website
    gameDateStr = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, 'upcomingGameSpan'))
    )[0].text
    gameDateTime = datetime.strptime(gameDateStr, "%A, %B %d, %Y")

    #get sport
    sportText = driver.find_element(By.CLASS_NAME, 'upcomingGameSport').text

    #TODO: Get ticket volume, aka how many students are interested in ticket
    #volume = driver.find_elements(By.CLASS_NAME, 'card-element-interior-dark')
    volume = 0

    #generate game id using team names, date, and sport
    game_string = ' '.join([team1, team2, str(gameDateTime), sportText])
    game_id = binascii.crc32(game_string.encode()) & 0xffffffff

    return Game(game_id, team1, team2, gameDateTime, sportText)

def load_tickets(driver):
    #load all ticket postings
    try:
        loader = driver.find_element(By.ID, 'loadMorePostsButton')
        yloc = loader.location['y']
        while True:
            driver.execute_script("arguments[0].click();", loader)
            loader = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.ID, 'loadMorePostsButton'))
            )
            if loader.location['y'] == yloc:
                break
            yloc = loader.location['y']
    except NoSuchElementException:
        pass
    except TimeoutException:
        pass

def get_posts(driver):
    users = driver.find_elements(By.CLASS_NAME, 'ticket-username')
    posts = []
    for user in users:
        posts.append(user.text + ' Post')
    return posts

def get_ticket(driver, post):
    listing = driver.find_element(By.ID, post)
    name_price_tup = listing.find_elements(By.CLASS_NAME, 'fa-2x')

    userName = name_price_tup[0].text
    ticketPrice = int(float(name_price_tup[1].text[1:]) * 100)

    ticket_info_groups = listing.find_elements(By.CLASS_NAME, 'ticket-info-group')
    seat_keys = ticket_info_groups[1].find_elements(By.CLASS_NAME, "text-gray")
    seat_vals = ticket_info_groups[1].find_elements(By.CLASS_NAME, "font-weight-bolder")

    verified, bolt = getUserCreds(listing)

    seat_info = {"Section": "", "Row": "", "Seat": ""}
    for seat_key, seat_val in zip(seat_keys, seat_vals):
        seat_info[seat_key.text] = seat_val.text

    return Ticket(userName, ticketPrice, seat_info, verified, bolt)

def get_game_date(element):
    date_str = element.find_elements(By.CLASS_NAME, "upcomingGameSpan")[0].text
    current_date = datetime.now()
    current_date = datetime(current_date.year, current_date.month, current_date.day)

    # Parse the date string into a datetime object
    game_date = datetime.strptime(date_str, '%B %d')
    game_date = game_date.replace(year=current_date.year)

    # If the game date has already occurred this year, set the year to next year
    if game_date < current_date:
        game_date = game_date.replace(year=current_date.year + 1)

    return game_date