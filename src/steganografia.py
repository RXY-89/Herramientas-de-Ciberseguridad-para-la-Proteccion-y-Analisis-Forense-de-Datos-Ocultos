import json
import wave
import fitz  # PyMuPDF
from PIL import Image
import os

def guardar_jsonl(mensaje, archivo="mensajes.jsonl"):
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps({"mensaje": mensaje}) + "\n")

def ocultar_en_imagen(imagen_path, mensaje, salida):
    try:
        img = Image.open(imagen_path)
        bin_mensaje = ''.join(format(ord(i), '08b') for i in mensaje)
        pixeles = img.load()

        if len(bin_mensaje) > img.width * img.height:
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
            bin_mensaje = ''.join(format(ord(i), '08b') for i in mensaje)
            bin_mensaje += '1111111111111110'

            for i in range(len(bin_mensaje)):
                frames[i] = (frames[i] & 254) | int(bin_mensaje[i])

            with wave.open(salida, 'wb') as nuevo_audio:
                nuevo_audio.setparams(audio.getparams())
                nuevo_audio.writeframes(frames)
        guardar_jsonl(mensaje)
        print(f" Mensaje ocultado en audio: {salida}")
    except Exception as e:
        print(f" Error al ocultar en audio: {e}")

def revelar_de_jsonl(archivo="mensajes.jsonl"):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f:
                print("💬", json.loads(linea)["mensaje"])
    except Exception as e:
        print(f" Error al leer JSONL: {e}")

def main():
    print("=== Esteganografía - PIA Entregable 2 ===")
    print("1. Ocultar mensaje")
    print("2. Revelar mensajes guardados")
    opcion = input("Elige una opción (1 o 2): ")

    if opcion == "1":
        archivo = input("Ingresa la ruta del archivo original: ").strip('"')
        mensaje = input("Escribe el mensaje que quieres ocultar: ")
        salida = input("Ingresa el nombre del archivo de salida (con extensión): ")

        if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            ocultar_en_imagen(archivo, mensaje, salida)
        elif archivo.lower().endswith('.pdf'):
            ocultar_en_pdf(archivo, mensaje, salida)
        elif archivo.lower().endswith('.wav'):
            ocultar_en_audio(archivo, mensaje, salida)
        else:
            print(" Formato no soportado. Usa .png, .jpg, .pdf o .wav")

    elif opcion == "2":
        revelar_de_jsonl()
    else:
        print("Opción inválida.")

if __name__ == "__main__":
    main()


