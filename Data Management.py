# this code is the code I used to insert the data from the csv file I retrieved from
# https://www.kaggle.com/yamaerenay/spotify-dataset-19212020-160k-tracks
import csv
import os
import sqlite3
import Song


def database_connection():
    conn = None
    try:
        print('Connecting to the database...')
        # change directory to be able to reach database
        working_dir = os.getcwd()
        os.chdir('DBMS/sqlite')
        # connect to database
        conn = sqlite3.connect('Capstone.db')
        # change directory back so csv file can be accessed
        os.chdir(working_dir)
        # create cursor to execute sql statement
        cur = conn.cursor()

        # open data file (tracks.csv) and read each row, create a song variable as a Song object that stores all of the
        # song attributes, organize each song into a string that can be used with an insert statement, add that string
        # to the end of an insert statement and execute the statement.
        #
        # the try statement catches any exceptions, which will only occur when there's a duplicate song_id,
        # so the program catches that and just moves on to the next insert statement.
        #
        # after running an insert statement for every row of data, the csv file is closed and the changes are
        # committed to the database.
        with open('tracks.csv', encoding='UTF-8') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            next(readCSV)
            for row in readCSV:
                # creating the Song object makes the string that's created much easier to read and edit
                song = Song.Song(row[0], row[1], row[5], row[6], row[7], row[3], row[2], row[4], row[12],
                                 row[10], row[19], row[18], row[14], row[8], row[9], row[15], row[16], row[11],
                                 row[13], row[17])
                data = ("('" + song.get_song_id() + "', '" + song.get_name().replace("'", "''") + "', '"
                        + song.get_artists().replace("'", "''") + "', '" + song.get_artists_id().replace("'", "''")
                        + "', '" + song.get_release_date() + "', '" + song.get_duration_ms() + "', '"
                        + song.get_popularity() + "', '" + song.get_explicit() + "', '" + song.get_mode()
                        + "', '" + song.get_key() + "', '" + song.get_time_signature() + "', '"
                        + song.get_tempo() + "', '" + song.get_acousticness() + "', '" + song.get_danceability()
                        + "', '" + song.get_energy() + "', '" + song.get_instrumentalness() + "', '"
                        + song.get_liveness() + "', '" + song.get_loudness() + "', '" + song.get_speechiness()
                        + "', '" + song.get_valence() + "')")
                try:
                    insert = ('INSERT INTO songs (song_id, name, artists, artists_id, release_date, duration_ms, '
                              'popularity, explicit, mode, key, time_signature, tempo, acousticness, danceability, '
                              'energy, instrumentalness, liveness, loudness, speechiness, valence) VALUES '
                              + data + ';')
                    cur.execute(insert)
                except (Exception, sqlite3.DatabaseError) as error:
                    print(error)
        csvfile.close()
        conn.commit()

    # catch any errors that may occur when connecting to the database
    except (Exception, sqlite3.DatabaseError) as error:
        print(error)
    # if conn isn't none, then a database connection was made, so that connection is closed.
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    database_connection()
