import subprocess,os,logging,json
from pathlib import Path
from datetime import datetime
try:
    from keyboard import read_key
except ImportError:
    logging.critical("El módulo 'keyboard no se encuentra instalado.")
    print("El módulo 'keyboard' no se encuentra instalado. Por favor, instálelo e intente de nuevo.")
    exit(1)

ruta_carpeta=Path(__file__).parent
ruta_script=ruta_carpeta  / "sacar_hashes.ps1"
ruta_hashes=ruta_carpeta / "hashes"
ruta_hashes.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=ruta_carpeta / "registro_hashes.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def ejecutar_powershell(ruta, guardar="False", archivo="None"):
    logging.debug(f"Ejecutando PowerShell con ruta: {ruta}, guardar: {guardar}, archivo: {archivo}")
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
        logging.info("Existe registro previo de hashes, verificando...")
        try:
            hashes_actuales=json.loads(ejecutar_powershell(ruta))
        except RuntimeError as e:
            logging.error(f"Error al ejecutar PowerShell:\n{e}")
            return
        except Exception as e:
            logging.error(f"Error inesperado al intentar ejecutar PowerShell: {e}")
            return
    else:
        logging.info("No existe registro previo de hashes, creando...")
        try:
            ejecutar_powershell(ruta, guardar="True", archivo=lista_hashes)
            logging.info("Hashes creados")
        except RuntimeError as e:
            logging.error(f"Error al ejecutar PowerShell:\n{e}")
        except Exception as e:
            logging.error(f"Error inesperado al intentar ejecutar PowerShell: {e}")
        return
    
    documentacion=[]
    cambios=False
    with lista_hashes.open("r", encoding="utf-8") as f:
        hashes_antiguos=json.load(f)
        for archivo in ruta.iterdir():
            if archivo.is_file():
                if hashes_antiguos[str(archivo.name)] is None:
                    documentacion.append(f"El archivo {archivo.name} es nuevo.")
                    cambios=True
                    logging.info(f"El archivo {archivo.name} es nuevo.")
                elif hashes_actuales[str(archivo.name)] != hashes_antiguos[str(Path(archivo).name)]:
                    documentacion.append(f"El archivo {archivo.name} ha sido modificado.")
                    cambios=True
                    logging.info(f"El archivo {archivo.name} ha sido modificado.")
        for archivo in hashes_antiguos:
            ruta_archivo=ruta /archivo
            if not ruta_archivo.exists():
                documentacion.append(f"El archivo {archivo} ha sido eliminado.")
                cambios=True
                logging.info(f"El archivo {archivo} ha sido eliminado.")
    
    if cambios:
        fecha=datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte=ruta_carpeta / f"cambios_{nombre}_{fecha}.txt"
        with reporte.open("w") as archivo:
            archivo.write("\n".join(documentacion))
        logging.debug(f"Se creo el reporte de cambios en {reporte}")
        logging.info("Cambios detectados, preguntando al usuario si desea actualizar...")

        
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
            logging.info("Hashes actualizados.")
        else:
            logging.info("El usuario decidió no actualizar los hashes.")
    else: 
        logging.info("Cambios no detectados, notificando al usuario.")
        print("No se detectaron cambios.")

def checar_hashes_archivos(ruta):

    lista_hashes=ruta_hashes / "lista_hashes.json"
    if not lista_hashes.exists():
        with lista_hashes.open("w", encoding="utf-8") as f:
            json.dump({}, f)
    with lista_hashes.open("r", encoding="utf-8") as f:
        hashes_antiguos=json.load(f)
    if str(ruta) in hashes_antiguos:
        logging.info("Existe registro previo de hashes, verificando...")
        try:
            hashes_actuales=ejecutar_powershell(ruta)
        except RuntimeError as e:
            logging.error(f"Error al ejecutar PowerShell:\n{e}")
            return
        except Exception as e:
            logging.error(f"Error inesperado al intentar ejecutar PowerShell: {e}")
            return
    else:
        logging.info("No existe registro previo de hashes, creando...")
        try:
            ejecutar_powershell(ruta, guardar="True", archivo=lista_hashes)
            logging.info("Hashes creados")
        except RuntimeError as e:
            logging.error(f"Error al ejecutar PowerShell:\n{e}")
        except Exception as e:
            logging.error(f"Error inesperado al intentar ejecutar PowerShell: {e}")
        return
    
    if hashes_actuales == hashes_antiguos[str(ruta)]:
        logging.info("El archivo no ha sufrido cambios.")
        print("No se detectaron cambios.")
    else:
        logging.info("El archivo ha sido modificado.")
        fecha=datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte=ruta_carpeta / f"cambios_hash_{fecha}.txt"
        with reporte.open("w") as archivo:
            archivo.write(f"El archivo {ruta.name} ha sido modificado.")
        
        logging.debug(f"Se ha reportado el cambio en {reporte}")
        logging.info("Cambios detectados, preguntando al usuario si desea actualizar...")
 
        while True:
            print(f"Se han detectado cambios. Revise {reporte.name} para más información.")
            print("¿Desea actualizar los hashes almacenados? (s/n)")
            respuesta=read_key()
            if respuesta in ("s","n"):
                break
            limpiar()
        if respuesta=="s":
            hashes_antiguos[str(ruta)]=hashes_actuales
            logging.info("Hash actualizado.")
            with lista_hashes.open("w", encoding="utf-8") as f:
                json.dump(hashes_antiguos, f, indent=2)
            logging.info("Hashes actualizados.")
        else:
            logging.info("El usuario decidió no actualizar los hashes.")



logging.info("Pidiendo ruta al usuario...")
ruta=Path(input("Introduzca la ruta al archivo o directorio a verificar: ").strip())
logging.debug(f"Ruta proporcionada: {ruta}")
if ruta.exists():
    if ruta.is_dir():
        checar_hashes_carpeta(ruta)
    else:
        checar_hashes_archivos(ruta)
else:
    logging.error("La ruta proporcionada no existe.")
    print("La ruta proporcionada no existe.")