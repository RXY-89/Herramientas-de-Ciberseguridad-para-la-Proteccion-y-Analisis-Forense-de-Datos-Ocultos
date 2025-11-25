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



# Tarea 2 - Verificación de Integridad de Archivos mediante Hashes

## Descripción general
Este módulo constituye un sistema de detección de intrusiones basado en host (HIDS) simplificado. Implementa una arquitectura híbrida que utiliza Python como controlador lógico y de gestión de registros, y PowerShell como motor de cálculo criptográfico subyacente. El script permite monitorear tanto archivos individuales como directorios completos, estableciendo una "línea base" de hashes para identificar cualquier alteración no autorizada (modificación, creación o eliminación de archivos).

## Objetivo
Asegurar la integridad de la información almacenada mediante la comparación de huellas digitales (hashes). El propósito es automatizar la detección de cambios en el sistema de archivos y generar evidencia forense (logs y reportes) cuando el estado actual de un archivo discrepa de su estado original registrado.

## Entradas y salidas

## Entradas esperadas:

* Ruta Objetivo: Ruta absoluta o relativa de un archivo o directorio que se desea auditar.
* Interacción de Usuario: Confirmación (S/n) para actualizar la base de datos de hashes cuando se detectan cambios.
* Script Auxiliar: Dependencia del archivo sacar_hashes.ps1 en el mismo directorio para el cálculo matemático.

## Salidas esperadas:

* Base de Datos de Integridad: Archivos JSON almacenados en la carpeta hashes/ que contienen los pares archivo-hash de referencia (ej. hashes_nombre_carpeta.json o lista_hashes.json).
* Logs de Auditoría: Registro detallado de eventos en run.log gestionado por la librería loguru.
* Reportes de Incidentes: Archivos de texto (cambios_...txt) generados automáticamente cuando se detectan discrepancias.
* Alertas en Consola: Avisos visuales inmediatos sobre el estado de la integridad (Íntegro, Modificado, Nuevo, Eliminado).

## Librerías utilizadas

* subprocess: Para la ejecución controlada del script de PowerShell y la captura de su salida estándar.
* loguru: Para la gestión avanzada y estructurada de logs (timestamps, niveles de severidad, IDs de ejecución).
* pathlib: Para el manejo orientado a objetos de rutas del sistema de archivos, asegurando compatibilidad entre SO.
* json: Para la lectura y escritura de las bases de datos de hashes y la interpretación de la salida de PowerShell.
* datetime: Para el timestamping de los reportes generados.

## Procedimiento general

1. Inicialización: Se configura el sistema de logging y se verifican las rutas de las dependencias (sacar_hashes.ps1).
2. Selección de objetivo: El usuario ingresa una ruta. El script determina si es un archivo único o un directorio.
3. Cálculo de hash (PowerShell): Python invoca a PowerShell mediante subprocess. PowerShell calcula el hash SHA-256 (u otro algoritmo definido en el ps1) y devuelve un objeto JSON a Python.
4. Comparación:
   * Primera ejecución: Si no existe registro previo, se crea la línea base.
   * Ejecuciones posteriores: Se comparan los hashes actuales contra los almacenados. Se utiliza para identificar archivos **Nuevos**, **Eliminados** y **Modificados**.
5. Reporte y acción:
   * Si hay cambios, se genera un reporte .txt, se escribe una alerta en el log y se pregunta al usuario si desea actualizar la línea base (aceptar los cambios como legítimos).
   * Si no hay cambios, se confirma la integridad.

## Ejemplo de uso

Escenario: Monitoreo de una carpeta sensible.

Ejecución Inicial:
1. Usuario ejecuta el script e introduce: C:\src
2. El script detecta que es la primera vez, calcula los hashes de todos los archivos dentro y crea hashes/hashes_Datos_Sensibles.json.

Resultado en consola:

`Registro creado correctamente.`

Escenario: Modificación, ejemplo: Un atacante modifica contratos.pdf dentro de esa carpeta.

Segunda ejecución de verificación:

1. Usuario ejecuta el script nuevamente sobre C:\Datos_Sensibles.
2. El script compara los hashes nuevos con el JSON guardado.

Resultado en Consola:

`¡ATENCIÓN! Se han detectado cambios.
Detalles guardados en: cambios_src_20251125_015631.txt
¿Desea actualizar la base de datos de hashes? [S/n]:`

3. Log generado (run.log):

