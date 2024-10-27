import socket
import threading
import os
import itertools
import random
import uuid
from shared import *

# Constantes
NODES = ["127.0.0.1:5003"]

# Variáveis globais
imagens = {}
round_robin = itertools.cycle(NODES)

def upload_to_data_node(ip: str, porta: int, img_name: str, img_path: str):
    nodo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodo_socket.connect((ip, int(porta)))
    enviar_str(nodo_socket, f"STORE {img_name}")
    enviar_arquivo_em_chunks(nodo_socket, img_path)
    nodo_socket.close()

def handle_cliente(cliente_socket):
    while True:
        comando = receber_str(cliente_socket)
        print(f"Comando recebido: {comando}")

        if comando == "UPLOAD":
            nome_imagem = receber_str(cliente_socket)
            print(f"Nome da imagem para upload: {nome_imagem}")
            temp_name = str(uuid.uuid4())
            receber_arquivo_em_chunks(cliente_socket, temp_name)

            threads = []
            nodos = []
            for i in range(FATOR_REPLICA):
                nodos.append(next(round_robin))

            for nodo in nodos:
                ip, porta = nodo.split(":")
                t = threading.Thread(target=upload_to_data_node, args=(ip, int(porta), nome_imagem, temp_name))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            os.remove(temp_name)

            imagens[nome_imagem] = nodos
            print(imagens)
            enviar_str(cliente_socket, "UPLOAD SUCCESS")

        elif comando == "LIST":
            if (bool(imagens)):
                lista_imagens = "\n".join(imagens.keys())
            else:
                lista_imagens = "Não há imagens."
            enviar_str(cliente_socket, lista_imagens)

        elif comando == "DOWNLOAD":
            nome_imagem = receber_str(cliente_socket)
            if nome_imagem in imagens:
                _nodes = imagens[nome_imagem]
                _node = ""
                if (len(_nodes)) > 1:
                    _node = _nodes[random.randint(0, (len(_nodes) - 1))]
                else:
                    _node = _nodes[0]
                enviar_str(cliente_socket, _node)
            else:
                enviar_str(cliente_socket, "IMAGE NOT FOUND")

        elif comando == "DELETE":
            nome_imagem = receber_str(cliente_socket)

            if nome_imagem in imagens:
                for nodo in NODES:
                    ip, porta = nodo.split(":")
                    nodo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    nodo_socket.connect((ip, int(porta)))
                    enviar_str(nodo_socket, f"DELETE {nome_imagem}")
                    nodo_socket.close()

                del imagens[nome_imagem]
                enviar_str(cliente_socket, "DELETE SUCCESS")
            else:
                enviar_str(cliente_socket, "IMAGE NOT FOUND")

        elif comando == "QUIT":
            print("Cliente encerrou conexao.")
            cliente_socket.close()
            break

        else:
            enviar_str(cliente_socket, "INVALID COMMAND")

def servidor():
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind(("127.0.0.1", 5000))
    servidor_socket.listen(CONN_LISTEN_LIMIT)
    print("Servidor aguardando conexões...")

    while True:
        cliente_socket, addr = servidor_socket.accept()
        threading.Thread(target=handle_cliente, args=(cliente_socket,)).start()

if __name__ == "__main__":
    servidor()
