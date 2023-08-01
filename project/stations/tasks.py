from schedulers.tasks import scheduler

from .scrappy_audi import ScrappyAudi
from .scrappy_icharging import ScrappyICharging
from .scrappy_teslaguru import ScrappyTeslaGuru
from .scrappy_teslahere import ScrappyTeslaHere

try:

    task_array = [
        ScrappyAudi(),
        ScrappyICharging(),
        ScrappyTeslaGuru(),
        ScrappyTeslaHere()
    ]

    def task_scrape_station_data():
        # Your task code goes here
        scheduler.logging("Executing scheduled task now... task_scrape_station_data")
        # This function will be executed at the scheduled time

        for s in task_array:
            s.start_scrape_data()


except Exception as e:
    scheduler.logging(e)


