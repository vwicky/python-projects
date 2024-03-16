import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk

from tkinter.filedialog import *
from ttkbootstrap.constants import *
from tkinter import messagebox 

from PIL import Image, ImageTk

from pygame import mixer

# my own modules
from document_cooker import *
from document_similarity import *
from testing_3d import *
from test_3d_initiales import *

#params
GUI_THEMA = 'darkly'
WINDOW_TITLE = 'GUI'
WINDOW_SIZE = '1010x600'

class NewGui:
    def __init__(self) -> None:
        self.window = ttk.Window(themename=GUI_THEMA)
        self.window.title(WINDOW_TITLE)
        self.window.geometry(WINDOW_SIZE)
        
        # variables used during computations
        self.folder_path = None
        self.folder_extantion = None
        self.parameters = None
        self.doc_cooker = None
        self.answer_list = None
        self.answer = None
        self.flag = False
        
        self.widget_placement()
        
    def execute(self) -> None:
        self.window.mainloop()
        
    # places all the widgets on their places
    def widget_placement(self) -> None:
        self.left_parameter_side()
        separator = ttk.Separator(self.window, orient='vertical')
        separator.pack(side='left', fill='y', padx=10)
        self.right_output_side()
        
    # functions gets a file path
    def get_file_path_from_entry(self) -> None:
        self.folder_path = self.entry_string.get()
    def get_file_path_from_messagebox(self) -> None:
        self.folder_path = askdirectory()
        self.entry_string.set(self.folder_path)
        
    # deals with all the computations
    def submit_button_2(self, event) -> None:
         self.submit_button()
    def submit_button(self) -> None:
        if self.was_path_entered():
            # parsing names and texts
            self.doc_cooker = DocumentCooker(self.folder_path, self.folder_extantion)
            name_list, text_list = self.doc_cooker.prepare_text_list()
            
            # adding files to asnwer_1
            self.answer_text.config(state='normal')
            self.answer_text.delete(1.0, tk.END)
            for i in range(len(name_list)):
                self.answer_text.insert(tk.END, chars=f'{i}) {name_list[i]}\n')
                print(i)
            self.answer_text.config(state='disabled')
            
            # adding answer of pairs to answer_2 <- retrievs self.answer
            self.computing_similarity(name_list, text_list)
            
            # showing answer
            self.answer_text_2.config(state='normal')
            self.answer_text.delete(1.0, tk.END)
            self.answer_text_2.insert(tk.END, self.answer)
            self.answer_text_2.config(state='disabled')
            
        return None
    
    # applying parameters
    def apply_parameters_button(self) -> None:
        token = self.token_textvariable.get() or 'letter'
        k_shingles = self.shingle_textvariable.get()
        buckets_amount = self.bucket_textvariable.get()
        bucket_size = self.bucket_size_textvariable.get()
        hf_amount = self.hf_textvariable.get()

        p = Parameters(token, k_shingles, hf_amount, buckets_amount, bucket_size)
        is_fine, list_wrong = p.validate_parameters()
        if is_fine == False:
            messagebox.showerror('invalid parameters', f'please, check if {list_wrong} values are correct...')
            return None
        
        self.parameters = p
        self.threshold = self.parameters.calc_threshold()
        
        # setting meter
        self.threshold_meter['amountused'] = int(self.threshold * 100)
        messagebox.showinfo('correct parameters', 'parameters applied succesfully')
        
        
        return None
        
    
    # it's for th multiprocessing
    def computing_similarity(self, name_list, text_list) -> None:
        if self.parameters is None:
            messagebox.showerror('wrong parameters', 'please, check the parameters')
            return None
        doc_manager = DocumentSimilarity(name_list, text_list, self.parameters)
        doc_manager.form_document_sketches_list()
        doc_manager.find_consecutive_pairs()
        
        similar_docs = doc_manager.form_similar_docs_list()
        self.answer_list = similar_docs
        self.answer = doc_manager.extraxt_text_from_pairs() or 'no similar pairs'
        
        self.meter['amountused'] = int(doc_manager.avg_similarity() *100)
        
        self.flag = True
        
        return None
    
    # plots a graph
    def plot_similarity_graph(self) -> None:
        if self.answer_list is not None:
            GraphPlotter.show_3d_grap_of_similarity(self.answer_list)
        else:
            messagebox.showwarning('graph plotting failed', 'No similar pairs avaible :(')
    
    # was path entered
    def was_path_entered(self) -> bool:
        self.get_file_path_from_entry()
        self.folder_extantion = self.entry_extansion_string.get()
        
        if self.folder_path and self.folder_extantion:
            return True
        else:
            messagebox.showwarning(
                title='entered path and extansion',
                message="error: check entered path and extansion ..."
            )
            return False
        
    def check_doc_cooker_exist(self) -> bool:
        return self.flag
        
    # method for saving into csv
    def save_csv_wrapper(self) -> None:
        if self.check_doc_cooker_exist():
            files = [('.csv files', '*.csv')] 
            file = asksaveasfile(filetypes = files, defaultextension = files)
            
            print(file.name)
            self.doc_cooker.save_into_csv(self.answer_list, file.name)
            messagebox.showinfo(
                title='file saved',
                message="file saved succesfully!"
            )
        return
            
    # for sending file to drive
    def send_csv_wrapper(self) -> None:
        if self.check_doc_cooker_exist():
            file_path = ''
            file_name = 'document_similaruty_results.csv'
            full_file_name = file_path + file_name
            
            print(file_name)
            self.doc_cooker.save_into_csv(self.answer_list, full_file_name)
            self.doc_cooker.send_to_drive(file_name).print_success()
            messagebox.showinfo(
                title='file sent',
                message= f"file {file_name} sent succesfully!"
            )
        return None
    
    # creates a left side of window
    def left_parameter_side(self) -> None:
        self.left_frame = ttk.Frame(
            master=self.window
        )
        self.left_side_place_sliders()
        self.left_frame.pack(side='left')
    
    # places all sliders
    def left_side_place_sliders(self) -> None:
        self.left_sliders_frame = ttk.Frame(master=self.left_frame)
        
        # frames for parameters
        starting_row = 0

        #shingle frame
        self.shingle_label = ttk.Label(
            master=self.left_sliders_frame,
            text="shingles",
            font='Consolas 12'
        )
        self.shingle_label.grid(row=starting_row, column=0)
        
        self.shingle_textvariable = tk.IntVar()
        self.shingle_entry = ttk.Entry(
            master= self.left_sliders_frame, 
            textvariable=self.shingle_textvariable
        )
        self.shingle_entry.grid(row=starting_row, column=1)
        
        #token frame
        self.token_label = ttk.Label(
            master=self.left_sliders_frame,
            text="token",
            font='Consolas 12'
        )
        self.token_label.grid(row=starting_row+1, column=0)
        
        self.token_textvariable = tk.StringVar()
        self.token_entry = ttk.Entry(
            master= self.left_sliders_frame, 
            textvariable=self.token_textvariable
        )
        self.token_entry.grid(row=starting_row+1, column=1)
        
        #bucket frame
        self.bucket_label = ttk.Label(
            master=self.left_sliders_frame,
            text="bucket amount",
            font='Consolas 12'
        )
        self.bucket_label.grid(row=starting_row+2, column=0)
        
        self.bucket_textvariable = tk.IntVar()
        self.bucket_entry = ttk.Entry(
            master= self.left_sliders_frame, 
            textvariable=self.bucket_textvariable
        )
        self.bucket_entry.grid(row=starting_row+2, column=1)
        
        #bucket size frame
        self.bucket_size_label = ttk.Label(
            master=self.left_sliders_frame,
            text="bucket size",
            font='Consolas 12'
        )
        self.bucket_size_label.grid(row=starting_row+3, column=0)
        
        self.bucket_size_textvariable = tk.IntVar()
        self.bucket_size_entry = ttk.Entry(
            master= self.left_sliders_frame, 
            textvariable=self.bucket_size_textvariable
        )
        self.bucket_size_entry.grid(row=starting_row+3, column=1)
        
        
        # hash function frame
        self.hf_label = ttk.Label(
            master=self.left_sliders_frame,
            text="hash f-s",
            font='Consolas 12'
        )
        self.hf_label.grid(row=starting_row+4, column=0)
        
        self.hf_textvariable = tk.IntVar()
        self.hf_entry = ttk.Entry(
            master= self.left_sliders_frame, 
            textvariable=self.hf_textvariable
        )
        self.hf_entry.grid(row=starting_row+4, column=1)
        
        # apply button
        self.apply_parametes_button = ttk.Button(
            master=self.left_sliders_frame,
            text='apply parameters',
            command=self.apply_parameters_button
        )
        self.apply_parametes_button.grid(row=starting_row+5, column=0, pady=5)
        
        # empty frane
        self.empty_frame = ttk.Frame(master =  self.left_sliders_frame, height=150)
        self.empty_frame.grid(row=starting_row+6, column=0)
        
        # labels for output
        # placing meter
        self.threshold_meter = ttk.Meter(
            self.left_sliders_frame,
            amountused=0,
            amounttotal=100,
            metersize=150,
            meterthickness=20,
            bootstyle=INFO,
            
            #interactive=True,
            textright='%',
            subtext='threshold'
        )
        self.threshold_meter.grid(row=starting_row+7, column=1)

        
        self.left_sliders_frame.pack()
    
    # creates a right side of window
    def right_output_side(self) -> None:
        self.right_frame = ttk.Frame(
            master=self.window
        )
        self.right_side_input_frame()
        self.right_side_output_documents_frame()
        self.right_side_output_answer_frame()
        self.right_side_placing_buttons()
        
        self.right_frame.pack(side='right')
        
    # placing buttons for output
    def right_side_placing_buttons(self) -> None:
        self.saving_frame = ttk.Frame(
            master=self.right_frame
        )
        
        # button for saving into csv
        self.saving_csv_button = ttk.Button(
            master=self.saving_frame,
            text='save on pc ...',
            command=self.save_csv_wrapper
        )
        self.saving_csv_button.pack(side='left', fill="x")
        
        # button for saving into csv
        self.send_csv_button = ttk.Button(
            master=self.saving_frame,
            text='send to google drive',
            command=self.send_csv_wrapper
        )
        self.send_csv_button.pack(side='left',fill="x")
        
        # for plotting graphs
        self.plot_graph = ttk.Button(
            master=self.saving_frame,
            text='plot a graph',
            command=self.plot_similarity_graph
        )
        self.plot_graph.pack(side='left',fill="x")
        
        self.saving_frame.pack(side='left')
        
    # for outputing answer
    def right_side_output_answer_frame(self) -> None:
        self.output_answer_frame = ttk.Frame(master=self.right_frame)
        
        # left side
        self.oaf_left_side = ttk.Frame(master = self.output_answer_frame)
        
        # prefix before the textbox
        self.prefix_before_answer_box = ttk.Label (
            master=self.oaf_left_side,
            text = 'answer:', 
            font = 'Consolas 12',
        )
        self.prefix_before_answer_box.pack(pady=10)
        
        #scrollbar for textbox
        self.sb_2 = ttk.Scrollbar(
            master=self.oaf_left_side
        )
        self.sb_2.pack(side='right', fill='both')
        
        # a text for answer
        self.answer_text_2 = ttk.Text (
            master=self.oaf_left_side,
            font='Consolas 12',
            width=31,
            height=6,
            bd=3,
            state='disabled',
            yscrollcommand=self.sb_2.set,
        )
        self.sb_2.config(command=self.answer_text_2.yview)
        self.answer_text_2.pack(side='left')
        
        self.oaf_left_side.pack(side='left')
        
        # right side
        self.oaf_rigth_side = ttk.Frame(master = self.output_answer_frame)
        # placing meter
        self.meter = ttk.Meter(
            self.oaf_rigth_side,
            amountused=0,
            metersize=150,
            meterthickness=20,
            bootstyle=INFO,
            
            #interactive=True,
            #textfont='Consolas 12',
            #textleft='Files ',
            textright='%',
            subtext='avg. sim.'
        )
        self.meter.pack(side='left', padx=10)
        self.oaf_rigth_side.pack(side='right')
        
        self.output_answer_frame.pack()
        
    # for output_information
    def right_side_output_documents_frame(self) -> None:
        self.output_frame = ttk.Frame(master=self.right_frame)
        
        # prefix before the textbox
        self.prefix_before_box = ttk.Label (
            master=self.output_frame,
            text = 'documents in path:', 
            font = 'Calibri 12',
        )
        self.prefix_before_box.pack(pady=10)
        
        #scrollbar for textbox
        self.sb = ttk.Scrollbar(
            master=self.output_frame
        )
        self.sb.pack(side='right', fill='both')
        
        # a text for answer
        self.answer_text = ttk.Text (
            master=self.output_frame,
            font='Consolas 12',
            width=50,
            height=5,
            bd=3,
            state='disabled',
            yscrollcommand=self.sb.set,
        )
        self.sb.config(command=self.answer_text.yview)
        self.answer_text.pack()
        self.output_frame.pack()    
    
    # for inout information
    def right_side_input_frame(self) -> None:
        self.input_frame = ttk.Frame(self.right_frame)
        
        self.first_row = ttk.Frame(
            master=self.input_frame
        )
        
        self.enter_path_label = ttk.Label(
            master= self.input_frame, 
            text = 'enter path', 
            font = 'Consolas 12 bold'
        )
        
        self.entry_string = tk.StringVar()
        self.entry = ttk.Entry(
            master= self.first_row, 
            textvariable=self.entry_string
        )
        self.entry.pack(side='left')
        
        self.file_folder_dialog = ttk.Button (
            master= self.first_row,
            text='...',
            command=self.get_file_path_from_messagebox
        )
        self.file_folder_dialog.pack(side='left')
        
        self.second_row = ttk.Frame(
            master=self.input_frame
        )
        
        self.enter_extansion_label = ttk.Label(
            master= self.input_frame, 
            text = 'enter extension', 
            font = 'Consolas 12 bold'
        )
        
        self.entry_extansion_string = tk.StringVar()
        self.entry_extansion = ttk.Entry(
            master=self.second_row, 
            textvariable=self.entry_extansion_string
        )
        self.entry_extansion.bind("<Return>", self.submit_button_2)
        self.entry_extansion.pack(side='left')
        
        self.button = ttk.Button(
            master= self.second_row, 
            text = 'submit', 
            command=self.submit_button
        )
        self.button.pack(side='left')
        
        self.enter_path_label.pack(pady=5)
        self.first_row.pack()
        self.enter_extansion_label.pack(pady=5)
        self.second_row.pack()
        self.input_frame.pack()
        
    