"""
アテンダンのアップデーターです。Gitにアクセスし，最新リリースバージョンを確認し，既存のバージョンより新しいリリースがあれば，アップデートします。
また，アップデートに必要な機能の関数を提供します。

@Author: Yuta Tanimura
"""
import requests
import pprint
import zipfile
import shutil
import os
import tempfile
import PySimpleGUI as sg
import json

# GitHub APIのURL
api_url = "https://api.github.com/repos/Cirno030409/AttenDan_release/releases"

def main():
    ret = is_exist_update()
    if ret == -1:
        return -1
    if ret:
        latest_ver, release_title, release_body, release_url = get_latest_release_info()
        latest_ver_str = str(latest_ver)
        latest_ver_str ="v" + latest_ver_str[0] + '.' + latest_ver_str[1] + '.' + latest_ver_str[2]
        if sg.PopupYesNo(f'新しいバージョン {latest_ver_str} が見つかりました。アップデートの内容は以下の通りです。\n\n\nアップデート名: {release_title}\n\nアップデート内容: {release_body}\n\n\nアップデートしますか？', title='アテンダン アップデーター', keep_on_top=True) == 'Yes':
            sg.popup_quick_message('アップデートしています...\nこの作業にはしばらくかかることがあります', title='アテンダン アップデーター', auto_close_duration=3)
            print("updating...")
            release_dir_path = download_latest_release()
            replace_with_latest_release(release_dir_path)
            sg.PopupOK(f'アップデートが完了しました。アプリケーションを再起動してください。', title='アテンダン アップデーター', keep_on_top=True)
            return


def get_latest_release_info():
    """
    Gitにアクセスして，アテンダンの最新バージョンを確認します。

    Returns:
        tuple(int, str, str): 最新バージョン，最新リリースのタイトル，最新リリースの本文，リリース本体のURL(ZIP)のタプル
    """
    response = requests.get(api_url)
    
    try:
        response.raise_for_status()  # ステータスコードが200以外の場合に例外を発生させる
    except requests.exceptions.HTTPError as e:
        sg.Popup(f'アップデートの確認に失敗しました。インターネット接続を確認してください。\n' + str(e), title='アテンダン アップデーター', keep_on_top=True)
        return e

    release = response.json() # レスポンスからJSONデータを取得

    
    max_ver = 0
    for i, data in enumerate(release):
        ver = data["tag_name"]
        ver = ver.replace('v', '')
        ver = int(ver.replace('.', '', 2))
        if max_ver < ver: # 最新バージョンを比較
            max_ver = ver
            release_title = data["name"]
            release_url = data["zipball_url"]
            release_body = data["body"]
            
    print(max_ver, release_title, release_url, release_body)

    return max_ver, release_title, release_body, release_url

def is_exist_update():
    """
    アップデートがあるかどうかを確認します。

    Returns:
        bool: アップデートがあるかどうか
    """
    values = json.load(open('saves/values.json', 'rb'))
    current_ver = int(values['system_version'].replace('.', '', 2)) 
    latest_release_info = get_latest_release_info()
    if isinstance(latest_release_info, Exception):
        return -1
    
    latest_ver = latest_release_info[0]
    if current_ver < latest_ver:
        return True
    else:
        return False

def download_latest_release():
    """
    最新リリースのZIPファイルをダウンロードします。

    Returns:
        str: ダウンロードした最新リリースのパス
    """
    print("downloading latest release...")
    _, _, _, release_url = get_latest_release_info()
    response = requests.get(release_url)
    
    try:
        response.raise_for_status()  # ステータスコードが200以外の場合に例外を発生させる
    except requests.exceptions.HTTPError as e:
        return e
    
    with open("AttenDan_release.zip", "wb") as f:
        f.write(response.content)
    
    print("extracting latest release...")
    # ZIPファイルを解凍する
    with zipfile.ZipFile("AttenDan_release.zip", 'r') as zip_ref:
        try:
            zip_ref.extractall("AttenDan_release")
        except Exception as e:
            return e
        
    print("downloaded latest release.")
    
    return "AttenDan_release"

def replace_with_latest_release(release_dir_path = "AttenDan_release"):
    """
    最新リリースのZIPファイルをダウンロードし，既存のファイルを置き換えます。

    Args:
        release_path (str): 既存のファイルのパス
    Returns:
        
    """
    path = get_release_file_path(release_dir_path)
    print("copying old files...")
    # ファイルをコピーする
    if not os.path.exists('old_files'):
        os.makedirs('old_files')
    shutil.rmtree('old_files')
    shutil.copytree('.', 'old_files')
    
    #! 既存ファイルの削除
    for item in os.listdir('.'):
        if (item != 'old_files' and 
            item != 'updator' and 
            item != 'updator.exe' and 
            item != 'AttenDan_release' and 
            item != 'saves'): # 一部のファイルを除いて既存のファイルを削除する
            try:
                if os.path.isfile(item):
                    os.remove(item)
                elif os.path.isdir(item):
                    shutil.rmtree(item)
            except Exception as e:
                print(f"Error removing {item}: {e}")
                    
    print("copying new files...")
    
    #! 新規ファイルのコピー
    for item in os.listdir(path):
        if (item != 'saves'): # セーブフォルダは除く
            try:
                if os.path.isfile(os.path.join(path, item)):
                    shutil.copy(os.path.join(path, item), '.')
                elif os.path.isdir(os.path.join(path, item)):
                    shutil.copytree(os.path.join(path, item), item)
            except Exception as e:
                print(f"Error copying {item}: {e}")
                return e
    print("copied new files.")
    
def get_release_file_path(path = "AttenDan_release"):
    root_dir = "AttenDan_release"
    directories = [name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
    root_dir = os.path.join(root_dir, directories[0])
    directories = [name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
    root_dir = os.path.join(root_dir, directories[0])
    directories = [name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
    
    return root_dir

def copy_and_overwrite_directory(src_dir, dst_dir):
    with tempfile.TemporaryDirectory() as tmp_dir:
        shutil.copytree(src_dir, tmp_dir)
        shutil.rmtree(dst_dir)
        shutil.copytree(tmp_dir, dst_dir)
    

if __name__ == "__main__":
    main()
