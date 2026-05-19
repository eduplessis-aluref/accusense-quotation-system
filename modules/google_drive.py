from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from oauth2client.service_account import ServiceAccountCredentials


def get_drive():

    scope = ["https://www.googleapis.com/auth/drive"]

    gauth = GoogleAuth()

    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json",
        scope
    )

    drive = GoogleDrive(gauth)

    return drive


def upload_pdf(local_path, filename):

    drive = get_drive()

    folder_id = "1jB8i_B3uUW4tQHoQYfyEmgGoq9q1ItRd"

    file_drive = drive.CreateFile({
        "title": filename,
        "parents": [{"id": folder_id}]
    })

    file_drive.SetContentFile(local_path)
    file_drive.Upload()

    return file_drive["alternateLink"]