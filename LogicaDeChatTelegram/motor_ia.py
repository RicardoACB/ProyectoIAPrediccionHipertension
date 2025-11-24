import pickle
import pandas as pd
import numpy as np
import os

# Nombre del modelo
MODEL_FILE = 'LogicaDeChatTelegram\modelo_hipertension.pkl'

def cargar_modelo():
    """Carga el modelo desde el archivo PKL."""
    if not os.path.exists(MODEL_FILE):
        return None
    with open(MODEL_FILE, 'rb') as f:
        return pickle.load(f)

def realizar_prediccion(datos_dict):
    """
    Recibe un diccionario con los datos del usuario, 
    crea el DataFrame y devuelve la predicción y la probabilidad.
    """
    modelo = cargar_modelo()
    if modelo is None:
        return {"error": "No se encontró el archivo del modelo .pkl"}

    # Definir las columnas EXACTAS que el modelo espera
    columnas = [
        'Edad', 
        'Fuma actualmente', 
        'Antecedentes de hipertension', 
        'Frecuencia de tomar bebida alcoholica', 
        'Frecuencia de actividad fisica', 
        'Peso(Kg)', 
        'Talla(cm)', 
        'Sistólica', 
        'Diastólica', 
        'Tiene diabetes'
    ]

    # Crear el DataFrame con una sola fila
    # Los valores que sean None o 'nan' se convertirán a np.nan
    df_input = pd.DataFrame([datos_dict], columns=columnas)
    
    # Asegurarse de que los tipos sean float para manejar NaNs correctamente
    df_input = df_input.astype(float)

    try:
        # Predicción de clase (0 o 1)
        prediccion_clase = modelo.predict(df_input)[0]
        # Probabilidad ([prob_no, prob_si])
        probs = modelo.predict_proba(df_input)[0]

        # Preparar respuesta legible
        es_hipertenso = True if prediccion_clase == 1 else False
        probabilidad = probs[1] if es_hipertenso else probs[0]

        return {
            "riesgo_hipertension": es_hipertenso,
            "confianza": round(probabilidad * 100, 2),
            "mensaje": "Riesgo ALTO detectado" if es_hipertenso else "Riesgo BAJO detectado"
        }
    except Exception as e:
        return {"error": f"Error al predecir: {str(e)}"}