import sys
import os
import wave
import struct
import json
import logging
import time
from PIL import Image

#esto confirma si se tienen las librerías que se necesitan.
try:
    import piexif 
except ImportError:
    print("ERROR: Necesitas 'piexif'. Ejecuta: pip install piexif")
    sys.exit()

try:
    from pypdf import PdfReader, PdfWriter 
except ImportError:
    print("ERROR: Necesitas 'pypdf'. Ejecuta: pip install pypdf")
    sys.exit()

# Directorio base
BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

# Carpeta donde se va a guardar todo
OUTPUT_DIR = os.path.join(BASE_DIR, "estega_salidas")

LOG_FILE_PATH = os.path.join(OUTPUT_DIR, "app_log.jsonl")
RESULTADOS_PATH = os.path.join(OUTPUT_DIR, "mensajes.jsonl")

os.makedirs(OUTPUT_DIR, exist_ok=True)

#esto será para el logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, 'props'):
            log_record["properties"] = record.props
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger():
    logger = logging.getLogger("StegaApp")
    logger.setLevel(logging.DEBUG)
    if logger.hasHandlers():
        logger.handlers.clear()
    file_handler = logging.FileHandler(LOG_FILE_PATH, mode='a', encoding='utf-8')
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()

def registrar_hallazgo(mensaje, ruta_archivo_origen):
    try:
        data = {
            "mensaje": mensaje,
            "archivo": ruta_archivo_origen
        }
        # En esto ponemos el 'a' para agregar al final sin borrar lo anterior
        with open(RESULTADOS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
        print(f" [+] Hallazgo guardado en: {RESULTADOS_PATH}")
        logger.info("Hallazgo registrado en JSONL", extra={"props": data})
        
    except Exception as e:
        print(f"Error al guardar hallazgo: {e}")
        logger.error("Error guardando hallazgo", exc_info=True)

#Esto es para IMÁGENES

def ocultar_en_png_pil(img, mensaje, ruta_salida):
    logger.debug("Iniciando ocultar PNG", extra={"props": {"file": ruta_salida}})
    print("Usando método de píxeles (PNG)...")
    
    if len(mensaje) > 255:
        print("Error: Mensaje muy largo para este método (Máx 255).")
        return False
    
    img_rgb = img.convert("RGB")
    r, g, b = img_rgb.getpixel((0, 0))
    img_rgb.putpixel((0, 0), (len(mensaje), g, b))

    for i, char in enumerate(mensaje):
        r, g, b = img_rgb.getpixel((i + 1, 0))
        img_rgb.putpixel((i + 1, 0), (ord(char), g, b))
    
    img_rgb.save(ruta_salida)
    return True

def revelar_de_png_pil(img):
    img_rgb = img.convert("RGB")
    r_len, g, b = img_rgb.getpixel((0, 0))
    longitud = r_len
    if longitud <= 0 or longitud > 255: 
        return None
        
    mensaje = ""
    for i in range(1, longitud + 1):
        try:
            r_char, g, b = img_rgb.getpixel((i, 0))
            mensaje += chr(r_char)
        except:
            return None
    return mensaje

def ocultar_en_metadatos_img(img, mensaje, ruta_salida, extension):
    print("Usando método de metadatos (JPG/WEBP)...")
    mensaje_bytes = f"ASCII\0\0\0{mensaje}".encode("ascii")
    exif_dict = {"Exif": {piexif.ExifIFD.UserComment: mensaje_bytes}}
    exif_bytes = piexif.dump(exif_dict)
    
    if extension == ".webp":
        img.save(ruta_salida, format="WEBP", exif=exif_bytes)
    else:
        img.save(ruta_salida, format="JPEG", exif=exif_bytes)
    return True

def revelar_de_metadatos_img(img):
    try:
        if "exif" not in img.info: return None
        exif_data = piexif.load(img.info["exif"])
        if piexif.ExifIFD.UserComment in exif_data["Exif"]:
            comentario_bytes = exif_data["Exif"][piexif.ExifIFD.UserComment]
            return comentario_bytes[8:].decode("ascii")
    except Exception:
        return None
    return None

def ocultar_en_imagen():
    try:
        nombre_imagen = input("Ruta de la imagen original: ").strip().strip('"')
        if not os.path.exists(nombre_imagen):
            print("El archivo no existe.")
            return

        nombre_base = os.path.basename(nombre_imagen)
        _, extension = os.path.splitext(nombre_base)
        extension = extension.lower()

        if extension not in [".png", ".jpg", ".jpeg", ".webp"]:
            print("Extensión no compatible.")
            return

        img = Image.open(nombre_imagen)
        mensaje = input("Mensaje a ocultar: ")
        
        # Aquí guarda ahora en la carpeta estega_salidas
        ruta_salida = preparar_ruta_salida(nombre_base)
        
        exito = False
        if extension == ".png":
            exito = ocultar_en_png_pil(img, mensaje, ruta_salida)
        elif extension in [".jpg", ".jpeg", ".webp"]:
            exito = ocultar_en_metadatos_img(img.copy(), mensaje, ruta_salida, extension)

        if exito:
            print(f"\n¡Éxito! Guardado en: {ruta_salida}")
            logger.info("Ocultado en imagen", extra={"props": {"out": ruta_salida}})
        else:
            print("Fallo al ocultar.")

    except Exception as e:
        print(f"Error: {e}")
        logger.error("Error en ocultar_en_imagen", exc_info=True)

def revelar_logica_imagen(ruta_completa):
    try:
        _, extension = os.path.splitext(ruta_completa)
        extension = extension.lower()
        if extension not in [".png", ".jpg", ".jpeg", ".webp"]: return None

        img = Image.open(ruta_completa)
        if extension == ".png":
            return revelar_de_png_pil(img)
        else:
            return revelar_de_metadatos_img(img)
    except:
        return None

def procesar_revelado_imagenes():
    ruta_target, modo = solicitar_ruta_analisis()
    if not ruta_target: return

    archivos_a_procesar = []
    
    if modo == "file":
        archivos_a_procesar.append(ruta_target)
    else:
        print(f"Escaneando carpeta: {ruta_target}")
        valid_exts = [".png", ".jpg", ".jpeg", ".webp"]
        try:
            for f in os.listdir(ruta_target):
                full_p = os.path.join(ruta_target, f)
                _, ext = os.path.splitext(f)
                if os.path.isfile(full_p) and ext.lower() in valid_exts:
                    archivos_a_procesar.append(full_p)
        except Exception as e:
            print(f"Error leyendo directorio: {e}")
            return

    count = 0
    for archivo in archivos_a_procesar:
        msg = revelar_logica_imagen(archivo)
        if msg:
            print(f" > ENCONTRADO en {os.path.basename(archivo)}: {msg}")
            registrar_hallazgo(msg, archivo)
            count += 1
            
    if count == 0:
        print("No se encontraron mensajes en las imágenes analizadas.")
    else:
        print(f"Proceso finalizado. {count} mensajes encontrados.")


#Esto es para AUDIO

def ocultar_en_audio():
    try:
        ruta_audio = input("Ruta del archivo .wav original: ").strip().strip('"')
        if not os.path.exists(ruta_audio) or not ruta_audio.lower().endswith(".wav"):
            print("Archivo inválido o no existe.")
            return

        mensaje = input("Mensaje a ocultar: ")
        mensaje_bytes = mensaje.encode('utf-8')
        longitud_bytes = struct.pack('>I', len(mensaje_bytes))
        bytes_a_ocultar = longitud_bytes + mensaje_bytes

        wav_file = wave.open(ruta_audio, 'rb')
        params = wav_file.getparams()
        frames = wav_file.readframes(wav_file.getnframes())
        wav_file.close()
        
        data_bytes = bytearray(frames)
        if len(data_bytes) < len(bytes_a_ocultar) * 8:
            print("Audio muy corto.")
            return

        data_index = 0
        for byte_msg in bytes_a_ocultar:
            for i in range(8):
                bit = (byte_msg >> i) & 1
                data_bytes[data_index] = (data_bytes[data_index] & 0xFE) | bit
                data_index += 1
        
        ruta_salida = preparar_ruta_salida(os.path.basename(ruta_audio))
        wav_out = wave.open(ruta_salida, 'wb')
        wav_out.setparams(params)
        wav_out.writeframes(data_bytes)
        wav_out.close()

        print(f"\n¡Éxito! Guardado en: {ruta_salida}")
        logger.info("Ocultado en audio", extra={"props": {"out": ruta_salida}})

    except Exception as e:
        print(f"Error: {e}")
        logger.error("Error ocultar audio", exc_info=True)

def revelar_logica_audio(ruta_completa):
    try:
        wav_file = wave.open(ruta_completa, 'rb')
        frames = wav_file.readframes(wav_file.getnframes())
        wav_file.close()
        data_bytes = bytearray(frames)
        
        if len(data_bytes) < 32: return None
        
        data_index = 0
        longitud_bytes = bytearray()
        for _ in range(4):
            byte_val = 0
            for i in range(8):
                bit = data_bytes[data_index] & 1
                byte_val |= (bit << i)
                data_index += 1
            longitud_bytes.append(byte_val)
            
        longitud_mensaje = struct.unpack('>I', longitud_bytes)[0]
        if longitud_mensaje > len(data_bytes) or longitud_mensaje > 10000: 
            return None

        bytes_necesarios = (4 + longitud_mensaje) * 8
        if len(data_bytes) < bytes_necesarios: return None

        mensaje_bytes = bytearray()
        for _ in range(longitud_mensaje):
            byte_val = 0
            for i in range(8):
                bit = data_bytes[data_index] & 1
                byte_val |= (bit << i)
                data_index += 1
            mensaje_bytes.append(byte_val)
            
        return mensaje_bytes.decode('utf-8', errors='ignore')
    except:
        return None

def procesar_revelado_audio():
    ruta_target, modo = solicitar_ruta_analisis()
    if not ruta_target: return

    archivos_a_procesar = []
    if modo == "file":
        archivos_a_procesar.append(ruta_target)
    else:
        print(f"Escaneando carpeta: {ruta_target}")
        try:
            for f in os.listdir(ruta_target):
                full_p = os.path.join(ruta_target, f)
                if os.path.isfile(full_p) and f.lower().endswith(".wav"):
                    archivos_a_procesar.append(full_p)
        except Exception as e:
            print(f"Error leyendo directorio: {e}")
            return

    count = 0
    for archivo in archivos_a_procesar:
        msg = revelar_logica_audio(archivo)
        if msg:
            print(f" > ENCONTRADO en {os.path.basename(archivo)}: {msg}")
            registrar_hallazgo(msg, archivo)
            count += 1
            
    if count == 0:
        print("No se encontraron mensajes en los audios analizados.")
    else:
        print(f"Proceso finalizado. {count} mensajes encontrados.")

#Esto es para PDF

def ocultar_en_pdf():
    try:
        ruta_pdf = input("Ruta del PDF original: ").strip().strip('"')
        if not os.path.exists(ruta_pdf) or not ruta_pdf.lower().endswith(".pdf"):
            print("PDF inválido.")
            return

        mensaje = input("Mensaje a ocultar: ")
        reader = PdfReader(ruta_pdf)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        metadata = reader.metadata
        writer.add_metadata(metadata)
        writer.add_metadata({"/MensajeOculto": mensaje})
        
        ruta_salida = preparar_ruta_salida(os.path.basename(ruta_pdf))
        with open(ruta_salida, "wb") as f:
            writer.write(f)

        print(f"\n¡Éxito! Guardado en: {ruta_salida}")
        logger.info("Ocultado en PDF", extra={"props": {"out": ruta_salida}})
    except Exception as e:
        print(f"Error: {e}")
        logger.error("Error ocultar PDF", exc_info=True)

def revelar_logica_pdf(ruta_completa):
    try:
        reader = PdfReader(ruta_completa)
        if "/MensajeOculto" in reader.metadata:
            return reader.metadata["/MensajeOculto"]
    except:
        pass
    return None

def procesar_revelado_pdf():
    ruta_target, modo = solicitar_ruta_analisis()
    if not ruta_target: return

    archivos_a_procesar = []
    if modo == "file":
        archivos_a_procesar.append(ruta_target)
    else:
        print(f"Escaneando carpeta: {ruta_target}")
        try:
            for f in os.listdir(ruta_target):
                full_p = os.path.join(ruta_target, f)
                if os.path.isfile(full_p) and f.lower().endswith(".pdf"):
                    archivos_a_procesar.append(full_p)
        except: return

    count = 0
    for archivo in archivos_a_procesar:
        msg = revelar_logica_pdf(archivo)
        if msg:
            print(f" > ENCONTRADO en {os.path.basename(archivo)}: {msg}")
            registrar_hallazgo(msg, archivo)
            count += 1
    
    if count == 0:
        print("No se encontraron mensajes en los PDF analizados.")
    else:
        print(f"Proceso finalizado. {count} mensajes encontrados.")


#Esto es en general

def preparar_ruta_salida(nombre_base_archivo):
    # Guarda siempre en la carpeta estega_salidas
    nombre_sin_ext, extension = os.path.splitext(nombre_base_archivo)
    nuevo_nombre = f"{nombre_sin_ext}_2{extension}"
    return os.path.join(OUTPUT_DIR, nuevo_nombre)

def solicitar_ruta_analisis():
    entrada = input("\nIngrese la ruta del ARCHIVO o CARPETA a analizar: ").strip().strip('"')
    
    if not entrada:
        print("Ruta vacía.")
        return None, None
        
    if not os.path.exists(entrada):
        print("Error: La ruta no existe.")
        return None, None
        
    if os.path.isfile(entrada):
        return entrada, "file"
    elif os.path.isdir(entrada):
        return entrada, "batch"
    else:
        return None, None

#Estos son los menús

def mostrar_menu_principal():
    print("1. Ocultar mensaje")
    print("2. Revelar mensaje")
    print("3. Salir")
    return input("Opción: ")

def mostrar_submenu_formatos(accion):
    print(f"\n--- {accion.upper()} ---")
    print("1. Imagen (.png, .jpg, .webp)")
    print("2. Audio (.wav)")
    print("3. PDF")
    print("4. Volver")
    return input("Opción: ")

def main():
    logger.info("Aplicación iniciada")
    print(f"Nota: Todos los logs y salidas se guardarán en:\n -> {OUTPUT_DIR}")
    
    while True:
        op = mostrar_menu_principal()
        
        if op == '1': # Para ocultar
            while True:
                sub = mostrar_submenu_formatos("ocultar")
                if sub == '1': ocultar_en_imagen()
                elif sub == '2': ocultar_en_audio()
                elif sub == '3': ocultar_en_pdf()
                elif sub == '4': break
                
        elif op == '2': # ära revelar
            while True:
                sub = mostrar_submenu_formatos("revelar")
                if sub == '1': procesar_revelado_imagenes()
                elif sub == '2': procesar_revelado_audio()
                elif sub == '3': procesar_revelado_pdf()
                elif sub == '4': break
                
        elif op == '3':
            print("Saliendo...")
            sys.exit()
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()