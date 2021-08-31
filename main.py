# Author: Anthony George
# Date Completed: 5/21/2021
# Description: This program works with the Capstone.db database file and uses data retrieved from
# https://www.kaggle.com/yamaerenay/spotify-dataset-19212020-160k-tracks. This program allows the user to sign up with
# a username and password and then log in to the program. Once logged in, the user can create a playlist based off of a
# song. The program will generate a set amount of songs using song variables and weights to find songs with a similar
# "score" to the song the playlist was created from. Once the playlist is created the user can like songs, dislike
# songs and unlike/undislike songs which will update the algorithm that generates the songs in the playlist. The hope is
# that by updating the algorithm, a playlist the the user likes is generated. The program also keeps track of some of
# the data and allows the user to view charts and graphs using that data. The user can also delete playlist and connect
# to Spotify to play the songs from their playlists.

# imports, used for various functions and for connecting the screens developed in QT Designer to the application
import os
import random
import sqlite3
import pyqtgraph
from PyQt5 import QtWidgets  # import PyQt5 widgets
import main_menu
import login
import signup
import createplaylist
import datavisulaization
import Algorithm
import Song
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import ast

# This variable determines if a user is logged in. The value 0 is not a possible user id, so this is initialized with
# no user being logged in. It is updated when the user logs in and is used to access the user's playlists.
user_id = 0
# This variable keeps a list of the logged in user's playlist ids. When main screen is populated with playlists, this
# list is updated to keep track of the playlists
playlist_ids = []
# This variable keeps a list of songs that are in a selected playlist. It's updated when a playlist is selected on the
# main screen.
song_ids = []
# This variable keeps track of the user's liked songs. It's updated when a playlist is selected and when likes/unlikes
# are performed
liked_songs = []
# This variable keeps track of the user's disliked songs. It's updated when a playlist is selected and when
# dislikes/undislikes are performed
disliked_songs = []
# This variable keeps track of the ids of songs being displayed in the search list on the create playlists screen. It's
# used when a playlist is created to identify which song is the basis of the playlist.
search_ids = []
# The number of songs that a playlist contains. This is left as 100 throughout the program, but I'd like to implement
# a feature that allows the user to choose the size of their playlist at some point, so this will make that easy
# to implement.
playlist_size = 100
# This variable is used to store the similarity score between songs for adjusting the algorithm on a like/dislike or
# unlike/undislike
song_weights = []
# 3 constants that I chose to multiply variable weights by for updating algorithms. When updating algorithms the top and
# bottom 3 variable weights are used, so I chose 3 constants to make the 1st of the 3 be weighted heaviest, 2nd weighted
# less than the 1st, and 3rd weighted the least.
scaling_constant_1 = 1
scaling_constant_2 = 0.5
scaling_constant_3 = 0.25
# the value of popularity is between 0 to 100 in the data. The variables it's compared to are between 0 and 1, so this
# is used to adjust the popularity to match that.
popularity_score_denominator = 100
# the value of tempo is generally between 30 to 250 in the data. The variables it's compared to are between 0 and 1, so
# this is used to adjust the tempo to match that.
tempo_score_denominator = 220
# the value of loudness is generally between 0 to -60 in the data. The variables it's compared to are between 0 and 1,
# so this is used to adjust the loudness to match that.
loudness_score_denominator = -60
# the base algorithm id is stored as 0 in the database, I chose to set it here as well in case it needs to be changed
# at any point
base_algorithm_id = 0


# Connects to the database and returns the connection
def database_connection():
    # create connection
    conn = None
    try:
        # change directory to be able to reach database
        working_dir = os.getcwd()
        os.chdir('DBMS/sqlite')
        # connect to database
        conn = sqlite3.connect('Capstone.db')
        # change directory back
        os.chdir(working_dir)

    # no sql errors should occur, so this shouldn't run, it's mostly here for testing
    except (Exception, sqlite3.DatabaseError) as error:
        print(error)
    # if the connection was created, it's returned
    finally:
        if conn is not None:
            return conn


# Activates when the user presses the exit button on any of the screens.
# Exits the application and stops the program from running.
def exit_program():
    sys.exit()


# Opens the login window, activated from main
def display_login():
    app = QtWidgets.QApplication(sys.argv)
    LoginWindow = QtWidgets.QDialog()
    ui = login.Ui_Dialog()
    ui.setupUi(LoginWindow)
    LoginWindow.show()

    # Run the program
    sys.exit(app.exec_())


# Activates when the user presses the login button on the login screen.
# Checks if the username and password match in the database, and then sets the user_id and redirects the user
# to the main menu
def login_button(self, Dialog):
    # gets the username and password from the text fields
    username = self.usernameLine.text()
    password = self.passwordLine.text()
    # sets a variable to false for later use
    successful_login = False
    # initializes the a message box and sets the title to "Error" and the text to "Invalid username or password"
    # since all errors will fall under that
    MessageBox = QtWidgets.QMessageBox()
    MessageBox.setWindowTitle('Error')
    MessageBox.setText('Invalid username or password.')
    # if there is a space in the username or password, the message box displays the message set above notifying
    # the user that the username or password is incorrect. This is mostly to try to prevent any SQL injections.
    if ' ' in username or ' ' in password:
        MessageBox.exec_()
    # if the username or password are blank, the message box displays the message set above notifying
    # the user that the username or password is incorrect.
    elif '' == username or '' == password:
        MessageBox.exec_()
    # otherwise, the credentials can be checked with the database
    else:
        # connect to database
        conn = database_connection()
        # create cursor to execute sql statement
        cur = conn.cursor()
        # this section runs a select statement that will return a row containing the user_id if the username and
        # password are a match
        try:
            # create select statement
            select = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "';"
            # execute select statement
            user = cur.execute(select)
            # since the username is unique, there will only by at most one row, so the result is stored to a variable
            user = user.fetchone()
            # if the user isn't none, then the username and password matched in the database, so the user can login
            if user is not None:
                # the global variable user_id is set to the user's id, logging the user in
                global user_id
                user_id = user[0]
                # successful login set to true for finally
                successful_login = True
        # no sql errors should occur, so this shouldn't run, it's mostly here for testing
        except sqlite3.DatabaseError as error:
            print(error)
        finally:
            # if successful_login was set to true, then the credentials matched, so the database connection is closed
            # and the user is sent to the main screen
            if successful_login:
                conn.close()
                # runs the function that will close the login screen and open the main screen
                open_main_screen(self, Dialog)
            # otherwise, the successful_login was never updated, meaning there were no rows returned from the sql
            # statement, so the message box displays the message set above notifying the user that the username
            # or password is incorrect and the database connection is closed
            else:
                MessageBox.exec_()
                conn.close()


# Activates when the user presses the sign up button on the login screen.
# Opens the sign up window where the user can create a username and password to login to the program.
def open_sign_up(self, Dialog):
    Dialog.hide()
    self.SignUpWindow = QtWidgets.QDialog()
    self.ui = signup.Ui_Dialog()
    self.ui.setupUi(self.SignUpWindow)
    self.SignUpWindow.show()


# Activates when user presses the Sign Up button.
# Checks if username and password are valid, then attempts to add them to the database, notifying the user if
# the username already exists in the database. After creating the user, the program redirects the user to
# the login screen.
def sign_up(self, Dialog):
    # gets the username and password from the text fields
    username = self.usernameLine.text()
    password = self.passwordLine.text()
    # sets a variable to false for later use
    created = False
    # initializes the a message box and sets the title to "Error"
    MessageBox = QtWidgets.QMessageBox()
    MessageBox.setWindowTitle('Error')
    # if the username is blank, the message box displays a message notifying the user no username was entered.
    if '' == username:
        MessageBox.setText('No username entered.')
        MessageBox.exec_()
    # if there is a space in the username, the message box displays a message notifying the user that the username
    # cannot contain spaces. This is mostly to try to prevent any SQL injections.
    elif ' ' in username:
        MessageBox.setText('Username cannot contain spaces.')
        MessageBox.exec_()
    # if the password is blank, the message box displays a message notifying the user no password was entered.
    elif '' == password:
        MessageBox.setText('No password entered.')
        MessageBox.exec_()
    # if there is a space in the password, the message box displays a message notifying the user that the password
    # cannot contain spaces. This is mostly to prevent any SQL injections.
    elif ' ' in password:
        MessageBox.setText('Password cannot contain spaces.')
        MessageBox.exec_()
    # if the password and confirm passwords don't match, then the message box displays a message notifying the user
    # that the passwords don't match.
    elif password != self.passwordLine_2.text():
        MessageBox.setText('Passwords do not match.')
        MessageBox.exec_()
    # if none of the above statements are true, then the user can be created
    else:
        # connect to database
        conn = database_connection()
        # create cursor to execute sql statement
        cur = conn.cursor()
        # this section tries to insert the username and password into the users table, catching any errors that may
        # occur. The only error that should occur is when the username already exists (the username is set to be unique
        # in the database), so if an error occurs the message box displays a message notifying the user that the
        # username is taken.
        try:
            # create insert statement
            insert = "INSERT INTO users(username, password) VALUES ('" + username + "', '" + password + "');"
            # execute insert statement
            cur.execute(insert)
            # commit changes
            conn.commit()
            # set created to true for finally
            created = True
        # error occurs if username is taken
        except sqlite3.DatabaseError:
            MessageBox.setText('Username is taken.')
            MessageBox.exec_()
        finally:
            # if created was set to true, then the user was successfully created, so the program will notify the user
            # that their user was created and will then return them to the login screen where they can login.
            if created:
                conn.close()
                MessageBox.setWindowTitle('User created')
                MessageBox.setText('User successfully created, returning to login screen.')
                MessageBox.exec_()
                # cancel sign up hides the sign up screen and opens the login screen, so that can just be called
                # instead of remaking it.
                cancel_sign_up(self, Dialog)
            # if created is still false then there was an error, so the program will remain on the sign up screen.
            else:
                conn.close()


# Activates when the user presses the cancel button on the sign up screen. It hides the sign up screen then opens
# the login screen.
def cancel_sign_up(self, Dialog):
    Dialog.hide()
    self.LoginWindow = QtWidgets.QDialog()
    self.ui = login.Ui_Dialog()
    self.ui.setupUi(self.LoginWindow)
    self.LoginWindow.show()


