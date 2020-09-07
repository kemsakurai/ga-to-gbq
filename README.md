# ga-to-gbq

Load free Google Analytics data into Goolge Big Query.   
It is designed to run as a cronjob on a Linux server.   

-----    
## Install   

This tool works with Python3.
You can use the tool by cloning the repository and installing the library with the pip command.
When installing on a virtual environment such as venv, it is necessary to create the environment and switch to the virtual environment before executing the following command.   

### Prerequisites   

The Tool requires two service account keys. One is a Google Analytics service account and the other is a Google Cloud Storage and Big Query service account.
You can specify different keys for each, You can also reuse a single key file, assuming you give the account permissions.

### Git clone and install libraries           
```console
git clone https://github.com/kemsakurai/ga-to-gbq.git    
cd ga-to-gbq
pip install -r requirements.txt
```

-----

## Command usage      

* **job list**   
```console
export FLASK_APP=cli
flask job 
```
```console
Usage: flask job [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  compress_gcs_data  Compress data uploaded Google Cloud Storage to gzip
  load_to_gbq        Load to Google Big Query from Google Cloud Storage
  merge_data_to_gcs  Merge database data and upload Google Cloud Storage
  save_ga            Save Google Anlaytics data in the database

```
Outputs a list of commands.

* **save_ga**    
```console
export FLASK_APP=cli
DATE="2020-05-18"
VIEW_ID="10xxxxxxx"
GA_CREDENTIALS_PATH=".ga_client.json"
flask job save_ga "$DATE" "$VIEW_ID" "$GA_CREDENTIALS_PATH"
```
Store Google analytics data in the sqlite database. Since the API of Gooogle Analytics has a limit on the number of dimensions and metrics that can be output, execute the API multiple times and save each in a table.   


* **merge_data_to_gcs**     
```console
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
export FLASK_APP=cli
DATE="2020-05-18"
BUCKET_NAME="monotalk.appspot.com"
FILE_DIR_NAME="GA Statistics/www.monotalk.xyz/"
flask job merge_data_to_gcs "$DATE" "$BUCKET_NAME" "$FILE_DIR_NAME"
```
The data saved with the `save_ga` command is merged into one, and the merged result is uploaded to Google Cloud Storage. The file is uploaded in JSON format.    


* **load_to_gbq**
```console
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
export FLASK_APP=cli
DATE="2020-05-18"
DATA_SET_ID="monotalk.GA_Statistics"
GCS_DIR="gs://monotalk.appspot.com/GA Statistics/www.monotalk.xyz/"
flask job load_to_gbq "$DATE" "$DATA_SET_ID" "$GCS_DIR"
```
Load the JSON file uploaded to Google Cloud Storage into Google BigQuery.   

* **compress_gcs_data**   
```console
export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
export FLASK_APP=cli
DATE="2020-05-18"
BUCKET_NAME="monotalk.appspot.com"
FILE_DIR_NAME="GA Statistics/www.monotalk.xyz/"
flask job compress_gcs_data "$DATE" "$BUCKET_NAME" "$FILE_DIR_NAME"
```
Compress the JSON file uploaded to Google Cloud Storage into gzip. A new compressed gzip file will be uploaded and the original JSON file will be deleted.    

---

## Command execution order   

Execute the commands on a daily basis in the following order.
Data of Google Analytics may not be acquired if specified on the day.
We recommend that you specify a date that is at least one day in advance and execute it.

1. save_ga  
2. merge_data_to_gcs  
3. load_to_gbq   
4. compress_gcs_data     

---   
## Job Scheduling EXAMPLES

This is an example of a script that executes a Python job and a cron job that uses that script.    

