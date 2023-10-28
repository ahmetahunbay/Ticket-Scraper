import csv

#instantiates global variables for csv files

statusCSV = "game_status.csv"
listingsCSV = "ticket_listings.csv"
gamesCSV = "games.csv"

def initCSVDir(dir):
    global csvDir
    csvDir = dir

def clearCSVs(csvDir):
    with open(csvDir + statusCSV, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["gameId", "volume", "sold", "listed", "scrapetime"])
    with open(csvDir + listingsCSV, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["userName", "price", "section", "row", "seat", "quicksell", "verified", "time", "gameId", "action"])
    with open(csvDir + gamesCSV, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["gameId", "team1", "team2", "date", "sport"])

def writeGameStatuses(statuses):
    try:
        with open(csvDir + statusCSV, 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            for status in statuses:
                csvwriter.writerow([status.gameId, status.volume, status.sold, status.listed, status.scrapeTime])
    except:
        raise Exception("Error writing Statuses to csv")

def writeTicketListings(listings):
    try:
        with open(csvDir + listingsCSV, 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            for listing in listings:
                real_price = float(listing.price) / 100
                csvwriter.writerow([listing.userName, real_price, listing.section, listing.row, listing.seat, listing.bolt, listing.verified, listing.time, listing.gameId, listing.action])
    except:
        raise Exception("Error writing Tickets to csv")


def writeGames(games):
    try:
        with open(csvDir + gamesCSV, 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            for game in games:
                csvwriter.writerow([game.gameId, game.team1, game.team2, game.date, game.sport])
    except:
        raise Exception("Error writing Games to csv")

def writeCSVs(status_list, game_list, ticket_list):
    try:
        writeGameStatuses(status_list)
        writeTicketListings(ticket_list)
        writeGames(game_list)
    except Exception as e:
        print(e)

def getCSVListings():
    with open(csvDir + listingsCSV, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        rows = []
        for row in csvreader:
            rows.append(row)
        return rows
    
def getCSVStatuses():
    with open(csvDir + statusCSV, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        rows = []
        for row in csvreader:
            rows.append(row)
        return rows

def getCSVGames():
    with open(csvDir + gamesCSV, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        rows = []
        for row in csvreader:
            rows.append(row)
        return rows
        