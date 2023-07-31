from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events

import logging

class TaskScheduler(BackgroundScheduler):

    logger = None

    def __init__(self):
        super().__init__()

        fileHandler = logging.FileHandler('/project/logs/log-tasks.txt')
        fileHandler.setFormatter( logging.Formatter('%(asctime)s - %(levelname)s : %(message)s') )

        self.logger = logging.getLogger('tasks')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(fileHandler)

    def logging(self, d):
        self.logger.info(d)


scheduler = TaskScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')

@scheduler.scheduled_job('cron', hour="*/4",
    name='task_scrape_station_data',
    coalesce=True,
    misfire_grace_time=60,
    max_instances=1)

def task_scrape_station_data():
    from stations import tasks
    tasks.task_scrape_station_data()

@scheduler.scheduled_job('cron', hour="*/4",
    name='task_scrape_ev_data',
    coalesce=True,misfire_grace_time=60,
    max_instances=1)
def task_scrape_ev_data():
    from evs import tasks
    tasks.task_scrape_ev_data()


#scheduler.shutdown()

