# marvel-project
# marvel-project
This project automates the process of collecting Marvel character data, transforming it into a structured format, and loading it into BigQuery for analysis. It is an end-to-end pipeline that can be reused or expanded for other datasets from Marvel or even other APIs.

Pre- requisites:
1) Create accound on marvel developers to get the keys ( never share the keys)
2) For big query 
    1) Install google cloud cli installer https://cloud.google.com/sdk/docs/install
    2) Once the set up cmd window will pop up which will ask you to continue
    3) Select y to continue and authenticate your google account
    4)Once your google account authenticated,it will now show
     you all your projects linked to your google account and ask you to select any one on which you want to work
    5) Select your project number on the cmd 
    6) Now run gcloud auth application-default login (for working on a local shell) , this will again authenticate your google account https://cloud.google.com/bigquery/docs/authentication/getting-started#python
     
 
Marvel API Interaction:

The MarvelAPI class handles authentication and requests to the Marvel API. It fetches data such as Marvel character details using public and private keys for authentication.
Authentication is done by generating a unique hash using a timestamp, public key, and private key.
The API supports fetching data with pagination, so large amounts of data are retrieved in batches.
The project includes error handling based on Marvel API status codes, such as handling rate limits, authentication issues, and missing resources.
Data Transformation:

After fetching character data from the API, the project converts the JSON data into a CSV file. This CSV file contains fields like id, name, modified, and availability of comics, series, stories, and events for each character.
The CSV conversion ensures that the data is clean, structured, and ready for further processing.
BigQuery Integration:

The MarvelBigQueryUploader class manages the process of uploading the CSV data to Google BigQuery.
Before uploading, the update_csv_for_bigquery_upload() method modifies the timestamp data to extract only the year, making the data more readable and consistent.
The project checks for any pre-existing tables in BigQuery and deletes them if found, ensuring clean uploads without interference from old data.
Finally, the updated CSV is uploaded to BigQuery in the appropriate dataset and table.
Key Features:
Error Handling: Robust error handling is implemented for both API requests and file uploads. Specific exceptions are raised for issues like authentication failures, rate limits, or malformed data.
Logging: The project uses a logging system to track events, errors, and the progress of operations. This helps in troubleshooting and ensures smooth execution.
Data Clean-up: The project includes mechanisms to clean up any pre-existing data in BigQuery tables to avoid data duplication or conflict.
