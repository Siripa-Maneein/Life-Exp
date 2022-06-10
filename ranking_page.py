"""This module contains RankingPage class."""
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import numpy as np
from ttkwidgets.autocomplete import AutocompleteCombobox
from detail import DetailPlot


class RankingPage(ttk.Frame):
    """This class is responsible for create ui for showing rank
    of life expectancy of countries."""
    def __init__(self, parent, life_exp_data):
        super().__init__(parent)
        # resize root window - make it bigger
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        window_width = screen_width - 100
        window_height = screen_width - 200
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        parent.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.root = parent

        # Store life_exp_data so it is ready to use
        self.life_exp_data = life_exp_data
        # Create all necessary variables for the widgets
        self.user_input = tk.StringVar()
        self.ascending = tk.BooleanVar()
        self.ascending.set(False)
        self.year = tk.IntVar()
        all_year = list(set(self.life_exp_data.Year))
        all_year.sort()
        latest_year = all_year[-1]
        self.year.set(latest_year)

        # calculate number of countries in dataset
        self.num_country = len(set(self.life_exp_data.Country))

        self.create_widgets()

    def create_widgets(self):
        """Create all components in the page."""
        help_button = ttk.Button(self, text="?", width=2,
                                 command=lambda: showinfo(
                                    title="Tips",
                                    message="Double click in the table to see "
                                            "details of each country"
                                 )
                                 )

        # Create frame for selecting year
        frame_year = ttk.LabelFrame(self)
        label_select_year = ttk.Label(frame_year, text="Select year:")
        cb_year = ttk.Combobox(frame_year, state="readonly", textvariable=self.year)
        cb_year.bind('<<ComboboxSelected>>', self.update_table)
        all_year = list(set(self.life_exp_data.Year))
        all_year.sort()
        cb_year['values'] = all_year

        # title of the table
        self.title_style = ttk.Style(self)
        self.title_style.configure("Title.TLabel", font=('Helvetica', 16))
        self.label_table_title = ttk.Label(self, text=f"Life expectancy rank of "
                                                      f"{len(set(self.life_exp_data.Country))} "
                                                      f"countries in {self.year.get()}",
                                           style="Title.TLabel")

        # Create Radiobutton in sort options frame
        frame_sort = ttk.LabelFrame(self, text="Sort Options")
        radio_high_low = ttk.Radiobutton(frame_sort, text="Highest to Lowest",
                                         value=False, variable=self.ascending,
                                         command=self.update_table)
        radio_low_high = ttk.Radiobutton(frame_sort, text="Lowest to Highest",
                                         value=True, variable=self.ascending,
                                         command=self.update_table)

        # process data
        rank = self.life_exp_data[(self.life_exp_data.Year == self.year.get()) &
                                  (self.life_exp_data.Sex == "Both sexes")]
        rank = rank.sort_values(by="Value", ascending=self.ascending.get())
        rank['Rank'] = np.arange(1, self.num_country + 1)

        # Create treeview showing rand of each countries
        data_in_table = zip(rank.Rank, rank.Country, rank.Value.map('{:,.2f}'.format))
        columns = ('rank', 'country', 'life_exp')
        self.table = ttk.Treeview(self, columns=columns, show='headings')
        self.table.heading('rank', text='Rank#')
        self.table.heading('country', text='Country')
        self.table.heading('life_exp', text='Average Life expectancy (years) (Both sexes)')
        for data in data_in_table:
            self.table.insert('', tk.END, values=data)
        self.table.bind('<Double-1>', self.show_detail)
        self.table.grid(row=3, column=0, columnspan=3, sticky='nsew', padx=2)
        self.table.rowconfigure(1, weight=1)
        self.table.columnconfigure(1, weight=1)

        # create a scrollbar for the treeview
        scroll_bar = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scroll_bar.set)

        # create frame for searching countries widgets
        frame_search = ttk.LabelFrame(self)
        label_country = ttk.Label(frame_search, text="Search Country: ")
        country_list = list(set(self.life_exp_data.Country))
        country_list.sort()
        self.cb_country = AutocompleteCombobox(frame_search, textvariable=self.user_input,
                                               completevalues=country_list)
        button_search = ttk.Button(frame_search, text="Search", command=self.alert)
        self.label_alert = ttk.Label(self)

        # Create quit button
        button_quit = ttk.Button(self, text="Quit", command=self.root.destroy)

        # grid all components
        frame_year.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        label_select_year.grid(row=0, column=0, padx=5, pady=5)
        cb_year.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        help_button.grid(row=0, column=2, sticky="E", padx=5, pady=5)
        self.label_table_title.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        frame_sort.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="NSEW")
        radio_high_low.grid(row=0, column=0, padx=5, pady=5)
        radio_low_high.grid(row=0, column=1, padx=5, pady=5)

        scroll_bar.grid(row=3, column=2, pady=5, sticky="ENS")

        frame_search.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="EW")
        label_country.grid(row=0, column=0, padx=5, pady=5)
        self.cb_country.grid(row=0, column=1, padx=5, pady=5)
        button_search.grid(row=0, column=2, padx=5, pady=5)
        self.label_alert.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="W")

        button_quit.grid(row=6, column=2, padx=10, pady=10, sticky="E")

        # configure each row and column
        (columns, rows) = self.grid_size()
        for i in range(rows):
            self.rowconfigure(i, weight=1)
        for i in range(columns):
            self.columnconfigure(i, weight=1)

    def alert(self):
        """In form user that the their searched country is highlighted
        or not found their country.
        """
        found = False
        for iid in self.table.get_children():
            if self.table.item(iid)['values'][1].lower() == self.user_input.get().lower().strip():
                self.table.focus(iid)
                self.table.selection_set(iid)
                found = True
        if found:
            self.label_alert.config(text="Your selected country is highlighted. "
                                         "If not seen, scroll up or down.")
        else:
            if not self.user_input.get():
                self.label_alert.config(text="Please fill in the country name "
                                             "that you want to find.")
            else:
                self.label_alert.config(text="Country Not found. Please try again "
                                             "or choose from the country list "
                                             "provided in the combobox.")

    def update_table(self, event=None):
        """When users select other year or new sort option, update the table
        according to the life exp data."""
        # update the title
        self.label_table_title.config(text=f"Life expectancy rank of {self.num_country} "
                                           f"countries in {self.year.get()}")
        # process data
        rank = self.life_exp_data[(self.life_exp_data.Year == self.year.get()) &
                                  (self.life_exp_data.Sex == "Both sexes")]
        rank = rank.sort_values(by="Value", ascending=self.ascending.get())
        if not self.ascending.get():
            rank['Rank'] = np.arange(1, self.num_country+1)
        else:
            rank['Rank'] = np.arange(self.num_country, 0, -1)

        # update treeview
        data_in_table = zip(rank.Rank, rank.Country, rank.Value.map('{:,.2f}'.format))

        # delete all existing items
        for item in self.table.get_children():
            self.table.delete(item)

        # insert all new items
        for data in data_in_table:
            self.table.insert('', tk.END, values=data)

    def show_detail(self, event):
        """When user click at a country in treeview, this method is called.
        It create new toplevel window showing details of that country."""
        for item_selected in self.table.selection():
            item = self.table.item(item_selected)
            country_name = item['values'][1]
            top = tk.Toplevel(master=self.root)
            top.title(country_name)
            top.geometry('1000x500')
            detail_frame = DetailPlot(top, self.life_exp_data, country_name, self.year.get())
            detail_frame.grid(row=0, column=0, sticky=tk.NSEW)
