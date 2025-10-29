## Tarea 1 
**Título:** Ocultamiento y Detección de Información Mediante Esteganografía. 
**Propósito:** Desarrollar una herramienta para insertar datos secretos dentro de un archivo carrier y otra para detectar o extraer el mensaje oculto. 
**Rol o área relacionada:** DFIR / Blue Team (análisis de malware) 
**Entradas esperadas:** Carrier: Archivo de imagen, audio o PDF (ejemplo: img.png, chaos.wav, cassie_explained.pdf ). Mensaje: Archivo de texto (secreto.txt). 
**Salidas esperadas:** Archivo original: Archivo carrier con el mensaje oculto (por ejemplo estego.png). Extracción: Archivo de texto con el mensaje recuperado (mensaje_extraido.txt). 
**Descripción del procedimiento:** Implementar una función para introducir el mensaje en el carrier y otra función inversa para revelarlo. 
**Complejidad técnica:** Librerías, además del parsing de formatos de archivo. 
**Controles éticos:** Uso exclusivo de imágenes y archivos de texto creados por el equipo para ese fin en específico. 
**Dependencias:** Librerías en Python: Pillow. 
//Commit hecho por Xochilpilli Castillo Andrade.
  
### Tarea 2
- **Título**: Utilería de Protección de Datos: Cifrado Simétrico y Hashing Forense con PowerShell
- **Propósito**: Crear un script para generar y verificar hashes criptográficos SHA-256 de archivos usando PowerShell. 
- **Rol o área relacionada**: Blue Team (en protección de datos) / DFIR (en este caso como análisis de integridad).
- **Entradas esperadas**: Directorio (Ruta): (ejemplo C:\Datos\Carpeta).
- **Salidas esperadas**: Hashes de los archivos (json): (ejemplo: hashes_carpeta.json) 
Reporte de cambios (txt): (ejemplo: cambios_carpeta_20251027095007.txt) 
- **Descripción del procedimiento**: Se le dará una ruta a un directorio al script y este procederá a buscarlo, checa si lo ha analizado antes viendo si tiene un archivo almacenando los hashes de este, y si no, los saca, los guarda y termina, de lo contrario, también los saca, los compara, y si nota alguna diferencia las anota a un archivo de texto, para sacar los hashes usa Get-FileHash de PowerShell, con un ciclo for sobre el directorio a analizar.  
- **Complejidad técnica**:  Criptografía, automatización de tareas de seguridad, integración con shell (se usará Powershell).
- **Controles éticos**: Solo se analizarán y hashearán archivos designados para ese propósito en específico sin información sensible en ellos.
- **Dependencias**: Librerías en Python:  json y pathlib Entorno: Sistema operativo Windows con PowerShell 5.1 o superior disponible. Comando: Get-FileHash de PowerShell.

### Tarea 3
- **Título**: Análisis Forense de Metadatos  
- **Propósito**: Desarrollar una utilidad para extraer, analizar y generar reportes legibles a partir de los metadatos de archivos comunes. 
- **Rol o área relacionada**: DFIR
- **Entradas esperadas**: Archivos objeto de análisis: Una lista de rutas a archivos de imagen (evidencia.jpg), documentos (reporte.docx) o PDF (contrato.pdf).
- **Salidas esperadas**: Reporte Estructurado (CSV): Un archivo con los campos de metadatos más relevantes extraídos de cada archivo analizado (reporte_metadata.csv). Las columnas incluirán: Nombre_Archivo, Ruta, Autor, Fecha_Creacion, Software, GPS_Latitud, etc.  
- **Descripción del procedimiento**: La tarea recibirá las rutas de los archivos. Utilizará librerías dedicadas para leer y parsear los metadatos de los archivos. Extraerá los campos designados y, al finalizar el análisis, escribirá todos los resultados en un archivo CSV, donde cada fila corresponderá a un archivo analizado. 
- **Complejidad técnica**: Parsing de formatos de archivo, librerías especializadas en parsing de metadatos, estructuración y escritura en CSV.
- **Controles éticos**: Solo se utilizarán archivos generados por nuestro el equipo o archivos de ejemplo libres de derechos. Se omitirá cualquier dato que pudiera identificarse como real. 
- **Dependencias**: Librerías en Python:  Librerías en Python: csv (para la escritura del reporte), Pillow (para EXIF de imágenes), librerías específicas para documentos en caso de que nos sean necesarias. 
