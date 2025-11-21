from PyPDF2 import PdfReader
from PIL import Image
import csv
try:
    from loguru import logger
except ImportError:
    print("El modulo 'loguru' no se encuentra instalado. Por favor, instálelo e intente de nuevo.")
    exit(1)

ruta_logging=Path(__file__).parent / "run.log"
fecha=datetime.now().strftime("%Y%m%d_%H%M%S")
logger.remove()
logger.add(ruta_logging, format="{time} - {level} - {extra[run_id]} - {extra[event]} - {extra[details]}", level="INFO")      
log = logger.bind(run_id=f"RUN_{fecha}",)

try:
    from docx import Document
    from pathlib import Path
    from datetime import datetime,timezone
    from mutagen import File
    import piexif
except ImportError as e:
    log.critical("", event="Import_Error", details=f"Una de las librerias necesarias no existe {e}")
    print(f"Uno de las librerias no existe: {e}")
    exit(1)




ruta_carpeta=Path(__file__).parent / "metadatos"
ruta_carpeta.mkdir(parents=True, exist_ok=True)
ruta_archivos=ruta_carpeta / "archivos.txt"
rutas_reportes=[ruta_carpeta / "docx.csv",
              ruta_carpeta / "pdf.csv",
              ruta_carpeta / "img.csv",
              ruta_carpeta / "aud.csv"]
encabezados=[["Archivo","Fecha analisis","Autor","Ultimo modificado por","Creado","Modificado","Identificador","Version","Ultimo imprimido","Revision","Comentarios","Categoria","Lenguaje","Estado","Clave","Sujeto","Titulo"],
             ["Archivo","Fecha analisis","Autor","Creado","Modificado","Titulo","Productor","Creador","Sujeto","XMP"],
             ["Archivo","Fecha analisis","Fabricante","Modelo","Software","Fecha captura","ISO","Exposicion","Apertura","GPS latitud","GPS longitud","GPS altitud"],
             ["Archivo","Fecha analisis","Album","Artista principal","Artista acompanamiento","Copyright","Parte conjunto","Genero","Titulo","Numero pista","Fecha grabacion","Duracion segundos"]]



for tipo in [0,1,2,3]:
    if not rutas_reportes[tipo].exists():
        log.info("", event="creating_CSV", details=f"Creando el archivo {rutas_reportes[tipo].name}")
        with rutas_reportes[tipo].open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=encabezados[tipo])
            writer.writeheader()

def guardar_csv(ruta: Path, encabezado: list, metadatos: list):
    with ruta.open("a",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=encabezado)
        for metadato in metadatos:
            writer.writerow(metadato)

def convertir_bytes(valor):
    if isinstance(valor, bytes):
        return valor.decode("utf-8", errors="ignore")
    return valor

def convertir_fecha(valor):
    if isinstance(valor, bytes):
        valor=valor.decode("utf-8", errors="ignore")
    try:
        fecha_dt=datetime.strptime(valor, "%Y:%m:%d %H:%M:%S")
        return fecha_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return valor

def convertir_gps(coord, ref):
    if not coord or not ref:
        return "N/A"
    grados=coord[0][0] / coord[0][1]
    minutos=coord[1][0] / coord[1][1]
    segundos=coord[2][0] / coord[2][1]
    decimal=grados+(minutos / 60.0)+(segundos / 3600.0)
    if ref in [b"S", b"W", "S", "W"]:
        decimal=-decimal
    return decimal

