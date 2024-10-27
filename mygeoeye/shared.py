import socket

FATOR_REPLICA = 1
CONN_LISTEN_LIMIT = 10

ENCODING = 'utf-8'
EOF_MARKER = b"EOF"  # Indicador de fim de arquivo
CHUNK_DATA_SIZE = 1024 * 1024  # Tamanho dos chunks de dados em bytes
CHUNK_COMM_SIZE = 1024  # Tamanho dos chunks de comunicação em bytes

CODES = {
    300: 'Comando maior que o chunk size.'
}

def enviar_str(_conn: socket.socket, _str: str):
    encoded_str = _str.encode(ENCODING)
    if len(encoded_str) > CHUNK_COMM_SIZE:
        raise Exception('CODE', 300)
    
    if len(encoded_str) < CHUNK_COMM_SIZE:
        encoded_str = encoded_str.ljust(CHUNK_COMM_SIZE, b'\0')
    
    _conn.sendall(encoded_str)

def receber_str(_conn: socket.socket) -> str:
    encoded_padded_str = _conn.recv(CHUNK_COMM_SIZE)    
    encoded_str = encoded_padded_str.rstrip(b'\0')
    return encoded_str.decode(ENCODING)

# Função para receber arquivo em chunks
def receber_arquivo_em_chunks(_conn, arquivo_path):
    with open(arquivo_path, "wb") as f:
        while True:
            chunk = _conn.recv(CHUNK_DATA_SIZE)
            
            # Verifica se o chunk contém o EOF_MARKER
            if chunk.endswith(EOF_MARKER):
                f.write(chunk[:-len(EOF_MARKER)])  # Grava o chunk sem o EOF
                #print("EOF recebido, finalizando o recebimento.")
                break
            
            f.write(chunk)  # Escreve o chunk no arquivo

    #print(f"Arquivo '{arquivo_path}' recebido e armazenado com sucesso.")

# Função para enviar arquivo ao servidor em chunks
def enviar_arquivo_em_chunks(_conn, arquivo_path):
    with open(arquivo_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_DATA_SIZE)
            if not chunk:
                break
            _conn.sendall(chunk)  # Enviar cada chunk

        # Envia o marcador de EOF para sinalizar fim de arquivo
        _conn.sendall(EOF_MARKER)
    #print(f"Envio do arquivo '{arquivo_path}' concluído.")