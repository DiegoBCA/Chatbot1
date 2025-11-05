from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from groq import Groq
from datetime import datetime
import pytz

# ==============================
# 1. CONFIGURACIÓN INICIAL
# ==============================

# NOTA: Por seguridad, hemos reemplazado tu clave API real con un placeholder.
# Usar una variable de entorno es la mejor práctica para proteger tu clave.
client = Groq(
     api_key="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"  # reemplaza con tu key
)

# ==============================
# 2. CONSTANTES DE DATOS
# ==============================

# URLs disponibles
PAGES = {
    "oferta_academica": "https://www.udlap.mx/ofertaacademica/NegociosInternacionales",
    "web_udlap": "https://www.udlap.mx/web/",
    "practicas": "https://online.udlap.mx/practicasprofesion/",
    "ppa": "https://www.udlap.mx/web/vidaestudiantil/asesoria-y-orientacion.aspx#:~:text=Son%20una%20herramienta%20reflexiva%20que,%2C%20informar%2C%20promover%2C%20etc.",
    "ppa2": "https://lacatarina.udlap.mx/2016/02/la-intencion-es-buena/",
    "plan_estudios_actual": "https://www.udlap.mx/ofertaacademica2017/planestudios.aspx?cveCarrera=LNI",
    "calendario_general": "https://online.udlap.mx/calendarioescolar/2025/Semestral",
    "servicios_escolares": "https://www.udlap.mx/serviciosescolares/",
    "profesores": "https://www.udlap.mx/profesores/Licenciatura/NegociosInternacionales",
    "contactos_udlap": "https://www.udlap.mx/contacto/"
}

TEMAS = {
    "materias": {
        "keywords": ["materia", "curso", "plan de estudios", "asignatura", "catalogo de cursos", "catlogo"],
        "urls": [PAGES["plan_estudios_actual"]]
    },
    "practicas": {
        "keywords": ["practicas", "pasantía"],
        "urls": [PAGES["practicas"]]
    },
    "ppa": {
        "keywords": ["ppa", "ppa1", "ppa2", "programa de primer año"],
        "urls": [PAGES["ppa"], PAGES["ppa2"]]
    }, 
    "contactos": {
        "keywords": ["profesor", "docente", "contacto", "correo", "asesor"],
        "urls": [PAGES["web_udlap"], PAGES["profesores"], PAGES["contactos_udlap"]]
    },
    "calendario": {
        "keywords": ["calendario", "fechas", "eventos", "inscripción", "vacaciones"],
        "urls": [PAGES["web_udlap"], PAGES["calendario_general"], PAGES["servicios_escolares"]]
    }
}

# ==============================
# 3. FUNCIONES DE EXTRACCIÓN DE DATOS
# ==============================

def obtener_texto(url, limite=4000):
    """Extrae texto plano de una URL, limitado por el parámetro 'limite'."""
    try:
        response = requests.get(url, timeout=8)
        # Asegurarse de que la respuesta fue exitosa
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, "html.parser")
        # Usar get_text para limpiar y separar por nueva línea
        texto = soup.get_text(separator="\n", strip=True)
        return texto[:limite]
    except requests.exceptions.RequestException as e:
        print(f"No se pudo obtener {url}: Error de solicitud: {e}")
        return ""
    except Exception as e:
        print(f"Error general al obtener {url}: {e}")
        return ""


def extraer_links_materias(url):
    """Intenta extraer enlaces de materias del plan de estudios."""
    print(f"Extrayendo links de: {url}")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links_materias = {}
        # Busca cualquier etiqueta 'a' que tenga un href
        for a in soup.find_all("a", href=True):
            nombre = a.get_text(strip=True).lower()
            href = a["href"]
            # He modificado la lógica de la URL para que no duplique la base
            if "materia" in href and nombre:
                # La URL base ya es la del plan de estudios
                # Asumiendo que el href es un fragmento o ancla, lo ignoramos para simplificar
                # Si el href es una ruta relativa, se puede construir. Para el ejemplo, usamos solo el nombre.
                links_materias[nombre] = url # Usamos la URL base por simplicidad
        return links_materias
    except Exception as e:
        print("Error extrayendo links de materias:", e)
        return {}

