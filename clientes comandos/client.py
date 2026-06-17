import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 12345

def recibir_mensaje_broadcast(sock):
    while True:
        try:
            # Escuchamos al servidor
            data = sock.recv(1024).decode('utf-8')
            
            # Si data está vacío, el servidor nos desconectó
            if not data:
                print("\n[SERVIDOR] Conexión cerrada por el servidor.")
                break
            
            #acomodamos el texto para que esto no se superponga(fue corregido)
            print(f"\r{data}Tú: ", end="", flush=True)
            
        except Exception as e:
            # Si ocurre un error (como que cerramos el socket al salir), terminamos el hilo
            break

def iniciar_cliente():
    # Usamos 'with' para asegurar que el socket se cierre al terminar
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            print("error el servidor no esta encendido")
            return
        #menu principal de bienvenida o mensajes de ayuda principales
        print("Conectado al servidor")
        print("lista de comandos")
        print(" -Inicia sesión con: /login <tu_nombre> <Contraseña>-obligatorio")
        print(" -Registro con: /register <tu_nombre> <Contraseña>-opcional si tiene cuenta")
        print(" -Envía mensajes a todos: /all <mensaje>")
        print(" -Para salir del server: /salir\n")
        
        hilo = threading.Thread(target=recibir_mensaje_broadcast, args=(s,), daemon=True)
        hilo.start()

        # bucle de envios recordad no separar con try sin poner en la misma fila #es
        while True:
                mensaje = input("Tú: ")
                
                # Evitar enviar mensajes vacíos si solo presionas Enter
                if not mensaje.strip():#se que ya hay una en el servidor pero por unas correcciones tambien deberia tener la verificacion de ambos lados 
                    continue
                
                # Enviamos el comando o mensaje al servidor en resumen envio de envios 
                s.sendall(mensaje.encode('utf-8'))
                
                # Si nosotros decidimos salir, rompemos el bucle
                if mensaje == '/salir':
                    print("Cerrando comunicación...")
                    break
                    


if __name__ == "__main__":
    iniciar_cliente()