Chat Multiusuario Asíncrono en Red
Esta aplicación implementa una comunicación cliente-servidor a través de sockets TCP en Python. Utiliza programación multihilo (threading) para manejar múltiples usuarios simultáneamente y conectarse a una base de datos PostgreSQL de forma persistente.

Un chat ligero y robusto diseñado para la consola de comandos con las siguientes características:

Asíncrono y Multitarea: Utiliza hilos (threads) tanto en el servidor (para atender múltiples clientes a la vez) como en el cliente (para recibir y enviar mensajes simultáneamente sin bloqueos).

Seguro: Autenticación y registro obligatorio de cuentas antes de poder acceder al chat general.

Persistente: Integración directa con bases de datos relacionales PostgreSQL (mediante la librería pure-Python pg8000) para guardar los usuarios y contraseñas de forma permanente.

-Comandos del Servidor
El servidor se ejecuta en segundo plano mostrando un registro (log) en tiempo real de todo lo que sucede:

Log de Conexiones: Muestra IP y puerto de cada cliente nuevo.

Log de Autenticación: Notifica cuando se registran nuevos usuarios en la BD.

Monitor de Hilos: Muestra la cantidad exacta de conexiones activas.

Cierre de Emergencia: Usa Ctrl + C o KeyboardInterrupt en la consola para apagar el servidor de forma segura cerrando las conexiones de red locales.

-Comandos del Cliente
Una vez establecida la conexión física con el servidor, el cliente debe interactuar mediante los siguientes comandos en su consola:

/register  
Registra una nueva cuenta de usuario y la guarda en PostgreSQL. (Nota: Tras un registro exitoso, el usuario debe usar /login para entrar).

/login  
Verifica las credenciales en la base de datos e inicia sesión en el chat.

/all 
Envía un mensaje de broadcast a todos los usuarios conectados y autenticados actualmente en el servidor.

/salir
Se desconecta del servidor, cierra el socket de red y finaliza el programa del cliente por completo.

-Estructura del Proyecto
El proyecto sigue una arquitectura modular y organizada:

-Plaintext
REPOSITORIO_CLIENTE_SERVIDOR/
├── base_de_datos/
│   └── db.py            # Conexión directa a PostgreSQL y operaciones CRUD
├── servidor/
│   └── server.py        # Código del Servidor (manejo de sockets, hilos y lógica de chat)
├── client.py            # Código del Cliente (hilos de envío/recepción y menú de usuario)
├── main.py              # Punto de entrada (Entry point) unificado del servidor
├── requirements.txt     # Dependencias necesarias para ejecutar el proyecto
└── README.md            # Documentación del proyecto (este archivo)
-Explicación por Archivo
main.py: El punto de entrada principal. Actúa como el orquestador: primero configura las rutas del sistema, luego inicializa la base de datos (creando las tablas si no existen) y finalmente arranca el bucle de escucha del servidor TCP.

base_de_datos/db.py: Maneja las operaciones de persistencia. Se conecta a PostgreSQL utilizando pg8000, permitiendo registrar nuevos usuarios de forma segura y verificar inicios de sesión sin saturar la memoria RAM del servidor.

servidor/server.py: Implementa el motor del servidor. Por cada cliente que se conecta, abre un Thread (hilo) dedicado. Actúa como un filtro de seguridad exigiendo registro/login antes de procesar cualquier comando /all.

client.py: La interfaz de usuario final. Crea un hilo en segundo plano (daemon) dedicado a escuchar permanentemente las respuestas del servidor, mientras el hilo principal espera los inputs del usuario. Esto permite enviar y recibir textos fluidamente sin parpadeos en consola.

-Librerías utilizadas (requirements.txt)
pg8000==1.31.5: Conector nativo de Python para bases de datos PostgreSQL (pure-Python), lo que facilita conexiones eficientes sin requerir compiladores externos.

scramp==1.4.8: Implementación del mecanismo de autenticación SCRAM (Salted Challenge Response Authentication Mechanism), necesario para la seguridad al iniciar sesión en servidores PostgreSQL modernos.

asn1crypto==1.5.1: Librería de análisis y serialización rápida, utilizada internamente como dependencia por los protocolos de seguridad de bases de datos.

six==1.17.0: Biblioteca de compatibilidad que provee utilidades para garantizar que las dependencias internas funcionen correctamente en diferentes versiones de Python.

python-dateutil==2.9.0.post0: Extensión del módulo estándar datetime utilizada como apoyo interno por el conector de la base de datos para manejar zonas horarias y registros de tiempo precisos.