* **run_ga_to_gbq.sh**  
```console
#!/bin/bash

shellName=$(basename $0)
homeDir=$(pwd)
toolHome="/home/jobuser/tools/ga-to-gbq"

prepareRun() {
  cd $toolHome
  source /home/jobuser/venv/ga_to_gbq/bin/activate
  export FLASK_APP=cli
  export GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
}

getTreeDaysAgo() {
  if [ "$(uname)" == 'Darwin' ]; then
    DATE=`date -v-3d +'%Y-%m-%d'`
  elif [ "$(expr substr $(uname -s) 1 5)" == 'Linux' ]; then
    DATE=`date '+%Y-%m-%d' --date '3 days ago'`
  elif [ "$(expr substr $(uname -s) 1 10)" == 'MINGW32_NT' ]; then
    DATE=`date '+%Y-%m-%d' --date '3 days ago'`
  else
    echo "Your platform ($(uname -a)) is not supported."
    exit 1
  fi
  echo $DATE
}

sub_help(){
    echo "Usage: $shellName <subcommand> [options]\n"
    echo "Subcommands:"
    echo "    saveGa    Save Google Analytics data to SQLite database."
    echo "    mergeDataToGcs Merge SQLite data and upload to Google Cloud Storage."
    echo "    loadToGbq Load data to Google Big Query from Google Cloud Storage."
    echo "    compressGcsData Compress data uploaded Google Cloud Storage to gzip."
    echo ""
    echo "For help with each subcommand run:"
    echo "$shellName <subcommand> -h|--help"
    echo ""
}

sub_loadToGbq() {
  prepareRun
  DATE=`getTreeDaysAgo`
  DATA_SET_ID="monotalk-analytics.GA_Statistics"
  GCS_DIR="gs://monotalk.appspot.com/GA Statistics/www.monotalk.xyz/"
  flask job load_to_gbq \
  "$DATE" \
  "$DATA_SET_ID" \
  "$GCS_DIR"

}

sub_mergeDataToGcs() {
  prepareRun
  DATE=`getTreeDaysAgo`
  BUCKET_NAME="monotalk-analytics.com"
  FILE_DIR_NAME="GA Statistics/www.monotalk.xyz/"
  flask job merge_data_to_gcs \
  "$DATE" \
  "$BUCKET_NAME" \
  "$FILE_DIR_NAME"
}

sub_saveGa() {
  prepareRun
  rm -f ga.db
  DATE=`getTreeDaysAgo`
  VIEW_ID="YOUR_VIEW_ID"
  GA_CREDENTIALS_PATH="./ga_client.json"
  flask job save_ga \
  "$DATE" \
  "$VIEW_ID" \
  "$GA_CREDENTIALS_PATH"
}

sub_compressGcsData() {
  prepareRun
  DATE=`getTreeDaysAgo`
  BUCKET_NAME="monotalk-analytics.appspot.com"
  FILE_DIR_NAME="GA Statistics/www.monotalk.xyz/"
  flask job compress_gcs_data \
  "$DATE" \
  "$BUCKET_NAME" \
  "$FILE_DIR_NAME"
}

for subcommand in "$@"; do
    case $subcommand in
        "" | "-h" | "--help")
            sub_help
            ;;
        *)
            shift
            sub_${subcommand} $@
            returnCode=$?
            if [ $returnCode = 127 ]; then
                echo "Error: '$subcommand' is not a known subcommand." >&2
                echo "       Run '$shellName --help' for a list of known subcommands." >&2
                exit 1
            elif [ $returnCode = 1 ]; then
                echo "Error: '$subcommand' is failed.." >&2
                exit 1            
            fi
            ;;
    esac
done

```

* **crontab**       
```console
# coomon settings
MAILTO="your.mail@example.com"
MAILFROM="error-notifications@example.com"
LOG_DIR="/var/log"
# gsc-to-gbq
SH_GSC_TO_GBQ="/home/jobuser/scripts/run_gsc_to_gbq.sh"

00 02 * * * /bin/sh $SH_GA_TO_GBQ saveGa &>> $LOG_DIR/ga_to_gbq_saveGa.log && /bin/sh $SH_GA_TO_GBQ mergeDataToGcs &>> $LOG_DIR/ga_to_gbq_mergeDataToGcs.log && /bin/sh $SH_GA_TO_GBQ loadToGbq &>> $LOG_DIR/ga_to_gbq_loadToGbq.log && /bin/sh $SH_GA_TO_GBQ compressGcsData &>> $LOG_DIR/ga_to_gbq_compressGcsData.log
```

---

## LICENSE   

MIT
