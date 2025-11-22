# Herramientas-de-Ciberseguridad-para-la-Proteccion-y-Analisis-Forense-de-Datos-Ocultos
Este proyecto tiene como propósito desarrollar un conjunto de utilidades para proteger la información mediante técnicas de cifrado y ocultamiento (esteganografía), así como para analizar forensemente archivos en busca de datos ocultos o evidencia (metadatos). Se abordarán tareas de ciberseguridad defensiva (Blue Team) y de Análisis Forense/DFIR. 

Nos enfocaremos en el uso de la esteganografía como un medio para ocultamiento de mensajes y el uso de los hashes de los archivos para la verificación de integridad de los mismos, por último emplearemos la metadata para poder marcar si el archivo ha sido o no modificado.


# Tarea 1 - Ocultamiento y Detección de Información mediante Esteganografía

## Descripción general
Tiene como objetivo crear una herramienta capaz de ocultar información dentro de un archivo carrier (imagen, audio o PDF) y luego poder extraerla nuevamente.  
La técnica utilizada se conoce como **esteganografía**, la cual permite insertar un mensaje secreto dentro de otro archivo sin que sea evidente a simple vista.

## Objetivo
Desarrollar un programa en Python que pueda:
1. Insertar un mensaje de texto en un archivo carrier (imagen, audio o PDF).
2. Extraer el mensaje oculto del archivo modificado para comprobar que se puede recuperar correctamente.

## Entradas y salidas
- **Entradas esperadas:**
  - Carrier: archivo de imagen, audio o PDF (por ejemplo `imagen.png`, `audio.wav`, `documento.pdf`)
  - Mensaje secreto: archivo de texto (`mensaje.txt`)

- **Salidas esperadas:**
  - Archivo esteganográfico con el mensaje oculto (`imagen_estego.png`)
  - Archivo de texto con el mensaje recuperado (`mensaje_extraido.txt`)

## Librerías utilizadas
- `Pillow` → para manejar imágenes y modificar píxeles.
- `os` → para manejar rutas de archivos.
- `base64` → para codificar y decodificar mensajes ocultos.

## Procedimiento general
1. Se carga la imagen o archivo carrier.
2. El mensaje secreto se convierte a una secuencia de bits.
3. Los bits se insertan dentro de los valores de color de los píxeles de la imagen (utilizando la técnica LSB – Least Significant Bit).
4. Se guarda la nueva imagen con el mensaje oculto.
5. Para la extracción, se lee nuevamente la imagen modificada y se reconstruye el mensaje original a partir de los bits ocultos.

## Ejemplo de uso
1. Ejecutar el script principal:
   python steganografia.py



