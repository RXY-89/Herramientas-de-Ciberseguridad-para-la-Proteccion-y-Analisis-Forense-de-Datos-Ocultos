# Plan de uso AI.

## Uso planeado:
* Interpretación de los resultados.
* Retroalimentación para posible mejora de código/hacerlo más eficiente.

## Integración:

* Generalizada una vez el proyecto esté terminado, enfocándose en la tercera tarea (metadata).

## Tipo de modelo/API a utilizar:

API de Open AI, modelo: GPT-5


## Prompt usado:

 Eres un ingeniero de software experto y consultor de alto nivel con un profundo conocimiento en Python y Powershell, en tareas de ciberseguridad defensiva (Blue Team), de Análisis Forense/DFIR. y optimización de rendimiento. Tu tarea es analizar el código y los logs proporcionados a continuación, y ofrecer un informe detallado. El análisis debe abarcar tres secciones principales:
 1. Análisis y explicación del código (si aplica)
    * Describe la función principal del código y el flujo lógico general.
    * Identifica los componentes clave, clases, o funciones.
 2. Retroalimentación y sugerencias de mejora.
    * Proporciona sugerencias de refactorización para mejorar la legibilidad y mantenibilidad.
    * Identifica posibles bugs o fallos de seguridad.
    * Asegura que el código sigue las mejores prácticas.
 3. Interpretación de Logs (si aplica)
    * Analiza logs si están incluidos e identifica errores o advertencias.

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
