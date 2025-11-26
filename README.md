# Herramientas-de-Ciberseguridad-para-la-Proteccion-y-Analisis-Forense-de-Datos-Ocultos
Este proyecto tiene como propósito desarrollar un conjunto de utilidades para proteger la información mediante técnicas de cifrado y ocultamiento (esteganografía), así como para analizar "forensemente2 archivos en busca de datos ocultos o evidencia (metadatos). Se abordarán tareas de ciberseguridad defensiva (Blue Team) y de Análisis Forense/DFIR. 

Nos enfocaremos en el uso de la esteganografía como un medio para ocultamiento de mensajes y el uso de los hashes de los archivos para la verificación de integridad de los mismos, por último emplearemos la metadata para poder marcar si el archivo ha sido o no modificado.

# INTEGRANTES Y ROLES DENTRO DEL PROYECTO.

1. Xochilpilli Castillo Andrade
   * Mantenimiento del repositorio, generación de los archivos de prueba del equipo, redacción del propuesta.md, reportes y README.md. Coordinación general. 
3. Simón Wenceslao Robledo Solís
   * Implementación del hashing con PowerShell y el parser de metadatos, además de algunas pruebas y correcciones de código.
5. Ian Haziel Gómez Ochoa
   * Desarrollo del módulo de detección basado en la esteganografía y AI_INT.py. 


# Estructura del repositorio

1. src:
   * main.py (El script principal e integrador).
   * steganografia.py (Funciones de ocultamiento o revelación).
   * metadatos.py (Funciones de análisis).
   * hashes.py (El script de integridad).
   * sacar_hashes.ps1 (Motor de hash en PowerShell para la extracción delos hashes de distintos archivos).
   * AI_INT.py (Módulo de Inteligencia Artificial, encargado de la retroalimentación, requiere una API key que se le pueda proporcionar).
2. docs:
   * Toda documentación del avance del proyecto.
3. examples:
   * Cualquier acrhivo de prueba creado para usar en el proyecto, además de los logs y salidas generadas.
4. proposals:
   * Contiene la propuesta inicial del proyecto.

# Estado final del repositorio:

Implementación de AI_INT.py a main.py, además de completar el módulo para que ambos tuvieran sus propios logs, en caso de AI_INT.py también la redacción de la solicitud a GPT-5 fue mejorada, todos los módulos funcionan de forma adecuada para su propósito y se integran correctamente dentro de main.py. Dichos módulos, sus descripciones y demás detalles se verán a continuación:



# Tarea 1 - Ocultamiento y Detección de Información mediante Esteganografía
## Descripción general
Este módulo implementa técnicas de esteganografía digital para establecer canales de comunicación encubiertos. El script permite ocultar mensajes de texto plano dentro de archivos multimedia (imágenes y audio) y documentos (PDF) sin alterar significativamente su percepción visual o auditiva. Adicionalmente, cuenta con un sistema de registro (logging) que almacena un historial de los mensajes procesados en formato JSONL para fines de auditoría o recuperación. A diferencia de versiones básicas, esta herramienta implementa un sistema robusto de auditoría: todas las salidas y registros se centralizan automáticamente en una carpeta dedicada (estega_salidas). El sistema soporta operaciones tanto en archivos individuales como en lotes (directorios completos), permitiendo escanear carpetas enteras en busca de mensajes ocultos.

## Objetivo
Proveer un mecanismo seguro para el transporte de mensajes encubiertos y, simultáneamente, ofrecer capacidades forenses para la detección de dichos mensajes. El objetivo secundario es mantener una trazabilidad completa de las acciones realizadas mediante logs técnicos detallados y un historial de hallazgos persistente.

## Entradas y salidas

## Entradas esperadas:

1. Archivos Portadores:
   * Imágenes: .png (Manipulación de píxeles RGB), .jpg/.webp (Inyección en metadatos EXIF).
   * Audio: .wav (Esteganografía LSB - Least Significant Bit).
   * Documentos: .pdf (Manipulación de metadatos del documento).
2. Modo de Entrada: Ruta a un archivo específico o ruta a una carpeta (para búsqueda masiva en modo revelar).
3. Mensaje: Texto a ocultar (Nota: En formato PNG, el límite actual es de 255 caracteres).

