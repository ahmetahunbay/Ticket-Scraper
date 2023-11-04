import sys


from csv_writer import initCSVDir, writeGameStatuses, clearCSVs, getCSVListings, writeCSVs, getCSVStatuses, getCSVGames
from db import initDB, clearDB, getGamesSet, closeDB
from scraper import Game, Ticket, GameStatus, CSVGameStatus
from handler import updateTickets, handle_changes
from datetime import date, timedelta, datetime
import string
import random
import binascii

#for debugging, watch
# [(game, list(ticketMap.keys())) for game, ticketMap in gameMap.items()]
# list(gameMap.keys())
# list(dbTicketMap.keys())

csvDir = "test_csv_data/"
db = "test_tickets.db"
# define the set of characters to choose from
characters = string.ascii_letters + string.digits

# generate the random string
def rand_str():
    return ''.join(random.choice(characters) for i in range(10))

def rand_date():
    start_date = date(2023, 1, 1)
    random_days = random.randint(0, 365)
    return start_date + timedelta(days=random_days)

def rand_bool():
    return bool(random.getrandbits(1))

def rand_int():
    return random.randint(0,100)

def random_ticket(i):
    userName = rand_str()
    price = rand_int()
    seat_info = {"Section": "General Admission", "Row": str(i % 10), "Seat": str(i)}
    bolt = rand_bool()
    verified = rand_bool()
    return Ticket(userName, price, seat_info, verified, bolt)

def random_game():
    team1 = rand_str()
    team2 = rand_str()
    gameDateTime = rand_date()
    sportText = rand_str()
    game_string = ' '.join([team1, team2, str(gameDateTime), sportText])
    game_id = binascii.crc32(game_string.encode()) & 0xffffffff
    return Game(game_id, team1, team2, gameDateTime, sportText)

#create test data for testing: 
def random_scrape(numGames, numTickets):
    scrape_time = datetime.now()
    gameMap = {}
    csv_statuses = []
    game_list = []
    snapshot_statuses = {}
    for _ in range(numGames):

        game = random_game()
        game_id = game.gameId
        ticketMap = {}

        for i in range(numTickets):
            ticket = random_ticket(i)
            if ticket not in ticketMap:
                ticketMap[ticket] = 0
            ticketMap[ticket] += 1

        gameMap[game] = ticketMap
        volume = rand_int()
        listed = numTickets
        sold = 0
        snapshot_statuses[game_id] = GameStatus(game_id, sold, listed)
        csv_statuses.append(CSVGameStatus(game_id, volume, sold, listed, scrape_time))
        game_list.append(game_id)
    return scrape_time, gameMap, csv_statuses, snapshot_statuses

def new_games(games, tickets):
    scrapeTime, gameMap, status_list, snapshot = random_scrape(games, tickets)
    handle_changes(scrapeTime, [], gameMap, {}, status_list, snapshot)
    return gameMap, status_list

def adjBase(gameMap):
    game_list = list(gameMap.keys())
    
    #delete a game (expired)
    del gameMap[game_list[0]]

    #add new game
    scrapeTime, new_game = random_scrape(1, 5)
    gameMap.update(new_game)

    #change prices (list delist)
    _, tickets = gameMap[game_list[1]]
    for _, ticket in tickets.items():
        ticket[0].price = ticket[0].price + 5
    
    updateTickets(scrapeTime, gameMap)

#expires game of the specified gameID given gameMap
def expire_game(exp_game, gameMap):
    scrapeTime = datetime.now()
    del gameMap[exp_game]
    handle_changes(scrapeTime, [exp_game.gameId], {}, {}, [], {})

def test_game_expired():
    start_test()

    gameMap, _ = new_games(2,1)
    exp_game = list(gameMap.keys())[0]
    exp_ticket = list(gameMap[exp_game].keys())[0]
    expire_game(exp_game, gameMap)
    listings = getCSVListings()
    usr_stat_tups = get_usr_stat_tups(listings)
    assert len(usr_stat_tups) == 3
    for game in gameMap:
        for ticket in gameMap[game]:
            assert (ticket.userName, "LISTED") in usr_stat_tups
    assert (exp_ticket.userName, "EXPIRED") in usr_stat_tups
    print("game expired test passed")

    closeDB()
    
def test_init_listing(gameMap):
    listings = getCSVListings()
    usr_stat_tups = get_usr_stat_tups(listings)
    assert len(usr_stat_tups) == 2
    for game in gameMap:
        for ticket in gameMap[game]:
            assert (ticket.userName, "LISTED") in usr_stat_tups
    print("init listing test passed")

def csv_to_statuses(csv_statuses):
    statuses = []
    for csv_status in csv_statuses:
        statuses.append(CSVGameStatus(int(csv_status[0]), int(csv_status[1]), int(csv_status[2]), int(csv_status[3]), csv_status[4]))
    return statuses

def test_init_statuses(status_list):
    csv_statuses = csv_to_statuses(getCSVStatuses())
    assert len(csv_statuses) == 2
    for status in status_list:
        assert status in csv_statuses

def csv_to_games(csv_games):
    games = []
    for csv_game in csv_games:
        date = datetime.strptime(csv_game[3], '%Y-%m-%d')
        games.append(Game(int(csv_game[0]), csv_game[1], csv_game[2], date, csv_game[4]))
    return games

def test_init_games(gameMap):
    csv_games = csv_to_games(getCSVGames())
    assert len(csv_games) == 2
    for game in gameMap:
        assert game in csv_games

