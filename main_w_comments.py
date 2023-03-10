import time
import requests
import json
import os
import logging
import shutil
from pprint import pprint
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# This class is used to download photos from VK social network

class VkSaver:

    url = 'https://api.vk.com/method/'

    # Class constructor. Sets user access token, API version, user ID and number of photos to download.
    def __init__(self, token: str, version, user_id, number=5):
        
        # Set params with access token and API version
        self.params = {
            'access_token': token,
            'v': version    
        }
        
        # If number parameter was not passed, set number_of_photos to 5
        # Otherwise, set it to the passed value converted to an integer
        if not number:
            self.number_of_photos = 5
        else:
            self.number_of_photos = int(number)
        
        # Send request to API to get user ID
        get_user_id_url = self.url + 'users.get'
        user_params = {
            'user_ids': user_id
        }
        result = requests.get(get_user_id_url, params={**self.params, **user_params}).json()
        
        # Set user ID based on response
        self.user_id = result['response'][0]['id']
    
    # Returns folder name based on user name and album name
    def get_folder_name(self):

        # Send request to API to get user name
        get_folder_name_url = self.url + 'users.get'
        user_params = {
            'user_ids': self.user_id,
            'v':'5.131' 
        }
        result = requests.get(get_folder_name_url, params={**self.params, **user_params}).json()
        
        # Format folder name based on user name and album name
        res = f"{result['response'][0]['first_name']} {result['response'][0]['last_name']} {self.album_name}"
        return res
    
    # Gets album ID and name from user
    def get_album(self):

        album_dict = {}

        # Send request to API to get all user albums
        get_album_url = self.url + 'photos.getAlbums'
        user_params = {
            'owner_id' : self.user_id,
            'need_system' : '1'
        }
        result = requests.get(get_album_url, params={**self.params, **user_params}).json()

        count = 0
        
        # Display all user albums and their corresponding number
        for album in result['response']['items']:
            count +=1
            album_dict[count] = [album['id'], album['title']]
            print(f'{count} - {album["title"]}')
        
        # Prompt user to select album number
        album_select = int(input())
        
        # If selected album number is valid, set album ID and album name based on user selection
        if album_select in album_dict.keys():
            self.album_id = album_dict[album_select][0]
        else:
            self.album_id = -6
        self.album_name = album_dict[album_select][1]
    
    # Gets list of photos and their metadata from selected album
    def get_photos(self, photo_sizes=1):

        # Send request to API to get all photos from selected album
        get_photos_url = self.url + 'photos.get'
        album_params = {
            'owner_id' : self.user_id,
            'album_id' : self.album_id,
            'photo_sizes' : photo_sizes,
            'extended' : 1
        }
        result = requests.get(get_photos_url, params={**self.params, **album_params}).json()
        
        # Return list of photos and their metadata
        return result['response']['items']

    # Gets download URLs
    def get_photos_urls(self):

        to_download = {}
        data_to_json = []
        list = self.get_photos(self.user_id)
        priority_old_photos = 'wzyrqpoxms'

           # It loops through the photos in the list.
        for photo in list:
            # If the number_of_photos is 0, it does nothing.
            if self.number_of_photos == 0:
                pass
            else:
                # If the number_of_photos is not 0, it checks if the number of likes is in to_download.keys().
                if photo['likes']['count'] not in to_download.keys():
                    # If it is not in to_download.keys(), it assigns the number of likes as the file_name.
                    file_name = photo['likes']['count']
                else:
                    # If it is in to_download.keys(), it assigns the number of likes and the date as the file_name.
                    file_name = str(photo['likes']['count']) + '_' + datetime.fromtimestamp(photo['date']).strftime("%Y-%m-%d_%H_%M_%S")
                # It initializes a variable called max_size to 0.
                max_size = 0
                # It loops through the sizes of the photo.
                for size in photo['sizes']:
                    # It initializes a counter called counter_old_photos to 9.
                    counter_old_photos = 9
                    # If the height of the size is greater than 0.
                    if size['height'] > 0:
                        # If the height of the size is greater than max_size, it assigns the url of the size to to_download[file_name].
                        if size['height'] > max_size:
                            to_download[file_name] = size['url']
                            max_size = size['height']
                            size_to_save = f"{size['width']}*{size['height']}"
                    else:
                        # If the height of the size is not greater than 0, it checks if the type of the size is in priority_old_photos.
                        if priority_old_photos.index(size['type']) < counter_old_photos:
                            # If it is in priority_old_photos, it assigns the url of the size to to_download[file_name].
                            to_download[file_name] = size['url']
                            counter_old_photos = priority_old_photos.index(size['type'])
                            size_to_save = size['type']
            # It appends a dictionary to data_to_json that has the file_name and the size_to_save.
            data_to_json.append({'file_name': f'{file_name}.jpg', 'size':size_to_save})
            # It decreases the number_of_photos by 1.
            self.number_of_photos -= 1
        # It opens a file called result.json and writes the data_to_json to it in json format.
        with open('result.json', 'w') as file:
            json.dump(data_to_json, file)
        # It returns to_download dictionary.
        return to_download

    def save_photos(self):
        # This method prints the user_id and assigns the user_id to a variable called user_id.

        # If the folder doesn't exist, it creates the folder using the get_folder_name() method.
        if not os.path.exists(self.get_folder_name()):
            os.makedirs(self.get_folder_name())
        folder = self.get_folder_name()
        # It loops through the key-value pairs
        for key, value in self.get_photos_urls().items():
            # It sends a request to get the content of the url and assigns it to a variable called response.
            response = requests.get(value)
        # It creates a file called key.jpg in the folder created earlier and writes the content of the response to it.
        with open(os.path.join(folder, str(key) +'.jpg'), 'wb') as file:
            file.write(response.content)
        # It returns None.
        return None


