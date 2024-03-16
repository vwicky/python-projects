from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class DriveSender:
    def __init__(self) -> None:
        # Authenticate and create PyDrive client
        self.gauth = GoogleAuth()
        self.gauth.LocalWebserverAuth()  # This creates a local webserver and automatically handles authentication.
        self.drive = GoogleDrive(self.gauth)

    def send_to_drive(self, file_path: str):
        # Specify the file to upload and the folder ID where you want to upload it
        upload_file = file_path
        folder_id = '1hOEzeCRcxes_oIoaeG8sPRDzlljcJRVO'  # Replace with the actual folder ID

        # Upload file 
        self.gfile = self.drive.CreateFile({'parents': [{'id': folder_id}]})  # Set the parent folder ID
        self.gfile.SetContentFile(upload_file)  # Read file and set it as the content of this instance.
        self.gfile.Upload()  # Upload the file.
        return True

class OptionalBool:
    def __init__(self, prefix: str, value: bool) -> None:
        self.value = value
        self.prefix = prefix
        
    def print_success(self) -> None:
        if self.value:
            print(f"> {self.prefix}: was succesfull :)")
        else:
            print(f"> {self.prefix}: an error occured :()")