def metadata_exif(ruta: Path) -> dict:
    img=Image.open(ruta)
    exif_bytes = img.info.get("exif")
    if not exif_bytes:
        log.error("", event="not_metadata_found", details=f"No se encontro metadata del archivo {ruta.name}")
        return None
    exif_dict = piexif.load(exif_bytes)

    return {
        "Archivo": ruta.name,
        "Fecha analisis": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "Fabricante": convertir_bytes(exif_dict["0th"].get(piexif.ImageIFD.Make)) if exif_dict["0th"].get(piexif.ImageIFD.Make) else "N/A",
        "Modelo": convertir_bytes(exif_dict["0th"].get(piexif.ImageIFD.Model)) if exif_dict["0th"].get(piexif.ImageIFD.Model) else "N/A",
        "Software": convertir_bytes(exif_dict["0th"].get(piexif.ImageIFD.Software)) if exif_dict["0th"].get(piexif.ImageIFD.Software) else "N/A",
        "Fecha captura": convertir_fecha(exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal)) if exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal) else "N/A",
        "ISO": exif_dict["Exif"].get(piexif.ExifIFD.ISOSpeedRatings) if exif_dict["Exif"].get(piexif.ExifIFD.ISOSpeedRatings) else "N/A",
        "Exposicion": exif_dict["Exif"].get(piexif.ExifIFD.ExposureTime) if exif_dict["Exif"].get(piexif.ExifIFD.ExposureTime) else"N/A",
        "Apertura": exif_dict["Exif"].get(piexif.ExifIFD.FNumber) if exif_dict["Exif"].get(piexif.ExifIFD.FNumber) else "N/A",
        "GPS latitud": convertir_gps(
            exif_dict["GPS"].get(piexif.GPSIFD.GPSLatitude),
            exif_dict["GPS"].get(piexif.GPSIFD.GPSLatitudeRef)
        ),
        "GPS longitud": convertir_gps(
            exif_dict["GPS"].get(piexif.GPSIFD.GPSLongitude),
            exif_dict["GPS"].get(piexif.GPSIFD.GPSLongitudeRef)
        ),
        "GPS altitud": exif_dict["GPS"].get(piexif.GPSIFD.GPSAltitude) if exif_dict["GPS"].get(piexif.GPSIFD.GPSAltitude) else "N/A",
    }

def metadata_docx(ruta: Path) -> dict:
    doc=Document(ruta)
    data=doc.core_properties
    if not data:
        log.error("", event="not_metadata_found", details=f"No se encontro metadata del archivo {ruta.name}")
        return None
    return {
        "Archivo": ruta.name,
        "Fecha analisis": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "Autor": data.author if data.author else "N/A",
        "Ultimo modificado por": data.last_modified_by if data.last_modified_by else "N/A",
        "Creado": data.created.strftime("%Y-%m-%d %H:%M:%S %Z") if data.created else "N/A",
        "Modificado": data.modified.strftime("%Y-%m-%d %H:%M:%S %Z") if data.modified else "N/A",
        "Identificador": data.identifier if data.identifier else "N/A",
        "Version": data.version if data.version else "N/A",
        "Ultimo imprimido": data.last_printed.strftime("%Y-%m-%d %H:%M:%S %Z") if data.last_printed else "N/A",
        "Revision": data.revision if data.revision else "N/A",
        "Comentarios": data.comments if data.comments else "N/A",
        "Categoria": data.category if data.category else "N/A",
        "Lenguaje": data.language if data.language else "N/A",
        "Estado": data.content_status if data.content_status else "N/A",
        "Clave": data.keywords if data.keywords else "N/A",
        "Sujeto": data.subject if data.subject else "N/A",
        "Titulo": data.title if data.title else "N/A"
    }

def metadata_pdf(ruta: Path) -> dict:
    pdf=PdfReader(ruta)
    data=pdf.metadata
    if not data:
        print(f"No se encontro metadata del archivo {ruta.name}")
        return None
    return {
        "Archivo": ruta.name,
        "Fecha analisis": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "Autor": data.author if data.author else "N/A",
        "Creado": data.creation_date.strftime("%Y-%m-%d %H:%M:%S %Z") if data.creation_date else "N/A",
        "Modificado": data.modification_date.strftime("%Y-%m-%d %H:%M:%S %Z") if data.modification_date else "N/A",
        "Titulo": data.title if data.title else "N/A",
        "Productor": data.producer if data.producer else "N/A",
        "Creador": data.creator if data.creator else "N/A",
        "Sujeto": data.subject if data.subject else "N/A",
        "XMP": data.xmp_metadata if data.xmp_metadata else "N/A"
    }

