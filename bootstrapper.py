from netmiko import ConnectHandler

def bootstrapper(dev_type, dev_ip, dev_un, dev_pw, config):
    try:
        config_file = open(config, 'r')
        config_lines = config_file.read().splitlines()
        config_file.close()

        open_connection = ConnectHandler(device_type=dev_type, ip=dev_ip, username=dev_un, password=dev_pw)
        open_connection.enable()

        output = open_connection.send_config_set(config_lines)
        print(output)
        open_connection.send_command_expect('write memory')
        open_connection.disconnect()

        return True
    except:
        return False
