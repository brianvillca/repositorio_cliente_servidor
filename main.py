import os
import sys
#siempre ejecutar desde main sino da error por problemas de carpetas en server y db
# Agregar el directorio raíz al path de Python para evitar errores de importación
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importamos usando los nombres EXACTOS de tus carpetas
from base_de_datos.db import inicializar_base_datos
from servidor.server import iniciar_servidor

def main():
    print("[MAIN] Iniciando aplicación de chat...")
    
    # 1. Inicializa la base de datos 
    inicializar_base_datos()
    
    # 2. Arranca el servidor de sockets
    iniciar_servidor()

if __name__ == "__main__":
    main()