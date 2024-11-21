import pandas as pd
import re

class DataCollector:
    def __init__(self, DATA_DIR):
        self.artist = pd.read_csv(DATA_DIR + "/artist.csv")
        self.museum = pd.read_csv(DATA_DIR + "/museum.csv")
        self.work = pd.read_csv(DATA_DIR + "/work.csv")
        self.subject = pd.read_csv(DATA_DIR + "/subject.csv")
        self.clean_data()
        self.set_identifiers()
    
    def clean_data(self):
        self.artist = self.artist.drop_duplicates()
        self.museum = self.museum.drop_duplicates()
        self.work = self.work.drop_duplicates()
        self.subject = self.subject.drop_duplicates()
        
    def set_identifiers(self):
        self.artist["identifier"] = self.artist.apply(
            lambda line: re.sub(r"[^a-zA-Z0-9]", "", str(line["full_name"])),
            axis=1
        )
        self.museum["identifier"] = self.museum.apply(
            lambda line: re.sub(r"[^a-zA-Z0-9]", "", str(line["name"])),
            axis=1
        )
        self.work["identifier"] = self.work.apply(
            lambda line: str(line["work_id"]) + "_" + re.sub(r"[^a-zA-Z0-9]", "", str(line["name"])),
            axis=1
        )
        self.subject["identifier"] = self.subject.apply(
            lambda line: "Subject_" + re.sub(r"[^a-zA-Z0-9]", "", str(line["subject"])),
            axis=1
        )
        

    def get_artists(self):
        artists = self.artist.drop_duplicates().reset_index(drop=True)
        return artists
    
    def get_museums(self):
        museums = self.museum.drop_duplicates().reset_index(drop=True)
        return museums

    def get_works(self):
        works = self.work.drop_duplicates().reset_index(drop=True)
        return works
    
    def get_work_subjects(self):
        subjects = self.subject.drop_duplicates().reset_index(drop=True)
        return subjects

    def get_countries(self):
        return self.museum["country"].dropna().unique().tolist()
    
    def get_artist_styles(self):
        return self.artist["style"].dropna().unique().tolist()
    
    def get_artist_nationalities(self):
        return self.artist["nationality"].dropna().unique().tolist()

    def get_subjects(self):
        return self.subject["subject"].dropna().unique().tolist()

    def get_work_styles (self):
        return self.work["style"].dropna().unique().tolist()

    def get_artist_by_id(self, id):
        values = self.artist[self.artist["artist_id"] == id]["identifier"].values
        if len(values) > 0:
            return values[0]
        return None
    
    def get_museum_by_id(self, id):
        values = self.museum[self.museum["museum_id"] == id]["identifier"].values
        if len(values) > 0:
            return values[0]
        return None
    
    def get_subject_by_id(self, id):
        values = self.subject[self.subject["work_id"] == id]["identifier"].values
        if len(values) > 0:
            return values[0]
        return None
    
    def get_style_by_id(self, id):
        style = self.work[self.work["work_id"] == id]["style"].values[0]
        return re.sub(r"[^a-zA-Z0-9]", "", style)