import time

from controller_agent import listenController, ServerMap

def main():
    def callback(server_id, model_name):
        print ('Update', time.time(), server_id, model_name)

    server_map = listenController('127.0.0.1', 9004, None, callback)
    while (True):
        time.sleep(5)
        server_list = server_map.server_list()
        print ('Summary')
        for server_id in server_list:
            print (server_id, server_map.get(server_id))
        print()

if __name__ == '__main__':
    main()