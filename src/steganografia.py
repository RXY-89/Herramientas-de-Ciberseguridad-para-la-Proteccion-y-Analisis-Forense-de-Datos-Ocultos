# Tarea 1
# Este programa permite esconder (ocultar) un mensaje de texto dentro de una imagen
# y también recuperarlo después. Usa la librería Pillow.

from PIL import Image
from pathlib import Path

# Rutas base (según tu estructura en /examples)
BASE_PATH = Path("examples/esteganografia")
ORIGINALES = BASE_PATH / "originales"
MODIFICADOS = BASE_PATH / "modificados"
NOTAS = BASE_PATH / "nota"


def ocultar_texto(imagen_original, mensaje_txt, imagen_salida):
    """Función para ocultar el texto dentro de una imagen."""
    with open(mensaje_txt, "r", encoding="utf-8") as f:
        mensaje = f.read()

    # Convertir el texto a bits
    mensaje_bits = ''.join(format(ord(c), '08b') for c in mensaje)
    mensaje_bits += '1111111111111110'  # marcador de fin

    imagen = Image.open(imagen_original)
    if imagen.mode != 'RGB':
        imagen = imagen.convert('RGB')

    pixeles = list(imagen.getdata())
    nuevos_pixeles = []

    i = 0
    for pixel in pixeles:
        r, g, b = pixel
        if i < len(mensaje_bits):
            r = (r & ~1) | int(mensaje_bits[i])
            i += 1
        if i < len(mensaje_bits):
            g = (g & ~1) | int(mensaje_bits[i])
            i += 1
        if i < len(mensaje_bits):
            b = (b & ~1) | int(mensaje_bits[i])
            i += 1
        nuevos_pixeles.append((r, g, b))

    imagen.putdata(nuevos_pixeles)
    imagen.save(imagen_salida)
    print(f" Mensaje ocultado correctamente en {imagen_salida}")


def extraer_texto(imagen_modificada, archivo_salida):
    """Función para extraer el texto oculto de una imagen."""
    imagen = Image.open(imagen_modificada)
    pixeles = list(imagen.getdata())

    bits = ""
    for pixel in pixeles:
        for color in pixel[:3]:
            bits += str(color & 1)

    # Cortar el mensaje donde termina
    mensaje_bits = bits.split('1111111111111110')[0]
    mensaje = ""
    for i in range(0, len(mensaje_bits), 8):
        byte = mensaje_bits[i:i+8]
        mensaje += chr(int(byte, 2))

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(mensaje)

    print(f" Mensaje extraído y guardado en {archivo_salida}")

# Ejemplo de uso (se ejecuta solo si corres el archivo)
if __name__ == "__main__":
    # Rutas de ejemplo (ajustadas a tu estructura)
    imagen_original = ORIGINALES / "imagenes" / "ejemplo.png"
    mensaje_secreto = NOTAS / "secreto.txt"
    imagen_modificada = MODIFICADOS / "imagenes" / "imagen_con_mensaje.png"
    mensaje_extraido = NOTAS / "mensaje_extraido.txt"

    # Llamamos a las funciones
    ocultar_texto(imagen_original, mensaje_secreto, imagen_modificada)
    extraer_texto(imagen_modificada, mensaje_extraido)
