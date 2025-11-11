# Programa de esteganografía con registro de acciones (logs)
# Descripción: Este programa permite ocultar y revelar mensajes en imágenes

from PIL import Image
import logging
from datetime import datetime

# CONFIGURACIÓN DEL REGISTRO
logging.basicConfig(
    filename='registro_esteganografia.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Inicio del programa de esteganografía")

# FUNCIONES PRINCIPALES
def ocultar_mensaje(ruta_imagen, mensaje, ruta_salida):
    """Oculta un mensaje de texto dentro de una imagen."""
    try:
        imagen = Image.open(ruta_imagen)
        imagen = imagen.convert("RGB")

        # Convertimos el mensaje en binario
        mensaje_binario = ''.join(format(ord(i), '08b') for i in mensaje)
        mensaje_binario += '1111111111111110'  # Marca de fin de mensaje

        datos = list(imagen.getdata())
        nuevos_datos = []
        index_mensaje = 0

        for pixel in datos:
            r, g, b = pixel
            if index_mensaje < len(mensaje_binario):
                r = (r & ~1) | int(mensaje_binario[index_mensaje])
                index_mensaje += 1
            if index_mensaje < len(mensaje_binario):
                g = (g & ~1) | int(mensaje_binario[index_mensaje])
                index_mensaje += 1
            if index_mensaje < len(mensaje_binario):
                b = (b & ~1) | int(mensaje_binario[index_mensaje])
                index_mensaje += 1
            nuevos_datos.append((r, g, b))

        imagen.putdata(nuevos_datos)
        imagen.save(ruta_salida)
        logging.info(f"Mensaje ocultado correctamente en {ruta_salida}")
        print(f" Mensaje ocultado correctamente en {ruta_salida}")

    except Exception as e:
        logging.error(f"Error al ocultar el mensaje: {e}")
        print(f" Error al ocultar el mensaje: {e}")


def revelar_mensaje(ruta_imagen):
    """Extrae el mensaje oculto de una imagen y lo guarda en un archivo .txt."""
    try:
        imagen = Image.open(ruta_imagen)
        imagen = imagen.convert("RGB")

        datos = list(imagen.getdata())
        mensaje_binario = ""

        for pixel in datos:
            for valor in pixel:
                mensaje_binario += str(valor & 1)

        # Convertimos de binario a texto hasta el marcador de fin
        bytes_mensaje = [mensaje_binario[i:i+8] for i in range(0, len(mensaje_binario), 8)]
        mensaje = ""
        for byte in bytes_mensaje:
            if byte == '11111110':  # Marca de fin
                break
            mensaje += chr(int(byte, 2))

        # Guardamos el mensaje extraído en un archivo de texto
        nombre_archivo = f"mensaje_revelado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(mensaje)

        logging.info(f"Mensaje revelado y guardado en {nombre_archivo}")
        print("💬 Mensaje oculto encontrado:")
        print(mensaje)
        print(f"📁 El mensaje fue guardado en: {nombre_archivo}")

        return mensaje

    except Exception as e:
        logging.error(f"Error al revelar el mensaje: {e}")
        print(f"❌ Error al revelar el mensaje: {e}")

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    print("=== Esteganografía - PIA Entregable 2 ===")
    print("1. Ocultar mensaje")
    print("2. Revelar mensaje")
    opcion = input("Elige una opción (1 o 2): ")

    if opcion == "1":
        ruta_imagen = input("Ingresa la ruta de la imagen original: ")
        mensaje = input("Escribe el mensaje que quieres ocultar: ")
        ruta_salida = input("Ingresa el nombre del archivo de salida (por ejemplo, salida.png): ")
        ocultar_mensaje(ruta_imagen, mensaje, ruta_salida)

    elif opcion == "2":
        ruta_imagen = input("Ingresa la ruta de la imagen con mensaje oculto: ")
        revelar_mensaje(ruta_imagen)

    else:
        print("Opción no válida.")
        logging.warning("Se eligió una opción no válida en el menú.")

