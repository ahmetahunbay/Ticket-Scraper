This is the base for a ticket price scraper using selenium and Python.

In the future, this will be a script that automatically excutes on a cloud platform every x minutes,
 and writes data to a cloud db.

What we want:

Game = struct{team1, team2, volume, date}

Ticket = struct{userName, ticketPrice, rank}

Data will be tracked by:
KEY = time of scrape
VALUE = list(tuple(Game, list(Ticket)))

but note this script will only store one scrape

Process:

currScrape = time.now
gameList = []
studentSeats = studentseats.com

for each upcomingGame in studentSeats:
    game = Game(upcomingGame data)
    tickets = []
    for each ticket in upcomingGame:
        tickets.append(Ticket(ticket data))
    Add (game, tickets) tuple to gameList

In the future: 
add (currScrape, gameList) to a database