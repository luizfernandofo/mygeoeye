import socket
import threading
import os
import itertools
import uuid
from shared import *

# Constantes
NODES = ["127.0.0.1:5003"]

# Variáveis globais
imagens = {}
round_robin = itertools.cycle(NODES)

def handle_cliente(cliente_socket):
    while True:
        comando = cliente_socket.recv(CHUNK_SIZE).decode('utf-8')
        print(f"Comando recebido: {comando}")

        if comando == "UPLOAD":
            nome_imagem = cliente_socket.recv(CHUNK_SIZE).decode('utf-8')
            print(f"Nome da imagem para upload: {nome_imagem}")
            temp_name = str(uuid.uuid4())
            receber_arquivo_em_chunks(cliente_socket, temp_name)

            for nodo in NODES:
                ip, porta = nodo.split(":")
                nodo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                nodo_socket.connect((ip, int(porta)))
                nodo_socket.sendall(f"STORE {nome_imagem}".encode('utf-8'))
                enviar_arquivo_em_chunks(nodo_socket, temp_name)
                nodo_socket.close()

            os.remove(temp_name)

            imagens[nome_imagem] = NODES
            cliente_socket.sendall("UPLOAD SUCCESS".encode('utf-8'))

        elif comando == "LIST":
            if (bool(imagens)):
                lista_imagens = "\n".join(imagens.keys())
            else:
                lista_imagens = "Não há imagens."
            cliente_socket.sendall(lista_imagens.encode('utf-8'))

        elif comando == "DOWNLOAD":
            nome_imagem = cliente_socket.recv(CHUNK_SIZE).decode('utf-8')

            if nome_imagem in imagens:
                nodo = next(round_robin)
                cliente_socket.sendall(nodo.encode('utf-8'))
            else:
                cliente_socket.sendall("IMAGE NOT FOUND".encode('utf-8'))

        elif comando == "DELETE":
            nome_imagem = cliente_socket.recv(CHUNK_SIZE).decode('utf-8')

            if nome_imagem in imagens:
                for nodo in NODES:
                    ip, porta = nodo.split(":")
                    nodo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    nodo_socket.connect((ip, int(porta)))
                    nodo_socket.sendall(f"DELETE {nome_imagem}".encode('utf-8'))
                    nodo_socket.close()

                del imagens[nome_imagem]
                cliente_socket.sendall("DELETE SUCCESS".encode('utf-8'))
            else:
                cliente_socket.sendall("IMAGE NOT FOUND".encode('utf-8'))

        else:
            cliente_socket.sendall("INVALID COMMAND".encode('utf-8'))

def servidor():
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind(("127.0.0.1", 5000))
    servidor_socket.listen(5)
    print("Servidor aguardando conexões...")

    while True:
        cliente_socket, addr = servidor_socket.accept()
        threading.Thread(target=handle_cliente, args=(cliente_socket,)).start()

if __name__ == "__main__":
    servidor()
