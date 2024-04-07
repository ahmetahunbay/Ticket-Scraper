import sqlite3
from db import closeDB, initDB, rollbackDB, allGameStatuses
from scraper import scrapeTickets
from handler import handle_changes
from csv_writer import write_to_csv, initCSVDir
from datetime import datetime


def local_run():
    connection = sqlite3.connect('tickets.db')
    initDB(connection)

    try:
        scrape_time = str(datetime.now())
        db_statuses = allGameStatuses()
        initCSVDir("csv_data")

        print("Retrieved stale game statuses")

        #old list is a list of games no longer on site
        #new map is a map of new games to tickets
        #changed map is a map of games to tickets where the listings have changed
        #perm_statuses is a list of new game statuses to write to the permanent db
        #current_statuses is a map of gameIds to statuses to update db
        old_list, new_map, changed_map, perm_statuses, current_statuses = scrapeTickets(scrape_time, db_statuses)

        print("Performed scrape")
        
        handle_changes(write_to_csv, scrape_time, old_list, new_map, changed_map, perm_statuses, current_statuses)
    except Exception as e:
        print(e)
        rollbackDB()

if __name__ == "__main__":
    local_run()