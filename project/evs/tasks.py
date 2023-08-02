
from .scrappy_8891 import Scrappy8891
#from .scrappy_evdatabase import ScrappyEVDatabase
from .scrappy_yahoo import ScrappyYahoo

task_array = [
    Scrappy8891(),
    ScrappyYahoo(),
    #scrappy_evdatabase
]

def task_scrape_ev_data():
    # Your task code goes here

    #scheduler.logging("Executing scheduled task now... task_scrape_ev_data")
    # This function will be executed at the scheduled time
    for s in task_array:
        s.start_scrape_data()

