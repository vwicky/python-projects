import PyPDF2
import csv
from pathlib import Path

from additional_functions.google_drive_sending import *

# has in itself static functions for document reading
class DocumentCooker:    
    def __init__(self, path: str, file_extantion: str) -> None:
        self.path = path
        self.file_extantion = file_extantion
    
    @staticmethod
    def read_txt(file_name:str):
        with open(file_name, 'r', encoding="utf-8") as file1:
            text1 = file1.read()
        return text1
    
    @staticmethod
    def read_pdf(file_name: str):
        pdfFileObj = open(file_name, 'rb')
 
        # creating a pdf reader object
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        
        text = ""
        for page in pdfReader.pages:
            text += page.extract_text()
        
        print(file_name, ' - read!')
        return text

    # writes consecucative list into csv
    def save_into_csv(self, consecucative_list: list, file_name: str) -> OptionalBool:
        prefix = 'saving into csv'
        fieldnames = ['doc_1', 'doc_2', 'similarity']
        
        with open(file_name, 'w', newline='') as file:
            csv_writer = csv.DictWriter(f=file, fieldnames=fieldnames, dialect='excel')
            csv_writer.writeheader()
            for row in consecucative_list:
                # writes first file, second, and their similarity
                csv_writer.writerow({'doc_1': self.name_list[row[0][0]], 
                                     'doc_2': self.name_list[row[0][1]], 
                                     'similarity': row[1]})
        return OptionalBool(prefix, True)
        

    @staticmethod
    def send_to_drive(file_name: str) -> OptionalBool:
        prefix = 'sending to drive'
        value = DriveSender().send_to_drive(file_name)
        return OptionalBool(prefix, value)

    # prints prepared documets info
    def print_docs_info(self) -> str:
        s = f'> there are {len(self.name_list)} files, with corresponding sizes:\n\t{[len(doc) for doc in self.text_list]}'
        print(s)
        return s

    # returns a tuple of (names, texts)
    def prepare_text_list(self) -> tuple[list, list]:
        self.text_list = []
        self.name_list = []
        
        # could I add multithreading here?
        entries = Path(self.path)
        for entry in entries.iterdir():
            entry_name = entry.name
            if entry_name[-4:] == self.file_extantion:
                self.name_list.append(entry_name)
                self.text_list.append(DocumentCooker.read_txt(entry.absolute()))
        
        return self.name_list, self.text_list
    