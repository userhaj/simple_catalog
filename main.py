import tkinter as tk
import glob
from catalog_db import DbManage
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
import os
import threading
from functools import partial


class App:
    def __init__(self, master):

        self.Db = DbManage()
        self.current_file = None

        master.title('Catalog')
        master.geometry('1048x600')
        master['padx'] = 0
        master['pady'] = 0

        movie_content = tk.Frame(master)
        movie_content.grid(column=0, row=0, sticky='NSEW')
        movie_content['padx'] = 10
        movie_content['pady'] = 10

        # Content to display
        movie_ui = MovieUI(movie_content, self.Db)

        # Menu Bar
        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Add Folder', command=self.add_folder)
        filemenu.add_command(label='Refresh List', command=movie_ui.update_movie_list)
        filemenu.add_command(label='Update Details', command=self.update_movie_details_thread)
        menubar.add_cascade(label='File', menu=filemenu)
        master.config(menu=menubar)

        # Statusbar
        self.status_string = tk.StringVar()
        statusbar = tk.Label(master, textvariable=self.status_string, relief=tk.SUNKEN, anchor='w')
        statusbar.grid(column=0, row=1000, sticky='SEW')

        # Force statusbar to stay same size while allowing resize of main window content
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        master.rowconfigure(1, weight=0)

    def add_folder(self):
        chosen_folder = askdirectory()

        if chosen_folder != '':
            # self.folder_thread(chosen_folder)
            folder_thread_method = partial(self.folder_thread, chosen_folder)
            # folder_thread_method()
            add_folder2db = threading.Thread(target=folder_thread_method)
            add_folder2db.start()

    def folder_thread(self, chosen_folder):
        list_of_files = glob.glob(chosen_folder + '/**/**', recursive=True)
        for file in list_of_files:
            self.status_string.set('Adding: ' + file)
            self.Db.add_file(file)
        self.status_string.set('')
        self.update_movie_list()

    def update_movie_details_thread(self):
        threading.Thread(target=self.Db.update_all_details).start()


class MovieUI:
    def __init__(self, movie_content: tk.Frame, Db: DbManage):
        self.Db = Db

        # List of movies
        file_list_frame = tk.Frame(movie_content)
        file_list_frame.grid(row=0, column=0, sticky='NSEW')
        self.fileList = tk.Listbox(file_list_frame, width=60)
        self.fileList.config(border=2, relief='sunken')
        self.fileList.bind('<<ListboxSelect>>', self.list_select)
        self.fileList.grid(row=0, column=0, sticky='NSEW')

        # Allow file list to grow with window vertically
        file_list_frame.rowconfigure(0, weight=1)


        db_output_frame = tk.Frame(movie_content)
        db_output_frame.grid(row=0, column=1, sticky='NSEW')

        self.update_movie_list()

        list_scroll = tk.Scrollbar(file_list_frame, orient=tk.VERTICAL, command=self.fileList.yview)
        list_scroll.grid(row=0, column=1, sticky='NSW', rowspan=100)
        self.fileList['yscrollcommand'] = list_scroll.set

        title_frame_with_release_rating = tk.Frame(db_output_frame)
        title_frame_with_release_rating.grid(row=2, column=3, sticky='NSWE')

        # Title
        title_frame = tk.LabelFrame(title_frame_with_release_rating, text='Title')
        title_frame.grid(column=0, row=0, sticky='NW')
        self.title_string = tk.StringVar()
        self.title_string.set('No selections')
        title_text = tk.Label(title_frame, textvariable=self.title_string, justify=tk.LEFT)
        title_text.config(font=('', 20))
        title_text.grid()

        # Rating
        rating_frame = tk.LabelFrame(title_frame_with_release_rating, text='Rating')
        rating_frame.grid(column=0, row=1, sticky='NW')
        self.rating_string = tk.StringVar()
        self.rating_string.set('No selections')
        rating_text = tk.Label(rating_frame, textvariable=self.rating_string, wraplength=200, justify=tk.LEFT)
        rating_text.grid()

        # Release Date
        release_date_frame = tk.LabelFrame(title_frame_with_release_rating, text='Release Date')
        release_date_frame.grid(column=0, row=1, sticky='NE')
        self.release_date_string = tk.StringVar()
        self.release_date_string.set('No selections')
        release_date_text = tk.Label(release_date_frame, textvariable=self.release_date_string, wraplength=400, justify=tk.LEFT)
        release_date_text.grid()

        # Open File
        open_file_button = ttk.Button(db_output_frame, text='Open Movie', command=self.run_movie)
        open_file_button.grid(column=3, row=5, sticky='NW')

        # Description
        description_frame = tk.LabelFrame(db_output_frame, text='Description')
        description_frame.grid(column=3, row=6, sticky='NWE')
        description_frame.rowconfigure(0, weight=10)
        description_frame.columnconfigure(0, weight=1)
        db_output_frame.rowconfigure(6, weight=100)

        self.description_string = tk.StringVar()
        self.description_string.set('No selections')
        # description_text = tk.Label(description_frame, textvariable=self.description_string, wraplength=400,
        #                             justify=tk.LEFT)
        self.description_text = tk.Text(description_frame, wrap=tk.WORD)
        self.description_text.grid(sticky='NWES')

        # Delete File
        delete_file_button = ttk.Button(db_output_frame, text='Remove From List', command=self.delete_movie)
        delete_file_button.grid(column=3, row=7, sticky='NW')

        movie_content.columnconfigure(3, weight=1)
        movie_content.rowconfigure(0, weight=1)

    def update_movie_list(self):

        self.fileList.delete(0, tk.END)
        for title_name in self.Db.get_all_title_guess():
            self.fileList.insert(tk.END, title_name[0])

    def delete_movie(self):
        self.Db.delete_file(self.current_file)
        self.update_movie_list()

    def run_movie(self):
        os.startfile(self.current_file)

    def list_select(self, event):
        event_widget = event.widget
        list_index = int(event_widget.curselection()[0])
        title = event_widget.get(list_index)

        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, str(self.Db.get_description(title)))
        self.title_string.set(self.Db.get_title(title))
        self.rating_string.set(self.Db.get_rating(title))
        self.release_date_string.set(self.Db.get_release_date(title))
        self.current_file = self.Db.get_file(title)


if __name__ == '__main__':

    root = tk.Tk()
    app = App(root)
    root.mainloop()
