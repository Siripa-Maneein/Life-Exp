"""This module contains DownloadData class."""
import tkinter as tk
from tkinter import ttk
import io
from threading import Thread
import requests
import pandas as pd
from ranking_page import RankingPage

# Get life expectancy value of each country.
# The dataset contains other kind of geographic area too(need to be eliminated).
LIFE_EXPECTANCY_URL = "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/UNICEF,DM" \
                      ",1.0/.DM_LIFE_EXP...?format=csv&labels=both"
# Use ref_area to compare with alpha-code of countries from below source
COUNTRY_NAME_URL = "https://gist.githubusercontent.com/tadast/8827699/raw/f5cac3d42d16b783" \
                   "48610fc4ec301e9234f82821/countries_codes_and_coordinates.csv"


class DownloadData(ttk.Frame):
    """This class responsible for downloading data from an online source and
     create a loading bar to inform the progress to users.
     """
    def __init__(self, parent):
        super().__init__(parent)
        parent.title('Life Exp')
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.root = parent
        self.init_components()
        self.show_progress_bar()

    def init_components(self):
        """Create all the components in this frame."""
        progress_label = ttk.Label(self, text="Downloading data...")
        self.progress_bar = ttk.Progressbar(self, orient='horizontal',
                                            mode='indeterminate', length=280)
        progress_label.grid(row=0, column=0, padx=5, pady=5, sticky="EW")
        self.progress_bar.grid(row=1, column=0, padx=5, pady=5, sticky="EW")

        (cols, rows) = self.grid_size()
        for i in range(cols):
            self.columnconfigure(i, weight=1)
        for i in range(rows):
            self.rowconfigure(i, weight=1)

    def show_progress_bar(self):
        """Tell the user the application is preparing the data
        and disable start button."""
        self.task_thread = Thread(target=self.download_and_clean_data)
        self.task_thread.start()
        self.progress_bar.start()
        self.after(1, self.check_progress)
        self.progress_bar.start()

    def check_progress(self):
        """Check task regularly whether the task has completed.

        If it has completed, enable the start button and show the frame that plot the data.
        """
        if self.task_thread.is_alive():
            self.after(1, self.check_progress)
        else:
            self.progress_bar.stop()
            self.grid_forget()
            ranking_frame = RankingPage(self.root, self.life_exp_data)
            ranking_frame.grid(row=0, column=0, sticky=tk.NSEW)

    def download_and_clean_data(self):
        """Download data from sources and organize the data to make it
        suitable for the program use."""
        life_expectancy_data = download_csv_from_url(LIFE_EXPECTANCY_URL)
        # Get the necessary columns from the life_expectancy dataset
        life_expectancy = life_expectancy_data[["REF_AREA", "Geographic area",
                                                "Sex", "TIME_PERIOD", "OBS_VALUE"]]

        # Get the necessary columns from the country_info dataset
        country_info = download_csv_from_url(COUNTRY_NAME_URL)
        country_info = country_info[['Alpha-3 code']]\
            .apply(lambda n: n.str.strip('" '))
        country_info = country_info.rename(columns={"Alpha-3 code": "REF_AREA"})
        # Get the dataframe of life expectancy in each countries
        life_expectancy = life_expectancy[life_expectancy.REF_AREA.isin(
            list(country_info["REF_AREA"]))]
        # Rename columns and reverb "Total" to "Both sexes"
        life_expectancy = life_expectancy.rename(columns={"Geographic area": "Country",
                                                          "TIME_PERIOD": "Year",
                                                          "OBS_VALUE": "Value"})
        life_expectancy = life_expectancy.replace('Total', "Both sexes")
        # eliminate "Other, non specified"
        life_expectancy = life_expectancy.loc[life_expectancy.Country != "Other, non specified"]
        country_list = life_expectancy.Country
        # remove bracket off the country name, the text in the brackets is incomplete.
        new_country_list = []
        for country_name in country_list:
            new_name = country_name
            for cha in country_name:
                if cha == "(":
                    k = country_name.index(cha)
                    new_name = country_name[:k]
                    break
            new_country_list.append(new_name)
        life_expectancy.Country = new_country_list
        # Save in the attribute
        self.life_exp_data = life_expectancy


def download_csv_from_url(url):
    """Return the dataframe of csv file from the given url."""
    csv_file = requests.get(url).content
    csv_data = pd.read_csv(io.StringIO(csv_file.decode('utf-8')))
    return csv_data
