Description of project:

	This project was developed as my Capstone project for WGU.
	
	This program works with the Capstone.db database file and uses data retrieved from
	https://www.kaggle.com/yamaerenay/spotify-dataset-19212020-160k-tracks. 
	
	This program allows the user to sign up with a username and password and then log in to the program. 
	Once logged in, the user can create a playlist based on a song. The program will generate a set 
	amount of songs using song variables and weights to find songs with a similar "score" to the song 
	the playlist was created from. Once the playlist is created the user can like songs, dislike songs, 
	and unlike/undislike songs which will update the algorithm that generates the songs in the playlist. 
	The hope is that by updating the algorithm, a playlist the user likes is generated. The program also 
	keeps track of some of the data and allows the user to view charts and graphs using that data. The user 
	can also delete playlists and connect to Spotify to play the songs from their playlists.

Note on Data:

	This program used SQLite and CSV files to import and manage data. If you would like to see or
	use these files with the program I uploaded them to Google Drive at:
	https://drive.google.com/file/d/1RehflYG5k__4t7AaQihDw9Cwdvl99neJ/view?usp=sharing
	
	The program will read these files if the .csv files and the DBMS folder are placed alongside the
	.py files.

Database Information:

	If you would like to browse the database, you can access the Capstone.db file from the link at the top 
	of this document and use the SQL DBMS of your choice to access the data (SQLite was used in the creation of this database)
	The tables that I used are named: 
	'algorithms' for storing playlist information and variable weights. 
	'algorithm_variable_updates' for storing variable counts which are used to display data in the 
	application. 
	'song_ratings' which contains liked and disliked songs. 
	'songs' which contains all of the songs (imported from the tracks.csv file in the Capstone folder). 
	And 'users' which stores user information. 
	Note that this database is viewable for testing purposes only, so any changes will affect the 
	application's data.

Note on running the program:

	The main screen can take a little while to open sometimes (usually happens when it's the
	first time running the application in a while). I'm not exactly sure why this happens, but
	if you just wait for a minute or so it will open and it seems to open quickly any time
	it's opened after that.

How to create a login:

	If it's your first time using the application you can navigate to the Sign Up screen to create
	a username and password. If you are testing this application and want to access the user I
	did testing with (there's a playlist with around 200 ratings, very useful for data visualization)
	you may use the following credentials:
	username: test
	password: pass

How to use the program:

	Once you're on the main screen the first thing you should do is press the create new playlist 
	button to search for a song to create a playlist with. After that the playlist will appear on
	the main screen and the songs list will be populated. After that you can use all of the functions
	of this application to rate songs, view your liked and disliked songs, play the playlist on Spotify,
	view data from the playlist, or delete the playlist.

How to select songs and playlists:

	To switch between playlists and to select songs to like and dislike, simply click on either in their
	respecitve lists.

Note on using this program with Spotify:

	When using the Play on Spotify function, this application will only shuffle the current playlist
	and play it on Spotify. Whenever you make changes to the playlist, they will not reflect in Spotify.
	This application contains no playback controls, use Spotify to control your playback.

How to connect this program to Spotify:

	In order to connect this program with Spotify you must have access to a Spotify account 
	with Spotify Premium. When you press the Play on Spotify button for the first time, a page 
	will open in your web browser which will ask you to give permission to this application so 
	it can play songs through your Spotify account. 

	Once you’ve authorized the application, you should get an error message saying that no active devices 
	have been found. In order to change that and start playing your playlist, either open the Spotify 
	desktop or mobile application or navigate to https://open.spotify.com/ and log in with the account you 
	authorized. Once you’ve logged in start playing anything and then pause, which will make your device active. 
	Now you can press the play on Spotify button again and the playlist will be shuffled and played via Spotify.

Spotify permissions requested by the program:

	This application will not ask for more 
	permissions than needed to play songs. The specific permissions requested are as follows:
		app-remote-control allows the program to control playback on the user's Android and iOS 
		devices.
		user-read-playback-state allows the program to see which device the user is using spotify 
		from so it can connect to it.
		user-modify-playback-state allows the program to control playback on the user's devices.
		user-read-currently-playing allows the program to see what's currently playing on the user's device.

How to sign out of Spotify:

	Note that there is no function to sign out of Spotify currently. If you need to switch Spotify
	accounts, you must follow these steps.
	1. Locate the Capstone folder that's located with this README file.
	2. Open the Capstone folder and  locate the .cache file
	3. Delete the .cache file
	The .cache file keeps an access token, allowing you to reconnect to Spotify easily, deleting this 
	will effectively log you out, and when you press the Play on Spotify button again it will act as 
	if it's your first time doing so.
