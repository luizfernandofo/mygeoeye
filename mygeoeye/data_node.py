import socket
import os
import threading
from shared import *

# Constantes
NODO_IP = "127.0.0.1"
NODO_PORTA = 5003

def handle_nodo(nodo_socket):
    try:
        comando = receber_str(nodo_socket)
        print(f"Comando recebido: {comando}")

        if comando.startswith("STORE"):
            _, nome_imagem = comando.split()
            print(f"Armazenando {nome_imagem}...")

            receber_arquivo_em_chunks(nodo_socket, f"data/{nome_imagem}")
            print(f"{nome_imagem} armazenada com sucesso.")

        elif comando.startswith("DOWNLOAD"):
            _, nome_imagem = comando.split()
            if os.path.exists(f"data/{nome_imagem}"):
                enviar_arquivo_em_chunks(nodo_socket, f"data/{nome_imagem}")
                print(f"{nome_imagem} enviada com sucesso.")
            else:
                print("Imagem não encontrada.")

        elif comando.startswith("DELETE"):
            _, nome_imagem = comando.split()
            if os.path.exists(f"data/{nome_imagem}"):
                os.remove(f"data/{nome_imagem}")
                print(f"{nome_imagem} deletada com sucesso.")
            else:
                print("Imagem não encontrada.")
    finally:
        nodo_socket.close()        

def nodo():
    if not os.path.isdir('data'):
        os.makedirs('data')

    nodo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodo_socket.bind((NODO_IP, NODO_PORTA))
    nodo_socket.listen(5)
    print(f"Nó de dados {NODO_IP}:{NODO_PORTA} aguardando conexões...")

    while True:
        cliente_socket, addr = nodo_socket.accept()
        print(f"Conexão aceita de {addr}")

        cliente_thread = threading.Thread(target=handle_nodo, args=(cliente_socket,))
        cliente_thread.start()

if __name__ == "__main__":
    nodo()
