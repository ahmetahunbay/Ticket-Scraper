from scraper import scrapeTickets
from scraper import Game, Ticket
from csv_writer import writeCSVs, initCSVDir
from db import closeDB, initDB, addGame, removeGame, getGameTickets, addTicket, updateTicketCount, removeTicket, removeGameTickets, allGameStatuses, removeStatuses, set_statuses, unpack_seat_info
from datetime import datetime
from dynamo_writer import write_to_dynamo

class CSVListing:
    def __init__(self, ticket, gameId, time, action):
        self.userName = ticket.userName
        self.price = ticket.price
        self.section, self.row, self.seat = unpack_seat_info(ticket.seat_info)
        self.bolt = ticket.bolt
        self.verified = ticket.verified
        self.time = time
        self.gameId = gameId
        self.action = action

def handleTicketListings(dbTicketMap, currTicketMap, gameId, scrapeTime, csv_tickets):

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
                        #list to csv
                        csv_tickets.append(CSVListing(ticket, gameId, scrapeTime, "LISTED"))
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
                #list to csv and db
                for i in range(num):
                    csv_tickets.append(CSVListing(ticket, gameId, scrapeTime, "LISTED"))
                addTicket(ticket, gameId, scrapeTime, num)
        for ticket, num in dbTicketMap.items():
            #delist from db
            removeTicket(ticket, gameId, num)
            for i in range(num):
                #list to csv
                csv_tickets.append(CSVListing(ticket, ticket.gameId, scrapeTime, "DELISTED"))

def removeTickets(scrape_time, old_list, all_tickets):
    for gameId in old_list:
        tickets = getGameTickets(gameId)
        for ticket, num in tickets.items():
            for i in range(num):
                all_tickets.append(CSVListing(ticket, gameId, scrape_time, "EXPIRED"))
        removeGameTickets(gameId)
        removeGame(gameId)
        removeStatuses(gameId)

def updateTickets(scrape_time, new_map, all_tickets):
    for game, ticketMap in new_map.items():
        gameId = game.gameId
        dbTicketMap = getGameTickets(game.gameId)
        handleTicketListings(dbTicketMap, ticketMap, gameId, scrape_time, all_tickets)

def newTickets(scrape_time, new_map, all_tickets, csv_games):
    for game, ticketMap in new_map.items():
        gameId = game.gameId
        csv_games.append(game)
        addGame(game)
        for ticket, num in ticketMap.items():
            for i in range(num):
                all_tickets.append(CSVListing(ticket, gameId, scrape_time, "LISTED"))
            addTicket(ticket, gameId, scrape_time, num)

def handle_changes(scrape_time, old_list, new_map, changed_map, csv_statuses, current_statuses):
    csv_games = []
    all_tickets = []
    removeTickets(scrape_time, old_list, all_tickets)
    updateTickets(scrape_time, changed_map, all_tickets)
    newTickets(scrape_time, new_map, all_tickets, csv_games)
    set_statuses(current_statuses)

    write_to_dynamo(csv_statuses, csv_games, all_tickets)

def lambda_handler(event, context):
    initCSVDir("csv_data/")
    initDB("tickets")
    scrape_time = str(datetime.now())
    db_statuses = allGameStatuses()

    #old list is a list of games no longer on site
    #new map is a map of new games to tickets
    #changed map is a map of games to tickets where the listings have changed
    #csv_statuses is a list of new game statuses to write to csv
    #current_statuses is a map of gameIds to statuses to update db
    old_list, new_map, changed_map, csv_statuses, current_statuses = scrapeTickets(scrape_time, db_statuses)
    
    handle_changes(scrape_time, old_list, new_map, changed_map, csv_statuses, current_statuses)
    closeDB()