
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
import re 

class DataModel:
    base = Namespace("http://www.semanticweb.org/ericarfs/ontologies/2024/10/famouspaintings#")
    foaf = Namespace("http://xmlns.com/foaf/0.1/")
    
    def __init__(self, collector, model):
        self.collector = collector
        self.model = model

        self.add_nationalities_to_model()
        self.add_subjects_to_model()
        self.add_countries_to_model()
        self.add_styles_to_model()
        self.add_museums_to_model()
        self.add_artists_to_model()
        self.add_works_to_model()

    def add_countries_to_model(self):
        countries = self.collector.get_countries()

        for country_name in countries:
            country_name_formated = re.sub(r"[^a-zA-Z0-9]", "", country_name)
            country = URIRef(base + country_name_formated)
            self.model.add((country, RDF.type, base.Country))
            self.model.add((country, foaf.name, Literal(country_name)))
    
    def add_styles_to_model(self):
        artist_styles = self.collector.get_artist_styles()
        work_styles = self.collector.get_work_styles()
        styles = set(artist_styles + work_styles)

        for style_name in styles:
            style_name_formated = re.sub(r"[^a-zA-Z0-9]", "", style_name)
            style = URIRef(base + style_name_formated)
            self.model.add((style, RDF.type, base.Style))
            self.model.add((style, foaf.name, Literal(style_name)))

    def add_subjects_to_model(self):
        subjects = self.collector.get_subjects()

        for subject_name in subjects:
            subject_name_formated = re.sub(r"[^a-zA-Z0-9]", "", subject_name)
            subject = URIRef(base + subject_name_formated)
            self.model.add((subject, RDF.type, base.Subject))
            self.model.add((subject, foaf.name, Literal(subject_name)))
    
    def add_nationalities_to_model(self):
        nationalities = self.collector.get_artist_nationalities()

        for nationality_name in nationalities:
            nationality_name_formated = re.sub(r"[^a-zA-Z0-9]", "", nationality_name)
            nationality = URIRef(base + nationality_name_formated)
            self.model.add((nationality, RDF.type, base.Nationality))
            self.model.add((nationality, foaf.name, Literal(nationality_name)))

    
    def add_museums_to_model(self):
        data = self.collector.get_museums()
        tam = data.shape[0]
        
        for i in range (tam):
            museum_identifier = data.iloc[i]["identifier"]
            museum = URIRef(base + museum_identifier)
            self.model.add((museum, RDF.type, base.Museum))

            museum_name = str(data.iloc[i]["name"])
            self.model.add((museum, foaf.name, Literal(museum_name)))

            country_name = re.sub(r"[^a-zA-Z0-9]", "", str(data.iloc[i]["country"]))
            if country_name != "nan":
                self.model.add((museum, base.hasCountry, URIRef(base + country_name )))

            state = str(data.iloc[i]["state"])
            if state != "nan":
                self.model.add((museum, base.state, Literal(state)))
            
            city = str(data.iloc[i]["city"])
            if city != "nan":
                self.model.add((museum, base.city, Literal(city)))
            
            address = str(data.iloc[i]["address"])
            if address != "nan":
                self.model.add((museum, base.address, Literal(address)))
            
            postal = str(data.iloc[i]["postal"])
            if postal != "nan":
                self.model.add((museum, base.postal, Literal(postal)))
            
            phone = str(data.iloc[i]["phone"])
            if phone != "nan":
                self.model.add((museum, base.phone, Literal(phone)))
            
            url = str(data.iloc[i]["url"])
            if city != "nan":
                self.model.add((museum, base.url, Literal(url)))  

    def add_artists_to_model(self):
        data = self.collector.get_artists()
        tam = data.shape[0]
        
        for i in range (tam):
            artist_identifier = data.iloc[i]["identifier"]
            artist = URIRef(base + artist_identifier)
            self.model.add((artist, RDF.type, base.Artist))

            full_name = str(data.iloc[i]["full_name"])
            self.model.add((artist, foaf.name, Literal(full_name)))

            first_name = str(data.iloc[i]["first_name"])
            if first_name != "nan":
                self.model.add((artist, foaf.firstName, Literal(first_name)))

            last_name = str(data.iloc[i]["last_name"])
            if last_name != "nan":
                self.model.add((artist, foaf.lastName, Literal(last_name)))
            
            birth = str(data.iloc[i]["birth"])
            if birth != "nan":
                self.model.add((artist, base.birth, Literal(birth)))

            death = str(data.iloc[i]["death"])
            if death != "nan":
                self.model.add((artist, base.death, Literal(death)))
            
            nationality = re.sub(r"[^a-zA-Z0-9]", "", str(data.iloc[i]["nationality"]))
            if nationality != "nan":
                self.model.add((artist, base.hasNationality, URIRef(base + nationality )))
            
            style = re.sub(r"[^a-zA-Z0-9]", "", str(data.iloc[i]["style"]))
            if style != "nan":
                self.model.add((artist, base.hasStyle, URIRef(base + style )))  

    def add_works_to_model(self):
        data = self.collector.get_works()
        tam = data.shape[0]

        for i in range (tam):
            work_identifier = data.iloc[i]["identifier"]
            work = URIRef(base + work_identifier)
            self.model.add((work, RDF.type, base.Work))

            name = str(data.iloc[i]["name"])
            self.model.add((work, foaf.name, Literal(name)))

            artist = collector.get_artist_by_id(data.iloc[i]["artist_id"])
            if artist is not None:
                self.model.add((work, base.wasPaintedBy, URIRef(base + artist )))
            
            style = re.sub(r"[^a-zA-Z0-9]", "", str(data.iloc[i]["style"]))
            if style != "nan":
                self.model.add((work, base.hasStyle, URIRef(base + style )))
            
            subject = collector.get_subject_by_id(data.iloc[i]["work_id"])
            if subject is not None:
                self.model.add((work, base.haSubject, URIRef(base + subject )))

            museum_id = data.iloc[i]["museum_id"]
            if museum_id != "nan":
                work_museum = collector.get_museum_by_id(museum_id)
                if work_museum is not None:
                    self.model.add((work, base.isLocatedAt, URIRef(base + work_museum)))
    
    def get_model(self):
        return self.model