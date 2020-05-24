from google.cloud import bigquery
import conf
import click
from google.cloud.bigquery.dataset import DatasetReference
from flask.cli import with_appcontext


@click.command('load_to_gbq', help="Load to Google Big Query from Google Cloud Storage")
@click.argument('date')
@click.argument('data_set_id')
@with_appcontext
def load_to_gbq(date, data_set_id, gcs_dir):
    table_name = conf.TABLE_PREFIX + date.replace("-", "")
    print("Load start [table_name]", table_name)
    client = bigquery.Client()
    data_set_ref = DatasetReference.from_string(data_set_id)
    job_config = bigquery.LoadJobConfig()
    # The source format defaults to CSV, so the line below is optional.
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    job_config.schema = conf.GBQ_SCHEMA

    table_ref = data_set_ref.table(table_name)

    try:
        client.delete_table(table_ref)  # API request
    except:
        pass
    uri = gcs_dir + table_name + '.json'
    load_job = client.load_table_from_uri(
        uri,
        data_set_ref.table(table_name),
        job_config=job_config)  # API request

    assert load_job.job_type == 'load'

    try:
        load_job.result()  # Waits for table load to complete.
    except Exception as e:
        for error in load_job.errors:
            print("Error detail [message]", error.get("message"))
        raise e
    assert load_job.state == 'DONE'