## Salidas esperadas:

1. Archivos Esteganografiados: Se guardan automáticamente en la carpeta estega_salidas con el sufijo _2 (ej. imagen_2.png), evitando sobrescribir los originales.
2. Logs de Aplicación (app_log.jsonl): Registro técnico de errores y eventos de ejecución en formato JSON.
3. Registro de Hallazgos (mensajes.jsonl): Base de datos acumulativa de todos los mensajes interceptados o revelados exitosamente.

## Librerías utilizadas
El script ha actualizado sus dependencias para optimizar la compatibilidad y el manejo de metadatos:

* PIL (Pillow): Manipulación de imágenes (lectura/escritura de píxeles).
* piexif: Gestión específica de metadatos EXIF para formatos JPG y WEBP.
* pypdf: (Reemplaza a PyMuPDF) Para lectura y escritura de estructuras PDF estándar.
* wave y struct: Manipulación nativa de archivos de audio WAV a nivel de byte.
* logging y json: Para la generación de logs estructurados y serialización de datos.

## Procedimiento general

1. Inicialización de Entorno: El script verifica la existencia de librerías críticas y crea el directorio estega_salidas si no existe. Configura el logger para escribir en formato JSONL.
2. Selección de Flujo: El usuario decide entre Ocultar (1) o Revelar (2).
3. Ocultamiento:
   * Se valida el archivo de entrada.
   * Se aplica el algoritmo correspondiente según la extensión (LSB para Audio, Píxeles para PNG, Metadatos para PDF/JPG).
   * El archivo resultante se guarda automáticamente en la carpeta de salidas.
4. Revelado:
   * El usuario puede introducir la ruta de un solo archivo o de una carpeta entera.
   * Si es carpeta, el script itera sobre todos los archivos compatibles.
   * Intenta extraer información oculta usando la lógica inversa del ocultamiento.
   * Si encuentra un mensaje, lo muestra en consola y lo registra en mensajes.jsonl.


## Ejemplo de uso

Escenario: Ocultar un mensaje en un audio.

1. Menú:
   Usuario selecciona `1. Ocultar mensaje -> 2. Audio (.wav).`
3. Entrada: C:\Musica\grabacion_original.wav
4. Mensaje: `Código Rojo`

Salida en consola:

`¡Éxito! Guardado en: ...\estega_salidas\grabacion_original_2.wav`

Escenario: Escaneo forense de una carpeta de imágenes.

1. Menú:
   Usuario selecciona `2. Revelar mensaje -> 1. Imagen (...).`
3. Entrada: `C:\Sospechosos\Fotos_Vacaciones.`
4. Proceso: El script detecta que es un directorio y activa el modo para procesar todos los archivos.

Salida en consola:

`Escaneando carpeta: C:\Sospechosos\Fotos_Vacaciones`
`> ENCONTRADO en playa_2.png: Coordenadas de encuentro`
 `> ENCONTRADO en montaña_2.jpg: 123456`
`[+] Hallazgo guardado en: ...\estega_salidas\mensajes.jsonl`
`Proceso finalizado. 2 mensajes encontrados.`



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

* Integridad de los archivos: Archivos JSON almacenados en la carpeta hashes/ que contienen los pares archivo-hash de referencia (ej. hashes_nombre_carpeta.json o lista_hashes.json).
* Logs de auditoría: Registro detallado de eventos en run.log gestionado por la librería loguru.
* Reportes de incidentes: Archivos de texto (cambios_...txt) generados automáticamente cuando se detectan discrepancias.
* Alertas en consola: Avisos visuales inmediatos sobre el estado de la integridad (Íntegro, Modificado, Nuevo, Eliminado).

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

Modo consola (-guardar "False"):
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
   * Si es un archivo único: Calcula el hash.
     Si se solicita guardar: Lee el JSON existente (si hay), inserta/actualiza la entrada específica para ese archivo y guarda.
     Si no se guarda: Imprime solo el hash.
   * Si es un directorio: Recorre todos los archivos dentro del mismo directorio.
     Si se solicita guardar: Deposita todo a un archivo JSON nuevo o sobreescribe el existente.
     Si no se guarda: Convierte la tabla a JSON string y la imprime en consola.




