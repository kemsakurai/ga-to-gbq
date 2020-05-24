import click
import sqlite3
import pandas as pd
import conf
from libs.utils import divide_list
from flask.cli import with_appcontext
import os
from google.cloud import storage


def get_table_data_as_dataframe(date, table_category_name):
    db_name = conf.SQLITE_DATABASE_NAME
    conn = sqlite3.connect(db_name)
    table_name = conf.TABLE_PREFIX + date.replace("-", "") + "_" + table_category_name
    try:
        # rdbのデータをpandasのDataFrame型で読み込む
        df = pd.read_sql("select * from " + table_name, conn)
    except:
        df = get_empty_dataframe()
    return df


def get_empty_dataframe():
    pk_keys = [k.get("name").replace("ga:", "") for k in conf.PK_DIMENSIONS]
    df = pd.DataFrame(columns=pk_keys)
    return df


@click.command('merge_data_to_gcs', help="Merge database data and upload Google Cloud Storage")
@click.argument('date')
@click.argument('bucket_name')
@click.argument('file_dir_name')
@with_appcontext
def merge_data_to_gcs(date, bucket_name, file_dir_name):
    print("Merge data start [date]", date.replace("-", ""))

    df = get_empty_dataframe()
    for k, v in conf.DIMENSIONS_METRICS_COMBINATIONS.items():
        dimensions = v.get("dimensions")
        divide_num = (len(dimensions) // (8 - len(conf.PK_DIMENSIONS))) + 1
        sublist = divide_list(dimensions, divide_num)
        for i, elem in enumerate(sublist):
            df = pd.merge(df, get_table_data_as_dataframe(date, k + "_" + str(i + 1)), how='outer')

    for k, v in conf.MERGE_DATA_FRAME_APPLY_SETTINGS.items():
        try:
            df[v.get("key_after_convert")] = df[k].apply(v.get("apply_func"))
        except KeyError as e:
            if v.get("raise_error"):
                    raise e

    temp_file_name = 'temp.json'
    df.to_json(temp_file_name,
               orient="records",
               lines=True)
    file_name = conf.CSV_PREFIX + date.replace("-", "") + ".json"
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_dir_name + file_name)
    blob.upload_from_filename(filename=temp_file_name)
    if os.path.exists(temp_file_name): os.remove(temp_file_name)
