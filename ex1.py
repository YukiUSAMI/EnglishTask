"""
We did the basic baseline and error handling ourselves. The code modifications were done by chatGPT.
Implementation of word token, lemma, POS, n-gram or regex was done by chatGPT.
GPT corrected the comments on arguments, etc.
All error handling: s1300215
level1-1 s1300237 and s1300215
level1-2 s1300215 and s1300237
The first one written first has the larger contribution.

Some of the “run()” functions were written by chatGPT.
(We plan to have chatGPT write the functions from level2 onward.)



Translated with DeepL.com (free version)
"""

import os
import re
import sqlite3
from datetime import datetime
import nltk
from nltk.stem import WordNetLemmatizer
import chardet

# nltkの初期化
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

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
            #LLM
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS files
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, original_name TEXT, updated_name TEXT, content TEXT)''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS search_results
                                (id INTEGER PRIMARY KEY AUTOINCREMENT, original_name TEXT, updated_name TEXT, context TEXT, search_term TEXT, search_time TEXT)''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"テーブル作成エラー: {e}")

    def insert_file(self, original_name, updated_name, content):
        try:
            self.cursor.execute('INSERT INTO files (original_name, updated_name, content) VALUES (?, ?, ?)', (original_name, updated_name, content))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"データ挿入エラー: {e}")

    def insert_search_result(self, original_name, updated_name, context, search_term):
        try:
            search_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute('INSERT INTO search_results (original_name, updated_name, context, search_term, search_time) VALUES (?, ?, ?, ?, ?)', (original_name, updated_name, context, search_term, search_time))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"検索結果挿入エラー: {e}")

    def get_files(self):
        try:
            self.cursor.execute('SELECT * FROM files')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"データ取得エラー: {e}")
            return []

    def get_search_results(self):
        try:
            self.cursor.execute('SELECT * FROM search_results')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"検索結果取得エラー: {e}")
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

    def select_files(self):
        filenames = input("ファイル名をカンマで区切って入力してください: ").split(',')
        filenames = [filename.strip() for filename in filenames]
        if not filenames:
            print("ファイルが選択されていません。")
            return []
        elif len(filenames) == 1:
            return [filenames[0]]
        else:
            return filenames

    def upload_file(self):
        filenames = self.select_files()
        if not filenames:
            return
        for filename in filenames:
            if not os.path.isfile(filename):
                print(f"ファイルが見つかりません ({filename})。")
                continue
            original_name = os.path.basename(filename)
            print("新しいファイル名の形式を選択してください:")
            print("1. Q#")
            print("2. K#")
            print("3. R#")
            name_choice = input("選択してください (1-3): ")
            if name_choice == '1':
                prefix = 'Q'
            elif name_choice == '2':
                prefix = 'K'
            elif name_choice == '3':
                prefix = 'R'
            else:
                print("無効な選択です。デフォルトで元の名前を使用します。")
                prefix = ""

            updated_name = input(f"新しいファイル名を入力してください ({prefix}): ")
            if not updated_name:
                updated_name = original_name
            else:
                updated_name = f"{prefix}{updated_name}"
            
            try:
                with open(filename, 'rb') as file:
                    raw_data = file.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']
                    if encoding is None:
                        encoding = 'utf-8'  # デフォルトのエンコーディングを設定

                with open(filename, 'r', encoding=encoding) as file:
                    content = file.read()
                self.insert_file(original_name, updated_name, content)
            except FileNotFoundError:
                print(f"ファイルが見つかりません ({filename})。")
            except IOError as e:
                print(f"ファイル読み取りエラー ({filename}): {e}")
            except UnicodeDecodeError as e:
                print(f"エンコーディングエラー ({filename}): {e}")

    def select_search_type(self):
        print("検索タイプを選択してください:")
        print("1. 単語トークン")
        print("2. レンマ")
        print("3. 品詞")
        print("4. n-gram")
        print("5. 正規表現")
        choice = input("検索タイプを入力してください (1-5): ")
        if choice == '1':
            return 'word_token'
        elif choice == '2':
            return 'lemma'
        elif choice == '3':
            return 'pos'
        elif choice == '4':
            return 'n-gram'
        elif choice == '5':
            return 'regex'
        else:
            print("無効な検索タイプです。デフォルトで単語トークン検索を実行します。")
            return 'word_token'

    def search_files(self, term):
        search_type = self.select_search_type()
        files = self.get_files()
        results = []
        for file in files:
            content = file[3]
            if search_type == 'word_token':
                tokens = content.split()
                for i, word in enumerate(tokens):
                    if term == word:
                        start = max(0, i - 5)
                        end = min(len(tokens), i + 6)
                        context = ' '.join(tokens[start:end]).replace(term, f'<mark>{term}</mark>')
                        results.append((file[1], file[2], context))
            elif search_type == 'lemma':
                lemmatizer = WordNetLemmatizer()
                words = nltk.word_tokenize(content)
                lemmas = [lemmatizer.lemmatize(word) for word in words]
                for i, lemma in enumerate(lemmas):
                    if term == lemma:
                        start = max(0, i - 5)
                        end = min(len(lemmas), i + 6)
                        context = ' '.join(lemmas[start:end]).replace(term, f'<mark>{term}</mark>')
                        results.append((file[1], file[2], context))
            elif search_type == 'pos':
                tokens = nltk.word_tokenize(content)
                pos_tags = nltk.pos_tag(tokens)
                pos_terms = [tag[1] for tag in pos_tags]
                for i, pos in enumerate(pos_terms):
                    if term == pos:
                        start = max(0, i - 5)
                        end = min(len(pos_tags), i + 6)
                        context = ' '.join([tag[0] for tag in pos_tags[start:end]]).replace(term, f'<mark>{term}</mark>')
                        results.append((file[1], file[2], context))
            elif search_type == 'n-gram':
                n = int(input("n-gramのサイズを入力してください: "))
                tokens = nltk.word_tokenize(content)
                ngrams = list(nltk.ngrams(tokens, n))
                ngram_terms = [' '.join(gram) for gram in ngrams]
                for i, ngram in enumerate(ngram_terms):
                    if term == ngram:
                        start = max(0, i - 5)
                        end = min(len(ngrams), i + 6)
                        context = ' '.join([' '.join(gram) for gram in ngrams[start:end]]).replace(term, f'<mark>{term}</mark>')
                        results.append((file[1], file[2], context))
            elif search_type == 'regex':
                pattern = re.compile(term)
                for match in pattern.finditer(content):
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end].replace(term, f'<mark>{term}</mark>')
                    results.append((file[1], file[2], context))
        # 検索結果を保存するかどうかを尋ねる
        save_results = input("検索結果を保存しますか? (y/n): ")
        if save_results.lower() == 'y':
            for result in results:
                self.insert_search_result(result[0], result[1], result[2], term)
            print(f"検索結果がデータベースに保存されました。")
        return results

    def run(self):
        while True:
            print("1: ファイルをアップロード")
            print("2: ファイルを表示")
            print("3: ファイル名を更新")
            print("4: ファイルを削除")
            print("5: ファイルを検索")
            print("6: 検索結果を表示")
            print("0: 終了")
            choice = input("選択してください: ")
            if choice == '1':
                self.upload_file()
            elif choice == '2':
                files = self.get_files()
                if files:
                    for i, file in enumerate(files, 1):
                        print(f"{i}: Original Name: {file[1]}, Updated Name: {file[2]}")
                    file_choice = int(input("表示するファイルの番号を選択してください: ")) - 1
                    if 0 <= file_choice < len(files):
                        print(files[file_choice][3])
                    else:
                        print("無効な番号です。")
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
            elif choice == '5':
                term = input("検索する単語を入力してください: ")
                results = self.search_files(term)
                if results:
                    for result in results:
                        print(f"Original Name: {result[0]}, Updated Name: {result[1]}, Context: {result[2]}")
                else:
                    print("検索結果が見つかりません。")
            elif choice == '6':
                search_results = self.get_search_results()
                if search_results:
                    for result in search_results:
                        print(f"Original Name: {result[1]}, Updated Name: {result[2]}, Context: {result[3]}, Search Term: {result[4]}, Search Time: {result[5]}")
                else:
                    print("検索結果が見つかりません。")
            elif choice == '0':
                self.close()
                break
            else:
                print("無効な選択です。もう一度お試しください。")

# テスト用の実行コード
if __name__ == "__main__":
    db = SimpleDatabase('files.db')
    db.run()
