import pandas as pd
import re
from DataCollector import DataCollector
from DataModel import DataModel
from geopy.geocoders import Nominatim
import random
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from owlrl import DeductiveClosure, RDFS_Semantics
from tkinter import *
from SPARQLWrapper import SPARQLWrapper, JSON
import webbrowser
import tkintermapview
from PIL import ImageTk, Image
import requests
from io import BytesIO

base = Namespace("http://www.semanticweb.org/ericarfs/ontologies/2024/10/famouspaintings#")
xsd  = Namespace("http://www.w3.org/2001/XMLSchema#")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
rdf  = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
dbo  = Namespace("http://dbpedia.org/ontology/")
dbp  = Namespace("http://dbpedia.org/property/")
dbr  = Namespace("http://dbpedia.org/resource/")

def obter_lat_lon_nominatim(endereco):
    geolocator = Nominatim(user_agent="sua_aplicacao")
    localizacao = geolocator.geocode(endereco)
    if localizacao:
        return localizacao.latitude, localizacao.longitude
    else:
        print("Endereço não encontrado")
        return None, None

def fetch_data_from_query(search_query, att_names):
    
    qres = inferred_model.query(
        search_query,
        initNs={
            'rdf': rdf,
            'foaf': foaf,
            'dbr': dbr,
            'dbo': dbo,
            'dbp': dbp,
            'rdfs': rdfs,
            'georss': 'http://www.georss.org/georss/'
        },
    )


    data = []
    for row in qres:
        obj = {}
        for idx, att_name in enumerate(att_names):
            value = row[idx]
            obj[att_name] = None if value is None else str(value)
        data.append(obj)

    return data

def show_museum_details(museum_name):
    museum_window = Toplevel()  # Create a new top-level window
    museum_window.title(f"{museum_name}")

    # Create a Canvas widget for scrolling
    canvas = Canvas(museum_window)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    # Create a vertical scrollbar linked to the canvas
    scrollbar = Scrollbar(museum_window, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill="y")

    # Configure the canvas to use the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold all the content
    content_frame = Frame(canvas)
    canvas.create_window((0, 0), window=content_frame, anchor="nw")

    query = f"""
            PREFIX : <http://www.semanticweb.org/ericarfs/ontologies/2024/10/famouspaintings#>

            SELECT ?abstract ?country ?state ?city ?address ?postal ?phone ?url ?coords ?thumbnail ?museum
            WHERE {{
                OPTIONAL {{
                    SERVICE <https://dbpedia.org/sparql> {{
                        ?museumDbo a dbo:Building ;
                            rdfs:label "{museum_name}"@en ;
                            georss:point ?coords ;
                            dbo:thumbnail ?thumbnail ;
                            dbo:abstract ?abstract .
                    }}
                }}
                ?museum
                    rdf:type dbo:Museum ;
                    foaf:name "{museum_name}" ;
                .
                OPTIONAL {{?museum dbp:country/foaf:name ?country .}}
                OPTIONAL {{?museum :state ?state .}}
                OPTIONAL {{?museum :city ?city .}}
                OPTIONAL {{?museum :address ?address .}}
                OPTIONAL {{?museum :postal ?postal .}}
                OPTIONAL {{?museum :phone ?phone .}}
                OPTIONAL {{?museum foaf:homepage ?url .}}
            }}
            LIMIT 1
        """
    
    att_names = ['abstract', 'country', 'state', 'city', 'address', 'postal', 'phone', 'url', 'coord', 'thumbnail', 'uri']
    museum_info = fetch_data_from_query(query, att_names)
    museum_info = museum_info[0]
    
    # Title
    title_label = Label(content_frame, text=museum_name, font=("Arial", 12))
    title_label.pack(pady=10)

    # Image
    if museum_info['thumbnail']:
        response = requests.get(museum_info['thumbnail'])
        if response.status_code == 200:
            thumbnail = Image.open(BytesIO(response.content))
            test = ImageTk.PhotoImage(thumbnail)
            label1 = Label(content_frame, image=test)
            label1.image = test
            label1.pack(pady=10)
    
    #Abstract
    if museum_info['abstract']:
        contact_label = Label(content_frame, text=museum_info['abstract'], font=("Arial", 10), wraplength=800, justify="left")
        contact_label.pack(pady=10)
    
    # Contact
    contact_title_label = Label(content_frame, text=f"Contact:", font=("Arial", 12))
    contact_title_label.pack(pady=10)
    if museum_info['city'].isdigit():
        museum_info['city'] = None
    address = (museum_info['address'] if museum_info['address'] else "---") + ", " + (museum_info['city'] if museum_info['city'] else "---") + ", " + (museum_info['state'] if museum_info['state'] else "---") + ", " + (museum_info['country'] if museum_info['country'] else "---")
    contact_info = f"Phone: {museum_info['phone']}\nWebsite: {museum_info['url']}\nAddress: {address}"
    contact_label = Label(content_frame, text=contact_info, font=("Arial", 10))
    contact_label.pack(pady=10)

    # URI
    more_info_label = Label(content_frame, text=f"URI {museum_info['uri']}:", font=("Arial", 10))
    more_info_label.pack(pady=5)
    
    # Map
    map_label = LabelFrame(content_frame)
    map_label.pack(pady=20)
    map_widget = tkintermapview.TkinterMapView(map_label, width=800, height=600, corner_radius=0)
      
    if museum_info['coord']:
        lat, lon = map(float, museum_info['coord'].split())
        map_widget.set_position(lat, lon)
    elif museum_info['address'] and museum_info['city'] and museum_info['state'] and museum_info['country']:
        map_widget.set_address(address)
    else:
        # Se não houver informações que podem ser usadas, usa o nominatim
        lat, lon = obter_lat_lon_nominatim(museum_name)
        map_widget.set_position(lat, lon)
    
    map_widget.pack()
    
    
    painting_list = get_list_of_paintings(museum_name)

    # Populate the scrollable frame with data
    for style in painting_list.keys():
        style_label = Label(content_frame, text=style, font=("Arial", 14, "bold"), pady=5)
        style_label.pack(anchor="w")
        
        for painting in painting_list[style]:
            link = Label(content_frame, text=painting['title'], fg="blue", cursor="hand2", pady=2)
            link.pack(anchor="w")
            link.bind("<Button-1>", lambda e, uri=painting['uri'], dbpedia_uri=painting['dbpedia_uri']:show_painting_details(uri, dbpedia_uri))
    
    # Update the scrollable region of the canvas
    content_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def create_gui(museums_by_country):
    root = Tk()
    root.title("Museums by Country")

    canvas = Canvas(root)
    scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Populate the scrollable frame with data
    for country in museums_by_country.keys():
        country_label = Label(scrollable_frame, text=country, font=("Arial", 14, "bold"), pady=5)
        country_label.pack(anchor="w")
        
        for museum in museums_by_country[country]:
            link = Label(scrollable_frame, text=museum, fg="blue", cursor="hand2", pady=2)
            link.pack(anchor="w")
            link.bind("<Button-1>", lambda e, name=museum: show_museum_details(name))

    root.mainloop()

