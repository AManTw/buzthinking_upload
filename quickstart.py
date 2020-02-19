from __future__ import print_function
import os
import io
import re
import time
from os import listdir
from os.path import isfile, isdir, join
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools

# 權限必須
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']



def name_restting(rename):
    cut = " - PressPlay 訂閱學習，時刻精進"
    name = re.sub(cut,'',rename)
    name = re.sub("｜",'|',name)
    name = re.sub("【",'[',name)
    name = re.sub("】",']',name)
    name = re.sub("\.", " ", name)
    name = name.split(" ")
    for i in range(len(name)):
        if i == 0 :
            rename=name[i]
            rename+='.'
        elif i == len(name)-1:
            rename+='.'
            rename+=name[i]
        else :
            rename+=name[i]

    #print (rename)
    return rename

def delete_drive_service_file(service, file_id):
    service.files().delete(fileId=file_id).execute()


def update_file(service, update_drive_service_name, local_file_path, update_drive_service_folder_id):
    """
    將本地端的檔案傳到雲端上
    :param update_drive_service_folder_id: 判斷是否有 Folder id 沒有的話，會上到雲端的目錄
    :param service: 認證用
    :param update_drive_service_name: 存到 雲端上的名稱
    :param local_file_path: 本地端的位置
    :param local_file_name: 本地端的檔案名稱
    """
    #print("正在上傳檔案...")
    file_metadata = {'name': update_drive_service_name,'parents': update_drive_service_folder_id}

    media = MediaFileUpload(local_file_path, )
    file_metadata_size = media.size()
    start = time.time()
    file_id = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    end = time.time()
    #print("上傳檔案成功！")
    print('已上傳: ' + str(file_metadata['name']))
    #print('雲端檔案ID為: ' + str(file_id['id']))
    #print('檔案大小為: ' + str(file_metadata_size) + ' byte')
    #print("上傳時間為: " + str(end-start))

    return file_metadata['name'], file_id['id']

def search_folder(service, update_drive_folder_name=None):
    """
    如果雲端資料夾名稱相同，則只會選擇一個資料夾上傳，請勿取名相同名稱
    :param service: 認證用
    :param update_drive_folder_name: 取得指定資料夾的id，沒有的話回傳None，給錯也會回傳None
    :return:
    """
    get_folder_id_list = []
    if update_drive_folder_name is not None:
        response = service.files().list(fields="nextPageToken, files(id, name)", spaces='drive',
                                       q = "name = '" + update_drive_folder_name + "' and mimeType = 'application/vnd.google-apps.folder' and trashed = false").execute()
        for file in response.get('files', []):
            # Process change
            #print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            get_folder_id_list.append(file.get('id'))
        if len(get_folder_id_list) == 0:
            print("你給的資料夾名稱沒有在你的雲端上！，因此檔案會上傳至雲端根目錄")
            return None
        else:
            return get_folder_id_list
    return None

def search_file(service, update_drive_service_name, is_delete_search_file=False):
    """
    本地端
    取得到雲端名稱，可透過下載時，取得file id 下載

    :param service: 認證用
    :param update_drive_service_name: 要上傳到雲端的名稱
    :param is_delete_search_file: 判斷是否需要刪除這個檔案名稱
    :return:
    """
    # Call the Drive v3 API
    results = service.files().list(fields="nextPageToken, files(id, name)", spaces='drive',
                                   q="name = '" + update_drive_service_name + "' and trashed = false",
                                   ).execute()
    items = results.get('files', [])
    if not items:
        #print('沒有發現你要找尋的 ' + update_drive_service_name)
        return 1
    else:
        print('...')
        return 0
'''    
    else:
        print('搜尋的檔案: ')
        for item in items:
            times = 1
            print(u'{0} ({1})'.format(item['name'], item['id']))
            if is_delete_search_file is True:
                print("刪除檔案為:" + u'{0} ({1})'.format(item['name'], item['id']))
                delete_drive_service_file(service, file_id=item['id'])

            if times == len(items):
                return item['id']
            else:
                times += 1
'''

def trashed_file(service, is_delete_trashed_file=False):
    """

    抓取到雲端上垃圾桶內的全部檔案，進行刪除

    :param service: 認證用
    :param is_delete_trashed_file: 是否要刪除垃圾桶資料
    :return:
    """
    results = service.files().list(fields="nextPageToken, files(id, name)", spaces='drive', q="trashed = true",
                                   ).execute()
    items = results.get('files', [])
    if not items:
        print('垃圾桶無任何資料.')
    else:
        print('垃圾桶檔案: ')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
            if is_delete_trashed_file is True:
                print("刪除檔案為:" + u'{0} ({1})'.format(item['name'], item['id']))
                delete_drive_service_file(service, file_id=item['id'])


def main():
    """
    :param is_update_file_function: 判斷是否執行上傳的功能
    :param update_drive_service_name: 要上傳到雲端上的檔案名稱
    :param update_file_path: 要上傳檔案的位置以及名稱
    """

    mypath="/home/jerrychen/Downloads/FireShot"
    files = listdir(mypath)
    folder="bussin_thinking"
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("/home/jerrychen/Downloads/FireShot/credentials.json", SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    print('*' * 10)
    get_folder_id = search_folder(service = service, update_drive_folder_name = folder)
    print("=====執行上傳檔案=====")

    for filePDF in files:
        # 產生檔案的絕對路徑
        fullpath = join(mypath, filePDF)
        # fullpath 是檔案
        if isfile(fullpath):
            name=name_restting(filePDF)
            new_fullpath = join(mypath,name)
            os.rename(fullpath, new_fullpath)
            # 清空 雲端垃圾桶檔案
            # trashed_file(service=service, is_delete_trashed_file=True)
            # 搜尋要上傳的檔案名稱是否有在雲端上並且刪除
            res=search_file(service=service, update_drive_service_name=name,is_delete_search_file=True)
            # 檔案上傳到雲端上
            if res == 1 :
                update_file(service, update_drive_service_name=name, local_file_path=new_fullpath, update_drive_service_folder_id=get_folder_id)
    print("=====上傳檔案完成=====")

if __name__ == '__main__':

    main()



