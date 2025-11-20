# Plan de uso AI.

## Uso esperado:
* Interpretación de los resultados.
* Retroalimentación para posible mejora de código/hacerlo más eficiente.

## Integración:

* Generalizada una vez el proyecto esté terminado, enfocándose en la tercera tarea (metadata).

## Tipo de modelo/API a utilizar:

API de Open AI, modelo: GPT-5


## Prompt inicial esperado para usar:

Tu tarea es analizar el código y los logs proporcionados a continuación, y ofrecer un informe detallado.

**El análisis debe abarcar tres secciones principales:**

### 1. Análisis y explicación del código
* Describe la **función principal** del código y el **flujo lógico** general.
* Identifica los **componentes clave**, clases, o funciones.
* Determina la **complejidad algorítmica** (Big O) de las secciones críticas o bucles, si aplica.

### 2. Retroalimentación y sugerencias de mejora
* Proporciona **sugerencias de refactorización** para mejorar la legibilidad y mantenibilidad (ej. nombres de variables, división de funciones).
* Identifica **posibles *bugs*** o **fallos de seguridad**.
* Ofrece recomendaciones específicas de **optimización de rendimiento**.
* Asegura que el código sigue las **mejores prácticas** y **patrones de diseño** del lenguaje especificado.

### 3. Interpretación de Logs 
* Analiza los logs proporcionados e identifica cualquier **error**, **advertencia** (*warning*), o **comportamiento inusual**.
* Explica las **causas probables** de los problemas encontrados en los logs y cómo se relacionan con el código.
* Ofrece **pasos de acción** concretos para corregir los problemas de los logs.

**A continuación, proporciono el código y los logs para el análisis:**

---
**[CÓDIGO A SER ANALIZADO]**
  (Aquí ponemos los códigos a que analice)


**[LOGS A SER INTERPRETADOS]**
  (Los logs a interpretar.)