# This is a class for uploading files to Yandex Disk using their API
class YdUploader:
    # The URL endpoint for the Yandex Disk API
    url = "https://cloud-api.yandex.net/v1/disk/resources/"

    def __init__(self, token: str):
        # The class constructor, which takes a token as input and saves it as an instance variable
        self.token = token

    def get_headers(self):
        # A method for creating the authorization headers for API requests
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }
    
    def get_link(self, file_path):
        # A method for obtaining an upload link for a specific file on Yandex Disk
        upload_url = self.url + "upload"
        headers = self.get_headers()
        link_params = {
            "path": file_path,
            "overwrite": "True"
            }
        response = requests.get(upload_url, headers=headers, params=link_params)
        return response.json()

    def create_folder(self):
        # A method for creating a new folder on Yandex Disk
        folder_path = vk_client.get_folder_name() # Here i don't like it how code calls vk_client instance of VkSaver class. But have no idea how to make it right
        headers = self.get_headers()
        folder_params = {
            'path' : folder_path
        }
        response = requests.put(self.url, headers=headers, params=folder_params)
        return folder_path

    def upload(self):
        # A method for uploading all files in a local folder to Yandex Disk
        folder_name = vk_client.get_folder_name() # Here i don't like it how code calls vk_client instance of VkSaver class. But have no idea how to make it right
        folder_path = self.create_folder()
        folder_content = os.listdir(folder_path)
        for file_name in folder_content:
            link = self.get_link(file_path= f'{folder_name}/{file_name}').get('href', '')
            if os.path.isfile(os.path.join(folder_path, file_name)):
                with open(os.path.join(folder_path, file_name), 'br') as file:
                    response = requests.put(link, file)
                response.raise_for_status()
                if response.status_code == 201:
                    print(f'\nFile {file_name} has been uploaded to folder "{folder_name}" with URL: "{link}".\n')
                    
