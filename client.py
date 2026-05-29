import socket
HOST = "127.0.0.1"
PORT = 12345

def recibir_mensaje_broadcast():
    

    return 

def iniciar_cliente():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"Hola soy el cliente")
        data = s.recv(1024).decode()
        print("El server dice: " + f"{data!r}")
        
        while True:
            mensaje = input("Tú: ")
            s.sendall(mensaje.encode('utf-8'))
            if mensaje == '/salir':
                print("Cerrando comunicación...")
                break
        data = s.recv(1024).decode('utf-8')
        print(f'Servidor: {data}')
if __name__ == "__main__":
    iniciar_cliente()