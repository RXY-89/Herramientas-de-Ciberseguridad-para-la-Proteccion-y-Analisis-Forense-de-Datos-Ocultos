import os
import pathlib
import logging
from openai import OpenAI
from datetime import datetime

CARPETA_DESTINO = "AI_int"
if not os.path.exists(CARPETA_DESTINO):
    os.makedirs(CARPETA_DESTINO)

logging.basicConfig(
    filename=os.path.join(CARPETA_DESTINO, 'registro_analisis.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

EXTENSIONES_PERMITIDAS = {'.py', '.ps1', '.jsonl', '.txt', '.log', '.json'}

def gestionar_api_key():
    nombre_archivo_key = "api_key.txt"
    
    if os.path.exists(nombre_archivo_key):
        with open(nombre_archivo_key, "r") as f:
            api_key = f.read().strip()
            if not api_key:
                print(f"El archivo {nombre_archivo_key} está vacío.")
                logging.warning("Archivo api_key.txt encontrado pero vacio.")
                return gestionar_api_key()
            return api_key
    else:
        print("--- Configuración Inicial ---")
        api_key = input("Introduce tu API Key de OpenAI: ").strip()
        with open(nombre_archivo_key, "w") as f:
            f.write(api_key)
        print(f"API Key guardada exitosamente en '{nombre_archivo_key}'.\n")
        logging.info("Nueva API Key configurada y guardada.")
        return api_key

def es_archivo_permitido(ruta_archivo): 
    ext = pathlib.Path(ruta_archivo).suffix.lower()
    return ext in EXTENSIONES_PERMITIDAS

def leer_archivo_seguro(ruta_completa):
    if not es_archivo_permitido(ruta_completa):
        return None
    
    # Aquí intenta leer lo que se encuentre,
    try:
        with open(ruta_completa, "r", encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        msg = f"Omitido '{os.path.basename(ruta_completa)}': parece binario o codificacion incorrecta."
        print(msg)
        logging.warning(msg)
        return None
    except Exception as e:
        msg = f"Error leyendo '{os.path.basename(ruta_completa)}': {e}"
        print(msg)
        logging.error(msg)
        return None

def obtener_archivos_desde_ruta(ruta_input):
    archivos_encontrados = []
    ruta_abs = os.path.abspath(ruta_input.strip().strip('"'))

    if not os.path.exists(ruta_abs):
        msg = f"La ruta no existe: {ruta_abs}"
        print(msg)
        logging.warning(msg)
        return []

    ##Esto es cuando sea un archivo individual.
    if os.path.isfile(ruta_abs):
        if es_archivo_permitido(ruta_abs):
            contenido = leer_archivo_seguro(ruta_abs)
            if contenido is not None:
                archivos_encontrados.append((os.path.basename(ruta_abs), contenido))
                print(f"Archivo agregado: {os.path.basename(ruta_abs)}")
                logging.info(f"Agregado archivo individual: {ruta_abs}")
        else:
            msg = f"El archivo '{os.path.basename(ruta_abs)}' no tiene extensión permitida."
            print(msg)
            logging.info(f"Ignorado archivo individual (extensión): {ruta_abs}")

    #Esto es cuando sea una carpeta
    elif os.path.isdir(ruta_abs):
        print(f"   Explorando carpeta: {ruta_abs} ...")
        logging.info(f"Iniciando exploracion de carpeta: {ruta_abs}")
        
        count_ignored = 0
        count_added = 0
        
        for root, dirs, files in os.walk(ruta_abs):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.idea', 'venv', 'node_modules']]
            
            for file in files:
                ruta_archivo = os.path.join(root, file)
                if es_archivo_permitido(ruta_archivo):
                    contenido = leer_archivo_seguro(ruta_archivo)
                    if contenido is not None:
                        nombre_relativo = os.path.relpath(ruta_archivo, start=os.path.dirname(ruta_abs))
                        archivos_encontrados.append((nombre_relativo, contenido))
                        count_added += 1
                else:
                    count_ignored += 1
        
        print(f"Se agregaron {count_added} archivos válidos.")
        logging.info(f"Exploracion finalizada. Agregados: {count_added}, Ignorados: {count_ignored}")
        
        if count_ignored > 0:
            print(f"Se ignoraron {count_ignored} archivos por seguridad.")

    return archivos_encontrados

def gestionar_cola_analisis():
    cola_total = []
    while True:
        print("\n--- Selección de Objetivo ---")
        print(f"Extensiones permitidas: {', '.join(EXTENSIONES_PERMITIDAS)}")
        ruta = input("Introduce la ruta de la carpeta o archivo a analizar: ")
        
        nuevos_archivos = obtener_archivos_desde_ruta(ruta)
        cola_total.extend(nuevos_archivos)
        
        print(f"\nTotal de archivos en cola para analizar: {len(cola_total)}")
        
        continuar = input("¿Deseas agregar otra ruta? (s/n): ").lower().strip()
        if continuar != 's':
            break
    return cola_total

def analizar_con_gpt(cliente, nombre_archivo, contenido):
    print(f"\n---> Analizando: '{nombre_archivo}' (Espere un momento...)")
    logging.info(f"Enviando a OpenAI: {nombre_archivo}")
    
    instrucciones = """
    Eres un ingeniero de software experto y consultor de alto nivel con un profundo conocimiento en Python y Powershell, en tareas de ciberseguridad defensiva (Blue Team), de Análisis Forense/DFIR. y optimización de rendimiento.
    Tu tarea es analizar el código y los logs proporcionados a continuación, y ofrecer un informe detallado.
    El análisis debe abarcar tres secciones principales:
    1. Análisis y explicación del código (si aplica)
    Describe la función principal del código y el flujo lógico general.
    Identifica los componentes clave, clases, o funciones.
    2. Retroalimentación y sugerencias de mejora.
    Proporciona sugerencias de refactorización para mejorar la legibilidad y mantenibilidad.
    Identifica posibles bugs o fallos de seguridad.
    Asegura que el código sigue las mejores prácticas.
    3. Interpretación de Logs (si aplica)
    Analiza logs si están incluidos e identifica errores o advertencias.
    """

    try:
        response = cliente.chat.completions.create(
            model="gpt-5", #Aquí se peude cambiar al modelo que uno más quiera usar, en nuestro caso decidimos irnos por GPT-5.
            messages=[
                {"role": "system", "content": instrucciones},
                {"role": "user", "content": f"Archivo: {nombre_archivo}\n\nContenido:\n{contenido}"}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        msg = f"Error critico al conectar con OpenAI para {nombre_archivo}: {e}"
        logging.critical(msg)
        return msg

def guardar_y_mostrar_resultado(nombre_origen, analisis):
    print("\n" + "░"*40)
    print(f"REPORTE IA: {nombre_origen}")
    print("░"*40 + "\n")
    print(analisis[:600] + "\n\n... [El reporte completo continúa en el archivo de texto] ...") 
    
    # La carpeta ya está definida y creada al inicio como constante global
    nombre_safe = nombre_origen.replace(os.sep, "_").replace("/", "_").replace("\\", "_")
    timestamp = datetime.now().strftime("%H%M%S")
    nombre_reporte = f"IA_{nombre_safe}_{timestamp}.txt"
    ruta_reporte = os.path.join(CARPETA_DESTINO, nombre_reporte)

    try:
        with open(ruta_reporte, "w", encoding='utf-8') as f:
            f.write(f"ANÁLISIS DE: {nombre_origen}\nFECHA: {datetime.now()}\n\n")
            f.write(analisis)
        print(f"\nReporte guardado exitosamente en: {ruta_reporte}")
        logging.info(f"Reporte guardado correctamente: {ruta_reporte}")
    except Exception as e:
        msg = f"Error al guardar reporte {nombre_reporte}: {e}"
        print(msg)
        logging.error(msg)

def main():
    try:
        logging.info("Iniciando sesion de analisis AI")
        api_key = gestionar_api_key()
        cliente = OpenAI(api_key=api_key)
        
        archivos_a_procesar = gestionar_cola_analisis()
        
        if not archivos_a_procesar:
            print("\nNo hay archivos en la cola. Finalizando.")
            logging.info("Sesion finalizada sin archivos procesados.")
            return

        print(f"\n--- INICIANDO ANÁLISIS DE {len(archivos_a_procesar)} ARCHIVOS ---\n")
        logging.info(f"Comenzando procesamiento por lotes de {len(archivos_a_procesar)} archivos.")
        
        for i, (nombre, contenido) in enumerate(archivos_a_procesar, 1):
            print(f"Procesando {i}/{len(archivos_a_procesar)}...")
            resultado = analizar_con_gpt(cliente, nombre, contenido)
            guardar_y_mostrar_resultado(nombre, resultado)
            
        print("\n--- Todos los análisis han finalizado ---")
        logging.info("Sesion de analisis finalizada con exito")
        
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
        logging.warning("Operacion cancelada manualmente por el usuario.")
    except Exception as e:
        print(f"\nError inesperado en main: {e}")
        logging.critical(f"Error no controlado en main: {e}")

if __name__ == "__main__":
    main()
