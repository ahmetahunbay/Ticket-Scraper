<h2>outdated readme (sorry)</h2>

<h3>Description</h3>
This is the base for a ticket price scraper using Selenium, Python, CSV, and SQLite.

It pulls data from a popular Student Ticket website: studentseats.com

Data:

Games have a unique game id, as well as their sport, teams, and date

Game statuses are also stored with the time of the data retrieval, the game id of the game, the total number of interested users, the number of sold and listed tickets at the time of the snapshot

Ticket listings are stored with user information, price, seat information, gameid, an action: listed, delisted or expired, and the time of this action

The SQLite database serves as an intermediate between the persistent storage and the current information. tickets that are scraped are stored on the sqlite db, then once a game is removed or a ticket is delisted, the ticket is removed from the database and listed to the persistent CSV.

NOTE: tickets with action "delisted" account for both tickets that are either sold or delisted, the distinction will be made upon analysis of whether the number of tickets sold changed (in the game statuses csv). also, when a ticket's price is changed, it is marked as being delisted and relisted.

Process:
1. scrape data
   * check main website and get metadata on games and listings
   * pull game snapshot data from database
   * track inconsistencies:
     * game found in scrape but not db (new game)
     * game found in db but not scrape (old game)
     * game status inconsistent with game status on db (changed game)
2. make updates
   * write new snapshots to db for future reference
   * for new games, write all listings and status to CSV
   * for old games, write all existing tickets of game to CSV with action = expired, since game expired
   * for changed games, write new listings or delistings to CSV