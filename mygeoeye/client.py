import socket
import os
from shared import *

# Constantes
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

def cliente():
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.connect((SERVER_IP, SERVER_PORT))

    while True:
        comando = input("Digite o comando (UPLOAD, LIST, DOWNLOAD, DELETE, QUIT): ").strip().upper()

        if comando == "UPLOAD":
            cliente_socket.sendall(comando.encode('utf-8'))

            nome_imagem = input("Digite o nome da imagem: ").strip()
            caminho_arquivo = input("Digite o caminho do arquivo: ").strip()

            if not os.path.exists(caminho_arquivo):
                print("Arquivo não encontrado!")
                continue

            cliente_socket.sendall(nome_imagem.encode('utf-8'))
            enviar_arquivo_em_chunks(cliente_socket, caminho_arquivo)
            resposta = cliente_socket.recv(CHUNK_SIZE).decode('utf-8')
            print(resposta)

        elif comando == "LIST":
            cliente_socket.sendall(comando.encode('utf-8'))
            resposta = cliente_socket.recv(CHUNK_SIZE).decode('utf-8')
            print("Imagens disponíveis:\n", resposta)

        elif comando == "DOWNLOAD":
            cliente_socket.sendall(comando.encode('utf-8'))

            nome_imagem = input("Digite o nome da imagem a baixar: ").strip()
            cliente_socket.sendall(nome_imagem.encode('utf-8'))

            nodo = cliente_socket.recv(CHUNK_SIZE).decode('utf-8')
            if nodo == "IMAGE NOT FOUND":
                print("Imagem não encontrada.")
            else:
                print(f"Baixando imagem do nó {nodo}...")
                ip_nodo, porta_nodo = nodo.split(":")
                nodo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                nodo_socket.connect((ip_nodo, int(porta_nodo)))

                nodo_socket.sendall(f"DOWNLOAD {nome_imagem}".encode('utf-8'))
                receber_arquivo_em_chunks(nodo_socket, f"baixado_{nome_imagem}")
                print(f"Imagem '{nome_imagem}' baixada com sucesso.")
                nodo_socket.close()

        elif comando == "DELETE":
            cliente_socket.sendall(comando.encode('utf-8'))

            nome_imagem = input("Digite o nome da imagem a deletar: ").strip()
            cliente_socket.sendall(nome_imagem.encode('utf-8'))

            resposta = cliente_socket.recv(CHUNK_SIZE).decode('utf-8')
            print(resposta)

        elif comando == "QUIT":
            cliente_socket.close()
            break

        else:
            print("Comando inválido!")

if __name__ == "__main__":
    cliente()
