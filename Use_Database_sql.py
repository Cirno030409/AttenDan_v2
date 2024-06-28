import csv
import sqlite3


class Database:
    def __init__(self):
        self.dbname = "saves/RoboDone_AttendanceSystem_Database.db"

    def connect_to_database(self):  # データベースを読み出す
        try:
            self.conn = sqlite3.connect(self.dbname)
        except Exception as e:
            print("[Error] Database connection failed. :", e)
            return -1
        self.cur = self.conn.cursor()
        print("[Database] connected.")

    def execute_database(self, sql, debug=False):
        """接続しているデータベースに対してSQLコマンドを実行する。実行結果がない場合，空のリストを返す。

        Args:
            sql (str): 実行するSQLコマンド
            debug (bool): Trueにすると実行されたSQLコマンドを表示する
            
        Returns:
            list: 実行結果
        """
        if debug:
            print("[Database] Executing command. -->", sql)
        try:
            self.cur.execute(sql)
        except Exception as e:
            print("[Error] SQL command execution failed. :", e)
            return -1
        fetch = self.cur.fetchall()  # 実行結果を取得
        for i in range(len(fetch)):
            fetch[i] = list(fetch[i])  # fetchをリストに変換
        return fetch

    def commit_database(self):
        try:
            self.conn.commit()
        except Exception as e:
            print("[Error] Database commit failed. :", e)
            return -1
        print("[Database] commited.")

    def rollback_database(self):
        try:
            self.conn.rollback()
        except Exception as e:
            print("[Error] Database rollback failed. :", e)
            return -1
        print("[Database] rollbacked.")

    def disconnect_from_database(self):
        try:
            self.cur.close()
        except Exception as e:
            print("[Error] Database close failed. :", e)
            return -1
        self.conn.close()
        print("[Database] disconnected.")
