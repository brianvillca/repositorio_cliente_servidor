import pg8000.dbapi

# Configuración de tu conexión a PostgreSQL
DB_CONFIG = {
    'database': 'test1',
    'user': 'postgres',      # Recuerda cambiarlo si tu usuario es diferente
    'contraseña': '123',       # Tu contraseña
    'host': 'localhost',
    'port': '5432'          #puerto generico modificar
}

def get_connection():
    #Establece y devuelve la conexión a la base de datos."""
    return pg8000.dbapi.connect(**DB_CONFIG)

def inicializar_base_datos():
    #Crea la tabla 'usuarios' la primera vez que se ejecuta el servidor."""
    try:
        conexion = get_connection()#abre la conexión usando los datos del diccionario
        cursor = conexion.cursor()#Crea un 'cursor'. El cursor es el mensajero que viaja con nuestro comando SQL hacia la base de datos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                usuario VARCHAR(50) UNIQUE NOT NULL,
                contraseña VARCHAR(255) NOT NULL
            )
        """)#Escribe el comando SQL usando el lenguaje nativo de bases de datos
        conexion.commit()#Confirma y guarda permanentemente los cambios en la base de datos
        print("[DB] Base de datos PostgreSQL inicializada y lista.")
    except Exception as e:
        print(f"[DB ERROR] No se pudo inicializar PostgreSQL: {e}")#Si no tienes PostgreSQL prendido o la contraseña es incorrecta, te avisa aquí
    finally:
        # El finally tiene un trabajo el cual es limpiar la memoria.
        # "if 'cursor' in locals():" revisa si la variable cursor se alcanzó a crear antes de que ocurriera algún error.
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def registrar_usuario_db(usuario, contraseña):
    #Intenta guardar un usuario en la BD. Retorna True si tiene éxito, False si ya existe."""
    try:
        conexion = get_connection()#abre la conexión usando los datos del diccionario
        cursor = conexion.cursor()#Crea un 'cursor'. El cursor es el mensajero que viaja con nuestro comando SQL hacia la base de datos
        # Usamos %s como "espacios en blanco" que luego rellenamos con la tupla (username, password).Esto previene el "SQL Injection"
        cursor.execute("INSERT INTO usuarios (usuario, contraseña) VALUES (%s, %s)", (usuario, contraseña))#Escribe el comando SQL usando el lenguaje nativo de bases de datos
        conexion.commit()# Guardamos los cambios
        return True
    except Exception:
        # Falla automáticamente si el usuario ya está registrado 
        return False 
    finally:
        # Limpieza obligatoria de conexiones para no saturar el servidor
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def verificar_login_db(usuario, contraseña):
    #Verifica si las credenciales coinciden con las de la base de datos."""
    try:
        conexion = get_connection()#abre la conexión usando los datos del diccionario
        cursor = conexion.cursor()#Crea un 'cursor'. El cursor es el mensajero que viaja con nuestro comando SQL hacia la base de datos
        cursor.execute("SELECT contraseña FROM usuarios WHERE usuario = %s", (usuario,))#Escribe el comando SQL usando el lenguaje nativo de bases de datos
        resultado = cursor.fetchone()# fetchone() trae el primer resultado de la búsqueda. Como usuario es unico, solo habrá un resultado.
        
        if resultado and resultado[0] == contraseña:#revisa si la contraseña coincide con la del resultado
            return True# Dale acceso
        return False # Contraseña equivocada o el usuario no existe
    except Exception as e:# Si la base de datos colapsa a la mitad de la consulta
        print(f"[DB ERROR] Error al intentar loguear: {e}")
        return False
    finally:# Cerramos los canales de comunicación
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()