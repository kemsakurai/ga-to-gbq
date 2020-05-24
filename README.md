# ga-to-gbq
Load free Google Analytics data into Goolge Big Query

## Usage

* git clone     
```console
git clone https://github.com/kemsakurai/ga-to-gbq.git    
```

* Move directory   
```console
cd ga-to-gbq
```

* pip install    
```console
pip install -r requirements.txt    
```

* job list   
```console
export FLASK_APP=cli
flask job 
```

```console
Usage: flask job [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  load_to_gbq        Load to Google Big Query from Google Cloud Storage
  merge_data_to_gcs  Merge database data and upload Google Cloud Storage
  save_ga            Save Google Anlaytics data in the database

```

* save_ga    
```console
export FLASK_APP=cli
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
flask job save_gsc {GSC_PROPERTY_NAME} \
{GSC_CREDENTIALS_PATH} \
{DATE} {BUCKET_NAME} {FILE_DIR_NAME}
```

* load_gbq     
```console
export FLASK_APP=cli
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
flask job load_gbq {DATE} \
{DATA_SET_ID} \
{GCS_DIR}
```

