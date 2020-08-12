from netmiko import ConnectHandler
import pyexcel
import os
import time
import psutil

def retv_excel(file):
    d = {}
    records = pyexcel.iget_records(file_name=file)
    for record in records:
        d.update({record['IP']: [record['driver'], record['username'], record['password']]})
    return d

def login_router(dev_type, dev_ip, dev_un, dev_pw):
    try:
        open_connection = ConnectHandler(device_type=dev_type, ip=dev_ip, username=dev_un, password=dev_pw)
        return True
    except:
        return False

def ping_router(hostname):
    response = os.system("ping -c 1 " + hostname)

    if response == 0:
        return True
    else:
        return False

def interface_check(dev_type, dev_ip, dev_un, dev_pw):
    try:
        open_connection = ConnectHandler(device_type=dev_type, ip=dev_ip, username=dev_un, password=dev_pw)
        my_command = open_connection.send_command("lanhosts show all")
    except:
        my_command = "** ISSUING COMMAND FAILED **"
    finally:
        return my_command

def bandwidth_test():
    old_value = 0
    while True:
        new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        if old_value:
            send_stat(new_value - old_value)

        old_value = new_value

        time.sleep(1)

def convert_to_mbit(value):
    return value/1024./1024.*8

def send_stat(value):
    print (f'The bandwidth is {"%0.3f" % convert_to_mbit(value)} Mbps')

def output(dev_type, dev_ip, dev_un, dev_pw):
    output = interface_check(dev_type, dev_ip, dev_un, dev_pw)
    output = output.strip("Bridge br0 \n MAC Addr          IP Addr     Lease Time Remaining    Hostname")
    for x in output.splitlines():
        x = x.split(" ")
        while ("" in x):
            x.remove("")
        print(f"The ip address of {x[3]} is {x[1]}")
        print("\n")
        if ping_router(x[1]):
            print("\n\t**IP: - " + x[1] + " - responding to ICMP\n")
        else:
            print("\n\t**IP: - " + x[1] + " - NOT responding to ICMP\n")

def ping(dev_type, dev_ip, dev_un, dev_pw):
    try:
        open_connection = ConnectHandler(device_type=dev_type, ip=dev_ip, username=dev_un, password=dev_pw)
        my_command = open_connection.send_command("ping -4 www.google.com")
    except:
        my_command = "** PING FAILED **"
    finally:
        return my_command

def reboot(dev_type, dev_ip, dev_un, dev_pw):
    try:
        open_connection = ConnectHandler(device_type=dev_type, ip=dev_ip, username=dev_un, password=dev_pw)
        my_command = open_connection.send_command("reboot")
    except:
        my_command = "** REBOOT FAILED **"
    finally:
        return my_command

def main():
    file_location = str(input("\nWhere is the file location? "))
    entry = retv_excel(file_location)

    print("\n***** BEGIN SSH CHECKING *****")
    for x in entry.keys():
        if login_router(str(entry[x][0]), x, str(entry[x][1]), str(entry[x][2])):
            print("\n\t**IP: - " + x + " - SSH connectivity UP\n")
        else:
            print("\n\t**IP: - " + x + " - SSH connectivity DOWN\n")

    print("\n***** BEGIN ICMP CHECKING *****")
    for x in entry.keys():
        if ping_router(x):
            print("\n\t**IP: - " + x + " - responding to ICMP\n")
        else:
            print("\n\t**IP: - " + x + " - NOT responding to ICMP\n")

    print("\n***** BEGIN SHOW IP INT BRIEF *****")
    for x in entry.keys():
        print("\n" + interface_check(str(entry[x][0]), x, str(entry[x][1]), str(entry[x][2])))

    print("\n***** BEGIN INTERFACES ICMP CHECKING *****")
    for x in entry.keys():
        output(str(entry[x][0]), x, str(entry[x][1]), str(entry[x][2]))

    print("\n***** REBOOT ROUTER IF PING FAILED *****")
    for x in entry.keys():
        print(ping(str(entry[x][0]), x, str(entry[x][1]), str(entry[x][2])))
        result = ping(str(entry[x][0]), x, str(entry[x][1]), str(entry[x][2]))
        while result == "** PING FAILED **":
            print(reboot(str(entry[x][0]), x, str(entry[x][1]), str(entry[x][2])))
            print(ping(str(entry[x][0]), x, str(entry[x][1]), str(entry[x][2])))
            result = ping(str(entry[x][0]), x, str(entry[x][1]), str(entry[x][2]))

    print("\n***** BEGIN NETWORK BANDWIDTH MONITOR*****")
    print(bandwidth_test())
main()