# Tarea 3 - Análisis Forense de Metadatos

## Descripción general
Este módulo se centra en la extracción y análisis de metadatos en diversos formatos de archivos digitales para revelar información que no es visible a simple vista, como geolocalización, autores, software de edición, fechas reales de creación y modificaciones previas, entre otros. El sistema clasifica automáticamente los resultados y los exporta a reportes CSV separados por tipo de archivo, manteniendo un registro detallado de la actividad mediante logs.

## Objetivo
Obtener evidencia digital contextual sobre el origen, historial y características técnicas de los archivos analizados. El propósito es identificar la autoría, validar la autenticidad (fechas de modificación vs. creación) y detectar posibles fugas de información sensible (como coordenadas GPS en fotografías o nombres de usuarios en documentos de ofimática).

## Entradas y salidas

## Entradas esperadas:
* Lista de archivos (archivos.txt): Un archivo de texto plano ubicado en la carpeta metadatos/ que debe contener las rutas absolutas de los archivos a analizar (una ruta por línea).
* Archivos objetivo: Archivos existentes en el disco con extensiones soportadas:
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



# Complemento - Integración de Inteligencia Artificial para auditoría (AI_INT.py).

## Descripción

Este módulo actúa como una especide de retroalimentación usando una API de OpenAI, permitiendo enviar el contenido de scripts (código fuente) o archivos de registro (logs) a GPT-5 (en el caso de este proyecto, se peude ajustar el modelo que uno busque usar). El script gestiona la autenticación mediante API Key, la lectura segura de archivos locales y la persistencia de los análisis generados. A diferencia de versiones anteriores, esta actualización introduce un sistema de procesamiento por lotes y escaneo recursivo por si se quiere escanear más, es decir, el script permite al usuario construir una "cola de análisis" agregando múltiples archivos o directorios completos. El sistema filtra automáticamente archivos binarios o irrelevantes, envía el contenido a la nube para su interpretación y genera reportes detallados sobre la calidad del código, seguridad y eventos encontrados en los logs. Está hecho para solo leer los archivos de extensión: .py, .ps1, .jsonl, .txt, .log y .json, para evitar que lea los reportes que podrían contener información sensible que no se quiera compartir con la AI.

## Objetivo
Potenciar las capacidades del analista humano mediante automatización de la labor del analista de seguridad (Blue Team) mediante la revisión masiva de código y logs. Enfocado principalmente a:

* Auditoría de código escalonable: Revisa repositorios enteros o múltiples scripts en una sola ejecución para detectar bugs o vulnerabilidades.
* Inteligencia de Amenazas en Logs: Procesar múltiples archivos de registro (logs) simultáneamente para correlacionar eventos, identificar anomalías, errores o alertas de seguridad sin necesidad de revisión manual línea por línea.

## Entradas y salidas

## Entradas esperadas:

* Credenciales: API Key de OpenAI (se solicita una única vez y se guarda localmente en api_key.txt).
* Rutas de origen: El usuario puede ingresar múltiples rutas (archivos individuales o carpetas).
* Contexto automático: El script inyecta un System Prompt predefinido que instruye a la IA para actuar como un experto en ciberseguridad y desarrollo.
* Filtros de extensión: El sistema solo procesa archivos de texto permitidos: .py, .ps1, .jsonl, .txt, .log, .json.

## Salidas esperadas:

* Reportes de IA: Un archivo de texto independiente por cada archivo analizado, conteniendo la evaluación completa (explicación, mejoras y análisis de Logs).
* Registro de las operaciones en el script: Log interno del propio script que audita qué archivos fueron procesados, ignorados o si hubo errores de conexión.
* Consola: Vista previa del análisis y progreso del procesamiento.

## Librerías utilizadas

* openai: Cliente oficial para comunicar con la API de OpenAI (GPT-5).
* logging: Para la creación del registro de auditoría interno del script.
* pathlib y os: Para la navegación recursiva de los directorios, filtrado de extensiones y manipulación de rutas.
* datetime: Para el timestamping de los reportes generados.

## Procedimiento general

