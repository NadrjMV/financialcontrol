import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import sqlite3
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

class FinanceTracker:
    """
    A personal finance tracker application with a modern GUI.
    It allows users to manage income and expenses, view reports, and visualize data.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("1200x800")
        tb.Style(theme='darkly')

        # --- Language and Translations ---
        self.current_language = tk.StringVar(value="en_us")
        self.translations = self.load_translations()

        # --- Database Setup ---
        self.db_conn = sqlite3.connect('personal_finance.db')
        self.create_tables()

        # --- Main UI Structure ---
        self.main_frame = tb.Frame(self.root, padding=10)
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        self.header_frame = tb.Frame(self.main_frame)
        self.header_frame.pack(fill=X, pady=(0, 20))

        self.title_label = tb.Label(self.header_frame, text="", font=("Helvetica", 24, "bold"))
        self.title_label.pack(side=LEFT, expand=YES)

        self.lang_toggle = tb.Checkbutton(
            self.header_frame,
            text="PT-BR",
            bootstyle="primary-round-toggle",
            variable=self.current_language,
            onvalue="pt_br",
            offvalue="en_us",
            command=self.toggle_language
        )
        self.lang_toggle.pack(side=RIGHT, padx=10)

        self.notebook = tb.Notebook(self.main_frame, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=YES)

        # --- Create Tabs ---
        self.dashboard_tab = ScrolledFrame(self.notebook, autohide=True)
        self.transactions_tab = tb.Frame(self.notebook)
        self.history_tab = tb.Frame(self.notebook)
        self.reports_tab = tb.Frame(self.notebook)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.transactions_tab, text="Add Transaction")
        self.notebook.add(self.history_tab, text="Transaction History")
        self.notebook.add(self.reports_tab, text="Reports & Charts")

        # --- Populate Tabs ---
        self.create_dashboard_widgets()
        self.create_transactions_widgets()
        self.create_history_widgets()
        self.create_reports_widgets()

        # --- Initial Load ---
        self.update_ui_text()
        self.update_dashboard()
        self.populate_history()


    def load_translations(self):
        """Loads the language dictionary for EN and PT-BR."""
        return {
            "en_us": {
                "title": "Personal Finance Tracker",
                "dashboard": "Dashboard",
                "add_transaction": "Add Transaction",
                "history": "Transaction History",
                "reports": "Reports & Charts",
                "current_balance": "Current Balance",
                "monthly_income": "Income (This Month)",
                "monthly_expenses": "Expenses (This Month)",
                "spending_percentage": "You spent {:.0f}% of your income this month.",
                "no_income_warning": "You spent ${:.2f} but had no income this month.",
                "add_income": "Add Income",
                "add_expense": "Add Expense",
                "amount": "Amount",
                "source": "Source",
                "date": "Date",
                "notes": "Notes (Optional)",
                "category": "Category",
                "payment_method": "Payment Method",
                "add_button": "Add Record",
                "income_success": "Income added successfully!",
                "expense_success": "Expense added successfully!",
                "filter_by": "Filter by:",
                "month": "Month",
                "type": "Type",
                "all": "All",
                "income": "Income",
                "expense": "Expense",
                "export_csv": "Export as CSV",
                "date_range": "Date Range",
                "from": "From",
                "to": "To",
                "generate_report": "Generate Report",
                "expenses_by_category": "Expenses by Category",
                "balance_evolution": "Balance Evolution Over Time",
                "col_date": "Date",
                "col_type": "Type",
                "col_category_source": "Category/Source",
                "col_payment": "Payment Method",
                "col_amount": "Amount",
                "col_notes": "Notes",
                "sources_options": ["Salary", "Gift", "Freelance", "Investment", "Other"],
                "categories_options": ["Food", "Bills", "Transport", "Entertainment", "Health", "Shopping", "Other"],
                "payment_options": ["Cash", "Card", "PIX", "Transfer"]
            },
            "pt_br": {
                "title": "Controle Financeiro Pessoal",
                "dashboard": "Painel",
                "add_transaction": "Adicionar Transação",
                "history": "Histórico de Transações",
                "reports": "Relatórios e Gráficos",
                "current_balance": "Saldo Atual",
                "monthly_income": "Renda (Este Mês)",
                "monthly_expenses": "Despesas (Este Mês)",
                "spending_percentage": "Você gastou {:.0f}% da sua renda este mês.",
                "no_income_warning": "Você gastou R${:.2f} mas não teve renda este mês.",
                "add_income": "Adicionar Renda",
                "add_expense": "Adicionar Despesa",
                "amount": "Valor",
                "source": "Fonte",
                "date": "Data",
                "notes": "Notas (Opcional)",
                "category": "Categoria",
                "payment_method": "Método de Pagamento",
                "add_button": "Adicionar Registro",
                "income_success": "Renda adicionada com sucesso!",
                "expense_success": "Despesa adicionada com sucesso!",
                "filter_by": "Filtrar por:",
                "month": "Mês",
                "type": "Tipo",
                "all": "Todos",
                "income": "Renda",
                "expense": "Despesa",
                "export_csv": "Exportar para CSV",
                "date_range": "Período",
                "from": "De",
                "to": "Até",
                "generate_report": "Gerar Relatório",
                "expenses_by_category": "Despesas por Categoria",
                "balance_evolution": "Evolução do Saldo ao Longo do Tempo",
                "col_date": "Data",
                "col_type": "Tipo",
                "col_category_source": "Categoria/Fonte",
                "col_payment": "Pagamento",
                "col_amount": "Valor",
                "col_notes": "Notas",
                "sources_options": ["Salário", "Presente", "Freelance", "Investimento", "Outro"],
                "categories_options": ["Alimentação", "Contas", "Transporte", "Lazer", "Saúde", "Compras", "Outro"],
                "payment_options": ["Dinheiro", "Cartão", "PIX", "Transferência"]
            }
        }

    def get_translation(self, key):
        """Gets a translated string for the current language."""
        return self.translations[self.current_language.get()].get(key, f"_{key}_")

    def toggle_language(self):
        """Switches the application language and updates all UI text."""
        self.update_ui_text()
        self.update_dashboard()
        self.populate_history()
        self.update_reports_ui()

    def create_tables(self):
        """Creates the necessary SQLite tables if they don't exist."""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                source TEXT NOT NULL,
                date TEXT NOT NULL,
                notes TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                date TEXT NOT NULL,
                notes TEXT
            )
        ''')
        self.db_conn.commit()

    # --- Dashboard Methods ---
    def create_dashboard_widgets(self):
        """Creates all widgets for the Dashboard tab."""
        frame = self.dashboard_tab.container
        
        # Balance Card
        balance_card = tb.Frame(frame, bootstyle=SECONDARY, padding=20)
        balance_card.pack(fill=X, pady=10)
        self.balance_label_title = tb.Label(balance_card, text="", font=("Helvetica", 16))
        self.balance_label_title.pack()
        self.balance_label_value = tb.Label(balance_card, text="", font=("Helvetica", 48, "bold"), bootstyle=PRIMARY)
        self.balance_label_value.pack()

        # Summary Cards (Income & Expenses)
        summary_frame = tb.Frame(frame)
        summary_frame.pack(fill=X, pady=10)
        summary_frame.columnconfigure((0, 1), weight=1)

        income_card = tb.Frame(summary_frame, bootstyle=SECONDARY, padding=20)
        income_card.grid(row=0, column=0, sticky=NSEW, padx=(0, 5))
        self.income_label_title = tb.Label(income_card, text="", font=("Helvetica", 16))
        self.income_label_title.pack()
        self.income_label_value = tb.Label(income_card, text="", font=("Helvetica", 28, "bold"), bootstyle=SUCCESS)
        self.income_label_value.pack()

        expense_card = tb.Frame(summary_frame, bootstyle=SECONDARY, padding=20)
        expense_card.grid(row=0, column=1, sticky=NSEW, padx=(5, 0))
        self.expense_label_title = tb.Label(expense_card, text="", font=("Helvetica", 16))
        self.expense_label_title.pack()
        self.expense_label_value = tb.Label(expense_card, text="", font=("Helvetica", 28, "bold"), bootstyle=DANGER)
        self.expense_label_value.pack()
        
        # Spending Percentage
        self.spending_label = tb.Label(frame, text="", font=("Helvetica", 14, "italic"))
        self.spending_label.pack(pady=20)

    def update_dashboard(self):
        """Fetches and displays the latest financial summary on the dashboard."""
        cursor = self.db_conn.cursor()
        
        # Total Balance
        cursor.execute("SELECT SUM(amount) FROM income")
        total_income = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM expenses")
        total_expenses = cursor.fetchone()[0] or 0
        balance = total_income - total_expenses
        currency_symbol = "R$" if self.current_language.get() == 'pt_br' else "$"
        self.balance_label_value.config(text=f"{currency_symbol}{balance:,.2f}")

        # Monthly Summary
        today = datetime.date.today()
        month_start = today.strftime('%Y-%m-01')
        cursor.execute("SELECT SUM(amount) FROM income WHERE date >= ?", (month_start,))
        monthly_income = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date >= ?", (month_start,))
        monthly_expenses = cursor.fetchone()[0] or 0
        self.income_label_value.config(text=f"{currency_symbol}{monthly_income:,.2f}")
        self.expense_label_value.config(text=f"{currency_symbol}{monthly_expenses:,.2f}")
        
        # Spending Percentage
        if monthly_income > 0:
            percentage = (monthly_expenses / monthly_income) * 100
            self.spending_label.config(text=self.get_translation("spending_percentage").format(percentage))
        elif monthly_expenses > 0:
            self.spending_label.config(text=self.get_translation("no_income_warning").format(monthly_expenses))
        else:
            self.spending_label.config(text="")
            

    # --- Add Transaction Methods ---
    def create_transactions_widgets(self):
        """Creates widgets for adding income and expenses."""
        trans_notebook = tb.Notebook(self.transactions_tab)
        trans_notebook.pack(fill=BOTH, expand=YES, padx=20, pady=10)

        # --- Income Tab ---
        income_frame = tb.Frame(trans_notebook, padding=20)
        self.income_source_var = tk.StringVar()
        self.income_amount_var = tk.DoubleVar()
        self.income_date_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
        self.income_notes_var = tk.StringVar()

        self.income_amount_label = tb.Label(income_frame, text="", font=("Helvetica", 12))
        self.income_amount_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        tb.Entry(income_frame, textvariable=self.income_amount_var, bootstyle=SUCCESS).grid(row=0, column=1, sticky=EW, padx=5, pady=5)

        self.income_source_label = tb.Label(income_frame, text="", font=("Helvetica", 12))
        self.income_source_label.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.income_source_combo = tb.Combobox(income_frame, textvariable=self.income_source_var, bootstyle=SUCCESS)
        self.income_source_combo.grid(row=1, column=1, sticky=EW, padx=5, pady=5)

        self.income_date_label = tb.Label(income_frame, text="", font=("Helvetica", 12))
        self.income_date_label.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        tb.DateEntry(income_frame, textvariable=self.income_date_var, bootstyle=SUCCESS, dateformat='%Y-%m-%d').grid(row=2, column=1, sticky=EW, padx=5, pady=5)
        
        self.income_notes_label = tb.Label(income_frame, text="", font=("Helvetica", 12))
        self.income_notes_label.grid(row=3, column=0, sticky=W, padx=5, pady=5)
        tb.Entry(income_frame, textvariable=self.income_notes_var, bootstyle=SUCCESS).grid(row=3, column=1, sticky=EW, padx=5, pady=5)

        self.add_income_button = tb.Button(income_frame, text="", command=self.add_income, bootstyle="success")
        self.add_income_button.grid(row=4, column=0, columnspan=2, pady=20)
        income_frame.columnconfigure(1, weight=1)

        # --- Expense Tab ---
        expense_frame = tb.Frame(trans_notebook, padding=20)
        self.expense_amount_var = tk.DoubleVar()
        self.expense_category_var = tk.StringVar()
        self.expense_payment_var = tk.StringVar()
        self.expense_date_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
        self.expense_notes_var = tk.StringVar()

        self.expense_amount_label = tb.Label(expense_frame, text="", font=("Helvetica", 12))
        self.expense_amount_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        tb.Entry(expense_frame, textvariable=self.expense_amount_var, bootstyle=DANGER).grid(row=0, column=1, sticky=EW, padx=5, pady=5)

        self.expense_category_label = tb.Label(expense_frame, text="", font=("Helvetica", 12))
        self.expense_category_label.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.expense_category_combo = tb.Combobox(expense_frame, textvariable=self.expense_category_var, bootstyle=DANGER)
        self.expense_category_combo.grid(row=1, column=1, sticky=EW, padx=5, pady=5)

        self.expense_payment_label = tb.Label(expense_frame, text="", font=("Helvetica", 12))
        self.expense_payment_label.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.expense_payment_combo = tb.Combobox(expense_frame, textvariable=self.expense_payment_var, bootstyle=DANGER)
        self.expense_payment_combo.grid(row=2, column=1, sticky=EW, padx=5, pady=5)

        self.expense_date_label = tb.Label(expense_frame, text="", font=("Helvetica", 12))
        self.expense_date_label.grid(row=3, column=0, sticky=W, padx=5, pady=5)
        tb.DateEntry(expense_frame, textvariable=self.expense_date_var, bootstyle=DANGER, dateformat='%Y-%m-%d').grid(row=3, column=1, sticky=EW, padx=5, pady=5)

        self.expense_notes_label = tb.Label(expense_frame, text="", font=("Helvetica", 12))
        self.expense_notes_label.grid(row=4, column=0, sticky=W, padx=5, pady=5)
        tb.Entry(expense_frame, textvariable=self.expense_notes_var, bootstyle=DANGER).grid(row=4, column=1, sticky=EW, padx=5, pady=5)

        self.add_expense_button = tb.Button(expense_frame, text="", command=self.add_expense, bootstyle="danger")
        self.add_expense_button.grid(row=5, column=0, columnspan=2, pady=20)
        expense_frame.columnconfigure(1, weight=1)

        trans_notebook.add(income_frame, text=self.get_translation("add_income"))
        trans_notebook.add(expense_frame, text=self.get_translation("add_expense"))
        self.trans_notebook = trans_notebook

    def add_income(self):
        """Validates and adds a new income record to the database."""
        amount = self.income_amount_var.get()
        source = self.income_source_var.get()
        date = self.income_date_var.get()
        notes = self.income_notes_var.get()

        if not amount or not source or not date:
            messagebox.showwarning("Input Error", "Amount, Source, and Date are required.")
            return

        cursor = self.db_conn.cursor()
        cursor.execute("INSERT INTO income (amount, source, date, notes) VALUES (?, ?, ?, ?)",
                       (amount, source, date, notes))
        self.db_conn.commit()
        messagebox.showinfo("Success", self.get_translation("income_success"))
        self.income_amount_var.set(0.0)
        self.income_notes_var.set("")
        self.update_dashboard()
        self.populate_history()
        
    def add_expense(self):
        """Validates and adds a new expense record to the database."""
        amount = self.expense_amount_var.get()
        category = self.expense_category_var.get()
        payment_method = self.expense_payment_var.get()
        date = self.expense_date_var.get()
        notes = self.expense_notes_var.get()
        
        if not amount or not category or not payment_method or not date:
            messagebox.showwarning("Input Error", "Amount, Category, Payment Method, and Date are required.")
            return

        cursor = self.db_conn.cursor()
        cursor.execute("INSERT INTO expenses (amount, category, payment_method, date, notes) VALUES (?, ?, ?, ?, ?)",
                       (amount, category, payment_method, date, notes))
        self.db_conn.commit()
        messagebox.showinfo("Success", self.get_translation("expense_success"))
        self.expense_amount_var.set(0.0)
        self.expense_notes_var.set("")
        self.update_dashboard()
        self.populate_history()


    # --- History Methods ---
    def create_history_widgets(self):
        """Creates widgets for the transaction history tab."""
        # Filters
        filter_frame = tb.Frame(self.history_tab, padding=10)
        filter_frame.pack(fill=X)
        self.history_filter_label = tb.Label(filter_frame, text="", font=("Helvetica", 12))
        self.history_filter_label.pack(side=LEFT, padx=(0, 10))

        self.history_month_var = tk.StringVar(value="All")
        self.history_month_label = tb.Label(filter_frame, text="")
        self.history_month_label.pack(side=LEFT, padx=5)
        months = [self.get_translation("all")] + [datetime.date(2000, i, 1).strftime('%B') for i in range(1, 13)]
        tb.Combobox(filter_frame, textvariable=self.history_month_var, values=months, state="readonly").pack(side=LEFT, padx=5)

        self.history_type_var = tk.StringVar(value="All")
        self.history_type_label = tb.Label(filter_frame, text="")
        self.history_type_label.pack(side=LEFT, padx=5)
        self.history_type_combo = tb.Combobox(filter_frame, textvariable=self.history_type_var, state="readonly")
        self.history_type_combo.pack(side=LEFT, padx=5)
        self.history_type_var.trace("w", lambda *args: self.populate_history())

        self.export_button = tb.Button(filter_frame, text="", command=self.export_to_csv, bootstyle="primary-outline")
        self.export_button.pack(side=RIGHT, padx=10)

        # Treeview
        tree_frame = tb.Frame(self.history_tab)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        self.history_tree = tb.Treeview(tree_frame, columns=("date", "type", "category_source", "payment", "amount", "notes"), show="headings", bootstyle=PRIMARY)
        self.history_tree.pack(side=LEFT, fill=BOTH, expand=YES)

        vsb = tb.Scrollbar(tree_frame, orient="vertical", command=self.history_tree.yview, bootstyle="primary-round")
        vsb.pack(side='right', fill='y')
        self.history_tree.configure(yscrollcommand=vsb.set)
        
        # Define column headings and colors
        self.history_tree.tag_configure('income', foreground=tb.Style().colors.success)
        self.history_tree.tag_configure('expense', foreground=tb.Style().colors.danger)
    
    def populate_history(self, *args):
        """Fetches and displays transaction data in the treeview based on filters."""
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)

        cursor = self.db_conn.cursor()
        
        income_query = "SELECT date, 'Income', source, '', amount, notes FROM income"
        expense_query = "SELECT date, 'Expense', category, payment_method, -amount, notes FROM expenses"

        trans_type = self.history_type_var.get()
        queries = []
        if trans_type == self.get_translation("all"):
            queries.extend([income_query, expense_query])
        elif trans_type == self.get_translation("income"):
            queries.append(income_query)
        elif trans_type == self.get_translation("expense"):
            queries.append(expense_query)
        
        all_transactions = []
        for query in queries:
            cursor.execute(query)
            all_transactions.extend(cursor.fetchall())
        
        # Sort by date
        all_transactions.sort(key=lambda x: x[0], reverse=True)
        
        currency_symbol = "R$" if self.current_language.get() == 'pt_br' else "$"
        for row in all_transactions:
            tag = 'income' if row[1] == 'Income' else 'expense'
            amount_str = f"{currency_symbol}{abs(row[4]):,.2f}"
            display_row = (row[0], self.get_translation(row[1].lower()), row[2], row[3], amount_str, row[5])
            self.history_tree.insert("", "end", values=display_row, tags=(tag,))

    def export_to_csv(self):
        """Exports the transaction history to a CSV file."""
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT date, 'Income' as type, source as 'category/source', '' as payment_method, amount, notes FROM income UNION ALL SELECT date, 'Expense' as type, category, payment_method, -amount, notes FROM expenses ORDER BY date DESC")
        data = cursor.fetchall()
        
        if not data:
            messagebox.showinfo("No Data", "There is no data to export.")
            return

        df = pd.DataFrame(data, columns=['Date', 'Type', 'Category/Source', 'Payment Method', 'Amount', 'Notes'])
        
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            if file_path:
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")

    # --- Reports Methods ---
    def create_reports_widgets(self):
        """Creates widgets for the reports tab."""
        self.reports_main_frame = tb.Frame(self.reports_tab, padding=10)
        self.reports_main_frame.pack(fill=BOTH, expand=YES)
        
        # Filters
        reports_filter_frame = tb.LabelFrame(self.reports_main_frame, text="", padding=10)
        reports_filter_frame.pack(fill=X, pady=(0,10))
        self.reports_filter_frame = reports_filter_frame

        today = datetime.date.today()
        start_of_month = today.replace(day=1)
        self.report_start_date = tk.StringVar(value=start_of_month.strftime('%Y-%m-%d'))
        self.report_end_date = tk.StringVar(value=today.strftime('%Y-%m-%d'))

        self.from_label = tb.Label(reports_filter_frame, text="")
        self.from_label.grid(row=0, column=0, padx=5, pady=5)
        tb.DateEntry(reports_filter_frame, textvariable=self.report_start_date, dateformat='%Y-%m-%d').grid(row=0, column=1, padx=5, pady=5)
        self.to_label = tb.Label(reports_filter_frame, text="")
        self.to_label.grid(row=0, column=2, padx=5, pady=5)
        tb.DateEntry(reports_filter_frame, textvariable=self.report_end_date, dateformat='%Y-%m-%d').grid(row=0, column=3, padx=5, pady=5)

        self.generate_report_button = tb.Button(reports_filter_frame, text="", command=self.generate_reports, bootstyle="primary")
        self.generate_report_button.grid(row=0, column=4, padx=20, pady=5)
        
        # Chart Frames
        chart_frame = tb.Frame(self.reports_main_frame)
        chart_frame.pack(fill=BOTH, expand=YES)
        chart_frame.columnconfigure((0, 1), weight=1)
        chart_frame.rowconfigure(0, weight=1)

        self.pie_chart_frame = tb.LabelFrame(chart_frame, text="", padding=10)
        self.pie_chart_frame.grid(row=0, column=0, sticky=NSEW, padx=(0,5), pady=5)

        self.line_chart_frame = tb.LabelFrame(chart_frame, text="", padding=10)
        self.line_chart_frame.grid(row=0, column=1, sticky=NSEW, padx=(5,0), pady=5)
        
        self.pie_canvas = None
        self.line_canvas = None


    def generate_reports(self):
        """Generates and displays the pie and line charts."""
        self.generate_pie_chart()
        self.generate_line_chart()
        
    def generate_pie_chart(self):
        """Creates a pie chart of expenses by category."""
        if self.pie_canvas:
            self.pie_canvas.get_tk_widget().destroy()

        start_date = self.report_start_date.get()
        end_date = self.report_end_date.get()

        cursor = self.db_conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE date BETWEEN ? AND ? GROUP BY category", (start_date, end_date))
        data = cursor.fetchall()

        fig = Figure(figsize=(5, 4), dpi=100, facecolor=tb.Style().colors.bg)
        ax = fig.add_subplot(111)
        ax.set_facecolor(tb.Style().colors.bg)
        fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

        if data:
            labels = [row[0] for row in data]
            sizes = [row[1] for row in data]
            
            wedges, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%', startangle=90,
                                              pctdistance=0.85, textprops={'color': 'white'})
            ax.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                      labelcolor='white')
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, "No expense data for this period", ha='center', va='center', color='white')

        self.pie_canvas = FigureCanvasTkAgg(fig, master=self.pie_chart_frame)
        self.pie_canvas.draw()
        self.pie_canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        
    def generate_line_chart(self):
        """Creates a line chart showing balance evolution."""
        if self.line_canvas:
            self.line_canvas.get_tk_widget().destroy()

        start_date = self.report_start_date.get()
        end_date = self.report_end_date.get()
        
        query = """
        SELECT date, SUM(amount) as daily_net
        FROM (
            SELECT date, amount FROM income
            UNION ALL
            SELECT date, -amount FROM expenses
        )
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        """
        df = pd.read_sql_query(query, self.db_conn, params=(start_date, end_date))
        
        fig = Figure(figsize=(5, 4), dpi=100, facecolor=tb.Style().colors.bg)
        ax = fig.add_subplot(111)
        ax.set_facecolor(tb.Style().colors.inputbg)
        fig.subplots_adjust(bottom=0.2)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['balance'] = df['daily_net'].cumsum()
            ax.plot(df['date'], df['balance'], marker='o', linestyle='-', color=tb.Style().colors.primary)
            ax.tick_params(axis='x', labelrotation=45, colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
        else:
            ax.text(0.5, 0.5, "No transaction data for this period", ha='center', va='center', color='white')

        self.line_canvas = FigureCanvasTkAgg(fig, master=self.line_chart_frame)
        self.line_canvas.draw()
        self.line_canvas.get_tk_widget().pack(fill=BOTH, expand=YES)

    # --- UI Update Methods ---
    def update_ui_text(self):
        """Updates all static text widgets with the current language."""
        lang = self.current_language.get()
        
        self.root.title(self.get_translation("title"))
        self.title_label.config(text=self.get_translation("title"))
        
        # Notebook tabs
        self.notebook.tab(0, text=self.get_translation("dashboard"))
        self.notebook.tab(1, text=self.get_translation("add_transaction"))
        self.notebook.tab(2, text=self.get_translation("history"))
        self.notebook.tab(3, text=self.get_translation("reports"))
        
        # Dashboard
        self.balance_label_title.config(text=self.get_translation("current_balance"))
        self.income_label_title.config(text=self.get_translation("monthly_income"))
        self.expense_label_title.config(text=self.get_translation("monthly_expenses"))

        # Add Transaction
        self.trans_notebook.tab(0, text=self.get_translation("add_income"))
        self.trans_notebook.tab(1, text=self.get_translation("add_expense"))
        
        self.income_amount_label.config(text=self.get_translation("amount"))
        self.income_source_label.config(text=self.get_translation("source"))
        self.income_date_label.config(text=self.get_translation("date"))
        self.income_notes_label.config(text=self.get_translation("notes"))
        self.add_income_button.config(text=self.get_translation("add_button"))
        self.income_source_combo['values'] = self.get_translation("sources_options")

        self.expense_amount_label.config(text=self.get_translation("amount"))
        self.expense_category_label.config(text=self.get_translation("category"))
        self.expense_payment_label.config(text=self.get_translation("payment_method"))
        self.expense_date_label.config(text=self.get_translation("date"))
        self.expense_notes_label.config(text=self.get_translation("notes"))
        self.add_expense_button.config(text=self.get_translation("add_button"))
        self.expense_category_combo['values'] = self.get_translation("categories_options")
        self.expense_payment_combo['values'] = self.get_translation("payment_options")

        # History
        self.history_filter_label.config(text=self.get_translation("filter_by"))
        self.history_month_label.config(text=self.get_translation("month"))
        self.history_type_label.config(text=self.get_translation("type"))
        self.history_type_combo['values'] = [self.get_translation("all"), self.get_translation("income"), self.get_translation("expense")]
        self.history_type_var.set(self.get_translation("all")) # reset filter
        self.export_button.config(text=self.get_translation("export_csv"))
        
        # History Treeview Columns
        self.history_tree.heading("date", text=self.get_translation("col_date"))
        self.history_tree.heading("type", text=self.get_translation("col_type"))
        self.history_tree.heading("category_source", text=self.get_translation("col_category_source"))
        self.history_tree.heading("payment", text=self.get_translation("col_payment"))
        self.history_tree.heading("amount", text=self.get_translation("col_amount"))
        self.history_tree.heading("notes", text=self.get_translation("col_notes"))
        
        # Reports
        self.update_reports_ui()

    def update_reports_ui(self):
        """Updates the text on the reports tab specifically."""
        self.reports_filter_frame.config(text=self.get_translation("date_range"))
        self.from_label.config(text=self.get_translation("from"))
        self.to_label.config(text=self.get_translation("to"))
        self.generate_report_button.config(text=self.get_translation("generate_report"))
        self.pie_chart_frame.config(text=self.get_translation("expenses_by_category"))
        self.line_chart_frame.config(text=self.get_translation("balance_evolution"))
        self.generate_reports()


if __name__ == "__main__":
    app = tb.Window(themename="darkly")
    finance_app = FinanceTracker(app)
    app.mainloop()

# Created by @Jordanlvs - all rights reserved
