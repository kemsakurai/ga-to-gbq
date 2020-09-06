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
DATE="2020-05-18"
VIEW_ID="10xxxxxxx"
GA_CREDENTIALS_PATH=".ga_client.json"
flask job save_ga "$DATE" "$VIEW_ID" "$GA_CREDENTIALS_PATH"
```

* merge_data_to_gcs     
```console
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
export FLASK_APP=cli
DATE="2020-05-18"
BUCKET_NAME="monotalk.appspot.com"
FILE_DIR_NAME="GA Statistics/www.monotalk.xyz/"
flask job merge_data_to_gcs "$DATE" "$BUCKET_NAME" "$FILE_DIR_NAME"
```

* load_to_gbq
```console
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
export FLASK_APP=cli
DATE="2020-05-18"
DATA_SET_ID="monotalk.GA_Statistics"
GCS_DIR="gs://monotalk.appspot.com/GA Statistics/www.monotalk.xyz/"
flask job load_to_gbq "$DATE" "$DATA_SET_ID" "$GCS_DIR"
```

* compress_gcs_data   
```console
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
export FLASK_APP=cli
DATE="2020-05-18"
BUCKET_NAME="monotalk.appspot.com"
FILE_DIR_NAME="GA Statistics/www.monotalk.xyz/"
flask job compress_gcs_data "$DATE" "$BUCKET_NAME" "$FILE_DIR_NAME"
```
