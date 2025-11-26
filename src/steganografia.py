#!/usr/bin/env python3

import json
import wave
import fitz  # PyMuPDF
from PIL import Image
import os
import time
import struct

LOGFILE = "mensajes.jsonl"

def guardar_jsonl_evento(evento, archivo=LOGFILE):
    """Guarda un diccionario de evento (no debe contener datos sensibles sin consentimiento)."""
    evento_base = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    evento_base.update(evento)
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(evento_base, ensure_ascii=False) + "\n")

def _mensaje_a_bits(mensaje: str) -> str:
    b = mensaje.encode("utf-8")
    length = len(b)
    # prefijo de 32 bits con la longitud en bytes
    prefijo = format(length, "032b")
    cuerpo = ''.join(format(byte, '08b') for byte in b)
    return prefijo + cuerpo

def _bits_a_mensaje(bits: str) -> str:
    # primero leer 32 bits -> longitud en bytes
    if len(bits) < 32:
        return ""
    prefijo = bits[:32]
    length = int(prefijo, 2)
    needed = 32 + (length * 8)
    if len(bits) < needed:
        # bits incompletos
        return ""
    cuerpo = bits[32:needed]
    bytes_list = [int(cuerpo[i:i+8], 2) for i in range(0, len(cuerpo), 8)]
    return bytes(bytes_list).decode("utf-8", errors="replace")

def ocultar_en_imagen(imagen_path, mensaje, salida):
    try:
        img = Image.open(imagen_path).convert("RGB")
        width, height = img.size
        capacidad_bits = width * height * 3
        bitstream = _mensaje_a_bits(mensaje)
        if len(bitstream) > capacidad_bits:
            raise ValueError(f"El mensaje ({len(bitstream)} bits) excede la capacidad ({capacidad_bits} bits) de la imagen.")

        data = list(img.getdata())
        new_data = []
        bit_index = 0
        for pixel in data:
            r, g, b = pixel
            r = (r & ~1) | (int(bitstream[bit_index]) if bit_index < len(bitstream) else (r & 1)); bit_index += 1 if bit_index < len(bitstream) else 0
            g = (g & ~1) | (int(bitstream[bit_index]) if bit_index < len(bitstream) else (g & 1)); bit_index += 1 if bit_index < len(bitstream) else 0
            b = (b & ~1) | (int(bitstream[bit_index]) if bit_index < len(bitstream) else (b & 1)); bit_index += 1 if bit_index < len(bitstream) else 0
            new_data.append((r, g, b))
        img.putdata(new_data)
        img.save(salida)
        guardar_jsonl_evento({"operacion": "ocultar", "tipo": "imagen", "archivo": salida, "nota": "mensaje ocultado (no se registró texto por privacidad)"})
        print("Mensaje ocultado en imagen:", salida)
    except Exception as e:
        print("Error al ocultar en imagen:", e)
        guardar_jsonl_evento({"operacion": "error", "tipo": "imagen", "archivo": imagen_path, "error": str(e)})

def revelar_de_imagen(imagen_path, registrar_texto=False):
    try:
        img = Image.open(imagen_path).convert("RGB")
        data = list(img.getdata())
        bits = ""
        for pixel in data:
            for chan in pixel:  # r,g,b
                bits += str(chan & 1)
        mensaje = _bits_a_mensaje(bits)
        if registrar_texto:
            guardar_jsonl_evento({"operacion": "revelar", "tipo": "imagen", "archivo": imagen_path, "mensaje": mensaje})
        else:
            guardar_jsonl_evento({"operacion": "revelar", "tipo": "imagen", "archivo": imagen_path, "nota": "mensaje revelado (no registrado texto)"})
        print("Mensaje revelado:", mensaje)
        return mensaje
    except Exception as e:
        print("Error al revelar desde imagen:", e)
        guardar_jsonl_evento({"operacion": "error", "tipo": "revelar_imagen", "archivo": imagen_path, "error": str(e)})

def ocultar_en_pdf(pdf_path, mensaje, salida):
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata or {}
        # guardamos el mensaje (texto) en metadata. Nota: visible con herramientas que lean metadata.
        metadata["mensaje_oculto"] = mensaje
        doc.set_metadata(metadata)
        doc.save(salida)
        guardar_jsonl_evento({"operacion": "ocultar", "tipo": "pdf", "archivo": salida, "nota": "mensaje guardado en metadata"})
        print("Mensaje ocultado en PDF (metadata):", salida)
    except Exception as e:
        print("Error al ocultar en PDF:", e)
        guardar_jsonl_evento({"operacion": "error", "tipo": "pdf", "archivo": pdf_path, "error": str(e)})

