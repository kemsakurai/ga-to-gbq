from flask.cli import AppGroup
from jobs.save_ga import save_ga
from jobs.merge_data_to_gcs import merge_data_to_gcs
from jobs.load_to_gbq import load_to_gbq

job = AppGroup('job')
job.add_command(save_ga)
job.add_command(merge_data_to_gcs)
job.add_command(load_to_gbq)