# Activates when the user presses the login button and their credentials match in the database.
# Closes the login screen and opens the main screen, filling in the user's playlists
def open_main_screen(self, Dialog):
    Dialog.hide()
    self.MainWindow = QtWidgets.QMainWindow()
    self.ui = main_menu.Ui_MainWindow()
    self.ui.setupUi(self.MainWindow)

    # calls the method that retrieves the user's playlists and adds them to a list that is displayed on the main screen
    display_playlists(self.ui)

    # the main screen is then displayed
    self.MainWindow.show()


# Activates when the main screen is opened, after a playlist has been created and after a playlist has been deleted.
# Adds all of a user's playlists to a list that is displayed on the main screen.
def display_playlists(self):
    # first it clears the playlists that are being shown on the main screen
    self.playlistList.clear()
    # Variable to be used at the end of this segment is set to false
    playlists_exist = False
    # connect to database
    conn = database_connection()
    # create cursor to execute sql statement
    cur = conn.cursor()
    # this section runs a select statement that obtains all playlists with the user's id and displays them on the
    # playlist list on the main screen
    try:
        # obtains the user_id which is set by the login_button() method
        global user_id
        # create select statement
        select = "SELECT * FROM algorithms WHERE user_id = '" + str(user_id) + "';"
        # execute select statement and save the results to a variable called playlists
        playlists = cur.execute(select).fetchall()
        # if the user hasn't made a playlist yet, then playlists will be an empty list, so this section will be skipped
        if len(playlists) != 0:
            # if the user does have any playlists, then the playlists_exist variable is set to true and this segment of
            # code is ran
            playlists_exist = True
            # a count is made to number the playlists on the main screen
            count = 1
            # for every playlist in the list of playlists a string is created to be displayed on the main screen.
            # the playlist ids are also stored in the global list playlist_ids, so the playlists can be accessed
            global playlist_ids
            playlist_ids = []
            for playlist in playlists:
                playlist_ids.append(playlist[0])
                # runs a select statement to obtain song name and artist information
                select = "SELECT * FROM songs WHERE song_id = '" + playlist[1] + "';"
                # since song_id is a primary key, only one result will be obtained
                song = cur.execute(select).fetchone()
                # the artists are saved in the database in the form of '['artist1', 'artist2']', so a literal evaluation
                # will convert that into a list
                artists = ast.literal_eval(song[2])
                # a string is initialized that will store all artist names
                artists_string = ''
                # another count is created for proper punctuation in the string
                count2 = 1
                # a for loop is ran for each artist in the list of artists
                for artist in artists:
                    # the first entry is added without any punctuation
                    if count2 == 1:
                        artists_string += artist
                        count2 += 1
                    # all other entries but the last are added with a comma and a space beforehand
                    elif count2 != len(artists):
                        artists_string += ', ' + artist
                        count2 += 1
                    # the last entry is added with a comma and an ampersand
                    else:
                        artists_string += ', & ' + artist
                # the string is completed and will look like "Playlist 1: track by artist1, artist2, & artist3"
                playlist_name = "Playlist " + str(count) + ": " + song[1] + " by " + artists_string
                # the string is added to the playlist list on the main screen
                self.playlistList.addItem(playlist_name)
                count += 1
    # no sql errors should occur, so this shouldn't run, it's mostly here for testing
    except sqlite3.DatabaseError as error:
        print(error)
    # the database connection is closed
    finally:
        conn.close()

    # if the user has any playlists, then the first playlist is selected and the function that runs when a playlist is
    # selected by the user is also executed to populate the songs list.
    if playlists_exist:
        self.playlistList.setCurrentRow(0)
        display_songs(self)


# Activates when the user selects a playlist on the playlist list on the main screen
# This method uses a selected playlist on the playlist list and retrieves and displays songs correlated to that playlist
# on the songs list.
# Since this method looks at all of the songs in the database (over 500,000 currently), I tried a few ways to get
# the quickest response since some queries could take up to a minute. This is the quickest method I was able to find.
# (Currently takes around 1 second to complete).
def display_songs(self):
    # checks the songs radio button (the only time it would be unchecked is if the user is viewing their liked songs
    # and switches playlists, so this just makes sure the correct radio is selected in that case)
    self.songsRadio.setChecked(True)
    # the songs list is first cleared, otherwise the songs just get added to the end of the list
    self.songsList.clear()
    # connect to database
    conn = database_connection()
    # create cursor to execute sql statement
    cur = conn.cursor()
    try:
        # uses the global variable playlist_ids which contain the user's playlist ids and the selected playlist on the
        # playlist list to retrieve the proper playlist id (algorithm_id since they're algorithms in the database)
        global playlist_ids
        algorithm_id = playlist_ids[self.playlistList.currentRow()]
        # this select statement returns the algorithm that the playlist is derived from
        select = "SELECT * FROM algorithms WHERE algorithm_id = " + str(algorithm_id) + ";"
        # since the algorithm_id is unique, there will only by at most one row, so the result is stored to a
        # variable
        algorithm = cur.execute(select).fetchone()
        # if an algorithm was found, otherwise there's no need for the rest of this to run
        if algorithm is not None:
            # an algorithm object is created, so the below select statements are easier to read/edit
            a = Algorithm.Algorithm(algorithm[0], algorithm[1], algorithm[2], algorithm[3], algorithm[4],
                                    algorithm[5], algorithm[6], algorithm[7], algorithm[8], algorithm[9],
                                    algorithm[10], algorithm[11], algorithm[12], algorithm[13])
            # this select statement returns all of the liked/disliked songs for the selected playlist
            select = "SELECT sr.song_id, s.name, s.artists, sr.rating FROM song_ratings as sr INNER JOIN songs as s " \
                     "ON s.song_id = sr.song_id WHERE algorithm_id = " + str(algorithm_id) + ";"
            # run the statement and save results to a variable
            rated_songs = cur.execute(select).fetchall()
            # the global variable liked_songs is retrieved and emptied
            global liked_songs
            liked_songs = []
            # the global variable disliked_songs is retrieved and emptied
            global disliked_songs
            disliked_songs = []
            # the global variable song_multiplier is retrieved for use below
            global playlist_size
            # a new variable is set to the playlist_size
            updated_playlist_size = playlist_size
            # this loop iterates through each song in the rated songs list retrieved from the previous select statement
            for song in rated_songs:
                # song[3] is either 1 or 0, 1 for like, 0 for dislike, so if it's liked it's added to the liked_songs
                # list, and if it's disliked, it's added to the disliked_songs list.
                # the variable updated_playlist_size is also reduced by 1 since all of the liked songs will be included
                # in the list of songs.
                if song[3]:
                    liked_songs.append(song)
                    updated_playlist_size -= 1
                else:
                    disliked_songs.append(song)
            # retrieves the global variables that are used to scale the popularity, tempo, and loudness scores so they
            # align with the other score (other variables range from 0-1, this effectively changes these 3 variables to
            # that range)
            global popularity_score_denominator, tempo_score_denominator, loudness_score_denominator
            # This select statement is used to retrieve the score of the song the algorithm is based on using the
            # selected playlist's (or algorithm's) weights
            select = "SELECT((" \
                     + str(a.get_popularity_score()/popularity_score_denominator) + "*popularity)+(" \
                     + str(a.get_tempo_score()/tempo_score_denominator) + "*tempo)+(" \
                     + str(a.get_acousticness_score()) + "*acousticness)+(" \
                     + str(a.get_danceability_score()) + "*danceability)+(" \
                     + str(a.get_energy_score()) + "*energy)+(" \
                     + str(a.get_instrumentalness_score()) + "*instrumentalness)+(" \
                     + str(a.get_liveness_score()) + "*liveness)+(" \
                     + str(a.get_loudness_score()/loudness_score_denominator) + "*loudness)+(" \
                     + str(a.get_speechiness_score()) + "*speechiness)+(" \
                     + str(a.get_valence_score()) + "*valence)) as score\n" \
                     "FROM songs " \
                     "WHERE song_id = '" + a.get_song_id() + "';"
            # since song_ids are unique, only one row will be returned, and the score is then retrieved from that row
            song_score = cur.execute(select).fetchone()[0]
            # a string containing all of the liked songs_ids is created
            # the string looks like: "'song_id1', 'song_id2', 'song_id3'"
            liked_song_ids = ''
            count = 1
            for song in liked_songs:
                if count != len(liked_songs):
                    liked_song_ids += "'" + song[0] + "', "
                    count += 1
                else:
                    liked_song_ids += "'" + song[0] + "'"
            # a string containing all of the disliked songs_ids is created
            # it will be added onto the liked_song_ids from above, so the format is different
            # the string looks like: ", 'song_id4', 'song_id5', 'song_id6'"
            disliked_song_ids = ''
            for song in disliked_songs:
                disliked_song_ids += ", '" + song[0] + "'"
            # This select statement uses a subquery to retrieve the songs in the playlist.
            #
            # The SCORED_SONGS subquery is used to give each song a score using variables from the algorithm. The where
            # statement selects all non-explicit songs then uses the algorithm's explicit to include explicit songs if
            # it's set to true (1), or continue to just use non-explicit songs if set to false (0).
            #
            # The main query takes all of the scores and orders them by the absolute value of the score -
            # the score retrieved from the song the algorithm is derived from. A where statement is also used here to
            # exclude any liked or disliked songs since liked songs will be added later on, and disliked songs shouldn't
            # be in the playlist. This subquery then limits the songs to a number equal to the remaining size of the
            # playlist (using updated_playlist_size).
            select = "WITH SCORED_SONGS AS(\n" \
                     + "  SELECT song_id, name, artists, explicit, ((" \
                     + str(a.get_popularity_score()/popularity_score_denominator) + "*popularity)+(" \
                     + str(a.get_tempo_score()/tempo_score_denominator) + "*tempo)+(" \
                     + str(a.get_acousticness_score()) + "*acousticness)+(" \
                     + str(a.get_danceability_score()) + "*danceability)+(" \
                     + str(a.get_energy_score()) + "*energy)+(" \
                     + str(a.get_instrumentalness_score()) + "*instrumentalness)+(" \
                     + str(a.get_liveness_score()) + "*liveness)+(" \
                     + str(a.get_loudness_score()/loudness_score_denominator) + "*loudness)+(" \
                     + str(a.get_speechiness_score()) + "*speechiness)+(" \
                     + str(a.get_valence_score()) + "*valence)) as score\n" \
                     + "  FROM songs \n" \
                     + "  WHERE explicit = 0 OR explicit = " + str(a.get_explicit()) + ") \n" \
                     + "SELECT * \n" \
                     + "FROM SCORED_SONGS \n" \
                     + "WHERE song_id NOT IN (" + liked_song_ids + disliked_song_ids + ")"\
                     + "ORDER BY Abs(score - " + str(song_score) + ") \n" \
                     + "LIMIT " + str(updated_playlist_size) + ";"
            # the select statement is executed and the results are saved to a variable
            playlist = cur.execute(select).fetchall()
            # all liked songs are appended to the newly created playlist.
            for song in liked_songs:
                playlist.append(song)
            # the playlist is then sorted into alphabetical order by song name, ignoring case.
            playlist = sorted(playlist, key=lambda x: x[1].casefold())
            # The global variable that will contain the song_ids is retrieved and emptied
            global song_ids
            song_ids = []
            # a count is started for numbering songs on the songs list
            count = 1
            # for every song in the playlist a string is created to be displayed on the main screen
            # the song ids are also stored in the global list playlist_ids, so the songs can be played on Spotify
            for song in playlist:
                song_ids.append([song[0], song[1], song[2]])
                # the artists are saved in the database in the form of '['artist1', 'artist2']', so a literal evaluation
                # will convert that into a list
                artists = ast.literal_eval(song[2])
                # a string is initialized that will store all artist names
                artists_string = ''
                # another count is created for proper punctuation in the string
                count2 = 1
                # a for loop is ran for each artist in the list of artists
                for artist in artists:
                    # the first entry is added without any punctuation
                    if count2 == 1:
                        artists_string += artist
                        count2 += 1
                    # all other entries but the last are added with a comma and a space beforehand
                    elif count2 != len(artists):
                        artists_string += ', ' + artist
                        count2 += 1
                    # the last entry is added with a comma and an ampersand
                    else:
                        artists_string += ', & ' + artist
                # the string is completed and will look like "1. track by artist1, artist2, & artist3"
                song_name = str(count) + ". " + song[1] + " by " + artists_string
                # the string is added to the songs list on the main screen
                self.songsList.addItem(song_name)
                count += 1
            # selects the first item in the song list
            self.songsList.setCurrentRow(0)
    # no sql errors should occur, so this shouldn't run, it's mostly here for testing
    except sqlite3.DatabaseError as error:
        print(error)
    finally:
        # the database connection is then closed
        conn.close()


