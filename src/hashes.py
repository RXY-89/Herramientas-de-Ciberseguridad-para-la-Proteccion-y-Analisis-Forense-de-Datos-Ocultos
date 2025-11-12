import subprocess,os,json
from pathlib import Path
from datetime import datetime,timezone
try:
    from loguru import logger
except ImportError:
    print("El modulo 'loguru' no se encuentra instalado. Por favor, instálelo e intente de nuevo.")
    exit(1)

ruta_carpeta=Path(__file__).parent
ruta_script=ruta_carpeta  / "sacar_hashes.ps1"
ruta_hashes=ruta_carpeta / "hashes"
ruta_hashes.mkdir(parents=True, exist_ok=True)
ruta_logging=ruta_carpeta / "run.log"
fecha=datetime.now().strftime("%Y%m%d_%H%M%S")

logger.remove()
logger.add(ruta_logging, format="{time} - {level} - {extra[run_id]} - {extra[event]} - {extra[details]}", level="INFO")      
log = logger.bind(run_id=f"RUN_{fecha}",)

try:
    from keyboard import read_key
except ImportError:
    log.critical("", event="import_error", details="El modulo 'keyboard' no se encuentra instalado.")
    print("El módulo 'keyboard' no se encuentra instalado. Por favor, instálelo e intente de nuevo.")
    exit(1)

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def ejecutar_powershell(ruta, guardar="False", archivo="None"):
    log.debug("", event="ejecutar_powershell",details=f"Ejecutando PowerShell con ruta: {ruta}, guardar: {guardar}, archivo: {archivo}")
    resultado = subprocess.run(
        ["powershell", "-File", ruta_script, "-ruta", ruta, "-guardar", guardar, "-archivo", archivo],
        capture_output=True,
        text=True
        )
    if resultado.returncode==0:
        return resultado.stdout.strip()
    else:
        raise RuntimeError(resultado.stderr)
    
def checar_hashes_carpeta(ruta):
        
    nombre=ruta.name.replace(".","_")
    lista_hashes=ruta_hashes / f"hashes_{nombre}.json"

    if lista_hashes.exists():
        log.info("", event="existing_hashes",details="Existe registro previo de hashes, verificando...")
        try:
            hashes_actuales=json.loads(ejecutar_powershell(ruta))
        except RuntimeError as e:
            log.critical("", event="powershell_error",details=f"Error al ejecutar PowerShell:\n{e}")
            return
        except Exception as e:
            log.critical("", event="powershell_error",details=f"Error inesperado al intentar ejecutar PowerShell: {e}")
            return
    else:
        log.info("", event="no_existing_hashes",details="No existe registro previo de hashes, creando...")
        print("No se encontró un registro previo de hashes. Creando uno nuevo...")
        try:
            ejecutar_powershell(ruta, guardar="True", archivo=lista_hashes)
            log.info("", event="hashes_created",details="Hashes creados y guardados exitosamente, terminando ejecución.")
            print("Los hashes han sido creados y guardados exitosamente.")
        except RuntimeError as e:
            log.critical("", event="powershell_error",details=f"Error al ejecutar PowerShell:\n{e}")
        except Exception as e:
            log.critical("", event="powershell_error",details=f"Error inesperado al intentar ejecutar PowerShell: {e}")
        return
    
    log.info("", event="comparing_hashes",details="Comparando hashes actuales con los almacenados...")
    documentacion=[]
    cambios=False
    with lista_hashes.open("r", encoding="utf-8") as f:
        hashes_antiguos=json.load(f)
        for archivo in ruta.iterdir():
            if archivo.is_file():
                if hashes_antiguos[str(archivo.name)] is None:
                    documentacion.append(f"El archivo {archivo.name} es nuevo.")
                    cambios=True
                    log.debug("", event="new_file_detected",details=f"El archivo {archivo.name} es nuevo.")
                elif hashes_actuales[str(archivo.name)] != hashes_antiguos[str(Path(archivo).name)]:
                    documentacion.append(f"El archivo {archivo.name} ha sido modificado.")
                    cambios=True
                    log.debug("", event="file_modified",details=f"El archivo {archivo.name} ha sido modificado.")
        for archivo in hashes_antiguos:
            ruta_archivo=ruta /archivo
            if not ruta_archivo.exists():
                documentacion.append(f"El archivo {archivo} ha sido eliminado.")
                cambios=True
                log.debug("", event="file_deleted",details=f"El archivo {archivo} ha sido eliminado.")
    
    if cambios:
        
        reporte=ruta_carpeta / f"cambios_{nombre}_{fecha}.txt"
        with reporte.open("w") as archivo:
            archivo.write("\n".join(documentacion))
        log.debug("", event="changes_reported",details=f"Se creo el reporte de cambios en {reporte}")
        log.info("", event="changes_detected",details="Cambios detectados, preguntando al usuario si desea actualizar...")
        
        while True:
            print(f"Se han detectado cambios. Revise {reporte.name} para más información.")
            print("¿Desea actualizar los hashes almacenados? (s/n)")
            respuesta=read_key()
            if respuesta in ("s","n"):
                break
            limpiar()
        
        if respuesta=="s":
            with lista_hashes.open("w", encoding="utf-8") as f:
                json.dump(hashes_actuales, f, indent=2)
            log.info("", event="hashes_updated",details="Hashes actualizados.")
        else:
            log.info("", event="hashes_not_updated",details="El usuario decidió no actualizar los hashes.")
    else: 
        log.info("", event="no_changes_detected",details="Cambios no detectados, notificando al usuario.")
        print("No se detectaron cambios.")

