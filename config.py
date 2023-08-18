class Config:
      backup_directory = '/home/backup/'               #備份檔案存放位置
      file_path = '/root/shell.files/devlist.yaml'     #設備清單位置
      log_path = '/var/log/NetworkDeviceBackup.log'    #日誌存放位置
      days_to_keep_backup = 10                         #保留天數

class LoginAccount:
      username = 'username'                            #登入設備帳號
      password = 'password'                            #登入設備密碼