import os
import sqlite3
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class SimpleDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS files
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, original_name TEXT, updated_name TEXT, content TEXT)''')
        self.conn.commit()

    def insert_file(self, original_name, updated_name, content):
        self.cursor.execute('INSERT INTO files (original_name, updated_name, content) VALUES (?, ?, ?)', (original_name, updated_name, content))
        self.conn.commit()

    def get_files(self):
        self.cursor.execute('SELECT * FROM files')
        return self.cursor.fetchall()

    def update_file(self, file_id, updated_name):
        self.cursor.execute('UPDATE files SET updated_name = ? WHERE id = ?', (updated_name, file_id))
        self.conn.commit()

    def delete_file(self, file_id):
        self.cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def upload_file(self):
        Tk().withdraw()
        filename = askopenfilename() 
        original_name = os.path.basename(filename)
        updated_name = input("新しいファイル名を入力してください: ")
        with open(filename, 'r') as file:
            content = file.read()
        self.insert_file(original_name, updated_name, content)

# テスト
db = SimpleDatabase('files.db')
db.upload_file()
files = db.get_files()
for file in files:
    print(file)
db.update_file(1, 'Q1_updated')
db.delete_file(2)
db.close()

