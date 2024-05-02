from threading import Thread

from server import start
from logger import Logger

from gs1_bot.gs1_bot import gs1_main
from curry_bot.curry_bot import cu_main

curry_thread = Thread(target=cu_main)
gs1_thread = Thread(target=gs1_main)
server_thread = Thread(target=start)

if __name__ == "__main__":
    curry_thread.start()
    gs1_thread.start()
    server_thread.start()
    curry_thread.join()
    gs1_thread.join()
    server_thread.join()