1. Configuración y autenticación: Verifica o solicita la API Key. Crea el directorio de trabajo AI_int si no existe.
2. Construcción de la cola:
   * El usuario ingresa rutas interactivamente.
   * Si es una carpeta, el script la explora recursivamente, omitiendo directorios de sistema (ej. .git, __pycache__).
   * Si es un archivo, verifica que la extensión sea válida y que la codificación sea UTF-8 (evitando binarios).
   * Todos los archivos válidos se agregan a una lista maestra de procesamiento.
3. Procesamiento por lotes:
   * El script procesa la cola de archivos.
   * Envía el contenido a la API con un prompt de experto en Ciberseguridad/DFIR.
   * Recibe la respuesta estructurada.
4. Guardado: Guarda el reporte completo con nombre y fecha, y muestra un resumen en pantalla.

## Ejemplo de uso

Escenario: Auditoría completa de un proyecto.

1. Inicio: El usuario ejecuta AI_INT.py.
2. Selección de Objetivo (Cola):
   * Introduce ruta: C:\Proyectos\Modulo_Cripto (Carpeta)
   * Salida: `"Explorando carpeta... Se agregaron 5 archivos válidos."
     ¿Deseas agregar otra ruta? (s/n): s`
   * ``Introduce ruta:` C:\Logs\error_ayer.log
   * Salida: `"Archivo agregado."`
3. Ejecución del Batch:

`--- INICIANDO ANÁLISIS DE 6 ARCHIVOS ---
Procesando 1/6... -> Generando reporte para hash_lib.py...
Procesando 2/6... -> Generando reporte para main.py...`

4. Resultados:
   * En consola: Muestra los primeros 600 caracteres de cada análisis.
   * En carpeta AI_int/: Se generan 6 archivos de texto (ej. `IA_hash_lib_py_123045.txt`) con las recomendaciones e interpretaciones.



# Declaración Ética.

## 1. Propósito Educativo y Defensivo

Este proyecto ha sido desarrollado estrictamente con fines educativos y para el entrenamiento en ciberseguridad defensiva (Blue Team). El objetivo principal es proporcionar herramientas para:

1. Comprender el funcionamiento de información oculta mediante esteganografía para mejorar su detección.
2. Automatizar tareas de análisis forense digital (DFIR) para la verificación de integridad y auditoría de metadatos.
3. Explorar el uso de Inteligencia Artificial como asistente en la auditoría de código seguro.


## 2. Límites de uso autorizado

El uso de este software está limitado exclusivamente a:
* Entornos de laboratorio aislados y controlados.
* Equipos y redes propiedad del usuario.
* Sistemas de terceros sobre los cuales el usuario cuente con autorización explícita y por escrito para realizar pruebas de seguridad o auditoría.

**Queda estrictamente prohibido utilizar estas herramientas para ocultar malware, exfiltrar información confidencial sin consentimiento, violar la privacidad de terceros o alterar la integridad de sistemas ajenos.**


## 3. Aviso sobre el módulo de Inteligencia Artificial.

El módulo AI_INT.py utiliza la API de OpenAI para procesar información. El usuario debe ser consciente de lo siguiente:

* Privacidad de datos: Al utilizar este módulo, fragmentos de código y registros (logs) son enviados a servidores de terceros.

**ADVERTENCIA**: Se recomienda encarecidamente NO enviar credenciales reales, claves privadas, información de identificación personal (PII) o datos corporativos sensibles a través de este módulo. El autor no se hace responsable por la exposición de datos confidenciales enviados voluntariamente por el usuario a la API, el módulo específicamente está hecho para evitar leer cualquier formato que no sea los usados para el logging y para los scripts. La modificación de este para que lea otros formatos que podrían accidentalmente contener información que no debería compartirse cae bajo responsabilidad de quien lo use.

## 4. Exención de responsabilidad

El código se proporciona "tal cual", sin garantía de ningún tipo. El autor y los colaboradores de este repositorio no se hacen responsables de:

1. Daños directos o indirectos causados a sistemas informáticos.
2. Pérdida de información derivada del uso de las herramientas de esteganografía o manipulación de archivos.
3. Consecuencias legales resultantes del uso indebido, ilícito o no ético de este código.

***El usuario final asume la responsabilidad total de sus acciones y del cumplimiento de las leyes locales e internacionales aplicables en materia de delitos informáticos y privacidad de datos.***
