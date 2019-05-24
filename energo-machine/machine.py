import requests
import time
import os

MY_ID = 5


def check_queries():
    headers = {'Accept-Encoding': 'identity'}
    params = {'id': str(MY_ID)}
    r = requests.get('http://192.168.1.61:7777/qch',
                     headers=headers,
                     params=params)
    print(r.text)
    resp = int(r.text)
    if resp == 1:
        os.system('eject cdrom')


def main():
    while(True):
        time.sleep(3)
        try:
            check_queries()
        except Exception:
            pass


main()
