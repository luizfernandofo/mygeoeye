import socket
import os
from shared import *
import threading
import time

# Constantes
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
IMG_PER_SEC = 30

def cliente(comando: str, image_name: str):
    if not os.path.isdir('images'):
        os.makedirs('images')
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.connect((SERVER_IP, SERVER_PORT))
    
        #comando = input("Digite o comando (UPLOAD, LIST, DOWNLOAD, DELETE, QUIT): ").strip().upper()

    if comando == "UPLOAD":
        images_dir = os.path.join(os.getcwd(), "images")
        arquivos = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
        print("Arquivos disponíveis para upload:")
        for arquivo in arquivos:
            print(f"- {arquivo}")
        #image_name = input("Digite o nome do arquivo a ser enviado: ")
        
        if image_name in arquivos:
            # Caminho completo do arquivo
            enviar_str(cliente_socket, comando)
            arquivo_path = os.path.join(images_dir, image_name)
            enviar_str(cliente_socket, image_name)
            enviar_arquivo_em_chunks(cliente_socket, arquivo_path)
            resposta = receber_str(cliente_socket)
            print(resposta)
            
        else:
            print("Arquivo não encontrado na lista disponível.")

    elif comando == "LIST":
        enviar_str(cliente_socket, comando)
        resposta = receber_str(cliente_socket)
        print("Imagens disponíveis:\n", resposta)

    elif comando == "DOWNLOAD":
        enviar_str(cliente_socket, comando)
        enviar_str(cliente_socket, image_name)

        nodo = receber_str(cliente_socket)

        if nodo == "IMAGE NOT FOUND":
            print("Imagem não encontrada.")
        else:
            print(f"Baixando imagem do nó {nodo}...")
            ip_nodo, porta_nodo = nodo.split(":")
            nodo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            nodo_socket.connect((ip_nodo, int(porta_nodo)))

            enviar_str(nodo_socket, f"DOWNLOAD {image_name}")
            receber_arquivo_em_chunks(nodo_socket, f"baixado_{image_name}")
            print(f"Imagem '{image_name}' baixada com sucesso.")
            nodo_socket.close()

    elif comando == "DELETE":
        enviar_str(cliente_socket, comando)
        enviar_str(cliente_socket, image_name)

        resposta = receber_str(cliente_socket)
        print(resposta)

    elif comando == "QUIT":
        enviar_str(cliente_socket, comando)

    else:
        print("Comando inválido!")
    enviar_str(cliente_socket, "QUIT")

def main():
    cliente("UPLOAD", "img.tif")
    tempo_inicio = time.time_ns()
    threads = []
    for i in range(IMG_PER_SEC):
        t = threading.Thread(target=cliente, args=('DOWNLOAD', 'img.tif'))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

    tempo_fim = time.time_ns()
    tempo_gasto = tempo_fim - tempo_inicio
    print(f"Tempo total de execução: {tempo_gasto * 10**-6:.2f} ms.")

if __name__ == '__main__':
    main()