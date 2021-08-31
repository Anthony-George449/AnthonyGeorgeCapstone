# Algorithm object, allows the program to create an object that's used to make the code in main.py read better

class Algorithm:
    def __init__(self, algorithm_id, song_id, user_id, explicit, popularity_score, tempo_score, acousticness_score,
                 danceability_score, energy_score, instrumentalness_score, liveness_score, loudness_score,
                 speechiness_score, valence_score):
        self.algorithm_id = algorithm_id
        self.song_id = song_id
        self.user_id = user_id
        self.explicit = explicit
        self.popularity_score = popularity_score
        self.tempo_score = tempo_score
        self.acousticness_score = acousticness_score
        self.danceability_score = danceability_score
        self.energy_score = energy_score
        self.instrumentalness_score = instrumentalness_score
        self.liveness_score = liveness_score
        self.loudness_score = loudness_score
        self.speechiness_score = speechiness_score
        self.valence_score = valence_score

    def get_algorithm_id(self):
        return self.algorithm_id

    def get_song_id(self):
        return self.song_id

    def get_user_id(self):
        return self.user_id

    def get_explicit(self):
        return self.explicit

    def get_popularity_score(self):
        return self.popularity_score

    def get_tempo_score(self):
        return self.tempo_score

    def get_acousticness_score(self):
        return self.acousticness_score

    def get_danceability_score(self):
        return self.danceability_score

    def get_energy_score(self):
        return self.energy_score

    def get_instrumentalness_score(self):
        return self.instrumentalness_score

    def get_liveness_score(self):
        return self.liveness_score

    def get_loudness_score(self):
        return self.loudness_score

    def get_speechiness_score(self):
        return self.speechiness_score

    def get_valence_score(self):
        return self.valence_score
