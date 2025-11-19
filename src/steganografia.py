import json
import wave
import fitz  # PyMuPDF
from PIL import Image
import os

# Guardar todos los mensajes en .jsonl
def guardar_jsonl(mensaje, archivo="mensajes.jsonl"):
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps({"mensaje": mensaje}) + "\n")

def ocultar_en_imagen(imagen_path, mensaje, salida):
     try:
         img = Image.open(imagen_path)
         bin_mensaje = ''.join(format(ord(i), '08b') for i in mensaje) + '1111111111111110'
         pixeles = img.load()

         if len(bin_mensaje) > img.width * img.height * 3:
             raise ValueError("El mensaje es demasiado largo para esta imagen")

         data = list(img.getdata())
         new_data = []
         msg_index = 0

         for pixel in data:
             pixel_list = list(pixel)
             for i in range(3):
                 if msg_index < len(bin_mensaje):
                     pixel_list[i] = pixel_list[i] & ~1 | int(bin_mensaje[msg_index])
                     msg_index += 1
             new_data.append(tuple(pixel_list))

         img.putdata(new_data)
         img.save(salida)
         guardar_jsonl(mensaje)
         print(f" Mensaje ocultado en imagen: {salida}")
     except Exception as e:
         print(f" Error al ocultar en imagen: {e}")
         
def ocultar_en_pdf(pdf_path, mensaje, salida):
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata or {}
        metadata["mensaje_oculto"] = mensaje
        doc.set_metadata(metadata)
        doc.save(salida)
        guardar_jsonl(mensaje)
        print(f" Mensaje ocultado en PDF: {salida}")
    except Exception as e:
        print(f" Error al ocultar en PDF: {e}")

def ocultar_en_audio(audio_path, mensaje, salida):
    try:
        with wave.open(audio_path, 'rb') as audio:
            frames = bytearray(list(audio.readframes(audio.getnframes())))
            bin_mensaje = ''.join(format(ord(i), '08b') for i in mensaje) + '1111111111111110'

            for i in range(len(bin_mensaje)):
                frames[i] = (frames[i] & 254) | int(bin_mensaje[i])

            with wave.open(salida, 'wb') as nuevo_audio:
                nuevo_audio.setparams(audio.getparams())
                nuevo_audio.writeframes(frames)

        guardar_jsonl(mensaje)
        print(f" Mensaje ocultado en audio: {salida}")
    except Exception as e:
        print(f" Error al ocultar en audio: {e}")

def revelar_de_imagen(imagen_path):
    try:
        img = Image.open(imagen_path)
        data = list(img.getdata())
        mensaje_bin = ""

        for pixel in data:
            for i in range(3):
                mensaje_bin += str(pixel[i] & 1)

        mensaje = ""
        for i in range(0, len(mensaje_bin), 8):
            byte = mensaje_bin[i:i+8]
            if byte == "11111111":
                break
            mensaje += chr(int(byte, 2))

        guardar_jsonl(mensaje)
        print("Mensaje revelado:", mensaje)
    except Exception as e:
        print(f"Error al revelar desde imagen: {e}")

def revelar_de_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        mensaje = metadata.get("mensaje_oculto", "No se encontró mensaje")
        guardar_jsonl(mensaje)
        print("Mensaje revelado:", mensaje)
    except Exception as e:
        print(f"Error al revelar PDF: {e}")

def revelar_de_audio(audio_path):
    try:
        with wave.open(audio_path, 'rb') as audio:
            frames = bytearray(list(audio.readframes(audio.getnframes())))

        mensaje_bin = ""
        for byte in frames:
            mensaje_bin += str(byte & 1)

        mensaje = ""
        for i in range(0, len(mensaje_bin), 8):
            byte = mensaje_bin[i:i + 8]
            if byte == "11111111":
                break
            mensaje += chr(int(byte, 2))

        guardar_jsonl(mensaje)
        print("Mensaje revelado:", mensaje)
    except Exception as e:
        print(f"Error al revelar audio: {e}")

def revelar_de_jsonl():
    try:
        with open("mensajes.jsonl", "r", encoding="utf-8") as f:
            for linea in f:
                print("💬", json.loads(linea)["mensaje"])
    except:
        print("No hay mensajes guardados aún.")

def main():
    print("=== Esteganografía - PIA Entregable 2 ===")
    print("1. Ocultar mensaje")
    print("2. Revelar desde archivo")
    print("3. Mostrar historial de mensajes (.jsonl)")
    opcion = input("Elige una opción (1-3): ")

    if opcion == "1":
        archivo = input("Ruta del archivo original: ").strip('"')
        mensaje = input("Mensaje a ocultar: ")
        salida = input("Nombre del archivo de salida: ")

        if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            ocultar_en_imagen(archivo, mensaje, salida)
        elif archivo.lower().endswith('.pdf'):
            ocultar_en_pdf(archivo, mensaje, salida)
        elif archivo.lower().endswith('.wav'):
            ocultar_en_audio(archivo, mensaje, salida)
        else:
            print("Formato no soportado (.png, .jpg, .pdf, .wav)")

    elif opcion == "2":
        archivo = input("Ruta del archivo para revelar mensaje: ").strip('"')
        if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            revelar_de_imagen(archivo)
        elif archivo.lower().endswith('.pdf'):
            revelar_de_pdf(archivo)
        elif archivo.lower().endswith('.wav'):
            revelar_de_audio(archivo)
        else:
            print("Formato no soportado.")

    elif opcion == "3":
        revelar_de_jsonl()

if __name__ == "__main__":
    main()
