from rpyc.utils.server import ThreadedServer
import rpyc
from shared import *

class DataNodeService(rpyc.Service):
  def __init__(self):
    self.server_conn = rpyc.connect(SERVER_HOST, SERVER_PORT)
    node_id = self.server_conn.root.register_data_node()
    print(f'Data node conectado no SERVER, id recebido: {node_id}')
  
  def exposed_hello(self):
    print('Hello world!')

if __name__ == '__main__':
  _data_node = DataNodeService()
  ts = ThreadedServer(_data_node, port=0)  # Usa uma porta aleatória
  ts.start()
