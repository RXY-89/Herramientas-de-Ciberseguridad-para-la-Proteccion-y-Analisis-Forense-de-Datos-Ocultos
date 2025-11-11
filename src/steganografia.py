import wave
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import logging
import os

# CONFIGURACIÓN DEL SISTEMA DE REGISTRO
logging.basicConfig(
    filename="registro_esteganografia.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# FUNCIÓN: OCULTAR MENSAJE EN IMAGEN
def ocultar_en_imagen(imagen_path, mensaje, salida_path):
    try:
        imagen = Image.open(imagen_path)
        binario = ''.join(format(ord(i), '08b') for i in mensaje) + '1111111111111110'
        pixeles = imagen.load()

        ancho, alto = imagen.size
        contador = 0

        for y in range(alto):
            for x in range(ancho):
                if contador < len(binario):
                    pixel = list(pixeles[x, y])
                    pixel[0] = (pixel[0] & ~1) | int(binario[contador])
                    pixeles[x, y] = tuple(pixel)
                    contador += 1

        imagen.save(salida_path)
        logging.info(f"Mensaje ocultado en imagen: {salida_path}")
        print(f" Mensaje ocultado correctamente en {salida_path}")
    except Exception as e:
        logging.error(f"Error al ocultar en imagen: {e}")
        print(f" Error al ocultar en imagen: {e}")

# FUNCIÓN: REVELAR MENSAJE EN IMAGEN
def revelar_en_imagen(imagen_path):
    try:
        imagen = Image.open(imagen_path)
        pixeles = imagen.load()
        ancho, alto = imagen.size
        bits = ""

        for y in range(alto):
            for x in range(ancho):
                bits += str(pixeles[x, y][0] & 1)

        bytes_mensaje = [bits[i:i+8] for i in range(0, len(bits), 8)]
        mensaje = ""
        for b in bytes_mensaje:
            if b == '11111110':
                break
            mensaje += chr(int(b, 2))

        logging.info(f"Mensaje revelado desde imagen: {imagen_path}")
        print(" Mensaje oculto encontrado:")
        print(mensaje)
    except Exception as e:
        logging.error(f"Error al revelar mensaje en imagen: {e}")
        print(f" Error al revelar mensaje en imagen: {e}")


# FUNCIÓN: OCULTAR MENSAJE EN AUDIO

def ocultar_en_audio(audio_path, mensaje, salida_path):
    try:
        audio = wave.open(audio_path, mode='rb')
        frames = bytearray(list(audio.readframes(audio.getnframes())))
        params = audio.getparams()
        audio.close()

        binario = ''.join(format(ord(i), '08b') for i in mensaje) + '1111111111111110'

        if len(binario) > len(frames):
            raise ValueError("El mensaje es demasiado grande para ocultarlo en este audio.")

        for i in range(len(binario)):
            frames[i] = (frames[i] & 254) | int(binario[i])

        with wave.open(salida_path, 'wb') as nuevo_audio:
            nuevo_audio.setparams(params)
            nuevo_audio.writeframes(bytes(frames))

        logging.info(f"Mensaje ocultado en audio: {salida_path}")
        print(f" Mensaje ocultado correctamente en {salida_path}")
    except Exception as e:
        logging.error(f"Error al ocultar en audio: {e}")
        print(f" Error al ocultar en audio: {e}")

# FUNCIÓN: REVELAR MENSAJE EN AUDIO
def revelar_en_audio(audio_path):
    try:
        audio = wave.open(audio_path, mode='rb')
        frames = bytearray(list(audio.readframes(audio.getnframes())))
        bits = [str(frames[i] & 1) for i in range(len(frames))]
        bytes_mensaje = [bits[i:i+8] for i in range(0, len(bits), 8)]
        mensaje = ""

        for b in bytes_mensaje:
            if ''.join(b) == '11111110':
                break
            mensaje += chr(int(''.join(b), 2))

        audio.close()
        logging.info(f"Mensaje revelado desde audio: {audio_path}")
        print(" Mensaje oculto encontrado:")
        print(mensaje)
    except Exception as e:
        logging.error(f"Error al revelar mensaje en audio: {e}")
        print(f" Error al revelar mensaje en audio: {e}")

# FUNCIÓN: OCULTAR MENSAJE EN PDF
def ocultar_en_pdf(pdf_path, mensaje, salida_path):
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Insertamos el mensaje oculto en los metadatos del PDF
        writer.add_metadata({"/MensajeOculto": mensaje})

        with open(salida_path, "wb") as salida:
            writer.write(salida)

        logging.info(f"Mensaje ocultado en PDF: {salida_path}")
        print(f" Mensaje ocultado correctamente en {salida_path}")
    except Exception as e:
        logging.error(f"Error al ocultar en PDF: {e}")
        print(f" Error al ocultar en PDF: {e}")

# FUNCIÓN: REVELAR MENSAJE EN PDF
def revelar_en_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        info = reader.metadata
        mensaje = info.get("/MensajeOculto", None)
        if mensaje:
            print(" Mensaje oculto encontrado en el PDF:")
            print(mensaje)
            logging.info(f"Mensaje revelado desde PDF: {pdf_path}")
        else:
            print(" No se encontró ningún mensaje oculto en los metadatos.")
    except Exception as e:
        logging.error(f"Error al revelar mensaje en PDF: {e}")
        print(f" Error al revelar mensaje en PDF: {e}")


# PROGRAMA PRINCIPAL
def main():
    print("===  Esteganografía Multiformato - PIA Entregable 2 ===")
    print("1. Ocultar mensaje")
    print("2. Revelar mensaje")
    opcion = input("Elige una opción (1 o 2): ")

    tipo = input("Selecciona tipo de archivo (imagen / audio / pdf): ").lower()

    if opcion == "1":
        archivo = input("Ruta del archivo original: ")
        mensaje = input("Mensaje a ocultar: ")
        salida = input("Nombre del archivo de salida (ej. salida.png, salida.wav o salida.pdf): ")

        if tipo == "imagen":
            ocultar_en_imagen(archivo, mensaje, salida)
        elif tipo == "audio":
            ocultar_en_audio(archivo, mensaje, salida)
        elif tipo == "pdf":
            ocultar_en_pdf(archivo, mensaje, salida)
        else:
            print(" Tipo no válido.")
    elif opcion == "2":
        archivo = input("Ruta del archivo con mensaje oculto: ")

        if tipo == "imagen":
            revelar_en_imagen(archivo)
        elif tipo == "audio":
            revelar_en_audio(archivo)
        elif tipo == "pdf":
            revelar_en_pdf(archivo)
        else:
            print(" Tipo no válido.")
    else:
        print(" Opción no válida.")

if __name__ == "__main__":
    main()
