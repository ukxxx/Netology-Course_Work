# VK Photo Backup

## This Python script can be used to save photos from a user's VKontakte account and upload them to a Yandex Disk or Google Drive. The script requires the installation of some libraries: requests, json, os, logging, shutil, pprint, datetime, google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client

## VkSaver class

### This class provides methods to connect to the VK API and download photos. To use this class, you need to provide your VK API access token, VK API version, VK user id, and the number of photos to download (optional, default is 5). The class has several methods

    get_folder_name(): returns a string containing the name of the folder where the downloaded photos will be saved.
    get_album(): allows the user to select the album from which photos will be downloaded.
    get_photos(photo_sizes=1): returns a list of photos (as dictionaries) from the selected album.
    get_photos_urls(): returns a dictionary where the keys are the names of the photos and the values are the URLs to download the photos.
    save_photos(): downloads the photos and saves them to the specified folder.

## YdUploader class

### This class provides methods to upload photos to Yandex Disk. To use this class, you need to provide your Yandex Disk API access token. The class has several methods

    get_headers(): returns a dictionary containing the headers required to make requests to the Yandex Disk API.
    get_link(file_path): returns a dictionary containing the URL and some additional data required to upload a file to Yandex Disk.
    create_folder(): creates a folder on Yandex Disk with the same name as the folder where the downloaded photos are stored.
    upload_file(file_path, url): uploads the file to Yandex Disk.

## GdUploader class

### This class is used to upload files to Google Drive. This class requires authentication using Google's OAuth2.0 protocol, and therefore requires valid credentials.json. The class provides the following methods

    __init__(self, credentials: Credentials): Constructor that takes a Credentials object as its argument.
    create_folder(self, folder_name: str) -> str: Creates a folder with the given folder_name on Google Drive and returns the folder ID.
    upload_file(self, file_path: str, folder_id: str): Uploads a file located at file_path to Google Drive in the folder with the given folder_id.
