import csv


class Database:
    def __init__(self):
        self.__database = [[]]
        self.__keys = []

    def LoadDatabase(self):  # データベースを読み出す
        with open("database.csv", "r", newline="", encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            self.__database = [row for row in reader]  # データベースをリストに格納
        with open("keys.csv", "r", newline="", encoding="utf8") as csvfile:
            self.__keys = csvfile.readline().split(",")  # データベースのキーをリストに格納
        print(">>>> Database loaded.")

    def SaveDatabase(self):
        with open("database.csv", "w", newline="", encoding="utf8") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerows(self.__database)  # データベースをcsvファイルに書き込む
        with open("keys.csv", "w", newline="", encoding="utf8") as csvfile:
            csvfile.write(",".join(self.__keys))  # データベースのキーをcsvファイルに書き込む
        print(">>>> Database saved.")

    def AddRecord(self, data):
        for i in range(len(self.__keys)):
            if len(data) != len(self.__keys) or data[i] == "":  # データが空欄か確認
                print(">>>> Coudn't add Record. Data is something wrong.")
                return -1
        for i in range(len(self.__database)):
            if self.__database[i][0] == data[0]:  # データベースに同じキーがあるか確認
                print(">>>> Coudn't add Record. The key already exists.")
                return -1
        self.__database.append(data)  # データベースにデータを追加
        print(">>>> Record added.", data)

    def DeleteRecord(self, id):
        for i in range(len(self.__database)):
            if self.__database[i][0] == id:
                del self.__database[i]
                print(">>>> Record deleted.")
                return 0
        print(">>>> Coudn't delete Record. The key not found.")
        return -1

    def GetKeys(self):
        return self.__keys  # データベースのキーを取得

    def GetDatabase(self):
        return self.__database
