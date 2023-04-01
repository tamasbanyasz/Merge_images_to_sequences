from tkinter import Listbox, Scrollbar, RIGHT, Y, END
from collections import defaultdict
from itertools import groupby
import customtkinter as ctk
from PIL import Image
import os.path


# User input example: C:\Users\Others\Pictures\Saved Pictures


class LoadImages:
    def __init__(self):
        self.path = None
        self.df = None  # temporary images
        self.name_of_the_selected_sequence = None  # temporary selected image sequence
        self.extensions = set()  # set for the different types of extension

    def user_path_is_valid(self, user_path):  # check path is valid
        self.path = ''.join(user_path.rstrip())  # store the path
        return os.path.exists(self.path)  # return True if valid the path

    def in_file_name_any_whitespace(self, splitted_images, image, merged_sequences):
        if ' ' in splitted_images:
            lenght_of_the_counter = len(splitted_images[-1])  # lenght of the counters

            image_without_counter = splitted_images[:-1]  # take off the counters from end of the images
            merged_sequences[f'{image_without_counter}{"#" * lenght_of_the_counter}.{image[-3:]}'].append(
                image)  # append merged sequences to the dictionary

    def digit_end_of_the_file_name(self, splitted_images, image, merged_sequences):
        if splitted_images[-1].isdigit():
            lenght_of_the_counter = len(splitted_images[-1])

            image_without_counter = splitted_images[:-1]

            # reunite the splitted names
            new_images_without_counter = ''.join(image_without_counter).replace(" ", "_")

            merged_sequences[f'{new_images_without_counter}{"#" * lenght_of_the_counter}.{image[-3:]}'].append(
                image)

    def end_of_the_file_name_is_not_digit(self, splitted_images, image, merged_sequences_without_counter):
        if not splitted_images[-1].isdigit():
            merged_sequences_without_counter[f'{splitted_images[-1]}.{image[-3:]}'].append(image)

    def merge_sequences(self, user_path):
        if self.user_path_is_valid(user_path):  # if the path valid

            extensions = (".jpg", ".png", ".bmp")  # image extensions examples

            folder = os.listdir(self.path)  # load folder

            images = [image for image in folder if image.endswith(extensions)]  # select only images

            merged_sequences = defaultdict(list)  # a dictionary to storing the merged images by image names with counter
            merged_sequences_without_counter = defaultdict(list)  # a dictionary to storing the merged images by image names without counter

            for image in images:
                self.extensions.add(image[image.rfind(  # store the extensions
                        "."):])
                # take off the extensions from end of the images, and if there is any whitespace replace to '_'
                image_without_extension = image[:image.rfind(".")]

                # split the name where be found digit
                splitted_images = ["".join(x) for _, x in groupby(image_without_extension, key=str.isdigit)]

                self.in_file_name_any_whitespace(splitted_images, image, merged_sequences)

                self.digit_end_of_the_file_name(splitted_images, image, merged_sequences)

                self.end_of_the_file_name_is_not_digit(splitted_images, image, merged_sequences_without_counter)

            image_sequences = {**merged_sequences, **merged_sequences_without_counter}  # merge the dictionaries

            return image_sequences

    def open_images(self, list_of_images):  # open images one by one
        for index, image in enumerate(list_of_images):
            if index < 3:  # show only the first 3 image because the image load is do slowly a little bit. Especially if you has a huge image data
                with Image.open(f"{self.path}\{image}") as img:  # open the images
                    img.show()

    def show_images(self):
        if self.name_of_the_selected_sequence:  # if had a selected image sequence
            list_of_images = self.df[self.name_of_the_selected_sequence]  # put to a list all merged images
            print(self.name_of_the_selected_sequence)
            self.open_images(list_of_images)


class InsertToListbox(LoadImages):
    def __init__(self, listbox):
        super().__init__()
        self.listbox = listbox

    def get_folder_content(self, user_path):  # get the images from the choosed folder
        self.df = self.merge_sequences(user_path)  # store the merged sequences

    def insert_items_to_listbox_from_df_series(self):  # insert the names of the merged sequences into the listbox
        if self.df:
            for image_names, images_in_list in self.df.items():
                self.listbox.insert(END, image_names)  # insert items from dict to the listbox

    def insert_items_into_listbox(self, user_path):  # after pressed the "OK" button
        self.get_folder_content(user_path)  # store the merged sequences temporary
        print(self.df)
        print(self.extensions)
        self.insert_items_to_listbox_from_df_series()  # insert the items to listbox

    def select_images_by_extensions(self, extension):  # display sequences name by a selected extension from combobox
        for image_names in self.df.keys():
            if image_names.endswith(extension):
                self.listbox.insert(END, image_names)

    def select_all_images_from_combobox(self, extension):  # display all sequences from combobox by value 'All'
        if extension == 'all':
            self.listbox.delete(0, END)
            self.insert_items_to_listbox_from_df_series()

    def insert_by_selected_combobox_value(self, extension):  # insert sequences by selected value from combobox
        self.select_images_by_extensions(extension)
        self.select_all_images_from_combobox(extension)

    def select_images(self):  # select a merged sequence by name from the listbox
        for item in self.listbox.curselection():
            self.name_of_the_selected_sequence = self.listbox.get(item)  # get the selected name of the merged sequence
            print(f'\n{self.name_of_the_selected_sequence}')
            self.show_images()  # then show the images under the choosed sequence