# Activates when the user presses the liked songs radio button.
# Displays all of the user's liked songs for the selected playlist
def liked_songs_list(self):
    # the songs list is first cleared, otherwise the songs just get added to the end of the list
    self.songsList.clear()
    # the global variable liked_songs is retrieved, this list contains all of the liked songs, so all liked songs can
    # be displayed using this list.
    global liked_songs
    liked_songs = sorted(liked_songs, key=lambda x: x[1].casefold())
    # a count is started for numbering songs on the songs list
    count = 1
    # for every song in the liked songs list a string is created to be displayed on the main screen
    for song in liked_songs:
        # the artists are saved in the database in the form of '['artist1', 'artist2']', so a literal evaluation
        # will convert that into a list
        artists = ast.literal_eval(song[2])
        # a string is initialized that will store all artist names
        artists_string = ''
        # another count is created for proper punctuation in the string
        count2 = 1
        # a for loop is ran for each artist in the list of artists
        for artist in artists:
            # the first entry is added without any punctuation
            if count2 == 1:
                artists_string += artist
                count2 += 1
            # all other entries but the last are added with a comma and a space beforehand
            elif count2 != len(artists):
                artists_string += ', ' + artist
                count2 += 1
            # the last entry is added with a comma and an ampersand
            else:
                artists_string += ', & ' + artist
        # the string is completed and will look like "1. track by artist1, artist2, & artist3"
        song_name = str(count) + ". " + song[1] + " by " + artists_string
        # the string is added to the songs list on the main screen
        self.songsList.addItem(song_name)
        count += 1
    # selects the first item in the song list
    self.songsList.setCurrentRow(0)


# Activates when the user presses the disliked songs radio button.
# Displays all of the user's disliked songs for the selected playlist
def disliked_songs_list(self):
    # the songs list is first cleared, otherwise the songs just get added to the end of the list
    self.songsList.clear()
    # the global variable disliked_songs is retrieved, this list contains all of the disliked songs, so all disliked
    # songs can be displayed using this list.
    global disliked_songs
    disliked_songs = sorted(disliked_songs, key=lambda x: x[1].casefold())
    # a count is started for numbering songs on the songs list
    count = 1
    # for every song in the disliked songs list a string is created to be displayed on the main screen
    for song in disliked_songs:
        # the artists are saved in the database in the form of '['artist1', 'artist2']', so a literal evaluation
        # will convert that into a list
        artists = ast.literal_eval(song[2])
        # a string is initialized that will store all artist names
        artists_string = ''
        # another count is created for proper punctuation in the string
        count2 = 1
        # a for loop is ran for each artist in the list of artists
        for artist in artists:
            # the first entry is added without any punctuation
            if count2 == 1:
                artists_string += artist
                count2 += 1
            # all other entries but the last are added with a comma and a space beforehand
            elif count2 != len(artists):
                artists_string += ', ' + artist
                count2 += 1
            # the last entry is added with a comma and an ampersand
            else:
                artists_string += ', & ' + artist
        # the string is completed and will look like "1. track by artist1, artist2, & artist3"
        song_name = str(count) + ". " + song[1] + " by " + artists_string
        # the string is added to the songs list on the main screen
        self.songsList.addItem(song_name)
        count += 1
    # selects the first item in the song list
    self.songsList.setCurrentRow(0)


# Activates when the user presses the Like Song button on the main screen
# Checks which list the user is viewing (all songs, liked songs, disliked songs), then runs like_song using the proper
# list (so the proper song_id can be used)
def like_song_get_list(self):
    if self.songsRadio.isChecked():
        global song_ids
        like_song(self, song_ids)
    elif self.likedRadio.isChecked():
        global liked_songs
        like_song(self, liked_songs)
    elif self.dislikedRadio.isChecked():
        global disliked_songs
        like_song(self, disliked_songs)


# adds a song as liked for the selected playlist and then updates the algorithm weights based off of the 3 most similar
# variables in the liked song compared to the base song
def like_song(self, song_list):
    # if there's any songs in the list that was sent
    if len(song_list) != 0:
        # retrieves the selected song's information and song id from the selected song (selected_song_info is used to
        # update the dislikes list if needed for accurate representation of disliked songs)
        selected_song_info = song_list[self.songsList.currentRow()]
        selected_song = selected_song_info[0]
        # retrieves the global variable playlist_ids, then sets the playlist id to the proper variable
        global playlist_ids
        selected_playlist = playlist_ids[self.playlistList.currentRow()]
        # connect to database
        conn = database_connection()
        # create cursor to execute sql statement
        cur = conn.cursor()
        # Performs a select statement to confirm if the selected song has already been liked/disliked, switching the
        # dislike to a like if it has been disliked, and doing nothing if it has been liked. Then performs an insert
        # statement that adds the song as a liked song for the selected playlist. After that, performs an update
        # statement that adjusts the base algorithm and current playlist algorithm using variable weights.
        try:
            # select statement that retrieves any liked/disliked songs matching the playlist id and song id
            select = "SELECT * FROM song_ratings WHERE algorithm_id = " + str(selected_playlist) + " AND song_id = '" \
                     + selected_song + "';"
            # algorithm_id + song_id is unique, so only one result will be returned at most, that result is then stored
            song_rated = cur.execute(select).fetchone()
            # if data was returned
            # otherwise the song hasn't been rated, so the program can continue
            if song_rated is not None:
                # if the data that was returned is a dislike, undo the dislike
                # no else is needed here, since otherwise the song is already liked, so I just let the program try to
                # insert the song, which will result in an error that will be caught and the program will continue
                # running
                if song_rated[2] == 0:
                    unlike_undislike_song(self, song_list)
            # Selects the highest value of rating count for the selected playlist (keeps track of which rating this is
            # for use with data visualization)
            select = "SELECT max(rating_count) FROM song_ratings WHERE algorithm_id = " + str(
                selected_playlist) + ";"
            rating_count = cur.execute(select).fetchone()[0]
            # insert statement that saves the song as a liked song for the playlist
            insert = "INSERT INTO song_ratings VALUES (" + str(selected_playlist) + ", '" + selected_song + "', 1, " \
                     + str(rating_count + 1) + ");"
            cur.execute(insert)
            # a function that stores variable weight comparison to the global variable song_weights is ran
            get_weights(cur, selected_playlist, selected_song)
            # these global variables are retrieved to be used in the update statement below
            global song_weights, base_algorithm_id, scaling_constant_1, scaling_constant_2, scaling_constant_3
            # Update statement that updates the variable weights using the top 3 and bottom 3 variables obtained from
            # comparing the variable weights between the selected song and the playlist's base song. The top 3 weights
            # are multiplied by constants and then added to the current, respective weights. The bottom 3 weights are
            # multiplied by the same constants and -1 so they are subtracted from their current, respective weights.
            update = "UPDATE algorithms SET " \
                     + song_weights[9][0] + " = " + song_weights[9][0] + "+" \
                     + str(scaling_constant_1 * song_weights[9][1]) + ", " \
                     + song_weights[8][0] + " = " + song_weights[8][0] + "+" \
                     + str(scaling_constant_2 * song_weights[8][1]) + ", " \
                     + song_weights[7][0] + " = " + song_weights[7][0] + "+" \
                     + str(scaling_constant_3 * song_weights[7][1]) + ", " \
                     + song_weights[2][0] + " = " + song_weights[2][0] + "+" \
                     + str(scaling_constant_3 * -1 * song_weights[2][1]) + ", " \
                     + song_weights[1][0] + " = " + song_weights[1][0] + "+" \
                     + str(scaling_constant_2 * -1 * song_weights[1][1]) + ", " \
                     + song_weights[0][0] + " = " + song_weights[0][0] + "+" \
                     + str(scaling_constant_1 * -1 * song_weights[0][1]) \
                     + " WHERE algorithm_id IN (" + str(base_algorithm_id) + ", " + str(selected_playlist) + ");"
            cur.execute(update)
            # Update statement that increases the like count for the 3 variables that are adjusted in the algorithm.
            # This updates both the selected playlist's data and the base algorithm's. Used for seeing how variables
            # contribute to likes.
            update = "UPDATE algorithm_variable_updates SET " \
                     + song_weights[9][0] + " = " + song_weights[9][0] + "+1, " \
                     + song_weights[8][0] + " = " + song_weights[8][0] + "+1," \
                     + song_weights[7][0] + " = " + song_weights[7][0] + "+1" \
                     + " WHERE algorithm_id IN (" + str(base_algorithm_id) + ", " + str(selected_playlist) + ")" \
                     + " AND like_dislike = 1;"
            cur.execute(update)
            # checks that both the base and selected playlist algorithms don't have score below 0. If scores go
            # below 0 then the variables will technically get weighed more since the size of the integer is the
            # weight, and sign doesn't matter.
            scores_above_0(cur, selected_playlist)
            conn.commit()
        # this will run if the user tries to like a song that has already been liked, but I see no reason to inform the
        # user of this error, so I just printed it, mostly for testing
        except sqlite3.DatabaseError as error:
            print(error)
        # close connection and display songs using updated algorithm weights
        finally:
            conn.close()
            # if the songs radio button is selected, run display_songs. if the disliked songs radio button is selected
            # remove the selected song from disliked songs and run disliked_songs_list.
            if self.songsRadio.isChecked():
                display_songs(self)
            elif self.dislikedRadio.isChecked():
                global liked_songs
                liked_songs.append(selected_song_info)
                disliked_songs_list(self)


