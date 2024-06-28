import time

import config.values as const
import Use_NFC as nfc

rd = nfc.CardReader()

id_tmp = []  # 直近でタッチされたNFCカードのIDを一時保存するリスト"


def check_nfc_was_touched(dismiss_time=30):
    """
    NFCカードがタッチされたかどうかを確認する。指定された秒数内で，同一IDのカードが連続で読み込まれた場合，タッチされたとみなさない。
    
    Args:
        dismiss_time (int): 同一IDのカードが連続で読み込まれた場合，指定された秒数だけ無視する。
    
    Returns: 
        ret (int): タッチされた場合はカードのID，タッチされていない場合は-1 を返す。
    """
    global id_tmp
    if const.nfc_data["touched_flag"]:  # NFCカードがタッチされた
        const.nfc_data["touched_flag"] = False  # NFCカードがタッチされたのを確認したのでフラグをFalseにする
        id_i = find_id_in_tmp(const.nfc_data["id"]) # 過去にタッチされたIDのリストを検索
        if (
            id_i == -1 or time.time() - id_tmp[id_i]["time"] > dismiss_time
        ):  # NFCカードがタッチされたかどうかを確認
            if id_i != -1:
                id_tmp[id_i]["time"] = time.time() # タッチされたIDに時刻を更新
            else:
                id_tmp.append({"id" : const.nfc_data["id"], "time" : time.time()})  # 新規追加

            return const.nfc_data["id"]
    return -1  # NFCカードがタッチされていない場合


def nfc_update_sub_thread():  # NFCの更新 別スレッドで実行される
    while True:
        if not const.nfc_data["touched_flag"]:
            const.nfc_data["id"] = rd.wait_for_card_touched()  # NFCカードの読み取りを待機
            const.nfc_data["touched_flag"] = True
            
def find_id_in_tmp(id):
    """
    id_tmp内に指定のidがあればそのidがあるリストの要素番号を返し，もしなければ-1を戻り値とする関数
    
    Args:
        id (str): 検索するID
    
    Returns:
        index (int): idが見つかった場合はその要素番号，見つからなかった場合は-1
    """
    for i, d in enumerate(id_tmp):
        if d['id'] == id:
            return i
    return -1



def disconnect_reader():  # NFCリーダーの切断
    rd.disconnect_reader()


def connect_reader():  # NFCリーダーの接続
    return rd.connect_reader()
