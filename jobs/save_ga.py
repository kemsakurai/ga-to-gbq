import click
from flask.cli import with_appcontext
import conf
from libs.utils import divide_list
import pandas as pd
from google2pandas import GoogleAnalyticsQueryV4
import copy
import sqlite3


@click.command('save_ga', help="Save Google Anlaytics data in the database")
@click.argument('date')
@click.argument('view_id')
@click.argument('ga_credentials_path')
@with_appcontext
def save_ga(date, view_id, ga_credentials_path):
    print("ga_to_sqlite start. date [", date, "]")
    for k, v in conf.DIMENSIONS_METRICS_COMBINATIONS.items():
        dimensions = v.get("dimensions")
        metrics = v.get("metrics")
        # dimensionのリストの分割数を求める
        divide_num = (len(dimensions) // (8 - len(conf.PK_DIMENSIONS))) + 1
        sublist = divide_list(dimensions, divide_num)
        for i, elem in enumerate(sublist):
            store_ga_to_sqlite(date, elem, metrics, k + "_" + str(i + 1), view_id, ga_credentials_path)


def store_ga_to_sqlite(date, dimensions, metrics, table_category_name, view_id, ga_credentials_path):
    query_dimensions = copy.deepcopy(conf.PK_DIMENSIONS)
    query_dimensions.extend(dimensions)
    query_dimensions = [dict(s) for s in set(frozenset(d.items()) for d in query_dimensions)]

    query = {
        'reportRequests': [{
            'viewId': view_id,
            'dateRanges': [{
                'startDate': date,
                'endDate': date}],
            'dimensions': query_dimensions,
            'metrics': metrics,
        }]
    }

    # Assume we have placed our client_secrets_v4.json file in the current
    # working directory.
    try:
        conn = GoogleAnalyticsQueryV4(secrets=ga_credentials_path)
        # table名生成
        table_name = "ga_sessions_" + date.replace("-", "") + "_" + table_category_name
        df = conn.execute_query(query)
        for k, v in conf.DATA_FRAME_APPLY_SETTINGS.items():
            try:
                df[k] = df[k].apply(v.get("apply_func"))
            except KeyError as e:
                if v.get("raise_error"):
                    raise e

    except TypeError as e:
        print("TypeError... table_name[", table_name, "]", "create empty table.")
        print(query)
        columns = []
        for i in query_dimensions:
            for value in i.values():
                columns.append(value.replace("ga:", ""))
        for i in metrics:
            for value in i.values():
                columns.append(value.replace("ga:", ""))
        df = pd.DataFrame(columns=columns)

    # ------------------
    # create database and insert
    # ------------------
    db_name = conf.SQLITE_DATABASE_NAME
    # dbコネクト
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn,
              index=False, if_exists="replace")
    # コネクションを閉じる
    conn.close()
