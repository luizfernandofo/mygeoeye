EOF_MARKER = b"EOF"  # Indicador de fim de arquivo
CHUNK_SIZE = 1024 * 1024  # Tamanho dos chunks em bytes

# Função para receber arquivo em chunks
def receber_arquivo_em_chunks(cliente_socket, arquivo_path):
    with open(arquivo_path, "wb") as f:
        while True:
            chunk = cliente_socket.recv(CHUNK_SIZE)
            
            # Verifica se o chunk contém o EOF_MARKER
            if chunk.endswith(EOF_MARKER):
                f.write(chunk[:-len(EOF_MARKER)])  # Grava o chunk sem o EOF
                print("EOF recebido, finalizando o recebimento.")
                break
            
            f.write(chunk)  # Escreve o chunk no arquivo

    print(f"Arquivo '{arquivo_path}' recebido e armazenado com sucesso.")

# Função para enviar arquivo ao servidor em chunks
def enviar_arquivo_em_chunks(cliente_socket, arquivo_path):
    with open(arquivo_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            cliente_socket.sendall(chunk)  # Enviar cada chunk

        # Envia o marcador de EOF para sinalizar fim de arquivo
        cliente_socket.sendall(EOF_MARKER)
    print(f"Envio do arquivo '{arquivo_path}' concluído.")