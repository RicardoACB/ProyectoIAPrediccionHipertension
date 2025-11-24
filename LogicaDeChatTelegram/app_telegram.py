from flask import Flask, request, jsonify
import requests
import numpy as np
import sys
import os

# Intentamos importar el motor. Si falla, el programa avisará pero no se cerrará de golpe.
try:
    import motor_ia
    print("✅ Motor IA cargado correctamente.")
except Exception as e:
    print(f"❌ ERROR CRÍTICO: No se pudo cargar motor_ia.py o el modelo pkl.")
    print(f"Detalle del error: {e}")
    # No detenemos el programa para que al menos el bot responda errores
    motor_ia = None 

app = Flask(__name__)

# ================= CONFIGURACIÓN =================
# ⚠️ ASEGÚRATE DE QUE ESTE TOKEN SEA EL NUEVO (NO EL QUE PUBLICASTE ANTES)
TOKEN = '8308127766:AAGdiIcibbJUwro2xZhiGpvP1Y0EmdWELXs' 
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

usuarios_state = {}

# ================= PREGUNTAS (Resumido para ahorrar espacio, funciona igual) =================
PREGUNTAS = [
    {"campo": "Edad", "texto": "1. ¿Cuál es su *Edad*? (Escriba número)", "tipo": "numero", "opciones": None},
    {"campo": "Fuma actualmente", "texto": "2. Tabaco:", "tipo": "boton", "opciones": [[{"text": "Diario", "callback_data": "1"}], [{"text": "Ocasional", "callback_data": "2"}], [{"text": "Ex-fumador", "callback_data": "3"}], [{"text": "Nunca", "callback_data": "4"}]]},
    {"campo": "Antecedentes de hipertension", "texto": "3. Antecedentes hipertensión:", "tipo": "boton", "opciones": [[{"text": "Sí", "callback_data": "1"}, {"text": "No", "callback_data": "2"}], [{"text": "No sabe", "callback_data": "-8888"}] ]},
    {"campo": "Frecuencia de tomar bebida alcoholica", "texto": "4. Alcohol:", "tipo": "boton", "opciones": [[{"text": "Sí", "callback_data": "1"}, {"text": "No", "callback_data": "2"}]]},
    {"campo": "Frecuencia de actividad fisica", "texto": "5. Actividad física:", "tipo": "boton", "opciones": [[{"text": "Alta", "callback_data": "1"}], [{"text": "Media", "callback_data": "2"}], [{"text": "Baja", "callback_data": "3"}]]},
    {"campo": "Peso(Kg)", "texto": "6. Peso (Kg):", "tipo": "numero", "opciones": None},
    {"campo": "Talla(cm)", "texto": "7. Talla (cm):", "tipo": "numero", "opciones": None},
    {"campo": "Sistólica", "texto": "8. Sistólica (Alta):", "tipo": "numero", "opciones": None},
    {"campo": "Diastólica", "texto": "9. Diastólica (Baja):", "tipo": "numero", "opciones": None},
    {"campo": "Tiene diabetes", "texto": "10. Diabetes:", "tipo": "boton", "opciones": [[{"text": "Sí", "callback_data": "1"}, {"text": "No", "callback_data": "2"}], [{"text": "No sabe", "callback_data": "-8888"}] ]}
]

# ================= FUNCIONES =================

def enviar_mensaje(chat_id, texto, reply_markup=None):
    print(f"   📤 Intentando enviar mensaje a {chat_id}...")
    try:
        payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
        if reply_markup: payload["reply_markup"] = reply_markup
        
        r = requests.post(f"{BASE_URL}/sendMessage", json=payload)
        
        if r.status_code == 200:
            print("   ✅ Mensaje enviado con éxito.")
        else:
            print(f"   ❌ Falló el envío. Telegram respondió: {r.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión enviando mensaje: {e}")