class GdUploader:

    # Google Drive API url
    url = "https://www.googleapis.com/upload/drive/v3/files?"

    def __init__(self):
        # Define OAuth2 authentication scope
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.creds = None

        # If token file exists, use it to authenticate
        if os.path.exists('gd_token.json'):
            with open('gd_token.json', 'r') as file:
                token = json.load(file)
            self.creds = Credentials.from_authorized_user_info(token, SCOPES)

        # If no valid token found, try to refresh or authorize
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except:
                    # If unable to refresh token, authenticate using client_secrets.json
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)

        # Write credentials to token file
        with open('gd_token.json', 'w') as token:
            token.write(self.creds.to_json())

        # Set refresh flag to true
        with open('gd_token.json', 'r') as f:
            data = json.load(f)
        refresh_flag = {'refresh_token': 'True'}
        data.update(refresh_flag)
        with open('gd_token.json', 'w') as f:
            json.dump(data, f)

    def get_headers(self):
        # Returns authentication headers
        headers = {
            'Authorization': f'Bearer {self.creds.token}',
            'Content-Type': 'application/octet-stream'
        }
        return headers
    
    def create_folder(self):
        # Creates a folder in Google Drive
        folder_name = vk_client.get_folder_name() # Here i don't like it how code calls vk_client instance of VkSaver class. But have no idea how to make it right
        drive_service = build('drive', 'v3', credentials=self.creds)
        folder_params = {
            'name' : folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        folder = drive_service.files().create(body=folder_params, fields='id').execute()
        return folder

    def upload(self):
        # Uploads files to Google Drive

        folder_name = vk_client.get_folder_name()
        drive_service = build('drive', 'v3', credentials=self.creds)
        folder = self.create_folder()

        # Upload each file to folder
        for file_name in os.listdir(folder_name):

            file_path= f'{folder_name}/{file_name}'

            # If folder not found, print error message
            if len(folder) == 0:
                print(f'Folder "{folder_name}" not found.')
            else:
                folder_id = folder[0]['id']
                 # Set file metadata and upload the file
                file_metadata = {'name': os.path.basename(file_path), 'parents': [folder.get("id")]}
                media = MediaFileUpload(file_path, resumable=True)
                file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

                # Print upload confirmation message
                print(f'\nFile "{file_metadata["name"]}" has been uploaded to folder "{folder_name}" with URL: "https://drive.google.com/drive/folders/{folder.get("id")}".\n')

if __name__ == '__main__':

    # This sets up the logging level to debug
    logging.basicConfig(level=logging.DEBUG)

    # This creates a loop that continues until an exception is caught
    while True:
        try:
            # This opens and reads the contents of the 'vk_token.txt' file
            with open('vk_token.txt', 'r') as file:
                vk_token = file.read().strip()
        except:
            # If an exception occurs, the user is prompted to enter a Vkontakte token
            vk_token = input('\nPlease enter Vkontakte token:\n')
        
        # This prompts the user to enter their Vkontakte user id or screen name
        vk_id = input('\nPlease enter Vkontakte user id or screen name:\n')

        # This prompts the user to enter the number of photos to backup
        number_of_photos = input('\nPlease enter number of photos to backup:\n')

        # This creates a VkSaver object with the given Vkontakte token, version, user id/screen name, and number of photos
        vk_client = VkSaver(vk_token, '5.131',vk_id, number_of_photos) 
        
        # This calls the get_album method of the VkSaver object
        vk_client.get_album()

        # This prompts the user to select a target drive
        com = input('\nSelect target drive:\n'
                    '1 - Yandex.Disk\n'
                    '2 - GoogleDrive\n')
        
        # If the user selects Yandex.Disk, this code block runs
        if com == '1':
            try:
                # This opens and reads the contents of the 'yd_token.txt' file
                with open('yd_token.txt', 'r') as file:
                    yd_token = file.read().strip()
            except:
                # If an exception occurs, the user is prompted to enter a Yandex token and the program waits for 5 seconds
                yd_token = input('\nPlease enter Yandex token:\n')
                time.sleep(5)

            # This creates a YdUploader object with the given Yandex token
            yd_instance = YdUploader(yd_token)

            # This calls the save_photos method of the VkSaver object
            vk_client.save_photos()

            # This calls the upload method of the YdUploader object
            yd_instance.upload()

            # This deletes the folder containing the backed up photos
            shutil.rmtree(vk_client.get_folder_name())

        # If the user selects GoogleDrive, this code block runs
        elif com == '2':

            # This creates a GdUploader object
            gd_instance = GdUploader()

            # This calls the save_photos method of the VkSaver object
            vk_client.save_photos()

            # This calls the upload method of the GdUploader object
            gd_instance.upload()

            # This deletes the folder containing the backed up photos
            shutil.rmtree(vk_client.get_folder_name())

        # If the user selects an invalid option, this code block runs
        else:
            print('\nWrong input. Please repeat.\n')
