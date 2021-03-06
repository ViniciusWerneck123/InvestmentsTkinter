from tkinter import Frame, Label, Button, Scrollbar, Listbox, Tk, ttk, LabelFrame
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas_datareader import data as web

class App:

    def __init__(self):
        # Back-end attributes
        self.database = 'Investimentos.ods'
        self.acoes, self.criptos = self.load_database() #pandas DataFrames
        self.current_date = self.acoes.index[0]
        self.current_sheet = self.acoes
        self.current_ticker = self.acoes['Quantidade'].columns[0]
        self.stock_data, self.cripto_data = self.load_financial_data()
        self.acoes_pressed = True
        self.criptos_pressed = False

        # Front-end attributes
        self.height, self.width = 600, 1200
        # Main window
        self.root = Tk()
        self.root.title('Meus investimentos')
        self.root.geometry(f'{self.width}x{self.height}')
        self.root.grid_propagate(0)

        # Second layer
        self.root1 = Frame(self.root, height=self.height, width=2*self.width/3) # Frame da esquerda
        self.root2 = Frame(self.root, height=self.height, width=self.width/3) # Frame da direita
        self.root1.grid_propagate(0)
        self.root2.grid_propagate(0)

        # Third layer
        self.root11 = Frame(self.root1, height=self.height / 15, width=2 * self.width / 3, borderwidth=2)
        self.root12 = Frame(self.root1, height=2*self.height / 15, width=2 * self.width / 3, borderwidth=2)
        self.root13 = Frame(self.root1, height=12 * self.height / 15, width=2 * self.width / 3, borderwidth=2)
        self.root21 = Frame(self.root2, height=self.height / 3, width=self.width / 3, borderwidth=2, relief='groove')
        self.root22 = Frame(self.root2, height=2 * self.height / 3, width=self.width / 3, borderwidth=2, relief='groove')
        self.root11.grid_propagate(0)
        self.root12.grid_propagate(0)
        self.root13.grid_propagate(0)
        self.root21.pack_propagate(0)
        self.root22.grid_propagate(0)

        # Fourth layer of third frame of third layer
        self.root131 = Frame(self.root13, height=2 * self.height / 15, width=2 * self.width / 3)
        self.root132 = Frame(self.root13, height=13 * self.height / 15, width=2 * self.width / 3)
        self.root131.grid_propagate(0)
        self.root132.pack_propagate(0)

        # Table
        self.style = ttk.Style()
        self.invest_info = ttk.Treeview(self.root21, columns=('name', 'quantidade'), show='headings', selectmode='none')
        # Create the header of each column
        self.invest_info.heading('name', text='A????es')
        self.invest_info.heading('quantidade', text='Qnt.')
        # Table formating
        self.invest_info.column('#1', stretch=False, anchor='w', width=int(self.width/3 - 120))
        self.invest_info.column('#2', stretch=False, anchor='center', width=100)
        self.style.configure('Treeview', font=('', 12))
        self.style.configure('Treeview.Heading', font=('bolder', 18))
        # Relationship between Treeview and Scrollbar
        self.scroll = ttk.Scrollbar(self.root21, orient='vertical', command=self.invest_info.yview)
        self.invest_info.configure(yscroll=self.scroll.set)
        self.update_listbox()
        self.invest_info.pack_propagate(0)
        self.scroll.pack_propagate(0)

        # Main buttons
        self.acoes_button = Button(self.root11, text='A????es', font=(12), relief='sunken', command=self.change_market_to_stock)
        self.criptos_button = Button(self.root11, text='Cripto', font=(12), relief='raised', command=self.change_market_to_cripto)
        self.acoes_button.grid_propagate(0)
        self.criptos_button.grid_propagate(0)

        self.graph_buttons = [Button(self.root131, text=f'{col}', font=10, relief='raised', command=lambda i=i:self.change_plot(int(i)))
                              for i, col in enumerate(self.current_sheet['Quantidade'].columns)]
        self.graph_buttons[0].config(relief='sunken')
        [obj.pack_propagate(0) for obj in self.graph_buttons]

        self.total_invested_label = LabelFrame(self.root12, text='Total Investido', font=('bolder', 10), width=150,
                                               height=2*self.height / 15 - 25)
        self.total_invest = Label(self.total_invested_label, text=self.total_invested(),
                                  justify='left', font=('bold', 20))
        self.total_invested_label.pack_propagate(0)

        sns.set_theme(style='darkgrid')
        self.fig = plt.figure(figsize=(8, 4.5), facecolor='lightgrey')
        self.ax = self.fig.gca()
        self.line = self.plot_graph()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root132)

        self.put_widgets()

    def plot_graph(self):
        line = sns.lineplot(ax=self.ax,
                            data=self.stock_data[self.current_ticker]['Adj Close'].loc[self.current_date:] if
                            self.acoes_pressed else self.cripto_data[self.current_ticker]['Adj Close'].loc[self.current_date:])
        self.ax.set_ylabel('Pre??o (R$)' if self.acoes_pressed else 'Pre??o ($)')
        self.ax.set_xlabel('')
        self.fig.tight_layout()
        return line

    def update_labels(self):
        self.total_invest.config(text=self.total_invested())

    def update_listbox(self):
        '''Updates the names and quantities of each stock or cripto market based on the current sheet.'''
        for item in self.invest_info.get_children():
            self.invest_info.delete(item)
        for col, series in self.current_sheet['Quantidade'].iteritems():
            if self.acoes_pressed:
                self.invest_info.heading('name', text='A????es')
                self.invest_info.insert('', 'end', values=(str(col), str(series.dropna()[-1])))
            elif self.criptos_pressed:
                self.invest_info.heading('name', text='Criptoativos')
                self.invest_info.insert('', 'end', values=(str(col[:3]), str(series.dropna()[-1])))

    def put_widgets(self):
        '''Puts all of the widgets at the screen.'''
        self.root1.grid(column=0, row=0)
        self.root2.grid(column=1, row=0)

        self.root11.grid(column=0, row=0)
        self.root12.grid(column=0, row=1)
        self.root13.grid(column=0, row=2)
        self.root21.grid(column=0, row=0)
        self.root22.grid(column=0, row=1)

        self.root131.grid(column=0, row=0)
        self.root132.grid(column=0, row=1)

        self.acoes_button.grid(column=0, row=0, padx=10, pady=5)
        self.criptos_button.grid(column=1, row=0, padx=10, pady=5)
        [obj.pack(side='left', pady=2, padx=1, fill='both') for obj in self.graph_buttons]

        self.total_invested_label.grid(column=0, row=0, padx=10, pady=5)
        self.total_invest.pack(side='top')
        self.invest_info.pack(side='left', fill='both')
        self.scroll.pack(side='right', fill='y')

        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both')

    def load_database(self) -> pd.DataFrame:
        '''Loads data from the sheet that has date and number of stock and cripto transactions.'''
        return pd.read_excel(self.database, sheet_name='A????es', index_col=0, header=[0, 1]), \
               pd.read_excel(self.database, sheet_name='Criptoativos', index_col=0, header=[0, 1])

    def load_financial_data(self) -> dict:
        '''Loads data from yahoo API'''
        stock_data = dict()
        cripto_data = dict()
        for col in self.acoes['Quantidade'].columns:
            stock_data[f'{col}'] = web.DataReader(f'{col}.SA', data_source='yahoo', start=self.current_date)
        for col in self.criptos['Quantidade'].columns:
            cripto_data[f'{col}'] = web.DataReader(f'{col}', data_source='yahoo', start=self.current_date)
        return stock_data, cripto_data

    def change_market_to_stock(self):
        '''Changes the main content of the window. It's used when the acoes_button is pressed.'''
        self.current_sheet = self.acoes
        self.current_ticker = self.acoes['Quantidade'].columns[0]
        self.acoes_pressed = True
        self.criptos_pressed = False
        self.update_window()

    def change_market_to_cripto(self):
        '''Changes the main content of the window. It's used when the criptos_button is pressed.'''
        self.current_sheet = self.criptos
        self.current_ticker = self.criptos['Quantidade'].columns[0]
        self.acoes_pressed = False
        self.criptos_pressed = True
        self.update_window()

    def update_graph_buttons(self):
        for i, obj in enumerate(self.graph_buttons):
            try:
                if self.acoes_pressed:
                    obj.config(text=f'{self.current_sheet["Quantidade"].columns[i]}')
                elif self.criptos_pressed:
                    obj.config(text=f'{self.current_sheet["Quantidade"].columns[i][:3]}')
            except IndexError:
                for item in self.graph_buttons[i:]:
                    item.destroy()
                    self.graph_buttons.remove(item)

        if i != len(self.current_sheet["Quantidade"].columns):
            for n in range(len(self.current_sheet["Quantidade"].columns)-i-1):
                i = i + 1
                if self.acoes_pressed:
                    self.graph_buttons.append(Button(self.root131, text=f'{self.current_sheet["Quantidade"].columns[i]}',
                                                     font=10, relief='raised', command=lambda i=i:self.change_plot(int(i))))
                    self.graph_buttons[i].pack(side='left', pady=2, padx=1, fill='both')
                elif self.criptos_pressed:
                    self.graph_buttons.append(
                        Button(self.root131, text=f'{self.current_sheet["Quantidade"].columns[i][:3]}',
                               font=10, relief='raised', command=lambda i=i: self.change_plot(int(i))))
                    self.graph_buttons[i].pack(side='left', pady=2, padx=1, fill='both')
        self.change_plot(0)

    def change_plot(self, i):
        self.current_ticker = self.current_sheet['Quantidade'].columns[i]
        for idx, obj in enumerate(self.graph_buttons):
            if idx is i:
                obj.config(relief='sunken')
            else:
                obj.config(relief='raised')
        self.ax.clear()
        self.line = self.plot_graph()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both')

    def total_invested(self) -> str:
        '''Return the total value invested in stock.'''
        sum = 0
        if self.acoes_pressed:
            for col in self.acoes['Quantidade'].columns:
                sum = sum + self.acoes['Quantidade'][col].dropna()[-1] * self.stock_data[col]['Adj Close'][-1]
            return 'R$ ' + f'{sum:.2f}'
        elif self.criptos_pressed:
            for col in self.criptos['Quantidade'].columns:
                sum = sum + self.criptos['Quantidade'][col].dropna()[-1] * self.cripto_data[col]['Adj Close'][-1]
            return '$' + f'{sum:.2f}'
        return None

    def update_window(self):
        if self.acoes_pressed:
            self.acoes_button.config(relief='sunken')
            self.criptos_button.config(relief='raised')
        elif self.criptos_pressed:
            self.criptos_button.config(relief='sunken')
            self.acoes_button.config(relief='raised')
        self.update_listbox()
        self.update_labels()
        self.update_graph_buttons()


