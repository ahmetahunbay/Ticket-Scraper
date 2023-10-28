import sqlite3
from scraper import Ticket, Game, GameStatus
from datetime import datetime

def unpack_seat_info(seat_info):
    section = seat_info["Section"]
    row = seat_info["Row"]
    seat = seat_info["Seat"]
    return section, row, seat

global conn
global cursor

def initDB(dbName):
    global conn
    global cursor

    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute('BEGIN')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            user TEXT,
            price INTEGER,
            section TEXT,
            row TEXT,
            seat TEXT,
            bolt TEXT,
            verified TEXT,
            time TEXT,
            gameId INTEGER,
            count INTEGER
        )
    ''')

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS games(
            gameId INTEGER PRIMARY KEY,
            team1 TEXT,
            team2 TEXT, 
            date TEXT,
            sport TEXT
        )
    '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS game_statuses(
            gameId INTEGER PRIMARY KEY,
            lowest_price INTEGER,
            sold INTEGER,
            listed INTEGER
        )
    '''
    )

def allGameStatuses():
    cursor.execute(
        '''
        SELECT * FROM game_statuses
    '''
    )

    sql_statuses = cursor.fetchall()
    status_map = {}

    for status in sql_statuses:
        status_map[status[0]] = GameStatus(status[1], status[2], status[3])
    
    return status_map

def removeStatuses(gameId):
    cursor.execute(
        '''
        DELETE FROM game_statuses WHERE gameId = ?
        ''', (gameId,)
    )
    conn.commit()

def set_statuses(statusMap):
    cursor.execute(
        '''
        DELETE FROM game_statuses
        '''
    )
    for gameId, status in statusMap.items():
        cursor.execute(
            '''
            INSERT INTO game_statuses VALUES (?, ?, ?, ?)
            ''', (gameId, status.lowest_price, status.sold, status.listed)
        )
    
    conn.commit()

def getGameTickets(gameId):
    
    cursor.execute(
        '''
        SELECT * FROM tickets WHERE gameId = ?
    ''', (gameId,)
    )
    
    gameListings = cursor.fetchall()
    tickets = {}

    for db_ticket in gameListings:

        bolt, verified = db_creds_to_bool(db_ticket[5], db_ticket[6])

        seat_info = pack_seat_info(db_ticket[2], db_ticket[3], db_ticket[4])

        ticket = Ticket(db_ticket[0], db_ticket[1], seat_info, bolt, verified, db_ticket[7], db_ticket[8])

        if ticket not in tickets:
            tickets[ticket] = 0

        tickets[ticket] += 1
    
    return tickets

def getGamesSet():
    
    cursor.execute(
        '''
        SELECT * FROM games
        '''
    )
    sql_games = cursor.fetchall()
    games = set()
    
    for game in sql_games:
        #app_date = transform_date(game[3])
        games.add(Game(game[0], game[1], game[2], game[3], game[4]))

    return games

def addGame(game):

    try:
        cursor.execute(
            '''
            INSERT INTO games VALUES (?, ?, ?, ?, ?)
            ''', (game.gameId, game.team1, game.team2, game.date, game.sport)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass

def addTicket(ticket, gameId, time, count):
    section, row, seat = unpack_seat_info(ticket.seat_info)
    db_bolt, db_verified = bool_to_db_creds(ticket.bolt, ticket.verified)

    cursor.execute(
        '''
        INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticket.userName, ticket.price, section, row, seat, db_bolt, db_verified, time, gameId, count)
    )

    conn.commit()

def getGame(game_id):
    global cursor
    global conn

    cursor.execute(
        '''
        SELECT * from games WHERE gameId = ?''', (game_id,)
    )
    sql_game = cursor.fetchone()

    return Game(sql_game[0], sql_game[1], sql_game[2], sql_game[3], sql_game[4])

def updateTicketCount(ticket, gameId, time, count):

    section, row, seat = unpack_seat_info(ticket.seat_info)

    cursor.execute(
        '''
        UPDATE tickets SET count = ? WHERE user = ? AND section = ? AND row = ? AND seat = ? AND price = ? AND gameId = ?
        ''', (count, ticket.userName, section, row, seat, ticket.price, gameId)
    )

    conn.commit()

def removeTicket(ticket, gameId, count):
    global cursor
    global conn

    db_count = getTicketCount(ticket, gameId)

    section, row, seat = unpack_seat_info(ticket.seat_info)

    if db_count > count:
        cursor.execute(
            '''
            UPDATE tickets SET count = ? WHERE user = ? AND section = ? AND row = ? AND seat = ? AND price = ? AND gameId = ?
            ''', (db_count - count, ticket.userName, section, row, seat, ticket.price, gameId)
        )
    else:
        cursor.execute(
            '''
            DELETE FROM tickets WHERE user = ? AND section = ? AND row = ? AND seat = ? AND price = ?
            ''', (ticket.userName, section, row, seat, ticket.price,)
        )

    conn.commit()

def removeGameTickets(gameId):
    global cursor
    global conn

    cursor.execute(
        '''
        DELETE FROM tickets WHERE gameId = ?
        ''', (gameId,)
    )
    conn.commit()

def removeGame(gameId):
    global cursor
    global conn

    cursor.execute(
        '''
        DELETE FROM games WHERE gameId = ?
        ''', (gameId,)
    )
    conn.commit()

def db_creds_to_bool(db_bolt, db_verified):
    bolt = False if db_bolt else True
    verified = False if db_verified else True
    return bolt, verified

def bool_to_db_creds(bolt, verified):
    db_bolt = 0 if bolt else 1
    db_verified = 0 if verified else 1
    return db_bolt, db_verified

def getTicketCount(ticket, gameId):
    global cursor
    global conn

    section, row, seat = unpack_seat_info(ticket.seat_info)

    cursor.execute(
        '''
        SELECT count FROM tickets WHERE user = ? AND section = ? AND row = ? AND seat = ? AND price = ? AND gameId = ?
        ''', (ticket.userName, section, row, seat, ticket.price, gameId,)
    )

    count = cursor.fetchone()

    if count is None:
        return 0

    return count[0]

def clearDB(dbName):
    global conn
    global cursor

    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()

    cursor.execute(
        '''
        DROP TABLE IF EXISTS games
        '''
    )
    cursor.execute(
        '''
        DROP TABLE IF EXISTS tickets
        '''
    )
    cursor.execute(
        '''
        DROP TABLE IF EXISTS game_statuses
        '''
    )
    conn.commit()

def closeDB():
    global conn
    global cursor

    cursor.close()
    conn.close()

def pack_seat_info(section, row, seat):
    seat_info = {"Section": section, "Row": row, "Seat": seat}
    return seat_info

def transform_date(db_date):
    return datetime.strptime(db_date, "%Y-%m-%d")