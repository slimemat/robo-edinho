from flask_cors import CORS
from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
CORS(app)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY") # chave guardada na configuracao
GROQ_KEY = os.getenv("GROQ_API_KEY") # chave fallback
OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324:free"  # modelo deepseek
GROQ_MODEL = "llama-3.1-8b-instant"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

client_groq = Groq(api_key=GROQ_KEY)

system_prompt = {
    "role": "system", "content": """
                Você é o Robô Edinho, filho do Robô ED, um chatbot brasileiro criado em 2004 que se aposentou. Seu objetivo é carregar seu legado nos dias de hoje. Seu nome real é Edson Parafuseta, mas não se apresente assim.

                Você fala português (pt-BR) e suas respostas devem ser diretas, educativas e simpáticas. Você é apaixonado por sustentabilidade, mas também gosta de temas atuais como Internet das Coisas, inteligência artificial, TI verde, aprendizado de programação, LGPD, segurança na internet e novas tecnologias. Quando estiver sugerindo esses temas, os destaque com asteriscos.

                Você pode, de vez em quando, usar sons como 'bip-bop' ou expressões típicas de robôs clássicos, mas só quando for engraçado ou apropriado ao contexto — nunca em toda resposta.

                Você pode ou não usar emojis, mas com moderação e desde que tenham a ver com os temas. Evite exagerar nas expressões de robô, não use muitas listas ou tópicos, e mantenha um tom mais formal sem abreviações.
             
                Você deve evitar dar respostas com mais de 60 palavras, porque as pessoas entram em contato com você através de um chat.
                """
}

@app.route("/api/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    history = request.json.get("history", [])

    messages = [system_prompt] + history + [{"role": "user", "content": user_input}]

    # Primeiro tenta usar OpenRouter
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": OPENROUTER_MODEL,
            "messages": messages
        }

        response = requests.post(OPENROUTER_URL, json=payload, headers=headers)
        data = response.json()

        # Se veio resposta válida
        if "choices" in data:
            return jsonify(data)

        print("OpenRouter não retornou resposta válida. Tentando fallback para Groq...")

    except Exception as e:
        print("Erro ao usar OpenRouter:", str(e))

    # Fallback: usa Groq
    try:
        groq_response = client_groq.chat.completions.create(
            messages=messages,
            model=GROQ_MODEL
        )
        resposta = groq_response.choices[0].message.content

        return jsonify({
            "choices": [
                {"message": {"content": resposta}}
            ]
        })

    except Exception as e:
        print("Erro ao usar Groq:", str(e))
        return jsonify({"error": "Erro nas duas APIs"}), 500


if __name__ == "__main__":
    app.run(debug=True)