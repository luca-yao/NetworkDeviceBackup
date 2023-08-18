import os, logging, yaml, config
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, AuthenticationException
from datetime import datetime, timedelta

def setup_logging():
    logging.basicConfig(
       filename=config.Config.log_path, 
       level=logging.INFO, 
       format='%(asctime)s:%(levelname)s:%(message)s', 
       filemode='w'
    )

def save_backup_log(hostname, backup_output):
    message = f'{hostname}: Configuration backup saved successfully.' if 'end' in backup_output else f'{hostname}: Failed to save configuration backup.'
    logging.info(message)

    timestamp = datetime.now().strftime('%Y-%m-%d')
    backup_filename = f'{config.Config.backup_directory}{hostname}_backup_{timestamp}.cfg'

    with open(backup_filename, 'w') as backup_file:
         backup_file.write(backup_output)
    logging.info(f"End save running-config for {hostname}...")
  
def backup_cisco_device(net_connect, hostname, secret):
    net_connect.send_command('enable', expect_string=r'Password:')
    enable_password = secret
    net_connect.send_command_timing(enable_password)

    logging.info(f"Start save running-config for {hostname}...")
    backup_output = net_connect.send_command_expect('show running-config')
    save_backup_log(hostname, backup_output)
    net_connect.disconnect()

def is_ssh_supported(device_info):
    try:
       net_connect = ConnectHandler(
            device_type = device_info["device_type"],
            host = device_info["host"],
            username = config.LoginAccount.username,
            password = config.LoginAccount.password
       )
       net_connect.disconnect()
       return True
    except (NetMikoTimeoutException, AuthenticationException):
        return False

def delete_old_backups(backup_directory, days_to_keep):
    current_date = datetime.now().date()
    delete_threshold = current_date - timedelta(days=days_to_keep)
    backup_files = os.listdir(backup_directory)

    for file in backup_files:
        filename_parts = file.split('_')
        date_part = filename_parts[-1].split('.')[0]

        try:
            backup_date = datetime.strptime(date_part, '%Y-%m-%d').date()
            if backup_date == delete_threshold:
               file_path = os.path.join(backup_directory, file)
               os.remove(file_path)
               logging.info(f"Deleted old backup file: {file}")
        except ValueError:
            pass

def load_device_info(file_path):
    with open(file_path, 'r') as file:
         device_info = yaml.safe_load(file)
    return device_info

def main():
    devices = []
    setup_logging()

    device_info_list = load_device_info(config.Config.file_path)
    for device_info in device_info_list:
        hostname = device_info["hostname"]
        device_type = device_info["device_type"]
        host = device_info["host"]
        secret = device_info["secret"]
        devices.append((device_info, hostname))

    for device_info, hostname in devices:
        if device_info["device_type"] == 'cisco_ios':
            if is_ssh_supported(device_info):
                net_connect = ConnectHandler(
                   device_type = device_info["device_type"],
                   host = device_info["host"],
                   username = config.LoginAccount.username,
                   password = config.LoginAccount.password
                )
                backup_cisco_device(net_connect, hostname, device_info["secret"])
            else:
                print(f"{hostname}: SSH is not supported. Using Telnet...")
                telnet_device = {
                    'device_type': 'cisco_ios_telnet',
                    'host': device_info["host"],
                    'port': 23,
                    'password': device_info["secret"]
                }
                net_connect_telnet = ConnectHandler(**telnet_device)
                backup_cisco_device(net_connect_telnet, hostname, device_info["secret"])
 
        elif device_info["device_type"] == 'fortinet':
            net_connect = ConnectHandler(
                   device_type = device_info["device_type"],
                   host = device_info["host"],
                   username = config.LoginAccount.username,
                   password = config.LoginAccount.password

            )
            logging.info(f"Start save running-config for {hostname}...")
            backup_output = net_connect.send_command('show full-configuration')
            save_backup_log(hostname, backup_output)
            net_connect.disconnect()

    # Delete old backup files
    delete_old_backups(config.Config.backup_directory, config.Config.days_to_keep_backup)

if __name__ == '__main__':
    main()
