import socket
import sys
import threading
from base_de_datos import db

clientes = {}# Diccionario global para rastrear las conexiones activas en este instante
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
            if not autenticado:

                if mensaje.startswith('/register '):
                    partes = mensaje.split(' ', 2)
                    if len(partes) < 3:
                        client_socket.send("ERROR: Faltan datos. Usa: /register <usuario> <contraseña>\n".encode('utf-8'))
                        continue
                        #divide el texto en máximo 3 partes: ['/register', 'usuario', 'contraseña']
                    nombre_pedido = partes[1].strip()
                    password_pedido = partes[2].strip()
                    
                    #Llamamos a la base de datos
                    if db.registrar_usuario_db(nombre_pedido, password_pedido):
                        client_socket.send("ÉXITO: Cuenta creada. Ahora inicia sesión con /login <usuario> <contraseña>\n".encode('utf-8'))
                    else:
                        client_socket.send("ERROR: Ese nombre de usuario ya está registrado.\n".encode('utf-8'))
                    continue

                elif mensaje.startswith('/login '):
                    partes = mensaje.split(' ', 2)#divide el texto en máximo 3 partes: ['/register', 'usuario', 'contraseña']
                    if len(partes) < 3:
                        client_socket.send("ERROR: Faltan datos. Usa: /login <usuario> <contraseña>\n".encode('utf-8'))
                        continue
                        
                    nombre_pedido = partes[1].strip()
                    password_pedido = partes[2].strip()
                    
                    #Verificamos en PostgreSQL si las credenciales son correctas
                    if not db.verificar_login_db(nombre_pedido, password_pedido):
                        client_socket.send("ERROR: Usuario no existe o contraseña incorrecta.\n".encode('utf-8'))
                        continue
                    
                    #Verificamos en el diccionario temporal si ya tiene una sesión abierta
                    with clientes_lock:
                        if nombre_pedido in clientes.values():
                            client_socket.send("ERROR: Esta cuenta ya está conectada en otro lado.\n".encode('utf-8'))
                        else:
                            usuario = nombre_pedido
                            clientes[client_socket] = usuario
                            autenticado = True
                            client_socket.send(f"ÉXITO: Te has autenticado como '{usuario}'. Ya puedes chatear.\n".encode('utf-8'))
                    continue

                else:
                    client_socket.send("INFO: Identifícate primero con /register <usuario> <contraseña> o /login <usuario> <contraseña>\n".encode('utf-8'))
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
    db.inicializar_base_datos()
    HOST = "127.0.0.1"
    PORT = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Crea el socket usando IPv4 (AF_INET) y el protocolo TCP garantizado (SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)# Permite reutilizar el puerto 12345 de inmediato si el servidor se apaga y se prende rápido
    server_socket.bind((HOST, PORT))# Asigna la IP y el Puerto al socket del servidor
    server_socket.listen(5)# Activa la escucha y crea una cola de espera para hasta 5 conexiones simultáneas en cola
    print(f'Servidor activo y escuchando en {HOST}: {PORT}')

    while True:
        conn, addr = server_socket.accept()# Se congela en esta línea hasta que un nuevo cliente intenta conectarse a la red
        thread = threading.Thread(target=manejar_cliente, args=(conn, addr))# Crea un nuevo hilo de ejecución dedicado exclusivamente a este nuevo cliente
        thread.start()# Arranca el hilo en segundo plano
        # Se resta 1 por el hilo principal que siempre está corriendo
        print(f'[CONEXIONES ACTIVAS] {threading.active_count() - 1}')

if __name__ == "__main__":
    # Si este archivo se ejecuta de forma directa en la consola, arranca el servidor
    iniciar_servidor()