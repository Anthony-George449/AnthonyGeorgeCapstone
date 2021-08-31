# Song object, allows the program to create an object that's used to make the code in main.py read better
# Definitions for each song variable are noted in the __init__ function, these definitions are not mine and are from:
# https://developer.spotify.com/documentation/web-api/reference/#endpoint-get-audio-features

class Song:
    def __init__(self, song_id, name, artists, artists_id, release_date, duration_ms, popularity, explicit, mode, key,
                 time_signature, tempo, acousticness, danceability, energy, instrumentalness, liveness, loudness,
                 speechiness, valence):
        self.song_id = song_id
        self.name = name
        self.artists = artists
        self.artists_id = artists_id
        self.release_date = release_date
        self.duration_ms = duration_ms
        # The popularity of the track. The value will be between 0 and 100, with 100 being the most popular.
        self.popularity = popularity
        self.explicit = explicit
        self.mode = mode
        self.key = key
        self.time_signature = time_signature
        # The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed
        # or pace of a given piece and derives directly from the average beat duration.
        self.tempo = tempo
        # A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the
        # track is acoustic.
        self.acousticness = acousticness
        # Danceability describes how suitable a track is for dancing based on a combination of musical elements
        # including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable
        # and 1.0 is most danceable.
        self.danceability = danceability
        self.energy = energy
        # Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as instrumental in this
        # context. Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness value is to 1.0, the
        # greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent
        # instrumental tracks, but confidence is higher as the value approaches 1.0.
        self.instrumentalness = instrumentalness
        # Detects the presence of an audience in the recording. Higher liveness values represent an increased
        # probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is
        # live.
        self.liveness = liveness
        # The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are
        # useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary
        # psychological correlate of physical strength (amplitude). Values typical range between -60 and 0 db.
        self.loudness = loudness
        # Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording
        # (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks
        # that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain
        # both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33
        # most likely represent music and other non-speech-like tracks.
        self.speechiness = speechiness
        # A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence
        # sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g.
        # sad, depressed, angry).
        self.valence = valence

    def get_song_id(self):
        return self.song_id

    def get_name(self):
        return self.name

    def get_artists(self):
        return self.artists

    def get_artists_id(self):
        return self.artists_id

    def get_release_date(self):
        return self.release_date

    def get_duration_ms(self):
        return self.duration_ms

    def get_popularity(self):
        return self.popularity

    def get_explicit(self):
        return self.explicit

    def get_mode(self):
        return self.mode

    def get_key(self):
        return self.key

    def get_time_signature(self):
        return self.time_signature

    def get_tempo(self):
        return self.tempo

    def get_acousticness(self):
        return self.acousticness

    def get_danceability(self):
        return self.danceability

    def get_energy(self):
        return self.energy

    def get_instrumentalness(self):
        return self.instrumentalness

    def get_liveness(self):
        return self.liveness

    def get_loudness(self):
        return self.loudness

    def get_speechiness(self):
        return self.speechiness

    def get_valence(self):
        return self.valence

