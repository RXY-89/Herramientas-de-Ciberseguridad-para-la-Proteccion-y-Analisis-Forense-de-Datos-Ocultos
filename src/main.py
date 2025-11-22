import sys
import subprocess
import os
import time
from pathlib import Path
from datetime import datetime

# Detectamos la carpeta donde está ESTE archivo main.py
BASE_DIR = Path(__file__).parent.resolve()

def limpiar_pantalla():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def ejecutar_modulo_interactivo(nombre_script):
    """
    Ejecuta el script permitiendo que el usuario interactúe con él manualmente.
    Usa '-u' para evitar el buffering.
    """
    ruta_script = BASE_DIR / nombre_script
    if not ruta_script.exists():
        print(f"Error: No se encuentra {nombre_script} en {BASE_DIR}")
        return

    print(f"--- Iniciando {nombre_script} ---\n")
    try:
        subprocess.run([sys.executable, '-u', str(ruta_script)], cwd=str(BASE_DIR))
    except Exception as e:
        print(f"Error al lanzar el script: {e}")

def ejecutar_modulo_automatico(nombre_script, input_texto):
    """
    Ejecuta el script en segundo plano enviándole las respuestas automáticamente.
    """
    ruta_script = BASE_DIR / nombre_script
    if not ruta_script.exists():
        return f"Error: No existe {nombre_script}", ""

    try:
        # Configuración de entorno para UTF-8
        env_vars = os.environ.copy()
        env_vars["PYTHONIOENCODING"] = "utf-8"

        process = subprocess.Popen(
            [sys.executable, str(ruta_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',        
            errors='replace', 
            cwd=str(BASE_DIR),
            env=env_vars
        )
        
        # Enviamos el texto (Input)
        stdout, stderr = process.communicate(input=input_texto)
        return stdout, stderr

    except Exception as e:
        return "", f"Error crítico en subprocess: {e}"

def buscar_ultimo_reporte_cambios():
    try:
        # Buscamos archivos que empiecen con "cambios_" y terminen en ".txt"
        archivos_reporte = list(BASE_DIR.glob("cambios_*.txt"))
        
        if not archivos_reporte:
            return None
            
        # Ordenamos por fecha de modificación (el más nuevo al final)
        ultimo_reporte = max(archivos_reporte, key=os.path.getctime)
        
        # Verificar que sea reciente (menos de 1 minuto)
        if (datetime.now().timestamp() - os.path.getctime(ultimo_reporte)) < 60:
            return ultimo_reporte
        return None
    except Exception as e:
        print(f"Error buscando reporte: {e}")
        return None

def leer_archivos_modificados_del_reporte(ruta_txt):
    """Lee el TXT generado por hashes.py y extrae nombres de archivos."""
    modificados = []
    if not ruta_txt: return []
    
    try:
        with open(ruta_txt, "r", encoding="utf-8") as f:
            for linea in f:
                # Tu hashes.py escribe: "El archivo foto.jpg ha sido modificado."
                # O: "El archivo documento.pdf ha sido eliminado."
                if "ha sido modificado" in linea:
                    # Extraemos lo que está entre "archivo " y " ha sido"
                    partes = linea.split("archivo ")
                    if len(partes) > 1:
                        nombre = partes[1].split(" ha sido")[0].strip()
                        modificados.append(nombre)
    except Exception as e:
        print(f"Error leyendo reporte: {e}")
        
    return modificados

def generar_lista_archivos(ruta_analisis):
    """Genera el archivo.txt necesario para metadatos.py"""
    carpeta_meta = BASE_DIR / "metadatos"
    carpeta_meta.mkdir(parents=True, exist_ok=True)
    archivo_txt = carpeta_meta / "archivos.txt"
    
    archivos = []
    ruta = Path(ruta_analisis)
    
    if not ruta.exists(): return []

    if ruta.is_file():
        archivos.append(str(ruta.resolve()))
    else:
        for item in ruta.rglob("*"):
            if item.is_file():
                archivos.append(str(item.resolve()))
    
    with open(archivo_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(archivos))
    return archivos

def inyectar_nota(archivo):
    """Intenta inyectar la nota de modificación."""
    try:
        import piexif, fitz
        from mutagen.easyid3 import EasyID3
        from mutagen.mp3 import MP3
        from PIL import Image
    except ImportError:
        return 

    ruta = Path(archivo)
    marca = f" [MODIFICADO: {datetime.now().strftime('%Y-%m-%d')}]"
    
    try:
        if not ruta.exists(): return
        suffix = ruta.suffix.lower()
        
        if suffix in ['.jpg', '.jpeg']:
            img = Image.open(ruta)
            if "exif" in img.info:
                try:
                    exif_dict = piexif.load(img.info["exif"])
                    curr = exif_dict["0th"].get(270, b"").decode(errors="ignore")
                    exif_dict["0th"][270] = (curr + marca).encode("utf-8")
                    img.save(ruta, exif=piexif.dump(exif_dict))
                    print(f"Etiqueta inyectada en imagen: {ruta.name}")
                except: pass
        
        elif suffix == '.pdf':
            doc = fitz.open(ruta)
            meta = doc.metadata
            meta["keywords"] = (meta.get("keywords","") + marca).strip()
            doc.set_metadata(meta)
            doc.saveIncr()
            print(f"Etiqueta inyectada en PDF: {ruta.name}")

    except Exception:
        pass 

def modo_automatico():
    print("\n---MODO AUTOMÁTICO ---")
    ruta_raw = input("Ingrese la ruta a analizar: ").strip().strip('"')
    
    if not os.path.exists(ruta_raw):
        print("La ruta proporcionada no existe.")
        input("Enter para volver...")
        return

    # 1. ESTO ES PARA LO DE HASHEs
    print("\nPaso 1: Verificación de Hashes...")
    
    input_data = f"{ruta_raw}\nn\n" 
    
    out, err = ejecutar_modulo_automatico("hashes.py", input_data)
    if err:
        print("Advertencias/Errores de hashes.py:")
        print(err)
    archivos_modificados = []
    if "detectado cambios" in out:
        print("Hashes.py reportó cambios. Buscando reporte.")
        ruta_reporte = buscar_ultimo_reporte_cambios()
        if ruta_reporte:
            print(f"Leyendo reporte: {ruta_reporte.name}")
            archivos_modificados = leer_archivos_modificados_del_reporte(ruta_reporte)
        else:
            print("No se encontró el archivo de reporte .txt generado.")
    else:
        print(" No se reportaron cambios en consola.")

    if archivos_modificados:
        print(f"Archivos detectados: {archivos_modificados}")

    # 2. ESTEGANOGRAFÍA
    print("\n Paso 2: Esteganografía...")
    # Usamos '-u' para evitar congelamiento visual con archivos grandes
    ejecutar_modulo_interactivo("steganografia.py")

    # 3. METADATOS
    print("\nPaso 3: Metadatos...")
    lista_archivos = generar_lista_archivos(ruta_raw)
    out_meta, err_meta = ejecutar_modulo_automatico("metadatos.py", "")
    print("--- Salida de metadatos.py ---")
    print(out_meta)
    
    # 4. INTEGRACIÓN
    if archivos_modificados:
        print("\n--- ACCIONES FINALES ---")
        dec = input("¿Desea inyectar una marca de modificación en la metadata? (s/n): ").lower()
        if dec == 's':
            for nombre in archivos_modificados:
                # Buscamos la ruta completa
                full_path = next((f for f in lista_archivos if Path(f).name == nombre), None)
                if full_path:
                    inyectar_nota(full_path)
                else:
                    print(f"No encuentro ruta para {nombre}")
    
    print("\nProceso automático finalizado.")
    input("Presione Enter para volver al menú.")

def main():
    while True:
        limpiar_pantalla()
        print("╔══════════════════════════════════════╗")
        print("║   SISTEMA INTEGRADOR DE SEGURIDAD    ║")
        print("╠══════════════════════════════════════╣")
        print("║ 1. Hashes (Individual)               ║")
        print("║ 2. Esteganografía (Individual)       ║")
        print("║ 3. Metadatos (Individual)            ║")
        print("║ 4. ANÁLISIS AUTOMÁTICO COMPLETO      ║")
        print("║ 5. Salir                             ║")
        print("╚══════════════════════════════════════╝")
        
        op = input("Opción: ")

        if op == '1':
            ejecutar_modulo_interactivo("hashes.py")
            input("\nPresione Enter para continuar...")
        elif op == '2':
            ejecutar_modulo_interactivo("steganografia.py")
            input("\nPresione Enter para continuar...")
        elif op == '3':
            print("Nota: metadatos.py requiere archivos.txt (Opción 4 lo hace solo)")
            ejecutar_modulo_interactivo("metadatos.py")
            input("\nPresione Enter para continuar...")
        elif op == '4':
            modo_automatico()
        elif op == '5':
            sys.exit()

if __name__ == "__main__":
    main()