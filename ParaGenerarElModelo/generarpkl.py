import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import recall_score, confusion_matrix
import pickle

# --- CONFIGURACIÓN ---
ARCHIVO_CSV = 'base_de_datos_ENS_2017_tratada.csv' # Nombre de tu archivo
ARCHIVO_PKL = 'modelo_hipertension.pkl'            # Nombre del modelo a generar

def entrenar():
    print("Cargando datos...")
    try:
        df = pd.read_csv(ARCHIVO_CSV)
    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo {ARCHIVO_CSV}")
        return

    # Preprocesamiento: Seleccionar variables
    # Se excluye 'Tiene hipertension' (target), 'Unnamed: 0' (id) e 'IMC' (muchos nulos)
    columnas_a_excluir = ['Unnamed: 0', 'IMC', 'Tiene hipertension']
    
    # Verificar que las columnas existan antes de borrarlas
    cols_drop = [c for c in columnas_a_excluir if c in df.columns]
    
    X = df.drop(columns=cols_drop)
    y = df['Tiene hipertension']

    # División de prueba y entrenamiento
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Creación del Pipeline
    # 1. Imputer: Rellena valores nulos (NaN) con el promedio, vital para que el modelo no falle
    # 2. RandomForest: El algoritmo de clasificación solicitado
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
        ('rf', RandomForestClassifier(random_state=42))
    ])

    print("Entrenando modelo Random Forest...")
    pipeline.fit(X_train, y_train)

    # Evaluación
    y_pred = pipeline.predict(X_test)
    sensibilidad = recall_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)

    print("\n--- Resultados del Entrenamiento ---")
    print(f"Sensibilidad (Recall): {sensibilidad:.2%}")
    print("Matriz de Confusión:")
    print(conf_matrix)

    # Guardar modelo
    with open(ARCHIVO_PKL, 'wb') as f:
        pickle.dump(pipeline, f)
    
    print(f"\nModelo guardado exitosamente como: {ARCHIVO_PKL}")
    print("Listo para ser usado en predicciones.")

if __name__ == '__main__':
    entrenar()