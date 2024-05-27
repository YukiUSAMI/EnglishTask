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

    def run(self):
        while True:
            print("1: ファイルをアップロード")
            print("2: ファイルを表示")
            print("3: ファイル名を更新")
            print("4: ファイルを削除")
            print("0: 終了")
            choice = input("選択してください: ")
            if choice == '1':
                self.upload_file()
            elif choice == '2':
                files = self.get_files()
                for file in files:
                    print(file)
            elif choice == '3':
                file_id = int(input("更新するファイルのIDを入力してください: "))
                updated_name = input("新しいファイル名を入力してください: ")
                self.update_file(file_id, updated_name)
            elif choice == '4':
                file_id = int(input("削除するファイルのIDを入力してください: "))
                self.delete_file(file_id)
            elif choice == '0':
                self.close()
                break
            else:
                print("無効な選択です。もう一度お試しください。")

# テスト

db = SimpleDatabase('files.db')
db.run()
