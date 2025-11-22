import os
from openai import OpenAI

def gestionar_api_key():
    nombre_archivo_key = "api_key.txt"
    
    if os.path.exists(nombre_archivo_key):
        with open(nombre_archivo_key, "r") as f:
            api_key = f.read().strip()
            if not api_key:
                print(f"El archivo {nombre_archivo_key} está vacío.")
                return gestionar_api_key()
            return api_key
    else:
        print("--- Configuración Inicial ---")
        api_key = input("Introduce tu API Key de OpenAI: ").strip()
        with open(nombre_archivo_key, "w") as f:
            f.write(api_key)
        print(f"API Key guardada exitosamente en '{nombre_archivo_key}'.\n")
        return api_key

def obtener_contenido_archivo():
    while True:
        ruta = input("Introduce la ruta de la carpeta (o '.' para la actual): ").strip()
        nombre = input("Introduce el nombre del archivo a analizar (ej. script.py): ").strip()
        
        ruta_completa = os.path.join(ruta, nombre)
        
        if os.path.exists(ruta_completa) and os.path.isfile(ruta_completa):
            try:
                with open(ruta_completa, "r", encoding='utf-8') as f:
                    contenido = f.read()
                return nombre, contenido
            except Exception as e:
                print(f"Error al leer el archivo: {e}")
        else:
            print(f"Error: No se encontró el archivo en: {ruta_completa}. Intenta de nuevo.\n")

def analizar_con_gpt(cliente, contenido):

    print("\nEnviando datos a OpenAI para análisis (esto puede tardar unos segundos)...")
    
    instrucciones = """
    Tu tarea es analizar el código y los logs proporcionados a continuación, y ofrecer un informe detallado.
    El análisis debe abarcar tres secciones principales:
    1. Análisis y explicación del código
    Describe la función principal del código y el flujo lógico general.
    Identifica los componentes clave, clases, o funciones.
    Determina la complejidad de las secciones críticas o bucles, si aplica.
    2. Retroalimentación y sugerencias de mejora
    Proporciona sugerencias de refactorización para mejorar la legibilidad y mantenibilidad (como nombres de variables, división de funciones).
    Identifica posibles bugs o fallos de seguridad.
    Ofrece recomendaciones específicas de optimización de rendimiento.
    Asegura que el código sigue las mejores prácticas y patrones de diseño del lenguaje especificado.
    3. Interpretación de Logs
    Analiza los logs proporcionados e identifica cualquier error, advertencia, o comportamiento inusual que se pueda presentar.
    Explica las causas probables de los problemas encontrados en los logs y cómo se relacionan con el código.
    Ofrece pasos de acción concretos para corregir los problemas de los logs.
    """

    try:
        response = cliente.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": instrucciones},
                {"role": "user", "content": f"Aquí está el contenido del archivo a analizar:\n\n{contenido}"}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al conectar con la API de OpenAI: {e}"

def guardar_y_mostrar_resultado(nombre_origen, analisis):
    print("\n" + "="*40)
    print("RESPUESTA DE GPT:")
    print("="*40 + "\n")
    print(analisis)
    print("\n" + "="*40)
    carpeta_destino = "AI_int"
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
        print(f"Carpeta '{carpeta_destino}' creada.")

    nombre_reporte = f"analisis_{nombre_origen}.txt"
    ruta_reporte = os.path.join(carpeta_destino, nombre_reporte)

    try:
        with open(ruta_reporte, "w", encoding='utf-8') as f:
            f.write(analisis)
        print(f"\n[Exito] El análisis se ha guardado en: {ruta_reporte}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

def main():
    api_key = gestionar_api_key()
    cliente = OpenAI(api_key=api_key)
    nombre_archivo, contenido_archivo = obtener_contenido_archivo()
    resultado = analizar_con_gpt(cliente, contenido_archivo)
    guardar_y_mostrar_resultado(nombre_archivo, resultado)

if __name__ == "__main__":
    main()