class SetInterface:
    def __init__(self, listbox, combobox):
        self.listbox = InsertToListbox(listbox)
        self.combobox = combobox

    def set_combobox_value_back_to_default(self):
        self.combobox.set('EXTENSIONS')
        self.listbox.extensions = set()  # clear the set of extensions

    def clear_listbox_and_clear_selected_images(self):  # clear the temporary stored datas if we give a new folder path
        self.listbox.listbox.delete(0, END)  # delete all displayed name from listbox
        self.listbox.df = None  # create empty variable to the next image sequences
        self.listbox.name_of_the_selected_sequence = None  # create new empty variable to the selected sequence name

    def put_in_sort_the_extensions(self):
        upper_extensions = [x.upper() for x in list(self.listbox.extensions)]
        upper_extensions.append('All')

        sorted_extensions = sorted(upper_extensions, key=lambda v: v.upper())
        sorted_extensions.reverse()

        return sorted_extensions

    def ok_click(self, user_path):  # Press 'OK' button to get the images from the folder and get extensions to Combobox

        self.set_combobox_value_back_to_default()  # Set the Combobox value to default when pressed the 'OK' button

        self.clear_listbox_and_clear_selected_images()  # clear the listbox and the selected sequence name
        self.listbox.insert_items_into_listbox(user_path)  # insert images to listbox

        self.combobox.configure(values=self.put_in_sort_the_extensions())  # add extensions to combobox values

    def select_by_extensions(self, selected_extension):
        self.listbox.listbox.delete(0, END)
        self.listbox.insert_by_selected_combobox_value(selected_extension)


class InterfaceOfMergedSequnces:
    ctk.set_appearance_mode("dark")  # set interface mode (light,dark)

    def __init__(self):
        self.window = ctk.CTk()

        # Interface configs
        self.window.geometry("1024x768")
        self.window.title("Merge Sequences")
        self.window.resizable(False, False)

        # Frames
        self.frame = ctk.CTkFrame(self.window, corner_radius=10, width=502, height=47)
        self.frame_2 = ctk.CTkFrame(self.window)

        # Labels
        self.folder_label = ctk.CTkLabel(master=self.window, text='Folder:', fg_color='#404040',
                                         font=('Ariel', 16), corner_radius=4)
        self.images_label = ctk.CTkLabel(master=self.window, text='Images', fg_color='#404040',
                                         font=('Roboto', 30), corner_radius=4)

        # Entry box
        self.entry = ctk.CTkEntry(self.window, width=493, height=36, fg_color="#151515", border_width=1,
                                  border_color="gray50", font=('Robot', 20))

        # Scrollbar
        self.scrollbar = Scrollbar(master=self.frame_2)

        # Listbox
        self.listbox = Listbox(self.frame_2, yscrollcommand=self.scrollbar.set, height=20, width=60, bg="#404040",
                               activestyle='dotbox', font="Helvetica",
                               fg="white")

        # ComboBox
        self.combobox = ctk.CTkComboBox(master=self.window,
                                        values=['EXTENSIONS'],
                                        state='readonly',
                                        command=lambda e: self.select_from_combobox(self.combobox.get().lower()))

        # Set Interface
        self.set_interface = SetInterface(self.listbox, self.combobox)

        # Buttons
        self.ok_button()
        self.select_button()

        # show selected images by a pressed 'Return' key
        self.listbox.bind('<Return>', lambda e: self.set_interface.listbox.select_images())

        # Scrollbar configs
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Widgets places
        self.frame.place(x=161, y=39)
        self.frame_2.pack(pady=150)
        self.entry.place(x=165, y=44)
        self.folder_label.place(x=100, y=47)
        self.images_label.place(x=442, y=100)
        self.listbox.pack()
        self.combobox.place(x=652, y=119)

        self.window.mainloop()

    def ok_button(self):
        submit_button = ctk.CTkButton(self.window, text='Ok',
                                      command=lambda: self.set_interface.ok_click(self.entry.get()),
                                      font=('Arial', 16))
        submit_button.place(x=680, y=47)

    def select_button(self):
        submit_button = ctk.CTkButton(self.window, text='Select',
                                      command=lambda: self.set_interface.listbox.select_images(), font=('Arial', 16))
        submit_button.place(x=440, y=570)

    def select_from_combobox(self, value):  # select by extensions from combobox
        self.set_interface.select_by_extensions(value)


if __name__ == "__main__":
    gui = InterfaceOfMergedSequnces()