def revelar_de_pdf(pdf_path, registrar_texto=False):
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata or {}
        mensaje = metadata.get("mensaje_oculto", "")
        if registrar_texto:
            guardar_jsonl_evento({"operacion": "revelar", "tipo": "pdf", "archivo": pdf_path, "mensaje": mensaje})
        else:
            guardar_jsonl_evento({"operacion": "revelar", "tipo": "pdf", "archivo": pdf_path, "nota": "mensaje revelado (no registrado texto)"})
        print("Mensaje revelado (PDF metadata):", mensaje if mensaje else "No se encontró mensaje")
        return mensaje
    except Exception as e:
        print("Error al revelar PDF:", e)
        guardar_jsonl_evento({"operacion": "error", "tipo": "revelar_pdf", "archivo": pdf_path, "error": str(e)})

def ocultar_en_audio(audio_path, mensaje, salida):
    try:
        with wave.open(audio_path, 'rb') as audio:
            params = audio.getparams()
            frames = bytearray(audio.readframes(audio.getnframes()))
        bitstream = _mensaje_a_bits(mensaje)
        if len(bitstream) > len(frames):
            raise ValueError(f"El mensaje ({len(bitstream)} bits) excede la capacidad de audio ({len(frames)} bytes).")
        # Modificar LSB de los bytes de frames
        for i, bit in enumerate(bitstream):
            frames[i] = (frames[i] & ~1) | int(bit)
        # escribir nuevo wav
        with wave.open(salida, 'wb') as nuevo:
            nuevo.setparams(params)
            nuevo.writeframes(bytes(frames))
        guardar_jsonl_evento({"operacion": "ocultar", "tipo": "audio", "archivo": salida, "nota": "mensaje ocultado (no registrado texto)"})
        print("Mensaje ocultado en audio:", salida)
    except Exception as e:
        print("Error al ocultar en audio:", e)
        guardar_jsonl_evento({"operacion": "error", "tipo": "audio", "archivo": audio_path, "error": str(e)})

def revelar_de_audio(audio_path, registrar_texto=False):
    try:
        with wave.open(audio_path, 'rb') as audio:
            frames = bytearray(audio.readframes(audio.getnframes()))
        bits = ''.join(str(byte & 1) for byte in frames)
        mensaje = _bits_a_mensaje(bits)
        if registrar_texto:
            guardar_jsonl_evento({"operacion": "revelar", "tipo": "audio", "archivo": audio_path, "mensaje": mensaje})
        else:
            guardar_jsonl_evento({"operacion": "revelar", "tipo": "audio", "archivo": audio_path, "nota": "mensaje revelado (no registrado texto)"})
        print("Mensaje revelado (audio):", mensaje if mensaje else "No se encontró mensaje")
        return mensaje
    except Exception as e:
        print("Error al revelar audio:", e)
        guardar_jsonl_evento({"operacion": "error", "tipo": "revelar_audio", "archivo": audio_path, "error": str(e)})

def mostrar_historial():
    try:
        with open(LOGFILE, "r", encoding="utf-8") as f:
            for linea in f:
                print(linea.strip())
    except FileNotFoundError:
        print("No hay historial (mensajes.jsonl) aún.")

def main():
    print("=== Esteganografía - PIA Entregable 2 ===")
    print("1. Ocultar mensaje")
    print("2. Revelar desde archivo")
    print("3. Mostrar historial de eventos (.jsonl)")
    opcion = input("Elige una opción (1-3): ").strip()
    if opcion == "1":
        archivo = input("Ruta del archivo original: ").strip('" ')
        mensaje = input("Mensaje a ocultar: ")
        salida = input("Nombre del archivo de salida: ").strip('" ')
        if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            ocultar_en_imagen(archivo, mensaje, salida)
        elif archivo.lower().endswith('.pdf'):
            ocultar_en_pdf(archivo, mensaje, salida)
        elif archivo.lower().endswith('.wav'):
            ocultar_en_audio(archivo, mensaje, salida)
        else:
            print("Formato no soportado (.png, .jpg, .pdf, .wav)")
    elif opcion == "2":
        archivo = input("Ruta del archivo para revelar mensaje: ").strip('" ')
        registrar = input("¿Registrar texto en logs? (s/N): ").strip().lower() == "s"
        if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            revelar_de_imagen(archivo, registrar_texto=registrar)
        elif archivo.lower().endswith('.pdf'):
            revelar_de_pdf(archivo, registrar_texto=registrar)
        elif archivo.lower().endswith('.wav'):
            revelar_de_audio(archivo, registrar_texto=registrar)
        else:
            print("Formato no soportado.")
    elif opcion == "3":
        mostrar_historial()
    else:
        print("Opción inválida.")

if __name__ == "__main__":
    main()
