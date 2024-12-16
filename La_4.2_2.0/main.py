import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


class Room:
    def __init__(self, number, info, price):
        self.number = number
        self.info = info
        self.price = price


class Client:
    def __init__(self, name, room):
        self.name = name
        self.room = room


class DB:
    def __init__(self, parent, rooms, clients, hotel):
        self.top = tk.Toplevel(parent)
        self.top.title("База данных")
        self.top.geometry("300x200")
        self.clients = clients
        self.rooms = rooms
        self.hotel = hotel

        tk.Button(self.top, text="Поиск клиента по фамилии", command=self.find_client).pack(pady=10)

        tk.Button(self.top, text="Сохранить в БД", command=self.save_to_database).pack(pady=10)
        tk.Button(self.top, text="Загрузить из БД", command=self.load_from_database).pack(pady=10)

    #def find_client(self):


    def init_database(self):
        self.conn = sqlite3.connect('rooms&clients.db')
        self.cursor = self.conn.cursor()

        # Создание таблиц если они не существуют
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms
            (room TEXT PRIMARY KEY, info TEXT, price REAL)
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients
            (name TEXT PRIMARY KEY, room_number TEXT,
            FOREIGN KEY(room_number) REFERENCES rooms(number))
        ''')

        self.conn.commit()

    def save_to_database(self):
        try:
            self.init_database()
            # Очистка существующих данных
            self.cursor.execute("DELETE FROM clients")
            self.cursor.execute("DELETE FROM rooms")

            # Сохранение тарифов
            for room in self.rooms:
                self.cursor.execute("INSERT INTO rooms (room, info, price) VALUES (?, ?, ?)",
                                    (room.number, room.info, room.price))

            # Сохранение клиентов
            for client in self.clients:
                self.cursor.execute("""
                    INSERT INTO clients (name, room_number)
                    VALUES (?, ?)""",
                                    (client.name, client.room.number))

            self.conn.commit()
            self.conn.close()
            messagebox.showinfo("Успех", "Данные успешно сохранены в базу данных")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении в базу данных: {str(e)}")

    def load_from_database(self):
        try:
            self.init_database()
            self.rooms.clear()
            self.clients.clear()

            # Загрузка тарифов
            self.cursor.execute("SELECT * FROM rooms")
            for row in self.cursor.fetchall():
                room = Room(row[0], row[1], row[2])
                self.rooms.append(room)
                self.hotel.room_listbox.insert(tk.END, f"Комната № {room.number}; информация о комнате: {room.info}; стоимость проживания: {room.price} руб.")

            # Обновление выпадающего списка тарифов
            self.hotel.update_room_dropdown()

            # Загрузка клиентов
            self.cursor.execute("SELECT * FROM clients")
            for row in self.cursor.fetchall():
                room = next((r for r in self.rooms if r.number == row[1]), None)
                if room:
                    client = Client(row[0], room)
                    self.clients.append(client)
                    self.hotel.client_listbox.insert(tk.END,
                                               f"Клиент {client.name} занял комнату № {room.number} по стоимости {room.price} руб")

            self.hotel.client_listbox.delete(0, tk.END)
            for client in self.clients:
                self.hotel.client_listbox.insert(
                    tk.END,
                    f"Клиент {client.name} занял комнату № {room.number} по стоимости {room.price} руб")

            self.conn.close()
            messagebox.showinfo("Успех", "Данные успешно загружены из базы данных")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке из базы данных: {str(e)}")

    def find_client(self):
        def perform_search():
            search_name = self.search_entry.get().strip()
            found_clients = [client for client in self.clients if search_name.lower() in client.name.lower()]

            result_text = ""
            if found_clients:
                for client in found_clients:
                    result_text += f"Клиент {client.name} проживает в комнате № {client.room.number}\n"
            else:
                result_text = "Клиент не найден"

            messagebox.showinfo("Результаты поиска", result_text)

        search_window = tk.Toplevel(self.top)
        search_window.title("Поиск клиента")
        search_window.geometry("300x200")

        tk.Label(search_window, text="Введите фамилию клиента:").pack(pady=10)
        self.search_entry = tk.Entry(search_window)
        self.search_entry.pack(pady=5)

        tk.Button(search_window, text="Найти", command=perform_search).pack(pady=10)


class Hotel:
    def __init__(self, root):
        self.root = root
        self.root.title("Информационная база Azur$Beach")
        self.root.geometry("1200x475")
        self.rooms = []
        self.clients = []

        # Создание вкладок
        self.tab_control = ttk.Notebook(root)

        # Вкладка тарифов
        self.room_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.room_tab, text='Комнаты')

        # Вкладка клиентов
        self.client_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.client_tab, text='Клиенты')

        self.tab_control.pack(expand=1, fill='both')

        self.setup_room_tab()
        self.setup_client_tab()

    def setup_room_tab(self):
        # Поля для создания комнат
        tk.Label(self.room_tab, text="Номер комнаты:").grid(row=0, column=0, padx=5, pady=5)
        self.room_number = tk.Entry(self.room_tab)
        self.room_number.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.room_tab, text="Информация:").grid(row=1, column=0, padx=5, pady=5)
        self.room_info = tk.Entry(self.room_tab)
        self.room_info.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.room_tab, text="Стоимость:").grid(row=2, column=0, padx=5, pady=5)
        self.room_price = tk.Entry(self.room_tab)
        self.room_price.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self.room_tab, text="Добавить комнату",
                  command=self.create_room).grid(row=3, column=0, columnspan=2, pady=10)

        # Список тарифов
        self.room_listbox = tk.Listbox(self.room_tab, width=100, height=10)
        self.room_listbox.grid(row=0, column=2, rowspan=5, columnspan=2, padx=5, pady=5)

        sort_frame = tk.Frame(self.room_tab)
        sort_frame.grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(sort_frame, text="Сортировать по цене", command=self.sort_rooms_by_price).pack(side=tk.LEFT, padx=5)

        try:
            image = Image.open("Без имени.jpg")
            image = image.resize((1200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label = tk.Label(self.room_tab, image=photo)
            image_label.image = photo
            image_label.grid(row=5, column=0, columnspan=3, pady=10)
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {e}")

    def setup_client_tab(self):
        # Поля для создания клиента
        tk.Label(self.client_tab, text="Фамилия клиента:").grid(row=0, column=0, padx=5, pady=5)
        self.client_name = tk.Entry(self.client_tab)
        self.client_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.client_tab, text="Номер для заселения:").grid(row=1, column=0, padx=5, pady=5)
        self.room_var = tk.StringVar()
        self.room_dropdown = ttk.Combobox(self.client_tab, textvariable=self.room_var)
        self.room_dropdown.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.client_tab, text="Добавить клиента",
                  command=self.create_client).grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(self.client_tab, text="Открыть базу данных",
                  command=self.find_client).grid(row=4, column=0, columnspan=2, pady=10)

        # Список клиентов
        self.client_listbox = tk.Listbox(self.client_tab, width=100, height=10)
        self.client_listbox.grid(row=0, column=2, rowspan=5, columnspan=2, padx=5, pady=5)

        sort_frame = tk.Frame(self.client_tab)
        sort_frame.grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(sort_frame, text="Сортировать по фамилии", command=self.sort_clients_by_name).pack(side=tk.LEFT, padx=5)

        try:
            image = Image.open("Без имени.jpg")
            image = image.resize((1200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label = tk.Label(self.client_tab, image=photo)
            image_label.image = photo
            image_label.grid(row=5, column=0, columnspan=4, pady=10)
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {e}")

    def create_room(self):
        try:
            number = self.room_number.get()
            info = self.room_info.get()
            price = float(self.room_price.get())

            if number and info and price > 0:
                room = Room(number, info, price)
                self.rooms.append(room)

                self.room_listbox.insert(tk.END, f"Комната № {number}; информация о комнате: {info}; стоимость проживания: {price} руб.")
                self.update_room_dropdown()
                self.room_number.delete(0, tk.END)
                self.room_info.delete(0, tk.END)
                self.room_price.delete(0, tk.END)
            else:
                    messagebox.showerror("Ошибка", "Некорректно введенные данные.")

        except ValueError:
            messagebox.showerror("Ошибка", "Номер комнаты/цена должна быть числом.")

    def create_client(self):
        name = self.client_name.get()
        selected_room = self.room_var.get()

        if name and selected_room:
            room = next((r for r in self.rooms if r.number == selected_room), None)
            if room:
                client = Client(name, room)
                self.clients.append(client)
                self.client_listbox.insert(tk.END,
                                               f"Клиент {name} занял комнату № {room.number} по стоимости {room.price} руб.")
                self.client_name.delete(0, tk.END)
            else:
                messagebox.showerror("Ошибка", "Не выбран номер для заселения.")
        else:
            messagebox.showerror("Ошибка", "Некорректно введенные данные.")

    def update_room_dropdown(self):
        room_numbers = [room.number for room in self.rooms]
        self.room_dropdown['values'] = room_numbers

    def find_client(self):
        DB(self.root, self.rooms, self.clients, self)

    def sort_rooms_by_price(self):
        self.rooms.sort(key=lambda x: x.price, reverse=False)
        self.update_room_listbox()

    def sort_clients_by_name(self):
        self.clients.sort(key=lambda x: x.name)
        self.update_client_listbox()

    def update_room_listbox(self):
        self.room_listbox.delete(0, tk.END)
        for room in self.rooms:
            self.room_listbox.insert(tk.END, f"Комната № {room.number}; информация о комнате: {room.info}; стоимость проживания: {room.price} руб.")

    def update_client_listbox(self):
        self.client_listbox.delete(0, tk.END)
        for client in self.clients:
            self.client_listbox.insert(tk.END, f"Клиент {client.name} занял комнату № {client.room.number} по стоимости {client.room.price} руб.")

if __name__ == "__main__":
    root = tk.Tk()
    app = Hotel(root)
    root.mainloop()