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
        comando = receber_str(cliente_socket)
        print(f"Comando recebido: {comando}")

        if comando == "UPLOAD":
            nome_imagem = receber_str(cliente_socket)
            print(f"Nome da imagem para upload: {nome_imagem}")
            temp_name = str(uuid.uuid4())
            receber_arquivo_em_chunks(cliente_socket, temp_name)

            for nodo in NODES:
                ip, porta = nodo.split(":")
                nodo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                nodo_socket.connect((ip, int(porta)))
                enviar_str(nodo_socket, f"STORE {nome_imagem}")
                enviar_arquivo_em_chunks(nodo_socket, temp_name)
                nodo_socket.close()

            os.remove(temp_name)

            imagens[nome_imagem] = NODES
            enviar_str(cliente_socket, "UPLOAD SUCCESS")

        # TO-DO: alterar daqui para baixo
        elif comando == "LIST":
            if (bool(imagens)):
                lista_imagens = "\n".join(imagens.keys())
            else:
                lista_imagens = "Não há imagens."
            enviar_str(cliente_socket, lista_imagens)

        elif comando == "DOWNLOAD":
            nome_imagem = receber_str(cliente_socket)

            if nome_imagem in imagens:
                nodo = next(round_robin)
                enviar_str(cliente_socket, nodo)
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
    servidor_socket.listen(5)
    print("Servidor aguardando conexões...")

    while True:
        cliente_socket, addr = servidor_socket.accept()
        threading.Thread(target=handle_cliente, args=(cliente_socket,)).start()

if __name__ == "__main__":
    servidor()
