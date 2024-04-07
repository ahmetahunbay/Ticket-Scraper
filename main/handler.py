from scraper import scrapeTickets
from scraper import Game, Ticket
#from csv_writer import writeCSVs, initCSVDir
from db import closeDB, initDB, rollbackDB, addGame, removeGame, getGameTickets, addTicket, updateTicketCount, removeTicket, removeGameTickets, allGameStatuses, removeStatuses, set_statuses, unpack_seat_info
from datetime import datetime
from dynamo_writer import write_to_perm
import pymysql
import os

db_name = "tickets"
test_db_name = "test_tickets"

user_name = os.environ['USER_NAME']
password = os.environ['PASSWORD']
rds_proxy_host = os.environ['RDS_PROXY_HOST']

#permanent listing class for data
class PermListing:
    def __init__(self, ticket, gameId, time, action):
        self.userName = ticket.userName
        self.price = ticket.price
        self.section, self.row, self.seat = unpack_seat_info(ticket.seat_info)
        self.bolt = ticket.bolt
        self.verified = ticket.verified
        self.time = time
        self.gameId = gameId
        self.action = action

def handleTicketListings(dbTicketMap, currTicketMap, gameId, scrapeTime, perm_tickets):

    #update db listings
        for ticket, num in currTicketMap.items():
            #checks if ticket not new
            if ticket in dbTicketMap:

                old_num = dbTicketMap[ticket]
                if old_num > num:
                    #this means some of old tickets were sold
                    #update old tickets
                    dbTicketMap[ticket] = old_num - num
                elif old_num < num:
                    #this means new tickets were listed
                    for _ in range(num - old_num):
                        #list to perm
                        perm_tickets.append(PermListing(ticket, gameId, scrapeTime, "LISTED"))
                    #list to db
                    updateTicketCount(ticket, gameId, scrapeTime, num)
                    #old tickets are covered
                    del dbTicketMap[ticket]
                else:
                    #this means no tickets were sold or listed
                    #old tickets are covered
                    del dbTicketMap[ticket]
            else:
                #if ticket is new
                #list to perm and temp
                for i in range(num):
                    perm_tickets.append(PermListing(ticket, gameId, scrapeTime, "LISTED"))
                addTicket(ticket, gameId, scrapeTime, num)
        for ticket, num in dbTicketMap.items():
            #delist from db
            removeTicket(ticket, gameId, num)
            for i in range(num):
                #list to permanent tickets
                perm_tickets.append(PermListing(ticket, ticket.gameId, scrapeTime, "DELISTED"))

def removeTickets(scrape_time, old_list, all_tickets):
    for gameId in old_list:
        tickets = getGameTickets(gameId)
        for ticket, num in tickets.items():
            for i in range(num):
                all_tickets.append(PermListing(ticket, gameId, scrape_time, "EXPIRED"))
        removeGameTickets(gameId)
        removeGame(gameId)
        removeStatuses(gameId)

def updateTickets(scrape_time, new_map, all_tickets):
    for game, ticketMap in new_map.items():
        gameId = game.gameId
        dbTicketMap = getGameTickets(game.gameId)
        handleTicketListings(dbTicketMap, ticketMap, gameId, scrape_time, all_tickets)

def newTickets(scrape_time, new_map, all_tickets, perm_games):
    for game, ticketMap in new_map.items():
        gameId = game.gameId
        perm_games.append(game)
        addGame(game)
        for ticket, num in ticketMap.items():
            for i in range(num):
                all_tickets.append(PermListing(ticket, gameId, scrape_time, "LISTED"))
            addTicket(ticket, gameId, scrape_time, num)

def handle_changes(write_func, scrape_time, old_list, new_map, changed_map, perm_statuses, current_statuses):
    perm_games = []
    all_tickets = []
    removeTickets(scrape_time, old_list, all_tickets)
    updateTickets(scrape_time, changed_map, all_tickets)
    newTickets(scrape_time, new_map, all_tickets, perm_games)
    set_statuses(current_statuses)

    write_func(perm_statuses, perm_games, all_tickets)

def lambda_handler(event, context):

    try:
        print(f"Trying to connect with {rds_proxy_host} as {user_name} and {password} to {db_name}")
        connection = pymysql.connect(host=rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)
    except Exception as e:
        print("Error connecting to database")
        print(e)
        return

    print("Connected to RDS MySQL")

    initDB(connection)
    try:
        scrape_time = str(datetime.now())
        db_statuses = allGameStatuses()

        #old list is a list of games no longer on site
        #new map is a map of new games to tickets
        #changed map is a map of games to tickets where the listings have changed
        #perm_statuses is a list of new game statuses to write to the permanent db
        #current_statuses is a map of gameIds to statuses to update db
        old_list, new_map, changed_map, perm_statuses, current_statuses = scrapeTickets(scrape_time, db_statuses)
        
        handle_changes(write_to_perm, scrape_time, old_list, new_map, changed_map, perm_statuses, current_statuses)
    except Exception as e:
        rollbackDB()
    closeDB()
    

def test_handler(connection, csv_perm_writes, get_scrape, scrape_status):
    scrape_time = str(datetime.now())
    db_statuses = allGameStatuses()

    old_list, new_map, changed_map, perm_statuses, current_statuses = get_scrape(scrape_time, db_statuses)
    
    handle_changes(csv_perm_writes, scrape_time, old_list, new_map, changed_map, perm_statuses, current_statuses)
    closeDB()