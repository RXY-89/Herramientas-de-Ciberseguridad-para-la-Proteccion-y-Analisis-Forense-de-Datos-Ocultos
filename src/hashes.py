import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    print("El modulo 'loguru' no se encuentra instalado.")
    sys.exit(1)

# --- CONFIGURACIÓN DE RUTAS ---
ruta_carpeta = Path(__file__).parent.resolve()
ruta_script = ruta_carpeta / "sacar_hashes.ps1"
ruta_hashes = ruta_carpeta / "hashes"
ruta_hashes.mkdir(parents=True, exist_ok=True)
ruta_logging = ruta_carpeta / "run.log"
fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

# --- CONFIGURACIÓN DE LOGS ---
logger.remove()
logger.add(ruta_logging, format="{time} - {level} - {extra[run_id]} - {extra[event]} - {extra[details]}", level="INFO")      
log = logger.bind(run_id=f"RUN_{fecha}")

def ejecutar_powershell(ruta: Path, guardar="False", archivo="None"):
    """
    Ejecuta el script de PowerShell asegurando codificación UTF-8 y manejo de errores.
    """
    ruta_absoluta = str(ruta.resolve())
    archivo_str = str(archivo) if archivo != "None" else "None"
    
    log.debug("", event="executing_PowerShell", details=f"Ruta: {ruta_absoluta}, Guardar: {guardar}")

    # -ExecutionPolicy Bypass es vital para evitar bloqueos de permisos en Windows
    cmd = [
        "powershell", 
        "-ExecutionPolicy", "Bypass",
        "-File", str(ruta_script), 
        "-ruta", ruta_absoluta, 
        "-guardar", guardar, 
        "-archivo", archivo_str
    ]

    resultado = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

    if resultado.returncode == 0:
        return resultado.stdout.strip()
    else:
        raise RuntimeError(f"Error PowerShell: {resultado.stderr}")

def checar_hashes_carpeta(ruta: Path):
    nombre = ruta.name.replace(".", "_")
    archivo_hashes_guardado = ruta_hashes / f"hashes_{nombre}.json"
    
    try:
        json_actual_str = ejecutar_powershell(ruta, guardar="False")
        if not json_actual_str: 
            hashes_actuales = {}
        else:
            hashes_actuales = json.loads(json_actual_str)
    except Exception as e:
        log.critical("", event="error_fetching_current", details=f"No se pudieron obtener hashes actuales: {e}")
        return

    if not archivo_hashes_guardado.exists():
        log.info("", event="first_run", details="No hay registro previo. Creando base de datos inicial.")
        print("Creando registro inicial de hashes...")
        try:
            with archivo_hashes_guardado.open("w", encoding="utf-8") as f:
                json.dump(hashes_actuales, f, indent=2)
            log.info("", event="hashes_created", details="Registro creado exitosamente.")
            print("Registro creado correctamente.")
            return
        except Exception as e:
            log.critical("", event="save_error", details=f"Error guardando JSON: {e}")
            return

    try:
        with archivo_hashes_guardado.open("r", encoding="utf-8") as f:
            hashes_antiguos = json.load(f)
    except Exception as e:
        log.critical("", event="read_error", details=f"El archivo JSON antiguo está corrupto: {e}")
        return

    set_actuales = set(hashes_actuales.keys())
    set_antiguos = set(hashes_antiguos.keys())

    archivos_nuevos = set_actuales - set_antiguos
    archivos_eliminados = set_antiguos - set_actuales
    archivos_comunes = set_actuales & set_antiguos
    
    documentacion = []
    hay_cambios = False