def test_init_csv():
    start_test()
    gameMap, status_list = new_games(2,1)
    test_init_listing(gameMap)
    test_init_statuses(status_list)
    test_init_games(gameMap)
    closeDB()
    
def test_hashing():
    gameMap, _ = new_games(2,1)
    dbGameSet = getGamesSet()
    for game in gameMap:
        assert game in dbGameSet
    print("hashing test passed")

def get_usr_stat_tups(listings):
    usr_stat_tups = set()
    for listing in listings:
        usr_stat_tups.add((listing[0], listing[9]))
    return usr_stat_tups
    
def start_test(): 
    clearCSVs(csvDir)
    clearDB(db)
    initCSVDir(csvDir)
    initDB(db)

def adjPrices(gameMap):
    for _, ticketMap in gameMap.items():
        for ticket in ticketMap:
            ticket.price = ticket.price + 50

    scrapeTime = datetime.now()
    status_list = []
    handle_changes(scrapeTime, [], {}, gameMap, status_list, {})

def get_old_tickets(gameMap):
    old_tickets = []
    for ticketMap in gameMap.values():
        for ticket in ticketMap:
            old_tickets.append(ticket)
    return old_tickets

def get_usr_price_stat_tups(listings):
    usr_stat_tups = set()
    for listing in listings:
        price = int(float(listing[1]) * 100)
        usr_stat_tups.add((listing[0], price, listing[9]))
    return usr_stat_tups

def test_price_change():
    start_test()
    gameMap, _ = new_games(2,1)
    handle_changes(datetime.now(), [], gameMap, {}, [], {})
    adjPrices(gameMap)
    listings = getCSVListings()
    usr_stat_tups = get_usr_price_stat_tups(listings)
    assert len(usr_stat_tups) == 6
    for game in gameMap:
        for ticket in gameMap[game]:
            assert (ticket.userName, ticket.price, "LISTED") in usr_stat_tups
            assert (ticket.userName, ticket.price - 50, "LISTED") in usr_stat_tups
            assert (ticket.userName, ticket.price - 50, "DELISTED") in usr_stat_tups
    print("price change test passed")
    closeDB()

def get_usr_ticket_num(listings):
    usr_stat_tups = {}
    for listing in listings:
        price = int(float(listing[1]) * 100)
        tup = (listing[0], price, listing[9])
        if tup not in usr_stat_tups:
            usr_stat_tups[tup] = 0
        usr_stat_tups[tup] += 1
    return usr_stat_tups

def add_duplicate():
    scrapeTime, gameMap, csv_statuses, curr_status_map = random_scrape(1, 1)
    game = list(gameMap.keys())[0]
    ticket = list(gameMap[game].keys())[0]
    gameMap[game][ticket] = 2
    handle_changes(scrapeTime, [], gameMap, {}, csv_statuses, curr_status_map)
    listings = getCSVListings()
    usr_ticket_nums = get_usr_ticket_num(listings)
    assert len(usr_ticket_nums) == 1
    for num in usr_ticket_nums.values():
        assert num == 2
    return scrapeTime, gameMap, game, ticket

def test_new_scrape():
    #make initial scrape
    #make minor changes, so one game requires new scrape
    #check if only 2 games, with 3 scrapes
    start_test()
    scrapeTime, gameMap, csv_statuses, curr_status_map = random_scrape(2, 1)
    handle_changes(scrapeTime, [], gameMap, {}, csv_statuses, curr_status_map)
    new_ticket = random_ticket(1)
    changed_game = list(gameMap.keys())[0]
    changed_game_map = {changed_game: {new_ticket: 1}}
    curr_status_map[changed_game.gameId] = GameStatus( 12, 0, 2)
    changed_csv_statuses = [CSVGameStatus(changed_game.gameId, 2, 0, 2, scrapeTime)]


    handle_changes(scrapeTime, [], {}, changed_game_map, changed_csv_statuses, curr_status_map)

    games = getCSVGames()
    statuses = csv_to_statuses(getCSVStatuses())
    assert len(games) == 2
    assert len(statuses) == 3
    for status in statuses:
        assert status in csv_statuses or status in changed_csv_statuses

    closeDB()
    print("new scrape status/game test passed")

def test_duplicate_tickets():
    #test to see if duplicate listings are listed
    start_test()
    scrapeTime, gameMap, game, ticket = add_duplicate()

    #test to see if changing one price is reflected
    gameMap[game][ticket] = 1
    changed_price_ticket = Ticket(ticket.userName, ticket.price + 50, ticket.seat_info, ticket.verified, ticket.bolt)
    gameMap[game][changed_price_ticket] = 1
    handle_changes(scrapeTime, [], {}, gameMap, [], {})
    listings = getCSVListings()
    usr_ticket_nums = get_usr_ticket_num(listings)
    assert len(usr_ticket_nums) == 2
    assert usr_ticket_nums[(changed_price_ticket.userName, changed_price_ticket.price, "LISTED")] == 1
    assert usr_ticket_nums[(ticket.userName, ticket.price, "LISTED")] == 2

    #change other price to match


    #change both

    closeDB()
    print("test duplicate tickets passed")

if __name__ == '__main__':
    #test_hashing()

    #test that games, statuses, and tickets get intialized correctly
    test_init_csv()

    #test new scrape on statuses and games
    test_new_scrape()

    #tests whether game expiring yields correct outcome
    test_game_expired()

    #test price changes
    test_price_change()

    #test duplicate tickets
    test_duplicate_tickets()

    #test that db and csv stay consistent if errors arise







    
