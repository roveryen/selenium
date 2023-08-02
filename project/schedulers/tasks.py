from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from django_apscheduler.jobstores import DjangoJobStore, register_events

import socket
import logging
import os
import time

from evs.tasks import task_scrape_ev_data
from stations.tasks import task_scrape_station_data



class TaskScheduler:

    logger = None
    scheduler = None

    def __init__(self):
        self.init_logger()
        self.init_tasks()


    def init_logger(self):

        self.logger = logging.getLogger('tasks')
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            fileHandler = logging.FileHandler('/project/logs/log-tasks.txt')
            fileHandler.setFormatter( logging.Formatter('%(asctime)s - %(levelname)s : %(message)s') )
            self.logger.addHandler(fileHandler)


    def logging(self, d):
        self.logger.info(d)


    def init_tasks(self):

        executors = {
            'default': {'type': 'threadpool', 'max_workers': 1},
            'processpool': ProcessPoolExecutor(max_workers=1)
        }

        self.scheduler = BackgroundScheduler(executors=executors)
        #self.scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')

        register_events(self.scheduler)

        self.scheduler.add_job(task_scrape_ev_data,'cron', hour="*/2", minute="5", id='task_scrape_ev_data')

        self.scheduler.add_job(task_scrape_station_data, 'cron', hour="*/2", minute="35", id='task_scrape_station_data')

        #self.scheduler.print_jobs()



    def start(self):
        # print("schedulers.tasks.TaskScheduler.start()")
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()


def start():

    task_scheduler = None

    try:
        # print("schedulers.tasks.start()")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 47200))

        task_scheduler = TaskScheduler()
        task_scheduler.start()

    except socket.error:
        # print("!!!scheduler already started, DO NOTHING")
        pass

    except :
        if task_scheduler is not None:
            task_scheduler.shutdown()