# Activates when the user presses the Disike Song button on the main screen
# Checks which list the user is viewing (all songs, liked songs, disliked songs), then runs dislike_song using the
# proper list (so the proper song_id can be used)
def dislike_song_get_list(self):
    if self.songsRadio.isChecked():
        global song_ids
        dislike_song(self, song_ids)
    elif self.likedRadio.isChecked():
        global liked_songs
        dislike_song(self, liked_songs)
    elif self.dislikedRadio.isChecked():
        global disliked_songs
        dislike_song(self, disliked_songs)


# adds a song as disliked for the selected playlist and then updates the algorithm weights based off of the 3 most
# similar variables in the disliked song compared to the base song
def dislike_song(self, song_list):
    # if there's any songs in the list that was sent
    if len(song_list) != 0:
        # retrieves the selected song's information and song id from the selected song (selected_song_info is used to
        # update the likes list if needed for accurate representation of liked songs)
        selected_song_info = song_list[self.songsList.currentRow()]
        selected_song = selected_song_info[0]
        # retrieves the global variable playlist_ids, then sets the playlist id to the proper variable
        global playlist_ids
        selected_playlist = playlist_ids[self.playlistList.currentRow()]
        # connect to database
        conn = database_connection()
        # create cursor to execute sql statement
        cur = conn.cursor()
        # Performs a select statement to confirm if the selected song has already been liked/disliked, switching the
        # like to a dislike if it has been liked, and doing nothing if it has been disliked. Then performs an insert
        # statement that adds the song as a disliked song for the selected playlist. After that, performs an update
        # statement that adjusts the base algorithm and current playlist algorithm using variable weights.
        try:
            # select statement that retrieves any liked/disliked songs matching the playlist id and song id
            select = "SELECT * FROM song_ratings WHERE algorithm_id = " + str(selected_playlist) + " AND song_id = '" \
                     + selected_song + "';"
            # algorithm_id + song_id is unique, so only one result will be returned at most, that result is then stored
            song_rated = cur.execute(select).fetchone()
            # if data was returned
            # otherwise the song hasn't been rated, so the program can continue
            if song_rated is not None:
                # if the data that was returned is a like, undo the like
                # no else is needed here, since otherwise the song is already disliked, so I just let the program try to
                # insert the song, which will result in an error that will be caught and the program will continue
                # running
                if song_rated[2] == 1:
                    unlike_undislike_song(self, song_list)
            # Selects the highest value of rating count for the selected playlist (keeps track of which rating this is
            # for use with data visualization)
            select = "SELECT max(rating_count) FROM song_ratings WHERE algorithm_id = " + str(selected_playlist) + ";"
            rating_count = cur.execute(select).fetchone()[0]
            # insert statement that saves the song as a disliked song for the playlist
            insert = "INSERT INTO song_ratings VALUES (" + str(selected_playlist) + ", '" + selected_song + "', 0, " \
                     + str(rating_count+1) + ");"
            cur.execute(insert)
            # a function that stores variable weight comparison to the global variable song_weights is ran
            get_weights(cur, selected_playlist, selected_song)
            # these global variables are retrieved to be used in the update statement below
            global song_weights, base_algorithm_id, scaling_constant_1, scaling_constant_2, scaling_constant_3
            # Update statement that updates the variable weights using the top 3 and bottom 3 variables obtained from
            # comparing the variable weights between the selected song and the playlist's base song. The top 3 weights
            # are multiplied by constants and -1 so they are subtracted from their current, respective weights. The
            # bottom 3 weights are multiplied by the same constants and then added to the current, respective weights.
            update = "UPDATE algorithms SET " \
                     + song_weights[9][0] + " = " + song_weights[9][0] + "+" \
                     + str(scaling_constant_1 * -1 * song_weights[9][1]) + ", " \
                     + song_weights[8][0] + " = " + song_weights[8][0] + "+" \
                     + str(scaling_constant_2 * -1 * song_weights[8][1]) + ", " \
                     + song_weights[7][0] + " = " + song_weights[7][0] + "+" \
                     + str(scaling_constant_3 * -1 * song_weights[7][1]) + ", " \
                     + song_weights[2][0] + " = " + song_weights[2][0] + "+" \
                     + str(scaling_constant_3 * song_weights[2][1]) + ", " \
                     + song_weights[1][0] + " = " + song_weights[1][0] + "+" \
                     + str(scaling_constant_2 * song_weights[1][1]) + ", " \
                     + song_weights[0][0] + " = " + song_weights[0][0] + "+" \
                     + str(scaling_constant_1 * song_weights[0][1]) \
                     + " WHERE algorithm_id IN (" + str(base_algorithm_id) + ", " + str(selected_playlist) + ");"
            cur.execute(update)
            # save changes to database
            conn.commit()
            # Update statement that increases the dislike count for the 3 variables that are adjusted in the algorithm.
            # This updates both the selected playlist's data and the base algorithm's. Used for seeing how variables
            # contribute to dislikes.
            update = "UPDATE algorithm_variable_updates SET " \
                     + song_weights[9][0] + " = " + song_weights[9][0] + "+1, " \
                     + song_weights[8][0] + " = " + song_weights[8][0] + "+1," \
                     + song_weights[7][0] + " = " + song_weights[7][0] + "+1" \
                     + " WHERE algorithm_id IN (" + str(base_algorithm_id) + ", " + str(selected_playlist) + ")" \
                     + " AND like_dislike = 0;"
            cur.execute(update)
            # checks that both the base and selected playlist algorithms don't have score below 0. If scores go
            # below 0 then the variables will technically get weighed more since the size of the integer is the
            # weight, and sign doesn't matter.
            scores_above_0(cur, selected_playlist)
            conn.commit()
        # this will run if the user tries to dislike a song that has already been disliked, but I see no reason to
        # inform the user of this error, so I just printed it, mostly for testing
        except sqlite3.DatabaseError as error:
            print(error)
        # close connection and display songs using updated algorithm weights
        finally:
            conn.close()
            # if the songs radio button is selected, run display_songs. if the liked songs radio button is selected
            # remove the selected song from liked songs and run liked_songs_list.
            if self.songsRadio.isChecked():
                display_songs(self)
            elif self.likedRadio.isChecked():
                global disliked_songs
                disliked_songs.append(selected_song_info)
                liked_songs_list(self)


# Activates when the user presses the Unlike/Undislike Song button on the main screen
# Checks which list the user is viewing (all songs, liked songs, disliked songs), then runs unlike_dislike_song using
# the proper list (so the proper song_id can be used)
def unlike_undislike_song_get_list(self):
    if self.songsRadio.isChecked():
        global song_ids
        unlike_undislike_song(self, song_ids)
    elif self.likedRadio.isChecked():
        global liked_songs
        unlike_undislike_song(self, liked_songs)
    elif self.dislikedRadio.isChecked():
        global disliked_songs
        unlike_undislike_song(self, disliked_songs)


