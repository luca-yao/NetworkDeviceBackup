# NetworkDeviceBackup
Back up network devices with Netmiko

# 前言
雖然我以前有透過Bash完成自動化備份Fortinet和Cisco設備的腳本，但我覺得那個太笨而且太醜了~~未來有機會再來自爆一下~~

再來是Cisco本身雖然有kron這內建的排成可以使用，但檔名實在太不人性化，看了我頭疼，而Fortinet要手動點，實在很笨

總結一個字 
# 懶 d(`･∀･)b

於是乎這個小垃圾就誕生了，原本是用Paramiko但寫到一半發現有更好用的模組netmiko於是又打掉重做，變成現在的樣子

我把一切需要使用者設定或者可能會需要設定的地方都做了模組化處理，所以**照理說**只要調整需要的部分照理說就可以正常運作了....吧?

本程式主要分成三大設定檔
- backup.py
- config.py
- devlist.yaml
  
運行作業系統：Centos 7

Python版本：Python3.11

以下開始一一為各位講解

## devlist.yaml
採用YAML檔編寫，所以應該會更方便各讀者參考使用
```yaml
- hostname: HQ_Switch1      #自行定義名稱，將會用於備份後產出的檔名
  device_type: cisco_ios    #Netmiko函數，不動
  host: 192.168.31.253      #設備IP
  secret: enable_password   #enable_password

- hostname: HQ_Core_Switch
  device_type: cisco_ios
  host: 192.168.31.1
  secret: enable_password

- hostname: HQ_FW           #自行定義
  device_type: fortinet     #Netmiko函數，不動
  host: 192.168.31.254      #設備IP
  secret: ''                #如果沒有就 ''

.................依此類推
```

## config.py
```python
class Config:
      backup_directory = '/home/backup/'               #備份檔案存放位置
      file_path = '/root/shell.files/devlist.yaml'     #設備清單位置
      log_path = '/var/log/NetworkDeviceBackup.log'    #日誌存放位置
      days_to_keep_backup = 10                         #保留天數

class LoginAccount:
      username = 'username'                            #登入設備帳號
      password = 'password'                            #登入設備密碼
```
## 成品如下圖：
![Imgur](https://i.imgur.com/2jkPCO1.png)
![Imgur](https://i.imgur.com/MvRzt17.png)

# 後記
我個人的習慣是會把備份用的帳號跟平常使用的帳號分開使用，這樣權限比較好管理，所以才會只需要一組帳密就可以進行後續備份處理了。

我的Fortinet本身都是有做Vdom處理的，所以應該是可以直接使用，不過我的環境沒有global配置的，所以我不確定能不能直接使用。

關於Cisco有些人可能設備不支援SSH，關於這部分我有處理好，如果確認到沒有SSH會自動進行TELNET的連線並備份，這點是測試過的 安啦 σ`∀´)σ