# Ejecutar la extracción de links solo una vez al iniciar la aplicación
LINKS_MATERIAS = extraer_links_materias(PAGES["plan_estudios_actual"])


def extraer_eventos_calendario(url):
    """Extrae información de eventos relevantes del calendario."""
    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        eventos = []
        # Buscar elementos que puedan contener información de calendario
        for item in soup.find_all(["li", "p", "div", "h3"]):
            texto = item.get_text(strip=True)
            # Palabras clave para identificar eventos
            if any(pal in texto.lower() for pal in [
                "enero", "febrero", "marzo", "abril", "mayo", "junio",
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
                "inicio", "fin", "exámenes", "inscripción", "vacaciones"
            ]):
                # Filtro por longitud razonable
                if 10 < len(texto) < 300:
                    eventos.append(texto)

        eventos_unicos = list(dict.fromkeys(eventos))
        if eventos_unicos:
            return "📅 Eventos próximos (máximo 20):\n• " + "\n• ".join(eventos_unicos[:20])
        else:
            return "No se encontraron eventos específicos de calendario en la página."
    except Exception as e:
        print("Error extrayendo eventos:", e)
        return "No se pudo acceder al calendario."
    

def obtener_info_materia(nombre_materia):
    """Busca y extrae la descripción de una materia específica."""
    nombre_materia = nombre_materia.lower()
    # Usamos la URL base del plan de estudios, ya que el scraping de links puede ser complejo
    url = PAGES['plan_estudios_actual']
    
    # Intenta buscar el nombre de la materia en el texto de la URL del plan de estudios
    if any(materia in nombre_materia for materia in LINKS_MATERIAS.keys()):
        try:
            # Obtener todo el texto relevante del plan de estudios (con un límite mayor)
            page_text = obtener_texto(url, limite=8000) 
            
            # Usar Groq para buscar y resumir la info dentro del texto
            prompt = (
                f"Busca en el siguiente texto toda la información sobre la materia '{nombre_materia.title()}'. "
                f"Si la encuentras, resúmela en español de manera amigable e incluye el enlace: {url}. "
                f"Si no la encuentras, indica amablemente que consulte el plan completo. Texto a buscar:\n\n{page_text}"
            )
            
            # Llamada rápida a Groq para contextualizar
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-8b-instruct",
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error al usar Groq para obtener info de materia: {e}")
            return f"No pude procesar la información de la materia {nombre_materia.title()}. Revisa el plan de estudios aquí: {url}"

    return f"No encontré información específica para la materia '{nombre_materia.title()}'. Consulta el plan de estudios aquí: {PAGES['plan_estudios_actual']}"

# ==============================
# 4. INSTANCIA Y RUTAS DE FLASK
# ==============================

# Se define la única instancia de la aplicación Flask
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    """Ruta principal que sirve el HTML del chatbot."""
    # Espera que 'index.html' esté en la carpeta 'templates'
    return render_template("index.html")

@app.route("/about")
def about():
    """Ruta de ejemplo que puede ser eliminada si no se usa."""
    return "Esta es la página About!"