# Activates when the user presses the Unlike/Undislike Song button on the main screen.
# Also activates when a song that has been liked is disliked, or vice versa.
def unlike_undislike_song(self, song_list):
    # if there's any songs in the list that was sent
    if len(song_list) != 0:
        # retrieves the index and song id from the selected song
        selected_index = self.songsList.currentRow()
        selected_song = song_list[selected_index][0]
        # retrieves the global variable playlist_ids, then sets the playlist id to the proper variable
        global playlist_ids
        selected_playlist = playlist_ids[self.playlistList.currentRow()]
        # connect to database
        conn = database_connection()
        # create cursor to execute sql statement
        cur = conn.cursor()
        # Performs a select statement to confirm if the selected song has already been liked/disliked, switching the
        # like to a dislike if it has been liked, and doing nothing if it has been disliked. Then performs an insert
        # statement that adds the song as a disliked song for the selected playlist. After that, performs an update
        # statement that adjusts the base algorithm and current playlist algorithm using variable weights.
        try:
            # select statement that retrieves any liked/disliked songs matching the playlist id and song id
            select = "SELECT * FROM song_ratings WHERE algorithm_id = " + str(selected_playlist) + " AND song_id = '" \
                     + selected_song + "';"
            # algorithm_id + song_id is unique, so only one result will be returned at most, that result is then stored
            song_rated = cur.execute(select).fetchone()
            # if data was returned delete the song from the song_ratings table
            # otherwise the song hasn't been rated, so nothing needs to happen
            if song_rated is not None:
                # delete statement that removes the song from the song_ratings table, effectively getting rid of the
                # like/dislike
                delete = "DELETE FROM song_ratings WHERE algorithm_id = " + str(selected_playlist) \
                         + " AND song_id = '" + selected_song + "';"
                cur.execute(delete)
                # a function that stores variable weight comparison to the global variable song_weights is ran
                get_weights(cur, selected_playlist, selected_song)
                # these global variables are retrieved to be used in the update statement below
                global song_weights, base_algorithm_id, scaling_constant_1, scaling_constant_2, scaling_constant_3
                # if the data that was returned is a like, adjust the algorithm so the like is removed from the weight
                # else if the data that was returned is a dislike, adjust the algorithm so the dislike is removed from
                # the weight
                if song_rated[2] == 1:
                    # Update statement that updates the variable weights using the top 3 and bottom 3 variables obtained
                    # from comparing the variable weights between the selected song and the playlist's base song. The
                    # top 3 weights are multiplied by constants and -1 so they are subtracted from their current,
                    # respective weights. The bottom 3 weights are multiplied by the same constants and then added to
                    # the current, respective weights.
                    # Equivalent to "disliking" the song
                    update = "UPDATE algorithms SET " \
                             + song_weights[9][0] + " = " + song_weights[9][0] + "+" \
                             + str(scaling_constant_1 * -1 * song_weights[9][1]) + ", " \
                             + song_weights[8][0] + " = " + song_weights[8][0] + "+" \
                             + str(scaling_constant_2 * -1 * song_weights[8][1]) + ", " \
                             + song_weights[7][0] + " = " + song_weights[7][0] + "+" \
                             + str(scaling_constant_3 * -1 * song_weights[7][1]) + ", " \
                             + song_weights[2][0] + " = " + song_weights[2][0] + "+" \
                             + str(scaling_constant_3 * song_weights[2][1]) + ", " \
                             + song_weights[1][0] + " = " + song_weights[1][0] + "+" \
                             + str(scaling_constant_2 * song_weights[1][1]) + ", " \
                             + song_weights[0][0] + " = " + song_weights[0][0] + "+" \
                             + str(scaling_constant_1 * song_weights[0][1]) \
                             + " WHERE algorithm_id IN (" + str(base_algorithm_id) + ", " + str(selected_playlist) + \
                             ");"
                    cur.execute(update)
                    # save changes to database
                    conn.commit()
                    # Update statement that decreases the like count for the 3 variables that are adjusted in the
                    # algorithm. This updates both the selected playlist's data and the base algorithm's. Used for
                    # seeing how variables contribute to likes.
                    update = "UPDATE algorithm_variable_updates SET " \
                             + song_weights[9][0] + " = " + song_weights[9][0] + "-1, " \
                             + song_weights[8][0] + " = " + song_weights[8][0] + "-1," \
                             + song_weights[7][0] + " = " + song_weights[7][0] + "-1" \
                             + " WHERE algorithm_id IN (" + str(base_algorithm_id) + ", " + str(selected_playlist) \
                             + ") AND like_dislike = 1;"
                    cur.execute(update)
                    # checks that both the base and selected playlist algorithms don't have score below 0. If scores go
                    # below 0 then the variables will technically get weighed more since the size of the integer is the
                    # weight, and sign doesn't matter.
                    scores_above_0(cur, selected_playlist)
                    conn.commit()
                elif song_rated[2] == 0:
                    # Update statement that updates the variable weights using the top 3 and bottom 3 variables obtained
                    # from comparing the variable weights between the selected song and the playlist's base song. The
                    # top 3 weights are multiplied by constants and then added to the current, respective weights. The
                    # bottom 3 weights are multiplied by the same constants and -1 so they are subtracted from their
                    # current, respective weights.
                    # Equivalent to "liking" the song
                    update = "UPDATE algorithms SET " \
                             + song_weights[9][0] + " = " + song_weights[9][0] + "+" \
                             + str(scaling_constant_1 * song_weights[9][1]) + ", " \
                             + song_weights[8][0] + " = " + song_weights[8][0] + "+" \
                             + str(scaling_constant_2 * song_weights[8][1]) + ", " \
                             + song_weights[7][0] + " = " + song_weights[7][0] + "+" \
                             + str(scaling_constant_3 * song_weights[7][1]) + ", " \
                             + song_weights[2][0] + " = " + song_weights[2][0] + "+" \
                             + str(scaling_constant_3 * -1 * song_weights[2][1]) + ", " \
                             + song_weights[1][0] + " = " + song_weights[1][0] + "+" \
                             + str(scaling_constant_2 * -1 * song_weights[1][1]) + ", " \
                             + song_weights[0][0] + " = " + song_weights[0][0] + "+" \
                             + str(scaling_constant_1 * -1 * song_weights[0][1]) \
                             + " WHERE algorithm_id IN (" + str(base_algorithm_id) + ", " + str(selected_playlist) + \
                             ");"
                    cur.execute(update)
                    # save changes to database
                    conn.commit()
                    # Update statement that decreases the like count for the 3 variables that are adjusted in the
                    # algorithm. This updates both the selected playlist's data and the base algorithm's. Used for
                    # seeing how variables contribute to dislikes.
                    update = "UPDATE algorithm_variable_updates SET " \
                             + song_weights[9][0] + " = " + song_weights[9][0] + "-1, " \
                             + song_weights[8][0] + " = " + song_weights[8][0] + "-1," \
                             + song_weights[7][0] + " = " + song_weights[7][0] + "-1" \
                             + " WHERE algorithm_id IN (" + str(base_algorithm_id) + ", " + str(selected_playlist) \
                             + ") AND like_dislike = 0;"
                    cur.execute(update)
                    # checks that both the base and selected playlist algorithms don't have score below 0. If scores go
                    # below 0 then the variables will technically get weighed more since the size of the integer is the
                    # weight, and sign doesn't matter.
                    scores_above_0(cur, selected_playlist)
                    conn.commit()
        # this will run if the user tries to like a song that has already been liked, but I see no reason to inform the
        # user of this error, so I just printed it, mostly for testing
        except sqlite3.DatabaseError as error:
            print(error)
        # close connection and display songs using updated algorithm weights
        finally:
            conn.close()
            # if the songs radio button is selected, run display_songs. if the liked songs radio button is selected
            # remove the selected song from liked songs and run liked_songs_list. if the disliked songs radio button is
            # selected remove the selected song from disliked songs and run disliked_songs_list.
            if self.songsRadio.isChecked():
                display_songs(self)
            elif self.likedRadio.isChecked():
                global liked_songs
                liked_songs.pop(selected_index)
                liked_songs_list(self)
            elif self.dislikedRadio.isChecked():
                global disliked_songs
                disliked_songs.pop(selected_index)
                disliked_songs_list(self)


# Retrieves 2 songs from the database that will be compared and stores the weights in a sorted order.
# When this function is called, a database connection is already established, so the cursor is just passed in to avoid
# nested database connections.
def get_weights(cur, selected_playlist, selected_song):
    # select statement that retrieves the id of the song that the currently selected playlist is based on
    select = "SELECT song_id FROM algorithms WHERE algorithm_id = " + str(selected_playlist) + ";"
    # algorithm_id is unique, so only one song_id will be returned, and that song_id is saved to a variable
    base_song = cur.execute(select).fetchone()[0]
    # select statement retrieves all of the song information using the song_id retrieved from above
    select = "SELECT * FROM songs WHERE song_id = '" + base_song + "';"
    # song_id is unique, so only one song will be returned, and that song is saved to a variable
    s = cur.execute(select).fetchone()
    # base_song is overwritten as a Song object for improved readability of the code below.
    base_song = Song.Song(s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], s[10], s[11], s[12], s[13],
                          s[14], s[15], s[16], s[17], s[18], s[19])
    # similar to above, the selected song_id is used to retrieve the selected song's information and that song is also
    # stored to a variable in the form of a Song object for improved readability of the code
    select = "SELECT * FROM songs WHERE song_id = '" + selected_song + "';"
    s = cur.execute(select).fetchone()
    selected_song = Song.Song(s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], s[10], s[11], s[12],
                              s[13], s[14], s[15], s[16], s[17], s[18], s[19])
    # retrieves the global variables that are used to scale the popularity, tempo, and loudness scores so they
    # align with the other score (other variables range from 0-1, this effectively changes these 3 variables to
    # that range)
    global popularity_score_denominator, tempo_score_denominator, loudness_score_denominator
    # the song variables that are needed for the weight comparison are stored in lists
    base_song_variables = [base_song.get_popularity()/popularity_score_denominator,
                           base_song.get_tempo()/tempo_score_denominator, base_song.get_acousticness(),
                           base_song.get_danceability(), base_song.get_energy(), base_song.get_instrumentalness(),
                           base_song.get_liveness(), base_song.get_loudness()/loudness_score_denominator,
                           base_song.get_speechiness(), base_song.get_valence()]
    selected_song_variables = [selected_song.get_popularity()/popularity_score_denominator,
                               selected_song.get_tempo()/tempo_score_denominator, selected_song.get_acousticness(),
                               selected_song.get_danceability(), selected_song.get_energy(),
                               selected_song.get_instrumentalness(), selected_song.get_liveness(),
                               selected_song.get_loudness()/loudness_score_denominator, selected_song.get_speechiness(),
                               selected_song.get_valence()]
    # a list of strings containing the names of the columns that will be updated is also created, so the weight
    # comparisons have context for later use
    variables_list = ['popularity_score', 'tempo_score', 'acousticness_score', 'danceability_score', 'energy_score',
                      'instrumentalness_score', 'liveness_score', 'loudness_score', 'speechiness_score',
                      'valence_score']
    # the global variable song_weights is retrieved and emptied
    global song_weights
    song_weights = []
    # a count is set to 0 for counting indexes
    count = 0
    # for each variable in the base_song list of variables, the function weigh_song_variables is called, using the
    # equivalent variable from the selected_song variables and variable name from variable_list
    for variable in base_song_variables:
        weigh_song_variables(variable, selected_song_variables[count], variables_list[count])
        count += 1
    # once all of the weights have been calculated, the global list of song_weights is sorted by weight
    song_weights = sorted(song_weights, key=lambda x: x[1])