def checar_hashes_archivos(ruta):

    lista_hashes=ruta_hashes / "lista_hashes.json"
    if not lista_hashes.exists():
        with lista_hashes.open("w", encoding="utf-8") as f:
            json.dump({}, f)
    with lista_hashes.open("r", encoding="utf-8") as f:
        hashes_antiguos=json.load(f)
    if str(ruta) in hashes_antiguos:
        log.info("", event="existing_hash",details="Existe registro previo del hash, verificando...")
        try:
            hashes_actuales=ejecutar_powershell(ruta)
        except RuntimeError as e:
            log.critical("", event="powershell_error",details=f"Error al ejecutar PowerShell:\n{e}")
            return
        except Exception as e:
            log.critical("", event="powershell_error",details=f"Error inesperado al intentar ejecutar PowerShell: {e}")
            return
    else:
        log.info("", event="no_existing_hash",details="No existe registro previo del hash, creando...")
        print("No se encontró un registro previo del hashe. Creando uno nuevo...")
        try:
            ejecutar_powershell(ruta, guardar="True", archivo=lista_hashes)
            log.info("", event="hash_created",details="Hash creado y guardado exitosamente, terminando ejecución.")
            print("Los hashes han sido creados y guardados exitosamente.")
        except RuntimeError as e:
            log.critical("", event="powershell_error",details=f"Error al ejecutar PowerShell:\n{e}")
        except Exception as e:
            log.critical("", event="powershell_error",details=f"Error inesperado al intentar ejecutar PowerShell: {e}")
        return
    
    if hashes_actuales == hashes_antiguos[str(ruta)]:
        log.debug("", event="file_not_modified",details=f"El archivo no ha sufrido cambios.")
        print("No se detectaron cambios.")
    else:
        log.debug("", event="file_modified",details=f"El archivo ha sufrido modificaciones.")
        fecha=datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte=ruta_carpeta / f"cambios_hash_{fecha}.txt"
        with reporte.open("w") as archivo:
            archivo.write(f"El archivo {ruta.name} ha sido modificado.")
        
        log.debug("", event="changes_reported",details=f"Se ha reportado el cambio en {reporte}")
        log.info("", event="changes_detected",details="Cambios detectados, preguntando al usuario si desea actualizar...")
 
        while True:
            print(f"Se han detectado cambios. Revise {reporte.name} para más información.")
            print("¿Desea actualizar los hashes almacenados? (s/n)")
            respuesta=read_key()
            if respuesta in ("s","n"):
                break
            limpiar()
        if respuesta=="s":
            hashes_antiguos[str(ruta)]=hashes_actuales
            with lista_hashes.open("w", encoding="utf-8") as f:
                json.dump(hashes_antiguos, f, indent=2)
            log.info("", event="hash_updated",details="Hash actualizado.")
        else:
            log.info("", event="hash_not_updated",details="El usuario decidió no actualizar el hash.")

def carpeta_sin_archivos(ruta) -> bool:
    p = Path(ruta)

    for item in p.iterdir():
        if item.is_file():
            return False 
    return True

log.info("", event="startup",details="Script iniciado correctamente, procediendo a solicitar ruta al usuario...")
ruta=Path(input("Introduzca la ruta al archivo o directorio a verificar: ").strip())
log.debug("", event="input_ruta",details=f"Ruta proporcionada por el usuario: {ruta}")
if ruta.exists():
    if ruta.is_dir():
        if carpeta_sin_archivos(ruta):
            log.warning("", event="empty_directory",details="La ruta es un directorio, pero no contiene archivos para verificar.")
        else:
            log.info("", event="check_path",details="La ruta es un directorio, procediendo a checar hashes de carpeta...")
            checar_hashes_carpeta(ruta)
        
    else:
        log.info("", event="check_path",details="la ruta es un archivo, procediendo a checar hashes de archivo...")
        checar_hashes_archivos(ruta)
else:
    log.error("", event="invalid_path",details="La ruta proporcionada no existe.")
    print("La ruta proporcionada no existe.")