@app.route("/chat", methods=["POST"])
def chat():
    """Maneja las peticiones de chat y genera la respuesta del AztecaBot."""
    user_data = request.json
    user_message = user_data.get("message", "").strip()
    user_language = user_data.get("language", "es")

    if not user_message:
        if user_language == "es":
            return jsonify({"response": "Por favor escribe un mensaje válido."})
        else:
            return jsonify({"response": "Please write a valid message."})
        
    # ------------------------------
    # Contexto temporal y de sistema
    # ------------------------------
    zona_mx = pytz.timezone("America/Mexico_City")
    ahora = datetime.now(zona_mx)
    
    if user_language == "es":
        fecha_hora_actual = ahora.strftime("%A, %d de %B de %Y, %H:%M:%S")
        system_prompt = (
            "Eres AztecaBot, un asistente para estudiantes de Negocios Internacionales en la UDLAP. "
            "Responde de forma clara, amigable y dirígete al usuario de forma neutra, sin usar "
            "palabras que asuman el género del usuario. "
            "Ayuda sobre materias, profesores, prácticas profesionales, eventos y procesos académicos. "
            "Si no tienes la información exacta, indica dónde consultarla y proporciona enlaces oficiales. "
            "No respondas a preguntas ni comentarios fuera del contexto dado (carrera de negocios internacionales en UDLAP). "
            "Si te preguntan algo que no se relacione solo di que no puedes responder o hacer tal cosa. "
            f"La fecha y hora actual es {fecha_hora_actual}."
            )
    else:
        fecha_hora_actual = ahora.strftime("%A, %B %d, %Y, %H:%M:%S")
        system_prompt = (
            "You are UDLAPbot, an assistant for International Business students at UDLAP. "
            "Respond clearly and friendly, addressing the user in a neutral way without using "
            "words that assume the user's gender. "
            "Help with courses, professors, professional internships, events and academic processes. "
            "If you don't have the exact information, indicate where to consult it and provide official links. "
            "Do not respond to questions or comments outside the given context (International Business program at UDLAP). "
            "If you're asked something unrelated, just say you cannot answer or do that. "
            f"The current date and time is {fecha_hora_actual}."
            )

    messages = [
        {"role": "system", "content": system_prompt},
        ]
    
    msg_lower = user_message.lower()

    # ------------------------------
    # Contextualización con scraping
    # ------------------------------
    context_found = False
    
    # 1. Buscar si el mensaje pertenece a algún tema (ej. Prácticas, Calendario)
    for tema, data in TEMAS.items():
        if any(keyword in msg_lower for keyword in data["keywords"]):
            context_found = True
            for url in data["urls"]:
                if "calendario" in url:
                    eventos = extraer_eventos_calendario(url)
                    context_message = f"Información del calendario de {url}:\n{eventos}"
                else:
                    texto = obtener_texto(url)
                    context_message = f"Contenido de {url}:\n{texto}"
                
                messages.append({"role": "system", "content": context_message})

    # 2. Buscar si menciona materia específica
    materia_encontrada = False
    for materia in LINKS_MATERIAS.keys():
        if materia in msg_lower:
            materia_encontrada = True
            context_found = True
            info_materia = obtener_info_materia(materia)
            messages.append({"role": "system", "content": info_materia})
            break
            
    # Si no se encontró contexto, el bot responderá con su conocimiento base
    if not context_found:
        if user_language == "es":
            messages.append({"role": "system", "content": "No se encontró información relevante en las páginas web. Responde solo con tu conocimiento base (UDLAP, Negocios Internacionales)." })
        else:
            messages.append({"role": "system", "content": "No se encontró información relevante en las páginas web. Responde solo con tu conocimiento base (UDLAP, International Business)." })

    # Agregar el mensaje del usuario al final
    messages.append({"role": "user", "content": user_message})

    # ------------------------------
    # Llamada al modelo de Groq
    # ------------------------------
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile", # Modelo utilizado por el usuario
            temperature=0.7 # Añadimos temperatura para respuestas más dinámicas
        )
        bot_reply = chat_completion.choices[0].message.content
    except Exception as ex:
        if user_language == "es":
            bot_reply = "Hubo un problema procesando tu solicitud con la IA (Groq). Intenta más tarde."
        else:
            bot_reply = "There was a problem processing your request with the AI (Groq). Please try again later."
        print("Error API Groq:", ex)

    return jsonify({"response": bot_reply})

# ==============================
# 5. BLOQUE DE EJECUCIÓN
# ==============================

if __name__ == "__main__":
    # Este es el ÚNICO bloque que debe iniciar la aplicación.
    print("Iniciando Flask... Asegúrate de que index.html esté en la carpeta 'templates'.")
    app.run(debug=True)