# Used with get_weights() to calculate the similarity between 2 weights.
# Adds a list in the form of ['variable_name', similarity_score] to the global variable song_weights
# This function takes a variable from base_song and a variable from selected_song as well a name for the variable
# and then retrieves a similarity number between 0 and 1 that is the evaluation of the variables. 0 means the two
# variables are very dissimilar and 1 means the two variables are similar.
# In order to calculate this, I decided to do largest variable/smallest variable, however, some variables can be very
# small (0.00001 for example), which could result in large numbers, so I decided to add 1 to each variable to solve
# this issue, giving me a much smaller range of results (almost always between 1 and 2). I then decided to
# subtract this result from 2, which gives me a number between 0 and 1.
# There is also a very small risk of a variable being -1, which could cause a divide by 0 error, so I just decided to
# check for that and add a small number that won't affect the outcome enough to be of significance if it does occur.
def weigh_song_variables(variable1, variable2, variable_name):
    global song_weights
    if variable1 >= variable2:
        if variable2 == -1:
            variable2 = variable2 + 0.001
        song_weights.append([variable_name, (2 - ((variable1 + 1) / (variable2 + 1)))])
    else:
        if variable1 == -1:
            variable1 = variable1 + 0.001
        song_weights.append([variable_name, (2 - ((variable2 + 1) / (variable1 + 1)))])


# Activates when the algorithms weights are updated by like_song, dislike_song, or unlike_undislike_song
# Checks if any of the weights are below 0 and sets them to 0 if they are. This is because the score for songs is
# calculated by adding all of the variable values * weights together. So the smaller the number added, the less impact
# a variable has. This means that a large negative number has a larger impact than a small negative number, and a weight
# of 0 means that variable has no effect. So, this will ensure that if any weights fall below 0, they just remain 0.
#
# Note that there is an issue caused from this function, however, it shouldn't occur often realistically.
# When a user likes/dislikes songs and weights are set to 0 using this function, if the user unlikes/undislikes
# songs, the weights will increase the same amount they would have dropped if the weights fell below 0. This means that
# unlikes and undislikes can potentially unbalance weights. However, when this program is used, likes and dislikes will
# be much more common than unlikes and undislikes, typically if a user rates a song they won't often change their
# rating. Also, weights start at scores of 100, and weights are adjusted by a number between 0 and 1 currently. This
# means that it takes over 100 ratings for a weight to reach 0, so this issue is unlikely to occur, and if it does, it
# won't happen often, and considering that many ratings will be needed to have this take effect, the impact this will
# have should be minimal.
def scores_above_0(cur, selected_playlist):
    # retrieves the global variable that keeps track of the base algorithm id
    global base_algorithm_id
    # selects the weights for the base algorithm
    select = "SELECT * FROM algorithms WHERE algorithm_id = " + str(base_algorithm_id) + ";"
    # algorithm_id is unique, so only one result is returned.
    results = cur.execute(select).fetchone()
    # for each weight, if it's below 0, set it to 0.
    if results[4] < 0:
        update = "UPDATE algorithms SET popularity_score = 0 WHERE algorithm_id = " + str(base_algorithm_id) + ";"
        cur.execute(update)
    if results[5] < 0:
        update = "UPDATE algorithms SET tempo_score = 0 WHERE algorithm_id = " + str(base_algorithm_id) + ";"
        cur.execute(update)
    if results[6] < 0:
        update = "UPDATE algorithms SET acousticness_score = 0 WHERE algorithm_id = " + str(base_algorithm_id) + ";"
        cur.execute(update)
    if results[7] < 0:
        update = "UPDATE algorithms SET danceability_score = 0 WHERE algorithm_id = " + str(base_algorithm_id) + ";"
        cur.execute(update)
    if results[8] < 0:
        update = "UPDATE algorithms SET energy_score = 0 WHERE algorithm_id = " + str(base_algorithm_id) + ";"
        cur.execute(update)
    if results[9] < 0:
        update = "UPDATE algorithms SET instrumentalness_score = 0 WHERE algorithm_id = " + str(base_algorithm_id) + ";"
        cur.execute(update)
    if results[10] < 0:
        update = "UPDATE algorithms SET liveness_score = 0 WHERE algorithm_id = " + str(base_algorithm_id) + ";"
        cur.execute(update)
    if results[11] < 0:
        update = "UPDATE algorithms SET loudness_score = 0 WHERE algorithm_id = " + str(base_algorithm_id) + ";"
        cur.execute(update)
    if results[12] < 0:
        update = "UPDATE algorithms SET speechiness_score = 0 WHERE algorithm_id = " + str(base_algorithm_id) + ";"
        cur.execute(update)
    if results[13] < 0:
        update = "UPDATE algorithms SET valence_score = 0 WHERE algorithm_id = " + str(base_algorithm_id) + ";"
        cur.execute(update)

    # same as above, just for the selected playlist
    select = "SELECT * FROM algorithms WHERE algorithm_id = " + str(selected_playlist) + ";"
    results = cur.execute(select).fetchone()
    if results[4] < 0:
        update = "UPDATE algorithms SET popularity_score = 0 WHERE algorithm_id = " + str(selected_playlist) + ";"
        cur.execute(update)
    if results[5] < 0:
        update = "UPDATE algorithms SET tempo_score = 0 WHERE algorithm_id = " + str(selected_playlist) + ";"
        cur.execute(update)
    if results[6] < 0:
        update = "UPDATE algorithms SET acousticness_score = 0 WHERE algorithm_id = " + str(selected_playlist) + ";"
        cur.execute(update)
    if results[7] < 0:
        update = "UPDATE algorithms SET danceability_score = 0 WHERE algorithm_id = " + str(selected_playlist) + ";"
        cur.execute(update)
    if results[8] < 0:
        update = "UPDATE algorithms SET energy_score = 0 WHERE algorithm_id = " + str(selected_playlist) + ";"
        cur.execute(update)
    if results[9] < 0:
        update = "UPDATE algorithms SET instrumentalness_score = 0 WHERE algorithm_id = " + str(selected_playlist) + ";"
        cur.execute(update)
    if results[10] < 0:
        update = "UPDATE algorithms SET liveness_score = 0 WHERE algorithm_id = " + str(selected_playlist) + ";"
        cur.execute(update)
    if results[11] < 0:
        update = "UPDATE algorithms SET loudness_score = 0 WHERE algorithm_id = " + str(selected_playlist) + ";"
        cur.execute(update)
    if results[12] < 0:
        update = "UPDATE algorithms SET speechiness_score = 0 WHERE algorithm_id = " + str(selected_playlist) + ";"
        cur.execute(update)
    if results[13] < 0:
        update = "UPDATE algorithms SET valence_score = 0 WHERE algorithm_id = " + str(selected_playlist) + ";"
        cur.execute(update)


# Activates when the user presses the delete playlist button on the main screen
# Confirm that the user wants to delete the selected playlist, and if they press yes, deletes the playlist from the
# database, and calls display_playlist to reflect the change.
def delete_playlist(self):
    # if there is a currently selected playlist
    if self.playlistList.currentItem() is not None:
        # retrieves the name of the currently selected playlist
        playlist_name = self.playlistList.currentItem().text()
        # creates a message box that asks if the user wants to delete the selected playlist, defaults to no
        MessageBox = QtWidgets.QMessageBox()
        result = MessageBox.question(None, 'Confirmation', 'Do you want to delete ' + playlist_name + '?',
                                     MessageBox.Yes | MessageBox.No, MessageBox.No)
        # if the user presses yes the playlist is deleted from the database
        # if the user presses no, nothing is executed and the program remains on the main screen
        if result == MessageBox.Yes:
            # retrieves the playlist (algorithm) id from the global variable playlist_ids
            global playlist_ids
            algorithm_id = playlist_ids[self.playlistList.currentRow()]
            # connect to database
            conn = database_connection()
            # create cursor to execute sql statement
            cur = conn.cursor()
            # performs a delete statement, catching any database errors that may occur, then closes the connection and
            # runs the function display_playlist
            try:
                # creates delete statement that deletes the selected playlist. Since algorithm_id is unique, only one
                # playlist will be affected.
                delete = "DELETE FROM algorithms WHERE algorithm_id = " + str(algorithm_id) + ";"
                # execute delete statement
                cur.execute(delete)
                # save changes to database
                conn.commit()

                # creates delete statement that deletes all of the likes and dislikes from the playlist that was
                # deleted, mostly so there isn't unnecessary leftover data in the database
                delete = "DELETE FROM song_ratings WHERE algorithm_id = " + str(algorithm_id) + ";"
                # execute delete statement
                cur.execute(delete)
                # save changes to database
                conn.commit()

                # creates delete statement that deletes the variable update counts for the selected playlist, mostly so
                # there isn't unnecessary leftover data in the database
                delete = "DELETE FROM algorithm_variable_updates WHERE algorithm_id = " + str(algorithm_id) + ";"
                # execute delete statement
                cur.execute(delete)
                # save changes to database
                conn.commit()
            # no sql errors should occur, so this shouldn't run, it's mostly here for testing
            except sqlite3.DatabaseError as error:
                print(error)
            # close database connection and redisplay the updated playlist list and songs in case playlist changed or
            # no playlists remain
            finally:
                conn.close()
                display_playlists(self)
                display_songs(self)


# Activates when the user presses the create playlist button on the main screen.
# Opens the create playlist window where the user can create a playlist based off a song that they search for.
def open_create_playlist(self, MainWindow):
    self.CreatePlaylistWindow = QtWidgets.QDialog()
    self.ui = createplaylist.Ui_Dialog()
    self.ui.setupUi(self.CreatePlaylistWindow, MainWindow)
    self.CreatePlaylistWindow.show()


