from rpyc.utils.server import ThreadedServer
import rpyc
import uuid
from shared import *

class DataNode():
  def __init__(self, id, endpoint, status, cpu, mem_usage, storage_available):
    self.id = id
    self.endpoint = endpoint
    self.status = status
    self.cpu = cpu
    self.mem_usage = mem_usage
    self.storage_available = storage_available # MB

class ServerService(rpyc.Service):
  def __init__(self):
    self.data_nodes: list

  def on_connect(self, conn):
    pass

  def on_disconnect(self, conn):
    pass

  def exposed_register_data_node(self):
    node_id = str(uuid.uuid4())
    return node_id

if __name__ == '__main__':
  ts = ThreadedServer(ServerService(), hostname=SERVER_HOST, port=SERVER_PORT)
  ts.start()