#Esto es para detectar los archivos nuevos.
    for f in archivos_nuevos:
        msg = f"El archivo {f} es nuevo."
        documentacion.append(msg)
        log.debug("", event="new_file", details=msg)
        hay_cambios = True

    #Esto es para detectar los archivos eliminado.s
    for f in archivos_eliminados:
        msg = f"El archivo {f} ha sido eliminado."
        documentacion.append(msg)
        log.debug("", event="file_deleted", details=msg)
        hay_cambios = True

    #Esto es para detectar los archivos modificados.
    for f in archivos_comunes:
        if hashes_actuales[f] != hashes_antiguos[f]:
            msg = f"El archivo {f} ha sido modificado."
            documentacion.append(msg)
            log.debug("", event="file_modified", details=msg)
            hay_cambios = True

    #esto es para los reportes
    if hay_cambios:
        reporte = ruta_carpeta / f"cambios_{nombre}_{fecha}.txt"
        with reporte.open("w", encoding="utf-8") as f:
            f.write("\n".join(documentacion))
        
        log.info("", event="changes_detected", details=f"Cambios encontrados. Reporte: {reporte.name}")
        print(f"\n¡ATENCIÓN! Se han detectado cambios.")
        print(f"Detalles guardados en: {reporte.name}")
        
        while True:
            respuesta = input("¿Desea actualizar la base de datos de hashes? [S/n]: ").strip().lower()
            if respuesta in ["s", "n", ""]:
                break
        
        if respuesta == "s" or respuesta == "":
            with archivo_hashes_guardado.open("w", encoding="utf-8") as f:
                json.dump(hashes_actuales, f, indent=2)
            log.info("", event="db_updated", details="Base de datos de hashes actualizada.")
            print("Base de datos actualizada.")
        else:
            print("No se realizaron cambios en la base de datos.")
    else:
        log.info("", event="no_changes", details="Verificación completada sin cambios.")
        print("No se detectaron cambios en los archivos.")

def checar_hashes_archivos(ruta: Path):
    lista_hashes = ruta_hashes / "lista_hashes.json"
    if not lista_hashes.exists():
        with lista_hashes.open("w", encoding="utf-8") as f:
            json.dump({}, f)

    # Obtiene el hash actual
    try:
        hash_actual = ejecutar_powershell(ruta, guardar="False")
    except RuntimeError as e:
        print(f"Error obteniendo hash: {e}")
        return

    with lista_hashes.open("r", encoding="utf-8") as f:
        registro_completo = json.load(f)

    ruta_key = str(ruta.resolve())
    
    if ruta_key not in registro_completo:
        log.info("", event="new_file_tracking", details="Archivo no rastreado previamente.")
        print("Este archivo no estaba en el registro. Agregándolo...")
        registro_completo[ruta_key] = hash_actual
        with lista_hashes.open("w", encoding="utf-8") as f:
            json.dump(registro_completo, f, indent=2)
        print("Archivo agregado y hash guardado.")
        return

    hash_antiguo = registro_completo[ruta_key]

    if hash_actual != hash_antiguo:
        log.warning("", event="file_modified", details=f"El archivo {ruta.name} cambió.")
        print(f"¡ALERTA! El archivo ha sido MODIFICADO.")
        
        reporte = ruta_carpeta / f"cambios_archivo_{fecha}.txt"
        with reporte.open("w", encoding="utf-8") as f:
            f.write(f"El archivo {ruta.name} ha sido modificado.\nHash Anterior: {hash_antiguo}\nHash Nuevo: {hash_actual}")
        
        resp = input("¿Desea actualizar el registro? [S/n]: ").strip().lower()
        if resp == "s" or resp == "":
            registro_completo[ruta_key] = hash_actual
            with lista_hashes.open("w", encoding="utf-8") as f:
                json.dump(registro_completo, f, indent=2)
            print("Registro actualizado.")
    else:
        print("El archivo está íntegro (No ha cambiado).")

def carpeta_sin_archivos(ruta: Path) -> bool:
    # Esto verifica si hay al menos un archivo
    for item in ruta.iterdir():
        if item.is_file():
            return False 
    return True

if __name__ == "__main__":
    log.info("", event="startup", details="Script iniciado.")
    entrada = input("Introduzca la ruta al archivo o directorio a verificar: ").strip().strip('"')
    
    if not entrada:
        print("Ruta vacía.")
        sys.exit(1)

    ruta_obj = Path(entrada)
    
    if not ruta_obj.exists():
        log.error("", event="invalid_path", details="Ruta no existe.")
        print("La ruta proporcionada no existe.")
    else:
        if ruta_obj.is_dir():
            if carpeta_sin_archivos(ruta_obj):
                print("El directorio está vacío (no hay archivos para hashear).")
            else:
                checar_hashes_carpeta(ruta_obj)
        else:
            checar_hashes_archivos(ruta_obj)
