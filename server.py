import socket
import sys
import threading

clientes = {}
clientes_lock = threading.Lock()# Cerrojo (Lock) para asegurar que el manejo del diccionario sea seguro entre hilos
def broadcast(mensaje, socket_remitente=None):
    """Envía un mensaje a todos los usuarios autenticados, excepto al remitente."""
    with clientes_lock:
        for cliente_socket in list(clientes.keys()):
            if cliente_socket != socket_remitente:  
                    cliente_socket.send(mensaje.encode('utf-8'))

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
                if mensaje.startswitch('/login'):#revisa desde todo el diccionario hasta el 0 para revisar si hay un usuario ya registrado con ese login es un metodo de seguridad
                    partes = mensaje.split(' ', 1)# separa el mensaje asegurando que este no llegue completamente roto por " " el[0] es directamente el comando que pusimos como /login
                    nombre_pedido = partes[1].strip() if len(partes) > 1 else ""#va a la parte del nombre y limpia con .strip los " " y guarda en nombre pedido. si esta vacio no lo toma y da aviso
                    if not nombre_pedido:
                        client_socket.send("error: El nombre de usuario no puede estar vacío. Usa: /login <usuario>\n".encode('utf-8'))
                        continue
                    with clientes_lock:#seguro que evita que todos los usuarios hagan la misma funcion al mismo tiempo sino se rompe todo 
                        #verficacion de que el nombre exista
                        if nombre_pedido in clientes.values():#revisa el string en el diccionario para ver si ya hay un usuario con el mismo nombre registrado. si esta en uso directo le dice
                            clientes.send("error: El nombre de usuario ya esta en uso\n".encode('utf-8'))
                        else: #guarda lo datos en el diccionario
                            usuario = nombre_pedido#guarda tu nombre en usuario
                            clientes[client_socket] = usuario#guarda tu nombre que pusiste en usuario en el diccionario de usuarios
                            autenticado = True#aca le dices que si esta bien verificado no mas

                            client_socket.send(f"Te has autenticado como '{usuario}'. Ya puedes enviar mensajes al servidor .\n".encode('utf-8'))
                            #print(f"[AUTENTICACIÓN] {addr} ahora es conocidos como '{usuario}'") es opcional sinceramente es algo mas como un poder de administrador al ver estos cambios
                        continue
                    if mensaje.startswitch('/all'):
                        partes = mensaje.split(' ', 1)#separa el mensaje en partes cortando los " "
                        contenido_mensaje = partes[1].strip() if len(partes) > 1 else ""
                        if contenido_mensaje:#le damos un contenido al mensaje para reemplazar lo datos necesarios como usuario y el contenido del mensaje
                            formato_msg = f"[{usuario} para TODOS]: {contenido_mensaje}\n"
                            print(f"Broadcast de {usuario}: {contenido_mensaje}")
                            broadcast(formato_msg, client_socket)

            print(f'[{addr}] dice: {mensaje}')
    except Exception as e:
        print("Error al intentar manejar el cliente: " + str(e))
    finally:
        client_socket.close()
        print(f'[CONEXIONES ACTIVAS] {threading.active_count() - 2}') 

def iniciar_servidor():
    HOST = "127.0.0.1"
    PORT = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'Servidor activo en {HOST}: {PORT}')

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=manejar_cliente, args=(conn, addr))
        thread.start()
        print(f'[CONEXIONES ACTIVAS] {threading.active_count() - 1}')

if __name__ == "__main__":
    iniciar_servidor()