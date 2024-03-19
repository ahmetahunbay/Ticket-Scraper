import json
import boto3
import secrets
import random

dynamo_client = boto3.client('dynamodb')

#TODO: make writes, ensure that if one fails they all fail
def write_to_perm(ticket_listings, game_statuses, games):
    dyn_listings = listings_to_dyn(ticket_listings)
    dyn_statuses = statuses_to_dyn(game_statuses)
    dyn_games = games_to_dyn(games)

    try:
        transact_items = dyn_listings + dyn_statuses + dyn_games
        dynamo_client.transact_write_items(TransactItems=transact_items)

    except Exception as e:
        print(f"Error: {e}")

def listings_to_dyn(listings):
    dyn_listings = []
    for listing in listings:
        listing_id = secrets.token_hex(10)
        item = {
            'ticket_id': {'S': listing_id},
            'game_id': {'S': str(listing.gameId)},
            'user_name': {'S': str(listing.userName)},
            'price': {'N': listing.price},
            'section': {'S': str(listing.section)},
            'row': {'S': str(listing.row)},
            'seat': {'S': str(listing.seat)},
            'bolt': {'BOOL': listing.bolt},
            'verified': {'BOOL': listing.verified},
            'time': {'S': str(listing.time)},
            'action': {'S': str(listing.action)}
        }
        dyn_listings.append({
            'Put': {
                'TableName': 'ticket_listings',
                'Item': item
            }
        })
    return dyn_listings

def statuses_to_dyn(statuses):
    dyn_statuses = []
    for status in statuses:
        item = {
            'game_id': {'S': str(status.gameId)},
            'volume': {'N': str(status.volume)},
            'sold': {'N': str(status.sold)},
            'listed': {'N': str(status.listed)},
            'scrape_time': {'S': str(status.scrapeTime)}
        }
        dyn_statuses.append({
            'Put': {
                'TableName': 'game_statuses',
                'Item': item  
            }
        })
    return dyn_statuses

def games_to_dyn(games):
    dyn_games = []
    for game in games:
        item = {
            'game_id': {'S': str(game.gameId)},
            'team1': {'S': str(game.team1)},
            'team2': {'S': str(game.team2)},
            'date': {'S': str(game.date)},
            'sport': {'S': str(game.sport)}
        }
        dyn_games.append({
            'Put': {
                'TableName': 'games',
                'Item': item
            }
        })
    return dyn_games