def enviar_pregunta(chat_id):
    if chat_id not in usuarios_state: return
    idx = usuarios_state[chat_id]['paso']
    if idx < len(PREGUNTAS):
        p = PREGUNTAS[idx]
        mk = {"inline_keyboard": p['opciones']} if p['tipo'] == 'boton' else None
        enviar_mensaje(chat_id, p['texto'], mk)
    else:
        procesar_resultado(chat_id)

def procesar_resultado(chat_id):
    if not motor_ia:
        enviar_mensaje(chat_id, "⚠️ Error: El sistema de IA no está funcionando en el servidor.")
        return

    datos = usuarios_state[chat_id]['datos']
    enviar_mensaje(chat_id, "🔄 Analizando...")
    res = motor_ia.realizar_prediccion(datos)
    
    if "error" in res:
        enviar_mensaje(chat_id, f"⚠️ Error IA: {res['error']}")
    else:
        msg = f"Resultado: {res['mensaje']} ({res['confianza']}%)"
        enviar_mensaje(chat_id, msg)
    del usuarios_state[chat_id]

# ================= ROUTE =================

@app.route('/webhook', methods=['POST'])
def webhook():
    print("\n📨 --- NUEVA SOLICITUD RECIBIDA DE TELEGRAM ---")
    try:
        data = request.json
    except:
        print("❌ Recibí algo, pero no es JSON válido.")
        return "error", 400

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        texto = data["message"].get("text", "")
        print(f"   👤 Usuario: {chat_id} | Texto: '{texto}'")
        
        # 1. LOGICA START
        if texto == "/start":
            print("   👉 Detectado comando /start. Iniciando encuesta.")
            usuarios_state[chat_id] = {"paso": 0, "datos": {}}
            enviar_mensaje(chat_id, "👋 ¡Hola! Soy tu IA de salud. Responde las preguntas.")
            enviar_pregunta(chat_id)
        
        # 2. LOGICA RESPUESTA NUMERICA
        elif chat_id in usuarios_state:
            print(f"   👉 Usuario en paso {usuarios_state[chat_id]['paso']}. Procesando respuesta...")
            # (Aquí va la lógica de números que ya tenías, simplificada para el ejemplo)
            idx = usuarios_state[chat_id]['paso']
            pregunta = PREGUNTAS[idx]
            
            if pregunta['tipo'] == 'numero':
                try:
                    val = np.nan if texto.lower() in ['omitir', 'no'] else float(texto)
                    usuarios_state[chat_id]['datos'][pregunta['campo']] = val
                    usuarios_state[chat_id]['paso'] += 1
                    enviar_pregunta(chat_id)
                except:
                    enviar_mensaje(chat_id, "⚠️ Escribe un número válido.")
            else:
                enviar_mensaje(chat_id, "⚠️ Usa los botones, por favor.")

        # 3. LOGICA BIENVENIDA (El Else que fallaba)
        else:
            print("   👉 El usuario escribió texto pero NO ha iniciado (/start). Enviando bienvenida.")
            msg = "👋 ¡Hola! Para iniciar el diagnóstico escribe: /start"
            enviar_mensaje(chat_id, msg)

    elif "callback_query" in data:
        print("   👉 Detectado clic en botón.")
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        # (Lógica de botones estándar...)
        # Importante responder al callback para que no cargue infinito
        try: requests.post(f"{BASE_URL}/answerCallbackQuery", json={"callback_query_id": data["callback_query"]["id"]})
        except: pass
        
        if chat_id in usuarios_state:
            # Procesar dato botón...
            val = float(data["callback_query"]["data"])
            if val == -8888: val = np.nan
            idx = usuarios_state[chat_id]['paso']
            usuarios_state[chat_id]['datos'][PREGUNTAS[idx]['campo']] = val
            usuarios_state[chat_id]['paso'] += 1
            enviar_pregunta(chat_id)

    print("🏁 Fin del procesamiento de solicitud.\n")
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("🤖 BOT INICIADO - Esperando mensajes...")
    app.run(host='0.0.0.0', port=5000)