# Herramientas-de-Ciberseguridad-para-la-Proteccion-y-Analisis-Forense-de-Datos-Ocultos
Este proyecto tiene como propósito desarrollar un conjunto de utilidades para proteger la información mediante técnicas de cifrado y ocultamiento (esteganografía), así como para analizar "forensemente2 archivos en busca de datos ocultos o evidencia (metadatos). Se abordarán tareas de ciberseguridad defensiva (Blue Team) y de Análisis Forense/DFIR. 

Nos enfocaremos en el uso de la esteganografía como un medio para ocultamiento de mensajes y el uso de los hashes de los archivos para la verificación de integridad de los mismos, por último emplearemos la metadata para poder marcar si el archivo ha sido o no modificado.


# Tarea 1 - Ocultamiento y Detección de Información mediante Esteganografía
## Descripción general
Este módulo implementa técnicas de esteganografía digital para establecer canales de comunicación encubiertos. El script permite ocultar mensajes de texto plano dentro de archivos multimedia (imágenes y audio) y documentos (PDF) sin alterar significativamente su percepción visual o auditiva. Adicionalmente, cuenta con un sistema de registro (logging) que almacena un historial de los mensajes procesados en formato JSONL para fines de auditoría o recuperación.

## Objetivo
Demostrar y ejecutar la capacidad de ocultar información confidencial dentro de portadores digitales comunes, utilizando la técnica del Bit Menos Significativo (LSB) para medios audiovisuales y la manipulación de metadatos para documentos, permitiendo tanto la inyección como la extracción posterior del mensaje secreto.

## Entradas y salidas

## Entradas esperadas:

* Archivos Portadores: Rutas a archivos existentes en formatos soportados: Imágenes (.png, .jpg, .jpeg), Audio (.wav) y Documentos (.pdf).
* Mensaje Secreto: Cadena de texto que el usuario desea ocultar.
* Ruta de Salida: Nombre o ruta donde se guardará el archivo modificado (estego-objeto).
* Opciones de Menú: Selección numérica (1, 2 o 3) para definir la operación a realizar.

## Salidas esperadas:

* Archivo Esteganografiado: Un nuevo archivo (imagen, audio o PDF) que contiene el mensaje oculto pero mantiene la funcionalidad del original.
* Consola: Confirmación de éxito, rutas de guardado o el texto del mensaje revelado.
* Historial (mensajes.jsonl): Un archivo de registro local que añade una nueva línea con el mensaje procesado en formato JSON ({"mensaje": "contenido"}).

## Librerías utilizadas
El script hace uso de las siguientes bibliotecas para la manipulación de archivos:

* PIL (Pillow): Para la manipulación de imágenes (apertura, acceso a píxeles RGB y guardado).
* fitz (PyMuPDF): Para acceder y modificar los metadatos de archivos PDF.
* wave: Librería estándar de Python para la lectura y escritura de archivos de audio .wav.
* json: Para la serialización y almacenamiento del historial de mensajes.
* os: Para validaciones de rutas y gestión del sistema de archivos.

## Procedimiento general
1. Selección de Operación: El usuario elige entre Ocultar (1), Revelar (2) o Ver Historial (3).
2. Validación: Se verifica que el archivo de entrada exista y que el formato sea compatible.

## Proceso de Ocultamiento:

* Imágenes/Audio: El mensaje se convierte a binario. Se utiliza la técnica LSB (Least Significant Bit), modificando el último bit de cada byte (de color en imágenes o de muestra en audio) para insertar la información sin generar ruido perceptible. Se añade un delimitador binario para marcar el fin del mensaje.
* PDF: Se inyecta el mensaje directamente en el campo de metadatos keywords (palabras clave) del documento.
* Persistencia: El archivo modificado se guarda en la ruta especificada y el mensaje se registra en mensajes.jsonl.

## Proceso de Revelado:

El script lee los bits menos significativos (imágenes/audio) o los metadatos (PDF), reconstruye la cadena binaria, la convierte a caracteres ASCII y detiene la lectura al encontrar el delimitador o el fin del mensaje, mostrando el resultado en pantalla.

## Ejemplo de uso

Escenario de ejemplo: Ocultar un mensaje en una imagen.

1. El usuario ejecuta el script y selecciona la opción 1 cuandoe ste le pida seleccionar una de las 3.
2. Ruta del archivo original: C:\Users\Usuario\Documents\paisaje.png
3. Mensaje a ocultar: La clave es 1234
4. Nombre del archivo de salida: paisaje_seguro.png

Resultado en consola:
`[OK] EXITO: Mensaje ocultado correctamente.
 -> Archivo guardado en: C:\Users\Usuario\Documents\paisaje_seguro.png`

Escenario de ejemplo: Revelar el mensaje.

1. El usuario selecciona la opción 2.
2. Ruta del archivo: paisaje_seguro.png

Resultado en consola:
`[REVELADO] Mensaje encontrado: La clave es 1234`
