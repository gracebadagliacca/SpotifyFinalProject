import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util 
from json.decoder import JSONDecodeError 
import sqlite3
import matplotlib.pyplot as plt
#Get username from terminal (argv)
username = sys.argv[1] 
try: 
	token = util.prompt_for_user_token(username)
except: 
	os.remove(f".cache-{username}")
	token = util.prompt_for_user_token(username)

# username can be found on spotify profile 
# click the circle with three dots and choose 'Copy Profile Link'
# your username is the account name/numbers that come at the end of the url after 'user/'

spotifyObject = spotipy.Spotify(auth=token)

# BELOW CODES MUST BE ENTERED INTO TERMINAL STARTING WITH 'EXPORT' ENDING WITH '
# export SPOTIPY_CLIENT_ID='1e7296e18e1b419ebbf585e3488395e6'
# export SPOTIPY_CLIENT_SECRET='8f9e61000da54f6f9f6f23d571332c22'
# export SPOTIPY_REDIRECT_URI='https://google.com/'

user = spotifyObject.current_user()

#print(json.dumps(user, sort_keys = True, indent = 4))
displayName = user['display_name']
followers = user['followers']['total']
conn = sqlite3.connect('/Users/gracebadagliacca/FinalProject.db')
curr = conn.cursor()
# create a loop that continues until user wants to stop the program

while True:
	print()
	print('Hey, ' + displayName +'!')
	print('You have ' + str(followers) + ' followers! ')
	print()
	print()
	print('0 - Search for an artist')
	print('x - exit')
	print()
	choice = input('Your choice: ')
	if choice != '0' and choice != 'x':
		print()
		print('Please choose either option 0 or option x.')
	if choice == 'x': 
		break
	#search for the artist
	if choice == '0':
		print()
		searchQuery = input('Ok, what is the artist name?: ')
		print()
		#get search results (format = .search(query, limit, offset, type))
		# print json data in format that is readable 
		searchResults = spotifyObject.search(searchQuery,1,0,'artist')
		# print(json.dumps(searchResults, sort_keys = True, indent = 4))
		#ARTIST DETAILS 
		artist = searchResults['artists']['items'][0]
		artistName = artist['name']
		artistFollowers = artist['followers']['total']
		artistGenre = artist['genres'][0]
		artistPopularity = artist['popularity']
		print('Name: ' + artistName)
		print('Number of Followers: ' + str(artistFollowers))
		print('Music Genre: ' + artistGenre)
		print(artistName + ' has a popularity score of ' + str(artistPopularity))
		print()
		print()
		artistID = artist['id']
		trackURI = []
		trackArt = []
		z = 0 
		#get Album data 
		albumResults = spotifyObject.artist_albums(artistID)
		#goes to next level of results
		ExplicitDict = {'Explicit': 0, 'Not Explicit': 0}
		albumResults = albumResults['items']
		for result in albumResults:
			print('ALBUM ' + result['name'])
			albumID = result['id']
			trackResults = spotifyObject.album_tracks(albumID)
			trackResults = trackResults['items']
			# print(json.dumps(SEARCH QUERY, sort_keys = True, indent = 4)) will print the results of your API index
			for item in trackResults:
				trackName = item['name']
				trackExplicit = str(item['explicit'])
				z += 1
				print(str(z) + ': ' + trackName)

				isExplicit = 0 
				isNotExplicit = 0 
				if trackExplicit == 'True': 
					isExplicit += 1 
					print('This song is EXPLICIT.')
					print()
				else:
					isNotExplicit += 1 
					print('This song NOT EXPLICIT.')
					print()
				# The code below will create a new table for each artist that is input by a user
				curr.execute('''CREATE TABLE IF NOT EXISTS''' + ' ' + artistName.replace(' ', '') + ''' (ArtistName TEXT, SongName TEXT, SongExplicit TEXT)''') 
				conn.commit()
				curr.execute('''INSERT OR IGNORE INTO''' + ' ' + artistName.replace(' ', '') + '''(ArtistName, SongName, SongExplicit) VALUES (?,?,?)''', (artistName, trackName, trackExplicit))
				conn.commit()
			if trackExplicit == 'True':
				ExplicitDict['Explicit'] += 1
			else:
				ExplicitDict['Not Explicit'] += 1 
		Explicit = ExplicitDict.keys()
		num_songs = ExplicitDict.values()
		bar_graph = plt.bar(Explicit, num_songs)
		plt.title(artistName + ' Songs')
		plt.xlabel('Appropriateness')
		plt.ylabel('Number of Songs')
		plt.savefig(artistName + '.png') 	
		# the figure will show up in the same directory as this code, as (user inputartist's name).png
		# the artist's name will be the title		
		print()
		exit = input('Enter x to exit: ')
		# exit code to go about your day or re-run code to find data for new artist
		if exit == 'x':
			break 
	