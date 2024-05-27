import os
import sqlite3
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class SimpleDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.create_table()
        except sqlite3.Error as e:
            print(f"データベース接続エラー: {e}")

    def create_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS files
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, original_name TEXT, updated_name TEXT, content TEXT)''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"テーブル作成エラー: {e}")

    def insert_file(self, original_name, updated_name, content):
        try:
            self.cursor.execute('INSERT INTO files (original_name, updated_name, content) VALUES (?, ?, ?)', (original_name, updated_name, content))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"データ挿入エラー: {e}")

    def get_files(self):
        try:
            self.cursor.execute('SELECT * FROM files')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"データ取得エラー: {e}")
            return []

    def update_file(self, file_id, updated_name):
        try:
            self.cursor.execute('UPDATE files SET updated_name = ? WHERE id = ?', (updated_name, file_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"データ更新エラー: {e}")

    def delete_file(self, file_id):
        try:
            self.cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"データ削除エラー: {e}")

    def close(self):
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(f"データベースクローズエラー: {e}")

    def upload_file(self):
        Tk().withdraw()
        filename = askopenfilename() 
        if not filename:
            print("ファイルが選択されていません。")
            return
        original_name = os.path.basename(filename)
        updated_name = input("新しいファイル名を入力してください: ")
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            self.insert_file(original_name, updated_name, content)
        except FileNotFoundError:
            print("ファイルが見つかりません。")
        except IOError as e:
            print(f"ファイル読み取りエラー: {e}")

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
                if files:
                    for file in files:
                        print(file)
                else:
                    print("ファイルが見つかりません。")
            elif choice == '3':
                try:
                    file_id = int(input("更新するファイルのIDを入力してください: "))
                    updated_name = input("新しいファイル名を入力してください: ")
                    self.update_file(file_id, updated_name)
                except ValueError:
                    print("無効なIDです。整数を入力してください。")
            elif choice == '4':
                try:
                    file_id = int(input("削除するファイルのIDを入力してください: "))
                    self.delete_file(file_id)
                except ValueError:
                    print("無効なIDです。整数を入力してください。")
            elif choice == '0':
                self.close()
                break
            else:
                print("無効な選択です。もう一度お試しください。")

# テスト
db = SimpleDatabase('files.db')
db.run()

