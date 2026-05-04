"""
Expense Tracker - приложение для отслеживания личных расходов
Автор: Нигаматуллин Глеб Владиславович
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

# Имя файла для хранения данных
DATA_FILE = "expenses.json"


class ExpenseTracker:
    """Главный класс приложения для учёта расходов"""

    def __init__(self, root):
        """
        Инициализация приложения
        root: корневое окно Tkinter
        """
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("950x650")
        self.root.resizable(True, True)

        # Загружаем сохранённые расходы
        self.expenses = self.load_expenses()

        # Текущий отфильтрованный список (для корректного удаления)
        self.current_displayed_list = []

        # Создаём интерфейс
        self.create_widgets()

        # Обновляем таблицу
        self.refresh_table()

    def load_expenses(self):
        """
        Загружает расходы из JSON-файла
        возвращает: список расходов (каждый расход - словарь)
        """
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_expenses(self):
        """Сохраняет расходы в JSON-файл"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def create_widgets(self):
        """Создаёт все элементы интерфейса"""

        # ==================== Панель ввода (левая часть) ====================
        input_frame = tk.LabelFrame(self.root, text="➕ Добавление расхода", padx=10, pady=10, font=("Arial", 10, "bold"))
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Поле "Сумма"
        tk.Label(input_frame, text="Сумма (руб):", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.amount_entry = tk.Entry(input_frame, width=20, font=("Arial", 12))
        self.amount_entry.grid(row=0, column=1, pady=5, padx=5)

        # Подсказка для поля суммы
        tk.Label(input_frame, text="(например: 150 или 49.99)", font=("Arial", 8), fg="gray").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        # Поле "Категория" (выпадающий список)
        tk.Label(input_frame, text="Категория:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, width=18)
        self.category_combo['values'] = ("Еда", "Транспорт", "Развлечения", "Коммунальные услуги", "Здоровье", "Одежда", "Другое")
        self.category_combo.grid(row=2, column=1, pady=5, padx=5)
        self.category_combo.current(0)

        # Поле "Дата" (календарь)
        tk.Label(input_frame, text="Дата:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.date_entry = DateEntry(input_frame, width=18, background='darkblue', foreground='white', borderwidth=2,
                                     date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=3, column=1, pady=5, padx=5)

        # Кнопка "Добавить расход"
        self.add_button = tk.Button(input_frame, text="Добавить расход", command=self.add_expense,
                                    bg="lightgreen", font=("Arial", 10, "bold"), width=18)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=15)

        # ==================== Панель фильтрации ====================
        filter_frame = tk.LabelFrame(self.root, text="🔍 Фильтрация и подсчёт суммы", padx=10, pady=10, font=("Arial", 10, "bold"))
        filter_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 10))

        # Фильтр по категории
        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar(value="Все")
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, width=15)
        self.filter_category_combo['values'] = ("Все", "Еда", "Транспорт", "Развлечения", "Коммунальные услуги", "Здоровье", "Одежда", "Другое")
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)

        # Период для подсчёта суммы
        tk.Label(filter_frame, text="Дата с:").grid(row=0, column=2, padx=5, pady=5)
        self.start_date = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="по:").grid(row=0, column=4, padx=5, pady=5)
        self.end_date = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка "Применить фильтр"
        self.filter_button = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter,
                                       bg="lightblue", width=15)
        self.filter_button.grid(row=1, column=0, columnspan=2, pady=5, padx=5)

        # Кнопка "Сбросить фильтр"
        self.reset_button = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter,
                                      bg="lightgray", width=15)
        self.reset_button.grid(row=1, column=2, columnspan=2, pady=5, padx=5)

        # Кнопка "Подсчитать сумму за период"
        self.sum_button = tk.Button(filter_frame, text="Подсчитать сумму", command=self.calculate_sum,
                                    bg="lightyellow", width=15)
        self.sum_button.grid(row=1, column=4, columnspan=2, pady=5, padx=5)

        # Метка для отображения суммы
        self.sum_label = tk.Label(filter_frame, text="💰 Сумма за период: 0.00 руб", font=("Arial", 10, "bold"), fg="green")
        self.sum_label.grid(row=2, column=0, columnspan=6, pady=5)

        # ==================== Таблица расходов ====================
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создаём Treeview (таблицу)
        columns = ("id", "date", "category", "amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Настройка заголовков
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма (руб)")

        # Настройка ширины колонок
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("date", width=120, anchor=tk.CENTER)
        self.tree.column("category", width=180, anchor=tk.CENTER)
        self.tree.column("amount", width=120, anchor=tk.CENTER)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления внизу
        button_bottom_frame = tk.Frame(self.root)
        button_bottom_frame.pack(pady=10)

        # Кнопка "Удалить выбранный расход"
        self.delete_button = tk.Button(button_bottom_frame, text="🗑 Удалить выбранный расход", command=self.delete_expense,
                                       bg="lightcoral", font=("Arial", 10), width=20)
        self.delete_button.pack(side=tk.LEFT, padx=10)

        # Кнопка "Выход"
        self.exit_button = tk.Button(button_bottom_frame, text="❌ Выход", command=self.root.quit,
                                     bg="lightgray", font=("Arial", 10), width=20)
        self.exit_button.pack(side=tk.LEFT, padx=10)

    def validate_amount(self, amount_str):
        """
        Проверяет корректность введённой суммы
        amount_str: строка с суммой
        возвращает: (bool, float) - (валидна ли, значение)
        """
        if not amount_str or amount_str.strip() == "":
            return False, None

        try:
            amount = float(amount_str)
            if amount <= 0:
                return False, None
            return True, amount
        except ValueError:
            return False, None

    def add_expense(self):
        """Добавляет новый расход в список"""
        amount_str = self.amount_entry.get().strip()
        category = self.category_var.get()
        date = self.date_entry.get()

        # Валидация суммы
        is_valid, amount = self.validate_amount(amount_str)
        if not is_valid:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом (например: 150 или 49.99)!")
            return

        # Валидация даты (проверяем, что дата в правильном формате)
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return

        # Создаём новый расход
        if self.expenses:
            new_id = max(e["id"] for e in self.expenses) + 1
        else:
            new_id = 1

        expense = {
            "id": new_id,
            "date": date,
            "category": category,
            "amount": amount
        }

        self.expenses.append(expense)
        self.save_expenses()
        self.refresh_table()

        # Очищаем поле суммы
        self.amount_entry.delete(0, tk.END)

        messagebox.showinfo("Успех", f"Расход {amount:.2f} руб добавлен!")

    def refresh_table(self, expenses_to_show=None):
        """
        Обновляет таблицу расходов
        expenses_to_show: список расходов для отображения (если None - показывает все)
        """
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Определяем, что показывать
        if expenses_to_show is not None:
            data = expenses_to_show
            self.current_displayed_list = expenses_to_show.copy()
        else:
            data = self.expenses
            self.current_displayed_list = self.expenses.copy()

        # Заполняем таблицу
        for exp in data:
            self.tree.insert("", tk.END, values=(exp["id"], exp["date"], exp["category"], f"{exp['amount']:.2f}"))

    def apply_filter(self):
        """Применяет фильтр по категории и дате"""
        filtered = self.expenses.copy()

        # Фильтр по категории
        selected_category = self.filter_category_var.get()
        if selected_category != "Все":
            filtered = [e for e in filtered if e["category"] == selected_category]

        # Фильтр по дате
        start = self.start_date.get()
        end = self.end_date.get()

        if start:
            filtered = [e for e in filtered if e["date"] >= start]
        if end:
            filtered = [e for e in filtered if e["date"] <= end]

        self.refresh_table(filtered)

        # Обновляем сумму за текущий отфильтрованный период
        total = sum(e["amount"] for e in filtered)
        self.sum_label.config(text=f"💰 Сумма за период: {total:.2f} руб")

    def reset_filter(self):
        """Сбрасывает все фильтры"""
        self.filter_category_var.set("Все")
        # Сбрасываем даты на начальные значения
        self.start_date.set_date(datetime.today())
        self.end_date.set_date(datetime.today())
        self.refresh_table()
        total = sum(e["amount"] for e in self.expenses)
        self.sum_label.config(text=f"💰 Сумма за период: {total:.2f} руб")

    def calculate_sum(self):
        """Подсчитывает сумму расходов за выбранный период (из полей с/по)"""
        start = self.start_date.get()
        end = self.end_date.get()

        filtered = self.expenses.copy()

        if start:
            filtered = [e for e in filtered if e["date"] >= start]
        if end:
            filtered = [e for e in filtered if e["date"] <= end]

        total = sum(e["amount"] for e in filtered)

        # Формируем сообщение
        if start or end:
            period_str = f"c {start} по {end}"
        else:
            period_str = "за всё время"

        messagebox.showinfo("Результат", f"Сумма расходов {period_str}:\n{total:.2f} руб")
        self.sum_label.config(text=f"💰 Сумма за {period_str}: {total:.2f} руб")

    def delete_expense(self):
        """Удаляет выбранный расход из списка"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите расход для удаления!")
            return

        # Получаем ID выбранного расхода
        item = self.tree.item(selected[0])
        expense_id = item['values'][0]

        # Находим расход для подтверждения
        expense_to_delete = None
        for exp in self.expenses:
            if exp["id"] == expense_id:
                expense_to_delete = exp
                break

        if not expense_to_delete:
            messagebox.showerror("Ошибка", "Расход не найден!")
            return

        # Подтверждение удаления
        confirm = messagebox.askyesno("Подтверждение",
                                       f"Удалить расход?\n"
                                       f"Дата: {expense_to_delete['date']}\n"
                                       f"Категория: {expense_to_delete['category']}\n"
                                       f"Сумма: {expense_to_delete['amount']:.2f} руб")
        if confirm:
            self.expenses = [e for e in self.expenses if e["id"] != expense_id]

            # Перенумеровываем ID для порядка
            for i, exp in enumerate(self.expenses, 1):
                exp["id"] = i

            self.save_expenses()

            # Обновляем отображение с сохранением текущего фильтра
            self.apply_filter()

            messagebox.showinfo("Успех", "Расход удалён!")


# ==================== Запуск приложения ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()