# Activates when the user presses the search button on the Create Playlist Screen
# Uses the user's search terms to find matching songs/artists
def search(self):
    # first, the search list is cleared since new searches would otherwise be appended to older search results
    self.searchedSongsList.clear()
    # the text in the search bar is retrieved and split up by spaces into a list of search terms
    # this not only makes it easy for the program to search term by term, but it also helps try to prevent SQL attacks
    # since each space is removed from the search text.
    search_text = self.SearchBar.text().split()
    # a string that will become the select statement is initialized
    select = ''
    # if the search_text list isn't empty
    if len(search_text):
        # connect to database
        conn = database_connection()
        # create cursor to execute sql statement
        cur = conn.cursor()
        # this section creates a select statement, executes it, then displays the results in the searched songs list
        try:
            # This creates one select statement that returns any songs where the search terms are found in the
            # song name or artists names.
            #
            # A loop is ran using count to start the string so it contains the select part of the statement like
            # ("SELECT * FROM songs WHERE (name LIKE '%term%' OR artists LIKE '%term%')")
            # if there is more than one term in the search text, it's added as an and statement to the where clause like
            # ("AND (name LIKE '%term%' OR artists LIKE '%term%')")
            # once the loop is done, the last bit of the statement is added like
            # ("ORDER BY popularity DESC LIMIT 1000;")
            #
            # The "ORDER BY popularity DESC" sorts the results by popularity, since I assume most searches would be
            # for more popular songs.
            # The "LIMIT 1000" makes it so only 1000 songs at most are returned. Since there's over 500,000 songs in the
            # database, having the ability to return any number of songs can make the program run slowly.
            count = 1
            for term in search_text:
                if count == 1:
                    select += ("SELECT * FROM songs WHERE (name LIKE '%" + term + "%' OR artists LIKE '%"
                               + term + "%')")
                    count += 1
                elif count <= len(search_text):
                    select += (" AND (name LIKE '%" + term + "%' OR artists LIKE '%" + term + "%')")
                    count += 1
            select += "ORDER BY popularity DESC LIMIT 1000;"
            # the select statement is executed and the results are saved to a list
            search_list = cur.execute(select).fetchall()
            # the global variables search_ids is retrieved and emptied
            global search_ids
            search_ids = []
            # this loop runs for every song in the search_list and adds a string to the searched songs list on the
            # screen so the user can see the songs that match their terms
            for song in search_list:
                # each song id is stored so when the user wants to make a playlist the id can easily be retrieved
                search_ids.append(song[0])
                # the artists are saved in the database in the form of '['artist1', 'artist2']', so a literal evaluation
                # will convert that into a list
                artists = ast.literal_eval(song[2])
                # a string is initialized that will store all artist names
                artists_string = ''
                # another count is created for proper punctuation in the string
                count = 1
                # a for loop is ran for each artist in the list of artists
                for artist in artists:
                    # the first entry is added without any punctuation
                    if count == 1:
                        artists_string += artist
                        count += 1
                    # all other entries but the last are added with a comma and a space beforehand
                    elif count != len(artists):
                        artists_string += ', ' + artist
                        count += 1
                    # the last entry is added with a comma and an ampersand
                    else:
                        artists_string += ', & ' + artist
                # the string is completed and will look like "1. track by artist1, artist2, & artist3"
                song_name = song[1] + " by " + artists_string
                # the string is added to the searched songs list on the create playlist screen
                self.searchedSongsList.addItem(song_name)
                # selects the first row in the list (no errors occur if the list is empty, so no need to check for that)
                # this just ensures that a song is always selected if the user presses the create playlist button
                self.searchedSongsList.setCurrentRow(0)
        # no sql errors should occur, so this shouldn't run, it's mostly here for testing
        except sqlite3.DatabaseError as error:
            print(error)
        # the database connection is closed
        finally:
            conn.close()


# Activates when the user presses the create playlist button on the create playlist screen
# If the selected song isn't explicit, asks if the user wants to allow explicit songs in their playlist, then confirms
# that they want to create the playlist, and then creates the playlist. After that, it adds the song the playlist was
# created with as a liked song for that playlist.
def create_playlist(self, Dialog, MainWindow):
    # if nothing is selected in the search list, nothing will happen, otherwise the playlist can be created
    is_song_selected = self.searchedSongsList.currentItem()
    if is_song_selected is not None:
        # the global variable search_ids is retrieved, and the selected song's id is retrieved
        global search_ids
        song_id = search_ids[self.searchedSongsList.currentRow()]
        # connect to database
        conn = database_connection()
        # create cursor to execute sql statement
        cur = conn.cursor()
        # First a select statement that checks if the selected song is explicit. If it isn't, gives the user an option
        # to include or exclude explicit songs from the playlist.
        # (If the playlist is based off an explicit song, I assume that explicit songs can be included).
        try:
            # select statement
            select = "SELECT explicit FROM songs WHERE song_id = '" + song_id + "';"
            # song_id is unique, so only one result is returned, and the value from that row is stored
            explicit = cur.execute(select).fetchone()[0]
            # message box is initialized
            MessageBox = QtWidgets.QMessageBox()
            # result is initialized as blank
            result = ''
            # if explicit was false then this section runs
            if not explicit:
                # asks the user if they want to allow explicit songs and saves the result
                result = MessageBox.question(None, 'Explicit?', 'Do you want to allow explicit songs to be played?',
                                             MessageBox.Yes | MessageBox.No | MessageBox.Cancel,
                                             MessageBox.Cancel)
                # if the user presses yes, explicit is set to 1
                if result == MessageBox.Yes:
                    explicit = 1
                # if the user presses no, explicit is set to 0
                elif result == MessageBox.No:
                    explicit = 0
            # if the user didn't press cancel if they got the message box above
            if result != MessageBox.Cancel:
                # asks the user if they want to create a playlist using the selected song
                result = MessageBox.question(None, 'Confirm', 'Create playlist using '
                                             + self.searchedSongsList.currentItem().text() + '?',
                                             MessageBox.Yes | MessageBox.No, MessageBox.No)
                # if the user presses yes, the playlist is created, the create playlist screen is hidden, and the
                # main screen is updated to show the new playlist.
                # if the user presses no, they just stay on the create playlist screen
                if result == MessageBox.Yes:
                    # select statement that retrieves the base algorithm for setting the playlist's (algorithm's)
                    # weights
                    select = "SELECT * FROM algorithms WHERE algorithm_id = 0"
                    a = cur.execute(select).fetchone()
                    # I use an algorithm object to make the next section easier to read
                    base_algorithm = Algorithm.Algorithm(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9],
                                                         a[10], a[11], a[12], a[13])
                    # retrieves the user's id
                    global user_id
                    # creates an insert statement using the song_id, user_id, the user's explicit choice and the
                    # algorithm weights
                    insert = "INSERT INTO algorithms (song_id, user_id, explicit, popularity_score, tempo_score, " \
                             "acousticness_score, danceability_score, energy_score, instrumentalness_score, " \
                             "liveness_score, loudness_score, speechiness_score, valence_score) VALUES ('" + song_id \
                             + "', " + str(user_id) + ", " + str(explicit) + ", " \
                             + str(base_algorithm.get_popularity_score()) + ", " \
                             + str(base_algorithm.get_tempo_score()) + ", " \
                             + str(base_algorithm.get_acousticness_score()) + ", " \
                             + str(base_algorithm.get_danceability_score()) + ", " \
                             + str(base_algorithm.get_energy_score()) + ", " \
                             + str(base_algorithm.get_instrumentalness_score()) + ", " \
                             + str(base_algorithm.get_liveness_score()) + ", " \
                             + str(base_algorithm.get_loudness_score()) + ", " \
                             + str(base_algorithm.get_speechiness_score()) + ", " \
                             + str(base_algorithm.get_valence_score()) + ");"
                    # statement is executed
                    cur.execute(insert)
                    # change is saved to database
                    conn.commit()
                    # create playlist screen is hidden
                    Dialog.hide()
                    # main screen playlists list is updated
                    display_playlists(MainWindow)
                    #
                    # after creating the playlist, adding the song that the playlist is based on makes sense, so the
                    # code below does that.
                    #
                    # since the main screen has been updated, the global variable playlist_ids now contains the id of
                    # the newly created playlist in the last spot, so this id is obtained
                    global playlist_ids
                    algorithm_id = playlist_ids[-1]
                    # the song that the playlist is based off of is then added as a liked song (1 is liked) (0 is the
                    # total number of ratings for this playlist, so it starts at 0)
                    insert = "INSERT INTO song_ratings VALUES (" + str(algorithm_id) + ", '" + song_id + "', 1, 0);"
                    cur.execute(insert)
                    conn.commit()
                    # the table that contains like and dislike data for each algorithm has the algorithm inserted twice,
                    # one for dislikes and one for likes
                    # This data is updated when a song is liked/disliked, and it contains counts for each variable. The
                    # 3 variables that are updated on a like/dislike are increased by 1 everytime a like or dislike
                    # occurs. This data is used to see how the variables contribute to likes and dislikes on the data
                    # visualization screen.
                    insert = "INSERT INTO algorithm_variable_updates VALUES (" + str(algorithm_id) \
                             + ", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);"
                    cur.execute(insert)
                    conn.commit()
                    insert = "INSERT INTO algorithm_variable_updates VALUES (" + str(algorithm_id) \
                             + ", 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);"
                    cur.execute(insert)
                    conn.commit()
        # no sql errors should occur, so this shouldn't run, it's mostly here for testing
        except sqlite3.DatabaseError as error:
            print(error)
        # connection to database is closed
        finally:
            conn.close()


# Activates when the user presses the cancel button on the create playlist screen.
# Hides the create playlist screen, which will leave the user on the main screen.
def cancel(self, Dialog):
    Dialog.hide()


# Activates when the user presses the logout button on the main screen.
# Confirms that the user wants to log out with a message box. If the user presses yes, logs them out and returns them
# to the login screen.
def logout(self, MainWindow):
    # creates a message box that asks if the user wants to log out, default selection is no
    MessageBox = QtWidgets.QMessageBox()
    result = MessageBox.question(None, 'Confirmation', 'Do you want to log out?', MessageBox.Yes | MessageBox.No,
                                 MessageBox.No)
    # if the user presses yes user_id is set to 0, the main screen is hidden, and the login screen is shown
    # if the user presses no, nothing is executed and the program remains on the main screen
    if result == MessageBox.Yes:
        # the global variable user_id stores the user's id, which is how they're considered logged in.
        # 0 is an id value that can't exist, so setting the user_id to that will effectively log the user out
        global user_id
        user_id = 0

        MainWindow.hide()
        self.LoginWindow = QtWidgets.QDialog()
        self.ui = login.Ui_Dialog()
        self.ui.setupUi(self.LoginWindow)
        self.LoginWindow.show()


