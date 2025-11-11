import os
import json
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from pydub import AudioSegment

# === UTILIDAD GENERAL ===
def guardar_en_jsonl(datos, archivo="mensajes.jsonl"):
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(datos, ensure_ascii=False) + "\n")
    print(f" Mensaje guardado en {archivo}")


# === OCULTAR MENSAJE ===
def ocultar_mensaje(ruta_archivo, mensaje, salida):
    ext = os.path.splitext(ruta_archivo)[1].lower()
    try:
        if ext in [".png", ".jpg", ".jpeg"]:
            imagen = Image.open(ruta_archivo)
            datos = list(imagen.getdata())

            mensaje_bits = ''.join(format(ord(c), '08b') for c in mensaje)
            mensaje_bits += '1111111111111110'  # fin del mensaje

            nuevos_datos = []
            bit_index = 0

            for pixel in datos:
                r, g, b = pixel[:3]
                if bit_index < len(mensaje_bits):
                    r = (r & ~1) | int(mensaje_bits[bit_index])
                    bit_index += 1
                if bit_index < len(mensaje_bits):
                    g = (g & ~1) | int(mensaje_bits[bit_index])
                    bit_index += 1
                if bit_index < len(mensaje_bits):
                    b = (b & ~1) | int(mensaje_bits[bit_index])
                    bit_index += 1
                nuevos_datos.append((r, g, b))

            imagen.putdata(nuevos_datos)
            imagen.save(salida)
            print(f" Mensaje ocultado en {salida}")

        elif ext == ".pdf":
            reader = PdfReader(ruta_archivo)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            metadata = reader.metadata or {}
            metadata.update({"/Oculto": mensaje})
            writer.add_metadata(metadata)

            with open(salida, "wb") as f:
                writer.write(f)

            print(f" Mensaje ocultado en metadatos de {salida}")

        elif ext in [".mp3", ".wav"]:
            audio = AudioSegment.from_file(ruta_archivo)
            tags = {"comment": mensaje}
            audio.export(salida, format=ext.replace(".", ""), tags=tags)
            print(f" Mensaje ocultado en {salida}")

        else:
            raise ValueError(" Tipo de archivo no compatible para ocultar mensajes")

        # Guarda registro JSONL
        datos = {
            "archivo_original": ruta_archivo,
            "archivo_modificado": salida,
            "mensaje_oculto": mensaje
        }
        guardar_en_jsonl(datos)

    except Exception as e:
        print(f" Error al ocultar el mensaje: {e}")


# === REVELAR MENSAJE ===
def revelar_mensaje(ruta_archivo):
    ext = os.path.splitext(ruta_archivo)[1].lower()
    try:
        if ext in [".png", ".jpg", ".jpeg"]:
            imagen = Image.open(ruta_archivo)
            datos = list(imagen.getdata())
            bits = ""

            for pixel in datos:
                for color in pixel[:3]:
                    bits += str(color & 1)

            mensaje = ""
            for i in range(0, len(bits), 8):
                byte = bits[i:i + 8]
                if byte == '11111110':
                    break
                mensaje += chr(int(byte, 2))

            print(f" Mensaje revelado: {mensaje}")

        elif ext == ".pdf":
            reader = PdfReader(ruta_archivo)
            metadata = reader.metadata
            if "/Oculto" in metadata:
                print(f" Mensaje revelado desde PDF: {metadata['/Oculto']}")
            else:
                print(" No se encontró mensaje oculto en el PDF")

        elif ext in [".mp3", ".wav"]:
            audio = AudioSegment.from_file(ruta_archivo)
            tags = getattr(audio, "tags", None)
            if tags and "comment" in tags:
                print(f" Mensaje revelado desde audio: {tags['comment']}")
            else:
                print(" No se encontró mensaje oculto en el audio")

        else:
            raise ValueError(" Tipo de archivo no compatible para revelar mensajes")

    except Exception as e:
        print(f" Error al revelar mensaje: {e}")


# === MENÚ PRINCIPAL ===
if __name__ == "__main__":
    print("=== Esteganografía - PIA Entregable 2 ===")
    print("1. Ocultar mensaje")
    print("2. Revelar mensaje")

    opcion = input("Elige una opción (1 o 2): ")

    if opcion == "1":
        ruta = input("Ingresa la ruta del archivo original: ").strip('"')
        mensaje = input("Escribe el mensaje que quieres ocultar: ")
        salida = input("Ingresa el nombre del archivo de salida: ")
        ocultar_mensaje(ruta, mensaje, salida)

    elif opcion == "2":
        ruta = input("Ingresa la ruta del archivo con mensaje oculto: ").strip('"')
        revelar_mensaje(ruta)

    else:
        print("⚠️ Opción inválida.")

