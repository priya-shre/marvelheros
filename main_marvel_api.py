from marvel_api import MarvelAPI
from exceptions import MarvelAPIException
from marvel_bigquery_upload import MarvelBigQueryUploader
from logger import setup_logging

def main():
    """ Main file of the project
    1)Collects data from marvel api
    2)Uploads data to bigquery
    """
    log = setup_logging()
    try:
        log.info("Starting Marvel Project")
        marvel_api = MarvelAPI()
        log.info("Getting Characters data from Marvel")
        marvel_api.fetch_characters(limit=100)
        log.info("Data set downloaded successfully from Marvel")
        log.info("Starting to upload Marvel data to BigQuery")
        uploader = MarvelBigQueryUploader()
        uploader.upload_csv_to_bigquery()
        log.info("Successfully uploaded data to BigQuery")

    except MarvelAPIException as e:
        log.error(f"Marvel API Exception: {e}")

if __name__ == "__main__":
    main()