# Activates when the user presses the Play on Spotify button on the main screen
# Shuffles the user's selected playlist, connects to the user's active Spotify device, and plays the playlist
def spotify_play():
    # These two variables are used to connect the program with spotify so the user can listen to their playlists.
    # The scope is the privileges the program needs to play songs on the user's devices.
    # app-remote-control allows the program to control playback on the user's Andriod and iOS devices.
    # user-read-playback-state allows the program to see which device the user is using spotify from so it can connect
    # to it.
    # user-modify-playback-state allows the program to control playback on the user's devices.
    # user-read-currently-playing allows the program to see what's currently playing on the user's device.
    scope = "app-remote-control user-read-playback-state user-modify-playback-state user-read-currently-playing"
    # sp uses a client_id and client_secret that was generated when I created an application on the spotify developer
    # site (https://developer.spotify.com/), this allows the user to connect to spotify through my application.
    # The redirect uri is the website that the user will be redirected to after authentication of their spotify account.
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='5c8b4c3ef3fa4386ac89c15e16354d49',
                                                   client_secret='c0b2c20f58324b93b745433b75e55771',
                                                   redirect_uri='http://localhost:8080',
                                                   scope=scope))
    # retrieves the global variable song_ids
    global song_ids
    # if there are songs in the list of song ids
    if len(song_ids) != 0:
        # creates an empty list
        playlist = []
        # adds every song id in the proper form for Spotify to play to the newly created playlist
        for song in song_ids:
            playlist.append("spotify:track:" + song[0])
        # shuffles the playlist so the songs are in random order
        random.shuffle(playlist)
        # tries to connect to spotify, catching an error if no active device is found
        try:
            # If the user has never connected to Spotify through this application, opens a webpage that asks for the
            # user's confirmation and connects to their Spotify account. This automatically saves this to a cache so the
            # user doesn't need to authorize every time they connect to Spotify. Once they are connected, the program
            # attempts to play the playlist on their active device.
            #
            # The Spotify account that the user connects with must have Spotify Premium, otherwise the program will be
            # unable to play the playlist.
            sp.start_playback(uris=playlist)
        # as long as the connected Spotify account has Spotify Premium, the only error that should occur is when there
        # is no active device found
        except spotipy.exceptions.SpotifyException:
            # creates a message box that informs the user that no active device has been found with information how to
            # make their device active
            MessageBox = QtWidgets.QMessageBox()
            MessageBox.setWindowTitle('Error')
            MessageBox.setText('No active devices found. Open Spotify in either the desktop application, a web '
                               'browser, or the mobile application and press play and then pause to make a device '
                               'active')
            MessageBox.exec_()


# Activates when the user presses the Playlist Data button on the main screen.
# First, retrieves the selected playlist's (algorithm's) id and then opens the playlist data window.
def data_visualization(self, MainWindow):
    global playlist_ids
    # if there are playlists in the list of playlists
    if len(playlist_ids) != 0:
        algorithm_id = playlist_ids[MainWindow.playlistList.currentRow()]
        self.DataWindow = QtWidgets.QDialog()
        self.ui = datavisulaization.Ui_Dialog()
        self.ui.setupUi(self.DataWindow, algorithm_id)
        ratio_data(self.ui, algorithm_id)
        self.DataWindow.show()


# Activates when the user selects the Likes/Dislikes Ratio Graph radio option on the playlist data screen and when they
# press the Playlist Data button on the main screen
# Displays a graph that shows the ratio of likes and dislikes vs the number of ratings
def ratio_data(self, algorithm_id):
    # clears the graph, otherwise data just gets put on top of any existing data
    self.graph.clear()
    # connect to database
    conn = database_connection()
    # create cursor to execute sql statement
    cur = conn.cursor()
    try:
        # sets the names of the title and axes for the graph
        self.title.setText("Likes/Dislikes vs Ratings")
        self.yaxis.setText("Like/Dislike Ratio")
        self.xaxis.setText("Ratings")
        # select statement that retrieves the likes and dislikes data from the database, orders them by rating_count
        # which will keep them in the order they were liked/disliked
        select = "SELECT * FROM song_ratings WHERE algorithm_id = " + str(algorithm_id) \
                 + " ORDER BY rating_count;"
        # executes select statement and saves result to a list
        ratings_list = cur.execute(select).fetchall()
        # initializes a count for liked and disliked songs to 0 and 1 (this is to avoid dividing by 0 while keeping an
        # accurate graph, which these values achieve)
        likes_count = 0
        dislikes_count = 1
        # creates a list of likes/dislikes ratios
        likes_dislikes_ratio = []
        # creates a list of number of ratings
        ratings_count_list = []
        # for each rating in the list of ratings
        for rating in ratings_list:
            # if the rating is a like (equal to 1)
            if rating[2]:
                # skip the first like since it's an automatic like for the base song, and it skews the data if added
                if rating[3] != 0:
                    # add the count to the end of the list (it will go up by 1 every loop, sometimes skipping numbers if
                    # songs have ever been unliked)
                    ratings_count_list.append(rating[3])
                    # increase the like count by 1 and append the likes/dislikes ratio to the list
                    likes_count += 1
                    likes_dislikes_ratio.append(likes_count/dislikes_count)
            # otherwise, the rating is a dislike
            else:
                # add the count to the end of the list (it will go up by 1 every loop, sometimes skipping numbers if
                # songs have ever been unliked)
                ratings_count_list.append(rating[3])
                # increase the dislike count by 1 and append the likes/dislikes ratio to the list
                dislikes_count += 1
                likes_dislikes_ratio.append(likes_count/dislikes_count)
        # plots the ratings list and the likes/dislikes ratio to the graph and sets the pen color of the line to green
        self.graph.plot(ratings_count_list, likes_dislikes_ratio, pen='g')
        # selects the x-axis of the graph
        ax = self.graph.getAxis('bottom')
        # sets the ticks to default (if it was changed by like_data or dislike_data then it's set to strings, so this
        # will revert it)
        ax.setTicks(None)
    # no sql errors should occur, so this shouldn't run, it's mostly here for testing
    except sqlite3.DatabaseError as error:
        print(error)
    # close database connection
    finally:
        conn.close()


# Activates when the user selects the Liked Variables radio option on the playlist data screen
# Displays a bar chart that contains the occurrences of each variable for likes
def like_data(self, algorithm_id):
    # clears the graph, otherwise data just gets put on top of any existing data
    self.graph.clear()
    # connect to database
    conn = database_connection()
    # create cursor to execute sql statement
    cur = conn.cursor()
    try:
        # sets the names of the title and axes for the graph
        self.title.setText("Number of Occurrences of Each Variable for Likes")
        self.yaxis.setText("Occurrences")
        self.xaxis.setText("Variables")
        # select statement that retrieves the occurrences of each variable from the database
        select = "SELECT * FROM algorithm_variable_updates WHERE algorithm_id = " + str(algorithm_id) + \
                 " AND like_dislike = 1;"
        # algorithm_id + like_dislike is unique, so only one value will be returned, that value is saved to a variable
        variable_scores = cur.execute(select).fetchone()
        # stores the last 10 values as a list of variable scores
        variable_scores = variable_scores[-10:]
        # creates a list of variable names linked to numbers, for being displayed on the graph
        variables = [[1, 'popularity'], [2, 'tempo'], [3, 'acousticness'], [4, 'danceability'], [5, 'energy'],
                     [6, 'instrumentalness'], [7, 'liveness'], [8, 'loudness'], [9, 'speechiness'], [10, 'valence']]
        # a list of numbers, the same as the numbers in variables
        v = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # creates the bargraph item, setting the x-axis, y-axis, width of the bars and the color of the bars
        bargraph = pyqtgraph.BarGraphItem(x=v, height=variable_scores, width=0.2, brush='g')
        # adds the bargraph item to the graph
        self.graph.addItem(bargraph)
        # selects the x-axis of the graph
        ax = self.graph.getAxis('bottom')
        # sets the ticks to the variable names, where each number becomes the corresponding variable name
        ax.setTicks([variables])
    # no sql errors should occur, so this shouldn't run, it's mostly here for testing
    except sqlite3.DatabaseError as error:
        print(error)
    # close database connection
    finally:
        conn.close()


# Activates when the user selects the Disliked Variables radio option on the playlist data screen
# Displays a bar chart that contains the occurrences of each variable for dislikes
def dislike_data(self, algorithm_id):
    # clears the graph, otherwise data just gets put on top of any existing data
    self.graph.clear()
    # connect to database
    conn = database_connection()
    # create cursor to execute sql statement
    cur = conn.cursor()
    try:
        # sets the names of the title and axes for the graph
        self.title.setText("Number of Occurrences of Each Variable for Dislikes")
        self.yaxis.setText("Occurrences")
        self.xaxis.setText("Variables")
        # select statement that retrieves the occurrences of each variable from the database
        select = "SELECT * FROM algorithm_variable_updates WHERE algorithm_id = " + str(algorithm_id) + \
                 " AND like_dislike = 0;"
        # algorithm_id + like_dislike is unique, so only one value will be returned, that value is saved to a variable
        variable_scores = cur.execute(select).fetchone()
        # stores the last 10 values as a list of variable scores
        variable_scores = variable_scores[-10:]
        # creates a list of variable names linked to numbers, for being displayed on the graph
        variables = [[1, 'popularity'], [2, 'tempo'], [3, 'acousticness'], [4, 'danceability'], [5, 'energy'],
                     [6, 'instrumentalness'], [7, 'liveness'], [8, 'loudness'], [9, 'speechiness'], [10, 'valence']]
        # a list of numbers, the same as the numbers in variables
        v = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # creates the bargraph item, setting the x-axis, y-axis, width of the bars and the color of the bars
        bargraph = pyqtgraph.BarGraphItem(x=v, height=variable_scores, width=0.2, brush='g')
        # adds the bargraph item to the graph
        self.graph.addItem(bargraph)
        # selects the x-axis of the graph
        ax = self.graph.getAxis('bottom')
        # sets the ticks to the variable names, where each number becomes the corresponding variable name
        ax.setTicks([variables])
    # no sql errors should occur, so this shouldn't run, it's mostly here for testing
    except sqlite3.DatabaseError as error:
        print(error)
    # close database connection
    finally:
        conn.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # connect()
    display_login()