def metadata_audio(ruta: Path) -> dict:
    audio = File(ruta)
    if audio is None or not audio.tags:
        log.error("", event="not_metadata_found", details=f"No se encontro metadata del archivo {ruta.name}")
        return None

    return {
        "Archivo": ruta.name,
        "Fecha analisis": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "Album": str(audio.tags.get("TALB")) if audio.tags.get("TALB") else "N/A",
        "Artista principal": str(audio.tags.get("TPE1")) if audio.tags.get("TPE1") else "N/A",
        "Artista acompanamiento": str(audio.tags.get("TPE2")) if audio.tags.get("TPE2") else "N/A",
        "Copyright": str(audio.tags.get("TCOP"))if audio.tags.get("TCOP") else "N/A",
        "Parte conjunto": str(audio.tags.get("TPOS")) if audio.tags.get("TPOS") else "N/A",
        "Genero": str(audio.tags.get("TCON")) if audio.tags.get("TCON") else "N/A",
        "Titulo": str(audio.tags.get("TIT2")) if audio.tags.get("TIT2") else "N/A",
        "Numero pista": str(audio.tags.get("TRCK")) if audio.tags.get("TRCK") else "N/A",
        "Fecha grabacion": str(audio.tags.get("TDRC")) if audio.tags.get("TDRC") else "N/A",
        "Duracion segundos": int(audio.info.length) if audio.info else "N/A"
    }

def checar_vacio(diccionario: dict) -> bool:
    for clave in diccionario:
        if clave in ["Archivo","Fecha analisis"]:
            continue
        elif diccionario[clave]!="N/A":
            return True
    return False

def checar_metadata(lista: list):
    print(lista)
    metadatos=[[],[],[],[]]
    vacio=0
    for ruta in lista:
        log.info("", event="checking_file", details=f"Checando la metadata de {ruta.name}")
        if not ruta.exists():
            log.info("", event="file_not_exists", details=f"El archivo {ruta.name} no existe")
            print(f"No existe tal archivo en {ruta}")
        elif ruta.suffix==".docx":
            dato=metadata_docx(ruta)
            if checar_vacio(dato):
                metadatos[0].append(dato)
        elif ruta.suffix==".pdf":
            dato=metadata_pdf(ruta)
            if checar_vacio(dato):
                metadatos[1].append(dato)
        elif ruta.suffix in [".jpg",".jpeg",".tif","tiff",".heif","heic"]:
            dato=metadata_exif(ruta)
            if checar_vacio(dato):
                metadatos[2].append(dato)
        elif ruta.suffix in [".mp3",".mp4",".m4a",".m4b",".flac",".ogg",".opus",".mpc",".ape",".wc",".wav",".aiff",".aif",".aac"]:
            dato=metadata_audio(ruta)
            if checar_vacio(dato):
                metadatos[3].append(dato)
        else:
            log.info("", event="incompatible_file", details=f"El script no saca metadatos de archivo {ruta.suffix}")
    for tipo in [0,1,2,3]:
        if len(metadatos[tipo])>0:
            log.info("", event="saving_CSV", details=f"Guardando los metadatos correspondientes en {rutas_reportes[tipo].name}")
            guardar_csv(rutas_reportes[tipo],encabezados[tipo],metadatos[tipo])
        else:
            log.info("", event="nothing_to_save", details=f"No hay metadata para guardar en {rutas_reportes[tipo].name}")
            vacios+=1
    if vacios==4:
        log.error("", event="no_metadata_to_save", details="No se encontro metadata en los archivos proporcionados")
        print("No se encontro metadata en los archivos proporcionados")

def leer_parrafos(ruta: Path) -> list:
    rutas=[]
    with ruta.open(encoding="utf-8") as f:
        for parrafo in f:
            rutas.append(parrafo.strip())
    return rutas

if __name__=="__main__":
    log.info("", event="startup", details="Script iniciado correctamente, procediendo a buscar los archivos...")
    if not ruta_archivos.exists:
        log.error("", event="file_not_found", details="No existe el archivo de texto con los archivos")
        print(f"No existe la lista en archivos en {ruta_archivos}, por favor hágala")
        exit(1)
    archivos=[]
    for archivo in leer_parrafos(ruta_archivos):
        archivos.append(Path(archivo))

    if len(archivos)>0:
        log.info("", event="checking_metadata", details="Iniciando a ver la metadata de los archivos...")
        checar_metadata(archivos)
    else:
        log.error("", event="empty_file", details="El archivo de texto con los archivos a analizar esta vacío")
        print("El archivo de texto esta vacio")
        exit(1)    
