import json
import csv
from datetime import datetime
from google.cloud import bigquery
from google.auth import exceptions 
from google.cloud.exceptions import NotFound
from logger import setup_logging
from typing import Optional

class MarvelBigQueryUploader:
    def __init__(self):
        self.log = setup_logging()
        try: 
            # Load configuration from the config.json file
            with open("config.json", 'r') as file:
                self.config = json.load(file)

            self.project_id = self.config['bigquery']['project_id']
            self.dataset_id = self.config['bigquery']['dataset_id']
            self.table_id = self.config['bigquery']['table_id']
            self.csv_file_path = self.config['bigquery']['csv_file_path']
            self.client = bigquery.Client(project=self.project_id)  
            self.dataset_ref = bigquery.DatasetReference(self.project_id, self.dataset_id)
            self.table_ref = self.dataset_ref.table(self.table_id)
            self.temp_file = "updated_marvel_character.csv"
        except exceptions.DefaultCredentialsError as e:
            self.log.error(f"Failed to specify credentials: {e}")
        except Exception as e:
            self.log.error(f"Exception occurred: {e}") 
            
    def extract_year(self,timestamp)-> Optional[str]:
        """ From a format of 2014-04-29T14:18:17-0400 it extracts the year

        Args:
            timestamp (_type_): string

        Returns:
            _type_: year
        """
        try:
            # Handling formats like '-0001-11-30T00:00:00-0500'
            if timestamp == "-0001-11-30T00:00:00-0500":
                self.log.info("Returning null value for year in place of unsual string")
                return "" 
            
            # Parse the timestamp and extract the year
            parsed_date = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
            return str(parsed_date.year)  # Return only the year as a string
        
        except ValueError:
            self.log.info("Returning null value for year in place of unsual string")
            return ""
        
    def update_csv_for_bigquery_upload(self)-> bool:
        """ Clean the datatime format to make the file ready
        to be uploaded to BigQuery

        Returns:
            bool: True if file updated else false
        """
        input_file= self.csv_file_path
        output_file = self.temp_file
        self.log.info("Updating csv to be ready for bigQuery upload")
        try:
            with open(input_file, mode='r', newline='') as infile, \
                open(output_file, mode='w', newline='') as outfile:
                
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                
                headers = next(reader, None) 
                if headers:
                    writer.writerow(headers) 
              
                for row in reader:
                    row[2] = self.extract_year(row[2])
                    writer.writerow(row)
            
            # If the execution completes successfully, return True
                
                return True
    
        except Exception as e:
            self.log.error(f"An error occurred: {e}")
            return False
    
    def delete_dataset_tables(self)-> bool:
        """ delete any pre-exiting table in the dataset
        (if you need to test the file it will help,
        not to mess up with the pre-existing table in BigQuery)
        
        Returns:
            bool: True if table is deleted , False if any exception occurs
        """

        tables = self.client.list_tables(f'{self.project_id}.{self.dataset_id}')
        for table in tables:
            self.client.delete_table(table)
            self.log.info(f"Deleted Table {table}")
        self.log.info('Pre exisiting Tables deleted')
        
    def check_if_table_exits(self)->bool:
        """
        I do not want any pre-existing table 
        so if exits it calls the delete method
        if not found then also it is a pass

        Returns:
            bool: True
        """
        try: 
            tables_list =  self.client.get_table
            self.log.info(f"Pre-exisiting table found:  {tables_list}")
            self.delete_dataset_tables()
            self.log.info("Deleted pre-exisitng tables")
            return True
        
        except NotFound as error:
            self.log.error(f"No table found in {self.dataset_id}")
            return True
                      
        
    def upload_csv_to_bigquery(self):
        """
        Uploads the updated csv with correct formated values to the BigQuery
        """
        
        if self.update_csv_for_bigquery_upload():
            self.log.info("Csv updated with valid values")
        
            if self.check_if_table_exits():
                self.log.info("Starting to upload the csv to BigQuery")
                
                job_config = bigquery.LoadJobConfig()
                job_config.autodetect = True          
                job_config.source_format = bigquery.SourceFormat.CSV
                job_config.skip_leading_rows = 1
                
                with open(self.temp_file, "rb") as source_file:
                    job = self.client.load_table_from_file(
                        source_file,
                        self.table_ref,
                        location="northamerica-northeast2",  
                        job_config=job_config,
                    )  # API request

                job.result()  # Waits for table load to complete.
                self.log.info(
                    "Loaded {} rows into {}:{}.".format(
                        job.output_rows, self.dataset_id, self.table_ref.table_id
                    )
                )
            
        

    