`2025-11-25T01:54:44.057271-0600 - INFO - RUN_20251125_015444 - startup - Script iniciado.
2025-11-25T01:55:02.305295-0600 - INFO - RUN_20251125_015444 - first_run - No hay registro previo. Creando base de datos inicial.
2025-11-25T01:55:02.305858-0600 - INFO - RUN_20251125_015444 - hashes_created - Registro creado exitosamente.
2025-11-25T01:55:30.207458-0600 - INFO - RUN_20251125_015530 - startup - Script iniciado.
2025-11-25T01:55:36.010421-0600 - INFO - RUN_20251125_015530 - changes_detected - Cambios encontrados. Reporte: cambios_src_20251125_015530.txt
2025-11-25T01:55:40.198186-0600 - INFO - RUN_20251125_015530 - db_updated - Base de datos de hashes actualizada.
2025-11-25T01:56:31.903529-0600 - INFO - RUN_20251125_015631 - startup - Script iniciado.
2025-11-25T01:56:45.142670-0600 - INFO - RUN_20251125_015631 - changes_detected - Cambios encontrados. Reporte: cambios_src_20251125_015631.txt
2025-11-25T01:56:48.370174-0600 - INFO - RUN_20251125_015631 - db_updated - Base de datos de hashes actualizada.
2025-11-25T01:56:52.853007-0600 - INFO - RUN_20251125_015652 - startup - Script iniciado.
2025-11-25T01:57:07.452078-0600 - INFO - RUN_20251125_015652 - changes_detected - Cambios encontrados. Reporte: cambios_src_20251125_015652.txt
2025-11-25T01:57:10.040842-0600 - INFO - RUN_20251125_015652 - db_updated - Base de datos de hashes actualizada.`

## Tarea 2 (Complemento) - Motor de Hashing Nativo en PowerShell (sacar_hashes.ps1)

## Descripción general
Este script está diseñado para ser invocado por el script de Python (hashes.py). Aprovecha la integración nativa de Windows y el cmdlet Get-FileHash para calcular sumas de verificación SHA-256 de manera eficiente, maneja tanto archivos individuales como directorios completos, formatea la salida para garantizar la interoperabilidad entre PowerShell y Python.

## Objetivo
Delegar la carga computacional del cálculo de hashes al sistema operativo nativo para ganar eficiencia y reducir la complejidad del código en Python. Su función principal es entregar resultados a través de la salida estándar o escribiendo directamente en archivos de registro, asegurando una codificación de caracteres (UTF-8) compatible.
## Entradas y salidas

## Entradas esperadas:

* ruta (Obligatorio): La ruta del sistema de archivos (archivo o carpeta) a procesar.
* guardar (Opcional): Interruptor lógico ("True" o "False") que decide si el resultado se imprime en consola o se escribe en disco.
* archivo (Opcional): Ruta del archivo .json de destino. Requerido solo si -guardar es "True".

## Salidas esperadas:

Modo Consola (-guardar "False"):
1. Si es un archivo: Imprime la cadena del hash SHA-256 plano.
2. Si es una carpeta: Imprime un objeto JSON comprimido con la estructura {"nombre_archivo": "hash"}.

Modo de guardado (-guardar "True"):

1. No imprime nada en consola.
2. Crea o actualiza el archivo JSON especificado en el parámetro -archivo.

Errores: Salida de error estándar si la ruta no existe.

## Cmdlets y Utilidades utilizadas
El script utiliza comandos nativos de PowerShell (Core/Windows):

* Get-FileHash: El núcleo criptográfico, configurado para usar el algoritmo SHA256.
* ConvertTo-Json / ConvertFrom-Json: Para serializar y deserializar datos, permitiendo el intercambio de información estructurada.
* Test-Path: Para validar la existencia de rutas.
* Get-ChildItem: Para iterar sobre los archivos de un directorio.
* Set-Content / Get-Content: Para la lectura y escritura de archivos con codificación UTF-8 forzada.

## Procedimiento general

1. Configuración de Entorno: Fuerza la codificación de la consola a UTF-8 para evitar problemas con caracteres especiales (tildes, ñ) al comunicarse con Python.
2. Validación: Verifica si la ruta de entrada existe; si no, termina con error.
3. Ramificación:
   * Si es un Archivo Único: Calcula el hash.
     Si se solicita guardar: Lee el JSON existente (si hay), inserta/actualiza la entrada específica para ese archivo y guarda.
     Si no se guarda: Imprime solo el hash.
   * Si es un Directorio: Recorre todos los archivos dentro del mismo directorio.
     Si se solicita guardar: Deposita todo a un archivo JSON nuevo o sobreescribe el existente.
     Si no se guarda: Convierte la tabla a JSON string y la imprime en consola.

