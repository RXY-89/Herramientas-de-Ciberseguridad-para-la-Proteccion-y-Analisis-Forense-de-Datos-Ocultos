# REPORTE FINAL PIA

# Propósito del proyecto.

Este proyecto tiene como objetivo principal desarrollar un ecosistema de utilidades enfocadas en la ciberseguridad defensiva (Blue Team) y el Análisis Forense Digital (DFIR). Sus misiiones son: Proteger la información crítica (o revelarla) y analizar evidencia digital.

El alcance del proyecto cubre tres pilares fundamentales:

* Esteganografía: Uso de técnicas de ocultamiento de mensajes para garantizar la confidencialidad. También se usará para revelar posible información oculta en algún medio (carrier).
* Integridad de Datos: Verificación de archivos mediante el cálculo de hashes para detectar corrupciones o manipulaciones no autorizadas.
* Análisis de Metadatos: Examen forense de la metadata para identificar trazas de modificación, autoría, ubicaciones, tiempos de edición entre otros datos que puedieran ser de importancia.

La arquitectura del proyecto ha sido refactorizada para integrar todas las herramientas en un flujo de trabajo unificado. A diferencia de versiones anteriores, ahora todos los módulos están integrados por un script central (main.py), eliminando la ejecución aislada de cada uno de ellos.
# Estado del proyecto

Actualmente, el proyecto ha pasado de ser scripts individuales a una aplicación modular y más centralizada. La arquitectura se basa ahora en un flujo de trabajo unificado donde todos los componentes operan bajo un mismo entorno de ejecución (el main.py).

* Arquitectura Centralizada: El núcleo del sistema es el script main.py, el cual actúa como orquestador. Ya no se ejecutan scripts por separado; en su lugar, main.py importa y llama a los demás archivos como funciones nativas, pasando argumentos y gestionando el flujo de datos entre ellos.
* Integración Híbrida: Se mantiene y optimiza la interacción entre Python y PowerShell. El módulo hashes.py actúa como el principal encargado de la tarea de hashes de archivos, ejecutando el script sacar_hashes.ps1 para aprovechar la velocidad de hash de Powershell, devolviendo los resultados al entorno de Python.

## Estructura actual de archivos:


main.py (El script principal e integrador)

steganografia.py (Funciones de ocultamiento o revelación)

metadatos.py (Funciones de análisis)

hashes.py (Wrapper de integridad)

sacar_hashes.ps1 (Motor de hash en PowerShell para la extracción delos hashes de distintos archivos)

AI_INT.py (Módulo de Inteligencia Artificial, encargado de la retroalimentación, requiere una API key que se le pueda proporcionar)


# Actualización del proyecto.

## Potenciado por Inteligencia Artificial.
La gran novedad de esta versión es la implementación de un módulo de Inteligencia Artificial (AI_INT.py) dentro de main.py que transforma la herramienta en una forma de retroalimentación continua:

* Análisis de Logs: Interpreta los resultados y registros generados por los scripts de auditoría, proporcionando resúmenes en lenguaje natural sobre la integridad y seguridad de los archivos.
* Optimización de Código: Revisa el código fuente del propio proyecto para sugerir mejoras, refactorizaciones y parches de seguridad.
