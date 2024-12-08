import pandas as pd
import re
from DataCollector import DataCollector
from DataModel import DataModel
DATA_DIR = "./src/data"
collector = DataCollector(DATA_DIR)

mymodel = DataModel(collector)

mymodel.save_model("model")