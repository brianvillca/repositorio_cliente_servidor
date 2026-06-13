import socket
import sys
import threading

clientes = {}
clientes_lock = threading.Lock()# Cerrojo (Lock) para asegurar que el manejo del diccionario sea seguro entre hilos
def broadcast(mensaje, socket_remitente=None):
    """Envía un mensaje a todos los usuarios autenticados, excepto al remitente."""
    with clientes_lock:
        for cliente_socket in list(clientes.keys()):
                 try:
                    cliente_socket.send(mensaje.encode('utf-8'))
                 except Exception as e:
                    print(f"Error al enviar mensaje a un cliente: {e}")

def manejar_cliente(client_socket, addr):
    print(f"Se ha establecido la conexión con: {addr}")
    usuario = None
    autenticado = False
    try:
        while True:
            #recibir usuarios
            data = client_socket.recv(1024)
            if not data:
                break
            #mensaje del usuario
            mensaje = data.decode('utf-8').strip()#strip elimina el caracter invisible " "
            #comando salir del servidor o salir directo para el usuario
            if not mensaje or mensaje == '/salir':
                print(f'[DESCONEXIÓN CONCRETADA] El cliente {addr} ha cerrado la conexión')
                break
            if not autenticado:#entra en este si no esta autentificado
                if mensaje.startswith('/register'):#revisa desde todo el diccionario hasta el 0 para revisar si hay un usuario ya registrado con ese login es un metodo de seguridad
                    partes = mensaje.split(' ', 1)# separa el mensaje asegurando que este no llegue completamente roto por " " el[0] es directamente el comando que pusimos como /login
                    nombre_pedido = partes[1].strip() if len(partes) > 1 else ""#va a la parte del nombre y limpia con .strip los " " y guarda en nombre pedido. si esta vacio no lo toma y da aviso
                    if not nombre_pedido:
                        client_socket.send("error: El nombre de usuario no puede estar vacío. Usa: /register <usuario>\n".encode('utf-8'))
                        continue
                        
                    with clientes_lock:
                        if nombre_pedido in clientes.values():#verifica si el nombre ya esta en uso
                            client_socket.send("error: El nombre de usuario ya esta en uso\n".encode('utf-8'))#manda error en ese caso
                        else:
                            usuario = nombre_pedido#guarda dentro de usuarios
                            clientes[client_socket] = usuario#en el diccionario lo guarda
                            autenticado = True#le da permiso para el chat
                            client_socket.send(f"Te has autenticado como '{usuario}'. Ya puedes enviar mensajes.\n".encode('utf-8'))
                else:
                    client_socket.send("INFO: Debes iniciar sesión primero con /login o crear un usuario con /register <usuario>\n".encode('utf-8'))
                
                # para que no intente ejecutar comandos de chat si no estás logueado.
                continue
            if mensaje.startswith('/all'):
                        partes = mensaje.split(' ', 1)#separa el mensaje en partes cortando los " "
                        contenido_mensaje = partes[1].strip() if len(partes) > 1 else ""
                        if contenido_mensaje:#le damos un contenido al mensaje para reemplazar lo datos necesarios como usuario y el contenido del mensaje
                            formato_msg = f"[{usuario} para TODOS]: {contenido_mensaje}\n"
                            print(f"Broadcast de {usuario}: {contenido_mensaje}")
                            broadcast(formato_msg, client_socket)
                        else:
                            client_socket.send("error el mensaje no puede estar vacio. Usa: /all <mensaje>\n".encode('utf-8'))
            else:
                     client_socket.send("INFO: Comando no reconocido. Para hablar con todos usa: /all <mensaje>\n".encode('utf-8'))
    except Exception as e:#detecion de errores recordar ponerlo en la misma columna sino no funciona 
        print(f"Error al intentar manejar al cliente {usuario or addr}: {e}")
        
    finally:
        with clientes_lock:#entra en el lock para el if 
            if client_socket in clientes:#consulta si todavia se guarda en el diccionario el hilo y en caso de ser positivo lo cierra cuando entra a finally
                del clientes[client_socket]#elimina del diccionario de hilos al client socket que cerro la conexion 
                client_socket.close()#todo lo anterior hasta el finally es para eliminar el hilo del diccionario y aca cierra el puerto que abrio 
        if autenticado and usuario:#verifica que el usuario si esta verificado entra en el if una vez que tiene el nombre de este
            broadcast(f"[SERVIDOR] {usuario} ha dejado el chat.\n")#da un mensaje global(como minecraft) de que el usuario a dejado el chat con el server y todos
        # Total de hilos menos el principal y el que está muriendo en este punto
        print(f'[CONEXIONES ACTIVAS] {threading.active_count() - 2}')#nos da el dato dentro del server de cuantos hilos abiertos quedan menos el que se cerro y el principal 
def iniciar_servidor():
    HOST = "127.0.0.1"
    PORT = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'Servidor activo y escuchando en {HOST}: {PORT}')

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=manejar_cliente, args=(conn, addr))
        thread.start()
        # Se resta 1 por el hilo principal que siempre está corriendo
        print(f'[CONEXIONES ACTIVAS] {threading.active_count() - 1}')

if __name__ == "__main__":
    iniciar_servidor()