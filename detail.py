"""This module contains DetailPlot class."""
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.use('TkAgg')


class DetailPlot(ttk.Frame):
    """A class that a frame showing the plot of the details of life exp in each country."""
    def __init__(self, parent, life_exp_data, selected_country, selected_year):
        super().__init__(parent)

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.root = parent

        self.life_exp_data = life_exp_data
        self.selected_country = selected_country
        self.selected_year = selected_year

        # Store info used in plot
        self.latest_year = self.life_exp_data.Year.max()
        self.earliest_year = self.life_exp_data.Year.min()
        self.min_value = self.life_exp_data.Value.min()
        self.max_value = self.life_exp_data.Value.max()

        # set variables for receiving the value from combobox in filters
        self.country_name = tk.StringVar()
        self.country_name.set(self.selected_country)
        self.year = tk.IntVar()
        self.year.set(self.selected_year)

        # set variables for receiving the value from checkbox in filters
        self.female = tk.StringVar()
        self.male = tk.StringVar()
        self.total = tk.StringVar()
        self.total.set('Both sexes')
        self.male.set('Male')
        self.female.set('Female')

        # initialize the sexes that will appear on the graph (all)
        self.sex_filters = ['Both sexes', 'Female', 'Male']
        self.colors = {'Male': "Blue", "Female": "Red", "Both sexes": "Green"}
        self.colors_in_plot = [self.colors['Both sexes'],
                               self.colors['Female'],
                               self.colors['Male']]

        # set variables for receiving the value from RadioButton
        self.selected_option = tk.StringVar()
        self.selected_option.set('bar')  # show country in specific year in bar graph first

        # Find number of all countries for later uses in the app
        self.num_country = len(set(self.life_exp_data.Country))

        # create all components and start plotting
        self.create_widgets()
        self.update_plots()

    def create_widgets(self):
        """Create all widgets necessary for the program."""
        # Create help button
        self.help_button = ttk.Button(self, text="?", width=2,
                                      command=lambda: showinfo(
                                          title="Tips",
                                          message="Adjust the scroll bar to change "
                                                  "the year you want to observe.\n"
                                                  "Use overall mode to see the trend "
                                                  "from 1950 to the latest year.\n"
                                                  "You can also choose the sex or "
                                                  "change country that you want "
                                                  "to observe in FILTERS."
                                      )
                                      )
        self.help_button.grid(row=0, column=0, padx=10, sticky="e")
        # creating frames for country adn sex filters
        self.frame_filter = ttk.LabelFrame(self, text="FILTERS")
        self.frame_filter.grid(row=1, column=0, sticky="EW",
                               padx=10, pady=10)
        country_label = ttk.Label(self.frame_filter, text="Country : ")
        country_label.grid(row=0, column=0)
        self.cb_country_filter = ttk.Combobox(self.frame_filter, state="readonly",
                                              textvariable=self.country_name)
        self.cb_country_filter.bind('<<ComboboxSelected>>', self.update_plots)
        country_list = list(set(self.life_exp_data.Country))
        country_list.sort()
        self.cb_country_filter['values'] = country_list
        self.cb_country_filter.grid(row=0, column=1, padx=5, pady=5)

        sex_label = ttk.Label(self.frame_filter, text="Sex : ")
        sex_label.grid(row=1, column=0, padx=5, pady=5)
        self.female_box = ttk.Checkbutton(self.frame_filter, text='Female',
                                          onvalue="Female", offvalue='',
                                          variable=self.female, command=self.update_sex)
        self.male_box = ttk.Checkbutton(self.frame_filter, text='Male',
                                        onvalue="Male", offvalue='',
                                        variable=self.male, command=self.update_sex)
        self.total_box = ttk.Checkbutton(self.frame_filter, text='Both sexes',
                                         onvalue="Both sexes", offvalue='',
                                         variable=self.total, command=self.update_sex)
        self.female_box.grid(row=1, column=1, padx=2, pady=10, sticky="w")
        self.male_box.grid(row=2, column=1, padx=2, pady=10, sticky="w")
        self.total_box.grid(row=3, column=1, padx=2, pady=10, sticky="w")

        # Create frame for mode filters
        self.frame_mode = ttk.LabelFrame(self, text="MODE")
        self.frame_mode.grid(row=2, column=0, sticky="EW",
                             padx=10, pady=10)
        self.mode_bar = ttk.Radiobutton(self.frame_mode, text='Specific year',
                                        value="bar", variable=self.selected_option,
                                        command=self.show_bar_graph)
        self.mode_line = ttk.Radiobutton(self.frame_mode, text='Overall',
                                         value="line", variable=self.selected_option,
                                         command=self.show_line_graph)
        self.mode_bar.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.mode_line.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # Create a year slider beside bar plot
        self.year_slider = tk.Scale(self,
                                    from_=self.earliest_year,
                                    to=self.latest_year,
                                    orient='vertical',
                                    variable=self.year,
                                    command=self.update_plots
                                    )
        self.year_slider.grid(row=0, column=2, rowspan=7, sticky="NS", padx=10, pady=10)

        # create Matplotlib figures and plotting axes
        self.fig_line = Figure()
        self.axes_line = self.fig_line.add_subplot()
        self.fig_bar = Figure()
        self.axes_year = self.fig_bar.add_subplot()

        # create canvases to host the figure
        self.fig_canvas_line = FigureCanvasTkAgg(self.fig_line, master=self)

        self.fig_canvas_bar = FigureCanvasTkAgg(self.fig_bar, master=self)
        self.fig_canvas_bar.get_tk_widget().grid(row=0, column=1, rowspan=7, sticky=tk.NSEW,
                                                 padx=10, pady=10)

        # create close button
        self.button_close = ttk.Button(self, text="Close", command=self.root.destroy)
        self.button_close.grid(row=6, column=0, padx=10, pady=10, sticky="e")

        # Create a description frame to inform rank of selected country in the selected year
        self.description_frame = ttk.LabelFrame(self, text="COUNTRY DESCRIPTION")
        self.update_rank()
        self.message = ttk.Label(self.description_frame,
                                 text=f"{self.country_name.get()}\n "
                                      f"- Rank #{int(self.rank[self.rank.Country == self.country_name.get()].Rank)} "
                                      f"out of {self.num_country} countries in {self.year.get()}")
        self.description_frame.grid(row=5, column=0, padx=10, sticky="NSEW")
        self.message.grid(row=0, column=0, padx=10, sticky="NSEW")

        # configure each row and column
        self.config_row_col()

    def config_row_col(self):
        (columns, rows) = self.grid_size()
        for i in range(rows):
            self.rowconfigure(i, weight=1)
        for i in range(columns):
            self.columnconfigure(i, weight=1)

    def update_rank(self):
        """Update the current data to the correct year and sort by value
        to get the current rank of each countries.
        """
        rank = self.life_exp_data[
            (self.life_exp_data.Year == self.year.get()) &
            (self.life_exp_data.Sex == "Both sexes")]
        self.rank = rank.sort_values(by="Value", ascending=False)
        self.rank['Rank'] = np.arange(1,  self.num_country+1)

    def show_bar_graph(self):
        """Hide line(overall) graph and show bar(specific year) graph."""
        self.fig_canvas_line.get_tk_widget().grid_forget()
        self.fig_canvas_bar.get_tk_widget().grid(row=0, column=1, rowspan=7,
                                                 sticky=tk.NSEW,
                                                 padx=10, pady=10)
        self.year_slider.grid(row=0, column=2, rowspan=7, sticky="NS", padx=10, pady=10)
        self.config_row_col()

    def show_line_graph(self):
        """Hide bar(specific year) graph and show bar(overall) graph."""
        self.fig_canvas_bar.get_tk_widget().grid_forget()
        self.year_slider.grid_forget()
        self.fig_canvas_line.get_tk_widget().grid(row=0, column=1, rowspan=7, columnspan=2,
                                                  sticky=tk.NSEW, padx=10, pady=10)
        self.config_row_col()

    def update_sex(self):
        """Update sex filters and its color in the plot accordingly.
        If only one sex is chosen, that box will be disabled so at least
        one box is check. Everytime the box is check, the plot is updated.
        """
        female = self.female.get()
        male = self.male.get()
        total = self.total.get()
        all_box = [self.female_box, self.male_box, self.total_box]
        new_sex_filters = [fil for fil in [female, male, total] if fil != '']
        if len(new_sex_filters) == 1:
            for box in all_box:
                if box.state() == ('selected',):
                    box.config(state=tk.DISABLED)
        else:
            for box in all_box:
                if box.state() == ('disabled', 'selected'):
                    box.config(state=tk.NORMAL)
        new_sex_filters.sort()  # so it is in a certain order appropriate for assigning color
        self.sex_filters = new_sex_filters
        # update colors used in plot
        colors_in_plot = []
        for sex in self.sex_filters:
            colors_in_plot.append(self.colors[sex])
        self.colors_in_plot = colors_in_plot
        self.update_plots()

    def update_data(self):
        """Create the life exp data in an attribute with the current country filters."""
        # get the dataframe of one country
        one_country = self.life_exp_data[self.life_exp_data.Country == self.country_name.get()]
        # pivot table so it can be graphed easily
        self.one_country = one_country.pivot_table(columns="Sex", values="Value",
                                                   index="Year")

    def update_plots(self, event=None):
        """Update the current plots of both graph."""
        self.root.title(self.country_name.get())
        self.update_rank()
        self.message.config(text=f"{self.country_name.get()}\n - "
                                 f"Rank #{int(self.rank[self.rank.Country == self.country_name.get()].Rank)} "
                                 f"out of {len(self.rank.Country)} countries in {self.year.get()}")
        self.plot_line()
        self.plot_bar()

    def plot_line(self):
        """Plot the line graph showing life expectancy of each sex in the selected country from
         the earliest year to the latest year provided in the dataset in the left canvas.
        """
        self.axes_line.clear()
        self.update_data()
        plt.rcParams['axes.titlepad'] = 12
        self.one_country[self.sex_filters].plot(xticks=np.arange(self.earliest_year,
                                                                 self.latest_year, 5),
                                                ylabel="Life expectancy (years)",
                                                xlabel="Year",
                                                xlim=(self.earliest_year, self.latest_year),
                                                ylim=(self.min_value, self.max_value),
                                                title=f"Life Expectancy in\n "
                                                      f"{self.country_name.get()}\n "
                                                      f"from {self.earliest_year} "
                                                      f"to {self.latest_year}",
                                                color=self.colors_in_plot,
                                                rot=90,
                                                grid=True,
                                                ax=self.axes_line)
        self.fig_canvas_line.draw()

    def plot_bar(self):
        """Plot the bar graph showing life expectancy of each sex in project demo
        specific country with the selected year in the right canvas.
        """
        self.axes_year.clear()
        self.update_data()
        # Get data of project demo specific year from the pivot table of dataframe of one country
        self.one_country[self.sex_filters].loc[self.year.get()].plot.bar(
             ylabel="Life expectancy (years)", ylim=(self.min_value, self.max_value),
             xlabel="Sex",
             title=f"Life Expectancy in \n"
                   f"{self.country_name.get()} "
                   f"in {self.year.get()}",
             grid=True, rot=0, color=self.colors_in_plot, edgecolor="black",
             ax=self.axes_year)
        self.axes_year.bar_label(self.axes_year.containers[0], fmt="%.2f")
        self.fig_canvas_bar.draw()
