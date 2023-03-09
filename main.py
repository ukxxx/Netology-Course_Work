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


class VkSaver:

    url = 'https://api.vk.com/method/'

    def __init__(self, token: str, version, user_id, number=5):
        self.params = {
            'access_token': token,
            'v': version    
        }
        if not number:
            self.number_of_photos = 5
        else:
            self.number_of_photos = int(number)
        
        get_user_id_url = self.url + 'users.get'
        user_params = {
            'user_ids': user_id
        }
        result = requests.get(get_user_id_url, params={**self.params, **user_params}).json()
        self.user_id = result['response'][0]['id']

    def get_folder_name(self):

        get_folder_name_url = self.url + 'users.get'
        user_params = {
            'user_ids': self.user_id,
            'v':'5.131' 
        }
        result = requests.get(get_folder_name_url, params={**self.params, **user_params}).json()
        res = f"{result['response'][0]['first_name']} {result['response'][0]['last_name']} {self.album_name}"
        return res

    def get_album(self):

        album_dict = {}

        get_album_url = self.url + 'photos.getAlbums'
        user_params = {
            'owner_id' : self.user_id,
            'need_system' : '1'
        }
        result = requests.get(get_album_url, params={**self.params, **user_params}).json()

        count = 0
        print('\nSelect user album number:')
        for album in result['response']['items']:
            count +=1
            album_dict[count] = [album['id'], album['title']]
            print(f'{count} - {album["title"]}')
        album_select = int(input())
        if album_select in album_dict.keys():
            self.album_id = album_dict[album_select][0]
        else:
            self.album_id = -6
        self.album_name = album_dict[album_select][1]
    
    def get_photos(self, photo_sizes=1):

        get_photos_url = self.url + 'photos.get'

        album_params = {
            'owner_id' : self.user_id,
            'album_id' : self.album_id,
            'photo_sizes' : photo_sizes,
            'extended' : 1
        }
        result = requests.get(get_photos_url, params={**self.params, **album_params}).json()
        return result['response']['items']

    def get_photos_urls(self):

        to_download = {}
        data_to_json = []
        list = self.get_photos(self.user_id)
        priority_old_photos = 'wzyrqpoxms'

        for photo in list:
            if self.number_of_photos == 0:
                pass
            else:
                if photo['likes']['count'] not in to_download.keys():
                    file_name = photo['likes']['count']
                else:
                    file_name = str(photo['likes']['count']) + '_' + datetime.fromtimestamp(photo['date']).strftime("%Y-%m-%d")
                max_size = 0
                for size in photo['sizes']:
                    counter_old_photos = 9
                    if size['height'] > 0:
                        if size['height'] > max_size:
                            to_download[file_name] = size['url']
                            max_size = size['height']
                            size_to_save = f"{size['width']}*{size['height']}"
                    else:
                        if priority_old_photos.index(size['type']) < counter_old_photos:
                            to_download[file_name] = size['url']
                            counter_old_photos = priority_old_photos.index(size['type'])
                            size_to_save = size['type']
                data_to_json.append({'file_name': f'{file_name}.jpg', 'size':size_to_save})
                self.number_of_photos -= 1
        with open('result.json', 'w') as file:
            json.dump(data_to_json, file)

        return to_download
    
    def save_photos(self):
        user_id = self.user_id
        if not os.path.exists(self.get_folder_name()):
            os.makedirs(self.get_folder_name())

        for key, value in self.get_photos_urls().items():
            response = requests.get(value)
            with open(os.path.join(self.get_folder_name(), str(key) +'.jpg'), 'wb') as file:
                file.write(response.content)
        return None

class YdUploader:

    url = "https://cloud-api.yandex.net/v1/disk/resources/"

    def __init__(self, token: str):
        self.token = token

    def get_headers(self):

        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }
    
    def get_link(self, file_path):

        upload_url = self.url + "upload"
        headers = self.get_headers()
        link_params = {
            "path": file_path,
            "overwrite": "True"
            }
        response = requests.get(upload_url, headers=headers, params=link_params)
        return response.json()

    def create_folder(self):

        folder_path = vk_client.get_folder_name()
        headers = self.get_headers()
        folder_params = {
            'path' : folder_path
        }
        response = requests.put(self.url, headers=headers, params=folder_params)
        return folder_path

    def upload(self):

        folder_name = vk_client.get_folder_name()
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

    url = "https://www.googleapis.com/upload/drive/v3/files?"

    def __init__(self):

        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.creds = None

        if os.path.exists('gd_token.json'):
            with open('gd_token.json', 'r') as file:
                token = json.load(file)
            self.creds = Credentials.from_authorized_user_info(token, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)

        with open('gd_token.json', 'w') as token:
            token.write(self.creds.to_json())
        with open('gd_token.json', 'r') as f:
            data = json.load(f)
        refresh_flag = {'refresh_token': 'True'}
        data.update(refresh_flag)
        with open('gd_token.json', 'w') as f:
            json.dump(data, f)

    def get_headers(self):

        headers = {
            'Authorization': f'Bearer {self.creds.token}',
            'Content-Type': 'application/octet-stream'
        }
        return headers
    
    def create_folder(self):

        folder_name = vk_client.get_folder_name()
        drive_service = build('drive', 'v3', credentials=self.creds)
        folder_params = {
            'name' : folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        folder = drive_service.files().create(body=folder_params, fields='id').execute()
        return folder

    def upload(self):

        folder_name = vk_client.get_folder_name()
        folder_content = os.listdir(folder_name)
        drive_service = build('drive', 'v3', credentials=self.creds)
        self.create_folder()

        for file_name in folder_content:
            folder_query = "mimeType='application/vnd.google-apps.folder' and trashed = false and name = '" + folder_name + "'"
            folder = drive_service.files().list(q=folder_query, fields='files(id)').execute().get('files', [])
            file_path= f'{folder_name}/{file_name}'
            if len(folder) == 0:
                print(f'Folder "{folder_name}" not found.')
            else:
                folder_id = folder[0]['id']
                file_metadata = {'name': os.path.basename(file_path), 'parents': [folder_id]}
                media = MediaFileUpload(file_path, resumable=True)
                file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print(f'\nFile "{file_metadata["name"]}" has been uploaded to folder "{folder_name}" with URL: "https://drive.google.com/drive/folders/{folder_id}".\n')

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    while True:
        try:
            with open('vk_token.txt', 'r') as file:
                vk_token = file.read().strip()
        except:
            vk_token = input('\nPlease enter Vkontakte token:\n')
        vk_id = input('\nPlease enter Vkontakte user id or its screen name:\n')
        number_of_photos = input('\nPlease enter the number of photos to backup:\n')
        vk_client = VkSaver(vk_token, '5.131',vk_id, number_of_photos) 
        vk_client.get_album()

        com = input('\nSelect target drive:\n'
                    '1 - Yandex.Disk\n'
                    '2 - GoogleDrive\n')
        if com == '1':
            try:
                with open('yd_token.txt', 'r') as file:
                    yd_token = file.read().strip()
            except:
                yd_token = input('\nPlease enter Yandex token:\n')
                time.sleep(5)
            yd_instance = YdUploader(yd_token)
            vk_client.save_photos()
            yd_instance.upload()
            shutil.rmtree(vk_client.get_folder_name())
        elif com == '2':
            gd_instance = GdUploader()
            vk_client.save_photos()
            gd_instance.upload()
            shutil.rmtree(vk_client.get_folder_name())
        else:
            print('\nWrong input. Please repeat.\n')
