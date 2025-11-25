# 🩺 Bot de Telegram para Predicción de Hipertensión con IA

Este proyecto es un Chatbot de Telegram inteligente diseñado para evaluar el riesgo de hipertensión arterial en usuarios mediante un cuestionario interactivo. Utiliza un modelo de Machine Learning (Random Forest) entrenado con datos reales de salud (ENS 2017) para realizar predicciones en tiempo real.

El sistema funciona mediante una arquitectura de Webhook conectando los servidores de Telegram con una aplicación local en Flask a través de Ngrok.

## 🚀 Características

* Interacción en Tiempo Real: Cuestionario guiado dentro de Telegram.

* Modelo de IA: Clasificador Random Forest (Entrenado con scikit-learn).

* Manejo de Datos Faltantes: El modelo imputa automáticamente valores desconocidos (si el usuario no sabe su presión o peso).

* Arquitectura de microservicios: Separación lógica entre el servidor (app_telegram.py) y el motor de inteligencia (motor_ia.py).

* Seguridad: Validación de inputs y manejo de errores.

## 📂 Estructura del Proyecto

* app_telegram.py (El Orquestador): Servidor Flask que gestiona el Webhook, recibe los mensajes de Telegram, mantiene el estado de la conversación y envía las respuestas.

* motor_ia.py (La Lógica): Carga el modelo .pkl y procesa los datos recibidos para devolver una predicción médica.

* generar_modelo_local.py (El Entrenador): Script para entrenar el modelo desde cero usando el dataset CSV y generar el archivo .pkl.

* modelo_hipertension.pkl: El modelo entrenado serializado (el "cerebro" de la IA).

* base_de_datos_ENS_2017_tratada.csv: Dataset utilizado para el entrenamiento.

## 🛠️ Requisitos Previos

* Python 3.8 o superior.

* Una cuenta de Telegram y un bot creado con @BotFather (Token).

* Ngrok instalado (para exponer el servidor local).

### Librerías necesarias

Puedes instalar todas las dependencias con:
Bash

    pip install flask requests pandas numpy scikit-learn

## ⚙️ Instalación y Configuración

1. Clonar el repositorio

Descarga el código en tu máquina local.

2. Generar el Modelo (Importante)

Para evitar errores de compatibilidad de versiones, genera el modelo en tu propio entorno ejecutando:

    python generar_modelo_local.py

Esto creará el archivo modelo_hipertension.pkl en tu carpeta.

3. Configurar el Token

Abre el archivo app_telegram.py y busca la variable TOKEN. Reemplázala con el token que te dio BotFather:

    TOKEN = 'TU_TOKEN_AQUI'

(Nota: Por seguridad, se recomienda usar variables de entorno en producción).

## 🚀 Ejecución del Proyecto

Paso 1: Iniciar el Servidor Flask

En tu terminal, ejecuta:

    python app_telegram.py

Luego verás que el servidor corre en el puerto 5000.

Paso 2: Iniciar el Túnel Ngrok

En una nueva terminal, ejecuta:

    ngrok http 5000

Copia la dirección HTTPS que te genera (ej: https://abcd-1234.ngrok-free.app).

Paso 3: Configurar el Webhook (Conexión)

Para conectar Telegram con tu PC, abre tu navegador web y visita la siguiente URL (reemplazando con tus datos):

    https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=<URL_DE_NGROK>/webhook

<TU_TOKEN>: Tu token de BotFather.

<URL_DE_NGROK>: La URL HTTPS que copiaste de Ngrok.

IMPORTANTE: No olvides poner /webhook al final.

Si todo sale bien, verás: {"ok": true, "result": true, "description": "Webhook was set"}.

Paso 4: ¡Usar el Bot!

Abre tu bot en Telegram y envía el comando:

/start

## ⚠️ Aviso Legal (Disclaimer)

Esta herramienta es un prototipo con fines académicos y educativos.

* No es un dispositivo médico.

* Las predicciones están basadas en estadísticas y no sustituyen el diagnóstico de un profesional de la salud.

* Ante cualquier duda sobre su salud, consulte a un médico.
