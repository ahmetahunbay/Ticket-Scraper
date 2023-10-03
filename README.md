<h3>Description</h3>
This is the base for a ticket price scraper using Selenium and Python.

In the future, this will be a script that automatically executes on a cloud platform every x minutes,
 and writes data to a cloud db.

 To run the code, run:
 make setup
 make install
 make run

<h3>Data Structures</h3>

Game = struct{team1, team2, volume, date}

Ticket = struct{userName, ticketPrice, rank}

data will be structured:
KEY = time of scrape
VALUE = list(tuple(Game, list(Ticket)))

This script only does one scrape

<h3>Pseudocode Process:</h3>

currScrape = time.now\
gameList = []\
studentSeats = studentseats.com\

for each upcomingGame in studentSeats:\
    game = Game(upcomingGame data)\
    tickets = []\
    for each ticket in upcomingGame:\
        tickets.append(Ticket(ticket data))\
    Add (game, tickets) tuple to gameList\

In the future: 
add (currScrape, gameList) to a database somehow
