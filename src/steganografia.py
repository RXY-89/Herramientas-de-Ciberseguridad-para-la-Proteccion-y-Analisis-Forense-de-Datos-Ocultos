# src/steganography/esteganografia.py
# Herramienta de Esteganografía
# Inserta y extrae mensajes ocultos dentro de imágenes PNG
# Dependencias: Pillow

from PIL import Image

def ocultar_mensaje(imagen_entrada, mensaje_txt, imagen_salida):
    """Oculta el contenido de un archivo de texto dentro de una imagen PNG."""
    with open(mensaje_txt, "r", encoding="utf-8") as f:
        mensaje = f.read()

    # Convertir mensaje a bits
    mensaje_binario = ''.join(format(ord(c), '08b') for c in mensaje)
    mensaje_binario += '1111111111111110'  # marcador de fin

    imagen = Image.open(imagen_entrada)
    if imagen.mode != 'RGB':
        imagen = imagen.convert('RGB')

    pixeles = list(imagen.getdata())
    nuevos_pixeles = []

    i = 0
    for pixel in pixeles:
        r, g, b = pixel
        if i < len(mensaje_binario):
            r = (r & ~1) | int(mensaje_binario[i])
            i += 1
        if i < len(mensaje_binario):
            g = (g & ~1) | int(mensaje_binario[i])
            i += 1
        if i < len(mensaje_binario):
            b = (b & ~1) | int(mensaje_binario[i])
            i += 1
        nuevos_pixeles.append((r, g, b))

    imagen.putdata(nuevos_pixeles)
    imagen.save(imagen_salida)
    print(f" Mensaje oculto correctamente en {imagen_salida}")


def extraer_mensaje(imagen_entrada, archivo_salida):
    """Extrae el mensaje oculto desde una imagen PNG."""
    imagen = Image.open(imagen_entrada)
    pixeles = list(imagen.getdata())

    bits = ""
    for pixel in pixeles:
        for color in pixel[:3]:
            bits += str(color & 1)

    # Buscar el marcador de fin
    mensaje_bits = bits.split('1111111111111110')[0]
    mensaje = ""
    for i in range(0, len(mensaje_bits), 8):
        byte = mensaje_bits[i:i+8]
        mensaje += chr(int(byte, 2))

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(mensaje)

    print(f" Mensaje extraído y guardado en {archivo_salida}")
