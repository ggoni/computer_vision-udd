# ---------------------------------------------------------------------------
# EJEMPLO DE CÓDIGO: VISIÓN POR COMPUTADORA (Detección de Objetos)
# ---------------------------------------------------------------------------
#
# OBJETIVO:
# Demostrar cómo un modelo de IA puede "ver" y "entender" una imagen.
#
# AUDIENCIA:
# Gerencial, no técnica. El código es para ilustrar el concepto.
#
# INSTRUCCIONES DE EJECUCIÓN:
# 1. Asegúrese de tener Python instalado en su computador.
# 2. Abra una terminal o línea de comandos.
# 3. Instale las librerías necesarias ejecutando (solo una vez):
#
#    pip install transformers torch Pillow requests
#
#    (Si 'torch' da problemas, 'tensorflow' también puede funcionar)
#
# 4. Guarde este archivo como "ejemplo_cv.py".
# 5. Ejecute el archivo desde su terminal:
#
#    python ejemplo_cv.py
#
# ---------------------------------------------------------------------------

# 1. IMPORTAR LAS HERRAMIENTAS
# Estas son las "cajas de herramientas" que usaremos.
# 'pipeline' es la herramienta mágica de Hugging Face que simplifica todo.
# 'Image' nos ayuda a abrir la imagen.
# 'requests' nos permite descargar la imagen desde internet.
from transformers import pipeline
from PIL import Image
import requests

def analizar_imagen():
    """
    Función principal que ejecuta el análisis de Visión por Computadora.
    """
    
    # 2. CARGAR EL "CEREBRO" (El modelo pre-entrenado)
    #
    # Le pedimos a Hugging Face un modelo experto en "object-detection" (Detección de Objetos).
    # Es como "llamar" a un experto mundial en identificación de objetos.
    # La primera vez que se ejecuta, descargará el modelo (aprox. 150MB).
    print("Cargando el modelo de IA (esto puede tardar un minuto la primera vez)...")
    try:
        # Usamos un modelo famoso, rápido y eficiente llamado 'YOLOS-tiny'
        # 'task' le dice al pipeline qué "menú" de CV queremos (ver Módulo 2 de la clase).
        detector = pipeline(task="object-detection", model="huggingface/yolos-tiny")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        print("Asegúrese de tener conexión a internet y las librerías 'transformers' y 'torch' instaladas.")
        return
        
    print("¡Modelo cargado con éxito!")

    # 3. DEFINIR LA IMAGEN QUE QUEREMOS ANALIZAR
    #
    # ¡Aquí puede experimentar! Cambie la URL por cualquier imagen de internet.
    # Pruebe con fotos de su propia industria (ej. una foto de una mina, un estante de retail, etc.)
    #
    # Algunas URLs de ejemplo para probar:
    
    # Ejemplo 1: Clásico de COCO (gatos y control remoto)
    url_imagen = "http://images.cocodataset.org/val2017/000000039769.jpg" 
    
    # Ejemplo 2: Escena de calle (autos, personas)
    # url_imagen = "http://images.cocodataset.org/val2017/000000039775.jpg"
    
    # Ejemplo 3: Comida (pizza)
    # url_imagen = "http://images.cocodataset.org/val2017/000000039781.jpg"
    
    # Ejemplo 4: Animales (llama)
    # url_imagen = "https://upload.wikimedia.org/wikipedia/commons/7/73/Lama_glama_001.jpg"

    print(f"\nAnalizando la imagen desde: {url_imagen}")
    
    try:
        # Abrimos la imagen desde la URL
        imagen = Image.open(requests.get(url_imagen, stream=True).raw)
    except Exception as e:
        print(f"Error al descargar o abrir la imagen: {e}")
        print("Por favor, verifique que la URL sea correcta y accesible.")
        return

    # 4. EJECUTAR LA "MAGIA" (Inferencia)
    #
    # Le pasamos la imagen al detector.
    # Aquí es donde la IA "mira" la imagen y encuentra los objetos.
    # Esto es lo que se llama "ejecutar inferencia".
    print("Procesando la imagen... (esto es rápido)")
    resultados = detector(images=imagen)

    # 5. MOSTRAR LOS RESULTADOS (De forma legible para un gerente)
    #
    # La IA no devuelve una imagen con cajas, devuelve DATOS (un JSON).
    # Este es el punto clave: la CV genera datos estructurados desde datos no estructurados.
    print("\n--- ¡Resultados del Análisis! ---")
    
    if not resultados:
        print("No se encontraron objetos conocidos en la imagen.")
    else:
        # Iteramos sobre cada objeto encontrado
        for i, objeto in enumerate(resultados):
            # Extraemos la información clave
            label = objeto['label']       # Qué es (la etiqueta)
            score = objeto['score']       # Qué tan seguro está (confianza)
            box = objeto['box']           # Dónde está (la caja)
            
            print(f"\nObjeto #{i+1}:")
            print(f"  > Etiqueta (Qué es): {label.capitalize()}")
            print(f"  > Confianza: {score * 100:.2f}%")
            print(f"  > Coordenadas (Dónde está): [ymin:{box['ymin']}, xmin:{box['xmin']}, ymax:{box['ymax']}, xmax:{box['xmax']}]")

    print("\n--- Fin del análisis ---")

# Esta línea permite que el script se ejecute cuando lo llamas desde la terminal
if __name__ == "__main__":
    analizar_imagen()
