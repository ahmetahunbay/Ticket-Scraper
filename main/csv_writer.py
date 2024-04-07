import csv
import tempfile
import shutil
import os

#instantiates global variables for csv files

statusCSV = "game_status.csv"
listingsCSV = "ticket_listings.csv"
gamesCSV = "games.csv"

def initCSVDir(dir):
    global csvDir
    csvDir = dir

def clearCSVs(csvDir):
    with open(os.path.join(csvDir, statusCSV), 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["gameId", "volume", "sold", "listed", "scrapetime"])
    with open(os.path.join(csvDir, listingsCSV), 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["userName", "price", "section", "row", "seat", "quicksell", "verified", "time", "gameId", "action"])
    with open(os.path.join(csvDir, gamesCSV), 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["gameId", "team1", "team2", "date", "sport"])

def write_to_csv(statuses, games, listings):
    global csvDir

    try:
        with tempfile.NamedTemporaryFile('w', delete=False) as temp_status, \
             tempfile.NamedTemporaryFile('w', delete=False) as temp_listings, \
             tempfile.NamedTemporaryFile('w', delete=False) as temp_games:

            csvwriter_status = csv.writer(temp_status)
            csvwriter_listings = csv.writer(temp_listings)
            csvwriter_games = csv.writer(temp_games)

            # Write to status CSV
            for status in statuses:
                csvwriter_status.writerow([status.gameId, status.volume, status.sold, status.listed, status.scrapeTime])

            # Write to listings CSV
            for listing in listings:
                real_price = float(listing.price) / 100
                csvwriter_listings.writerow([listing.userName, real_price, listing.section, listing.row, listing.seat, listing.bolt, listing.verified, listing.time, listing.gameId, listing.action])

            # Write to games CSV
            for game in games:
                csvwriter_games.writerow([game.gameId, game.team1, game.team2, game.date, game.sport])

        with open(temp_status.name, 'r') as temp_file, open(os.path.join(csvDir, statusCSV), 'a', newline='') as orig_file:
            shutil.copyfileobj(temp_file, orig_file)
        with open(temp_listings.name, 'r') as temp_file, open(os.path.join(csvDir, listingsCSV), 'a', newline='') as orig_file:
            shutil.copyfileobj(temp_file, orig_file)
        with open(temp_games.name, 'r') as temp_file, open(os.path.join(csvDir, gamesCSV), 'a', newline='') as orig_file:
            shutil.copyfileobj(temp_file, orig_file)

    except Exception as e:
        # If any write operation fails, discard the temporary files and raise an error
        raise Exception("Error writing to csv files: " + str(e))

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