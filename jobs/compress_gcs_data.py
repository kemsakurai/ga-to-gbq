import conf
import click
from flask.cli import with_appcontext
from google.cloud import storage
import gzip
import os


@click.command('compress_gcs_data', help="Compress data uploaded Google Cloud Storage to gzip")
@click.argument('date')
@click.argument('bucket_name')
@click.argument('file_dir_name')
@with_appcontext
def compress_gcs_data(date, bucket_name, file_dir_name):
    file_name = conf.CSV_PREFIX + date.replace("-", "") + ".json"
    print("Compress start [json]", file_name)
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_dir_name + file_name)
    downloadString = blob.download_as_string()
    temp_gz = 'temp.json.gz'
    with gzip.open(temp_gz, 'wb') as f:
        f.write(downloadString)
    gzip_name = file_name + ".gz"
    gzip_blob = bucket.blob(file_dir_name + gzip_name)
    gzip_blob.upload_from_filename(filename=temp_gz, content_type="application/gzip")
    if os.path.exists(temp_gz): os.remove(temp_gz)

    # delete
    blob.delete()
    print("Blob {} deleted.".format(blob.name))
    print("Compress end [json]", file_name)