def get_list_of_paintings(museum_name):
    q = f"""
        PREFIX : <http://www.semanticweb.org/ericarfs/ontologies/2024/10/famouspaintings#>
        SELECT ?workLocal ?workDbo ?title ?style
        WHERE {{
            SERVICE <https://dbpedia.org/sparql> {{
                ?workDbo a dbo:Work ;
                         dbp:title ?title ;
                         dbo:museum/rdfs:label "{museum_name}"@en .
            }}
            OPTIONAL {{
                ?workLocal
                    rdf:type dbo:Painting ;
                    foaf:name ?titleLocal ;
                    dbp:style/foaf:name ?style ;
                .
                FILTER (STR(?title) = STR(?titleLocal))
            }}
        }}
    """

    painting_list = fetch_data_from_query(q, ['painting_uri', 'painting_dbpedia_uri', 'title','style'])
    
    organized = {}
    for painting in painting_list:
        uri = painting['painting_uri'] if painting['painting_uri'] else None
        dbpedia_uri = painting['painting_dbpedia_uri'] if painting['painting_dbpedia_uri'] else None
        title = painting['title'] if painting['title'] else 'Untitled'
        style = painting['style'] if painting['style'] else 'Unclassified'
        
        if style not in organized:
            organized[style] = []
        obj = {'title': title, 'uri': uri, 'dbpedia_uri': dbpedia_uri}
        organized[style].append(obj)
    
    return organized

def organize_by_country(museums):
    organized = {}
    for museum in museums:
        country = museum['country']
        museum_name = museum['museum_name']
        
        if country not in organized:
            organized[country] = []
        organized[country].append(museum_name)
    
    return organized

