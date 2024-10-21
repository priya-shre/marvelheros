import hashlib
import time
import json
import csv
import requests
from logger import setup_logging
from typing import Optional, Tuple, Dict
from exceptions import (
    MarvelAPIAuthenticationError,
    MarvelAPIDataError,
    MarvelAPIResourceNotFound,
    MarvelAPIRateLimitExceeded,
    MarvelAPIException
)

class MarvelAPI:
    def __init__(self):
        self.base_url = "http://gateway.marvel.com/v1/public/"
        self.public_key, self.private_key = self.load_api_keys()
        # Setup logger with type hint
        self.log = setup_logging()

    def load_api_keys(self) -> Tuple [str , str] :
        """_summary_

        Raises:
            MarvelAPIException: Config file for marvel keys not found
            MarvelAPIException: Invalid config file format

        Returns:
            Tuple [str , str]: _description_
        """
        try:
            with open('config.json') as config_file:
                config = json.load(config_file)
                public_key = config['marvel']['public_key']
                private_key = config['marvel']['private_key']
            return public_key, private_key
        except FileNotFoundError:
            self.log.error("Config file for marvel keys not found")
            raise MarvelAPIException("Config file not found.")
        except KeyError as e:
            self.log.error(f"Invalid format : {e}")
            raise MarvelAPIException("Invalid config file format.")

    def create_auth_params(self) -> Dict[str, str]:
        """
        Generates authentication parameters required to make requests to the Marvel API
        Returns:
            Dict[str, str]: A dictionary containing the authentication parameters
        """
        self.log.info("Setting up the hash_result")
        ts = str(time.time())  # Timestamp
        hash_input = ts + self.private_key + self.public_key  # Create the hash string
        hash_result = hashlib.md5(hash_input.encode('utf-8')).hexdigest()  # MD5 hash
        return {
            "ts": ts,
            "apikey": self.public_key,
            "hash": hash_result
        }

    def get_marvel_data(self, endpoint, params={}) -> Optional[dict]:
        """
        Sends request to get the required data from marvel api

        Args:
            endpoint (_type_): url to get the data eg "get /v1/public/characters"
            params (dict, optional): _description_. Defaults to {}.

        Returns:
            Optional[dict]: json is captured as output data
        """
        auth_params = self.create_auth_params()
        params.update(auth_params)

        try:
            response = requests.get(self.base_url + endpoint, params=params)
            #status code 200 means request successfully completed
            self.log.info(f"check request response : {response}")
            response.raise_for_status() 
            return response.json()  
        except requests.exceptions.RequestException as e:
            self.log.error(f"Exception occured while fetching the data {e}")
            self.handle_request_error(response) 
            return None  
        
    def handle_request_error(self, response ):
        """ Handles exception from the api response
         as per the marvel api dcoumentation

        Args:
            response (_type_): error

        Raises:
            MarvelAPIAuthenticationError:Authentication failed. Please check your API keys.
            MarvelAPIResourceNotFound: The requested resource was not found.
            MarvelAPIDataError: Error retrieving data from the Marvel API.
            MarvelAPIRateLimitExceeded: Rate limit exceeded. Try again later
            MarvelAPIException: Any unknown exception
        """
        if response.status_code == 401:
            raise MarvelAPIAuthenticationError("Authentication failed. Please check your API keys.")
        elif response.status_code == 404:
            raise MarvelAPIResourceNotFound("The requested resource was not found.")
        elif response.status_code == 500:
            raise MarvelAPIDataError("Error retrieving data from the Marvel API.")
        elif response.status_code == 429:
            raise MarvelAPIRateLimitExceeded("Rate limit exceeded. Try again later.")
        else:
            raise MarvelAPIException(f"An unknown error occurred: {response.text}")

    def convert_characters_json_to_csv(self, json_data, csv_filename):
        self.log.info(f"converting json to csv file")
        characters_data = json_data['data']['results']
        fieldnames = ['id', 'name', 'modified', 
                      'comics_available', 'series_available',
                      'stories_available', 'events_available']

        with open(
            csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for character in characters_data:
                row = {
                    'id': character.get('id', ''),
                    'name': character.get('name', ''),
                    'modified': character.get('modified', ''),
                    'comics_available': character.get('comics', {}).get('available', ''),
                    'series_available': character.get('series', {}).get('available', ''),
                    'stories_available': character.get('stories', {}).get('available', ''),
                    'events_available': character.get('events', {}).get('available', '')
                }
                writer.writerow(row)
        self.log.info(f"Character data successfully written to {csv_filename}")
       



    def fetch_characters(self, limit=100):
        """Fetches a list of Marvel characters from the Marvel API.

        This method sends requests to the Marvel API to
        retrieve character data in batches.
        It handles pagination by updating the `offset` 
        parameter and fetching data until 
        the desired number of characters is fetched.

        Args:
            limit (int, optional): The maximum number of 
            characters to fetch per request (default is 100).
            offset (int, optional): The number of characters 
            to skip before starting to fetch (default is 0).

        Returns:
            Optional[list]: A list of character data dictionaries.
            Returns `None` if no data is fetched or an error occurs.
        
        Raises:
            MarvelAPIException: If any error occurs during the 
            request or data retrieval process.
        """
        params = {
            "limit": limit,
        }
        all_characters = []
        offset = 0

        try:
            while True:
                params['offset'] = offset
                result = self.get_marvel_data("characters", params)

                if result:
                    characters = result['data']['results']
                    all_characters.extend(characters)

                    # If fewer than the limit, stop fetching
                    if len(characters) < limit:
                        break

                    offset += limit
                else:
                    self.log.info("No data fetched.")
                    break

            # Save the fetched character data to a JSON file
            with open('character_data.json', 'w') as json_file:
                json.dump(all_characters, json_file, indent=4)
            self.log.info("Character data has been saved to character_data.json.")

            # Convert character data to CSV
            self.convert_characters_json_to_csv({'data': {'results': all_characters}}, 'marvel_characters.csv')

            return all_characters

        except requests.exceptions.RequestException as e:
            self.log.error(f"Error fetching data: {e}")
            return None