# Tarea 3 - Análisis Forense de Metadatos

## Descripción general
Este módulo se centra en la extracción y análisis de metadatos en diversos formatos de archivos digitales para revelar información que no es visible a simple vista, como geolocalización, autores, software de edición, fechas reales de creación y modificaciones previas, entre otros. El sistema clasifica automáticamente los resultados y los exporta a reportes CSV separados por tipo de archivo, manteniendo un registro detallado de la actividad mediante logs.

## Objetivo
Obtener evidencia digital contextual sobre el origen, historial y características técnicas de los archivos analizados. El propósito es identificar la autoría, validar la autenticidad (fechas de modificación vs. creación) y detectar posibles fugas de información sensible (como coordenadas GPS en fotografías o nombres de usuarios en documentos de ofimática).

## Entradas y salidas

## Entradas esperadas:
* Lista de Archivos (archivos.txt): Un archivo de texto plano ubicado en la carpeta metadatos/ que debe contener las rutas absolutas de los archivos a analizar (una ruta por línea).
* Archivos Objetivo: Archivos existentes en el disco con extensiones soportadas:
* Documentos: .docx, .pdf
* Imágenes: .jpg, .jpeg, .tiff, .heic
* Audio: .mp3, .wav, .flac, .ogg, entre otros.

## Salidas esperadas:

* Reportes CSV: Archivos generados en la carpeta metadatos/ conteniendo la información extraída:
  docx.csv: Metadatos de Office (Autor, Revisiones, Tiempos de edición).
  pdf.csv: Metadatos de Adobe/PDF (Creador, Productor, XMP).
  img.csv: Datos EXIF (Cámara, ISO, Apertura, GPS).
  aud.csv: Etiquetas ID3/Tags (Artista, Álbum, Año).

* Logs de Auditoría: Registro de eventos en run_metadata.log (ej. "Metadata found", "File not exists").

## Librerías utilizadas
El script integra múltiples librerías especializadas para el parsing de cada formato:

* python-docx: Para acceder a las Core Properties de documentos Word.
* PyPDF2: Para la extracción de diccionarios de info y XMP en PDFs.
* PIL (Pillow) & piexif: Para la manipulación de imágenes y decodificación de datos EXIF (incluyendo cálculos matemáticos para convertir coordenadas GPS a formato decimal).
* mutagen: Para el manejo versátil de etiquetas de metadatos en archivos de audio.
* loguru: Para la gestión estructurada de logs.
* csv: Para la generación de reportes.

## Procedimiento general

1. Configuración inicial: Se crean los directorios de salida y se inicializan los archivos CSV con sus respectivos encabezados si no existen.
2. Lectura de fuentes: El script lee el archivo metadatos/archivos.txt y carga la lista de rutas a procesar.
3. Iteración y clasificación: Recorre cada archivo, valida su existencia e identifica su extensión para seleccionar el extractor adecuado (metadata_docx, metadata_pdf, metadata_exif o metadata_audio).
4. Extracción y conversión:
   * Se extraen los datos crudos.
   * Se realizan conversiones de formato (bytes a string, fechas a formato legible, coordenadas GPS sexagesimales a decimales).
5. Filtrado: Se utiliza la función checar_vacio para asegurar que no se guarden registros de archivos que no contienen metadatos útiles.
6. Reporte: Los datos válidos se escriben en el CSV correspondiente y el evento se registra en el log.

## Ejemplo de uso

1. Se ejecuta metadatos.py.
2. Resultado en img.csv (Ejemplo de fila generada):

`| Archivo | Fecha analisis | Fabricante | Modelo | Software | Fecha captura | ISO | Exposicion | Apertura | GPS latitud | GPS longitud | GPS altitud|
example.jpg	2025-11-22 03:51:33 UTC	Apple	iPhone 4	Microsoft Windows Photo Viewer 6.1.7600.16385	7/16/2012 12:13	80	(1, 2011)	(14, 5)	27.757	-15.56916667	(22411, 559)`

Resultado en log:
`INFO - RUN_2023... - checking_file - Checando la metadata de contrato_final.docx
INFO - RUN_2023... - saving_CSV - Guardando los metadatos correspondientes en docx.csv
INFO - RUN_2023... - checking_file - Checando la metadata de vacaciones.jpg
INFO - RUN_2023... - saving_CSV - Guardando los metadatos correspondientes en img.csv`