def show_painting_details(painting_uri, dbpedia_uri):
    painting_window = Toplevel()  # Create a new top-level window
    painting_window.title(f"{painting_uri}")

    # Create a Canvas widget for scrolling
    canvas = Canvas(painting_window)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    # Create a vertical scrollbar linked to the canvas
    scrollbar = Scrollbar(painting_window, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill="y")

    # Configure the canvas to use the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold all the content
    content_frame = Frame(canvas)
    canvas.create_window((0, 0), window=content_frame, anchor="nw")

    query = f"""
            PREFIX : <http://www.semanticweb.org/ericarfs/ontologies/2024/10/famouspaintings#>
    
            SELECT ?title ?artist ?style ?subject ?museum ?thumbnail ?abstract
            WHERE {{

                SERVICE <https://dbpedia.org/sparql> {{
                    <{dbpedia_uri}> a dbo:Work .
                                    OPTIONAL {{<{dbpedia_uri}> dbp:title ?title .}}
                                    OPTIONAL {{<{dbpedia_uri}> dbp:artist/foaf:name ?artist .}}
                                    OPTIONAL {{<{dbpedia_uri}> dbp:subject ?subject .}}
                                    OPTIONAL {{<{dbpedia_uri}> dbo:museum/foaf:name ?museum .}}
                                    OPTIONAL {{<{dbpedia_uri}> dbo:thumbnail ?thumbnail .}}
                                    OPTIONAL {{<{dbpedia_uri}> dbo:abstract ?abstract .}}          
                                    
                }}      

                OPTIONAL {{ <{painting_uri}> dbp:style/foaf:name ?style .}}
            }}
            LIMIT 1
        """
    
    att_names = ['title', 'artist', 'style', 'subject', 'museum', 'thumbnail', 'abstract']    
    
    painting_info = fetch_data_from_query(query, att_names)    
    painting_info = painting_info[0]
    print(painting_info)
    
     # Title
    title_label = Label(content_frame, text=painting_info['title'], font=("Arial", 12))
    title_label.pack(pady=10)

    # Image
    if painting_info['thumbnail']:
        print(painting_info['thumbnail'])
        response = requests.get(painting_info['thumbnail'], allow_redirects=True)
        print(response.status_code)
        if response.status_code == 200:
            thumbnail = Image.open(BytesIO(response.content))
            test = ImageTk.PhotoImage(thumbnail)
            label1 = Label(content_frame, image=test)
            label1.image = test
            label1.pack(pady=10)
    
    # Info
    contact_label = Label(content_frame, text=painting_info['abstract'], font=("Arial", 10), wraplength=800, justify="left")
    contact_label.pack(pady=10)
    contact_label = Label(content_frame, text=f"Artist: {painting_info['artist']}", font=("Arial", 10))
    contact_label.pack(pady=5)
    contact_label = Label(content_frame, text=f"Style: {painting_info['style']}", font=("Arial", 10))
    contact_label.pack(pady=5)
    contact_label = Label(content_frame, text=f"Museum: {painting_info['museum']}", font=("Arial", 10))
    contact_label.pack(pady=5)

    # URI
    more_info_label = Label(content_frame, text=f"URI: {painting_uri if painting_uri else dbpedia_uri}", font=("Arial", 10))
    more_info_label.pack(pady=5)
    
    # Update the scrollable region of the canvas
    content_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

if __name__ == "__main__":
    
    DATA_DIR = "./src/data"
    collector = DataCollector(DATA_DIR)

    mymodel = DataModel(collector)

    output_file = "model.ttl"
    mymodel.save_model(output_file)

    schema_file = "./paintingsontology.ttl"

    schema = Graph()
    schema.parse(schema_file)  # Ler o esquema

    data = mymodel.get_model()

    inferred_model = Graph()
    inferred_model += schema
    inferred_model += data

    DeductiveClosure(RDFS_Semantics).expand(inferred_model)  # Inferência RDFS

    q = """
        PREFIX : <http://www.semanticweb.org/ericarfs/ontologies/2024/10/famouspaintings#>

        SELECT ?country ?MuseumName
        WHERE {
            ?museum rdf:type dbo:Museum ;
                    foaf:name ?MuseumName .
            OPTIONAL { ?museum dbp:country/foaf:name ?country . }
        }
        ORDER BY ?country
    """
    att_names = ['country', 'museum_name']
    data = fetch_data_from_query(q, att_names)
    museums_by_country = organize_by_country(data)
    create_gui(museums_by_country)

