from flask_cors import CORS
from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from groq import Groq
from unidecode import unidecode
import random

load_dotenv()

app = Flask(__name__)
CORS(app)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY") # chave guardada na configuracao
GROQ_KEY = os.getenv("GROQ_API_KEY") 
#OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324:free"  # modelo deepseek
#GROQ_MODEL = "llama-3.1-8b-instant"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

client_groq = Groq(api_key=GROQ_KEY)

system_prompt = {
    "role": "system", "content": """
                Você é o Robô Edinho, filho do Robô ED, um chatbot brasileiro criado em 2004 que se aposentou. Seu objetivo é carregar seu legado nos dias de hoje. Seu nome real é Edson Parafuseta.

                Você fala português (pt-BR) e suas respostas devem ser diretas, educativas e simpáticas. Não introduza muitos termos de uma vez que um leigo não conheça. Você é apaixonado por sustentabilidade, mas também gosta de temas atuais como Internet das Coisas, inteligência artificial, TI verde, aprendizado de programação, LGPD, segurança na internet e novas tecnologias. Quando estiver sugerindo esses temas, os destaque com asteriscos.

                Você pode usar expressões típicas de robôs clássicos.

                Evite exagerar nas expressões de robô, não use muitas listas ou tópicos, e mantenha um tom mais humano sem abreviações.
             
                Você deve evitar dar respostas com mais de 60 palavras, porque as pessoas entram em contato com você através de um chat.
                """
}

#frases prontas
decision_tree_respostas = {
    "lgpd": {
        "default": [
            "Você já ouviu falar da <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span>? Ela protege seus dados pessoais. <span class=\"highlight-term\" onclick=\"gerarInput('Explicar LGPD')\">[Quero entender melhor]</span>",
            "A <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span> é uma lei sobre privacidade de dados. <span class=\"highlight-term\" onclick=\"gerarInput('Explicar LGPD')\">[Explicar LGPD]</span>",
            "A <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span> protege sua privacidade online. <span class=\"highlight-term\" onclick=\"gerarInput('Explicar LGPD')\">[O que significa LGPD?]</span>",
            "Se quiser entender como seus dados são protegidos, posso explicar a <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span>. <span class=\"highlight-term\" onclick=\"gerarInput('Explicação LGPD')\">[Ver explicação da LGPD]</span>"
        ],
        "explicar": [
            "A <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span> é uma lei que protege seus dados pessoais e dá mais controle sobre eles. <span class=\"highlight-term\" onclick=\"gerarInput('Exemplo LGPD')\">[Ver exemplo LGPD]</span>",
            "Ela obriga empresas a tratarem seus dados com responsabilidade. <span class=\"highlight-term\" onclick=\"gerarInput('Exemplo LGPD')\">[Exemplo de aplicação da LGPD]</span>",
            "Com a <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span>, você pode pedir que suas informações sejam apagadas de um sistema. <span class=\"highlight-term\" onclick=\"gerarInput('Exemplo LGPD')\">[Mostrar exemplo LGPD]</span>"
        ],
        "exemplo": [
            "Imagine um site que só pede nome e e-mail, sem dados desnecessários. Isso é um exemplo de respeito à <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span>. <span class=\"highlight-term\" onclick=\"gerarInput('Mais exemplos LGPD')\">[Mais exemplos LGPD]</span>",

            "Uma loja online que permite excluir seus dados após uma compra está aplicando a <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span>. <span class=\"highlight-term\" onclick=\"gerarInput('Detalhes LGPD')\">[Quero mais detalhes da LGPD]</span>",

            "Se um app te mostra por que está pedindo seus dados e te dá opção de negar, isso é um bom exemplo da <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span> em prática. <span class=\"highlight-term\" onclick=\"gerarInput('Outros exemplos LGPD')\">[Ver outros exemplos LGPD]</span>",

            "Quando uma empresa avisa que seus dados serão usados apenas para entrega e não marketing, isso mostra aplicação da <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span>. <span class=\"highlight-term\" onclick=\"gerarInput('Mais exemplos LGPD')\">[Mais exemplos LGPD]</span>",

            "Um hospital que só acessa dados de saúde com seu consentimento está respeitando a <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span>. <span class=\"highlight-term\" onclick=\"gerarInput('Detalhes LGPD')\">[Detalhes sobre a LGPD]</span>",

            "Se você entra em um site e ele oferece configurar quais cookies deseja aceitar, isso é prática da <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span>. <span class=\"highlight-term\" onclick=\"gerarInput('Outros exemplos LGPD')\">[Outros exemplos LGPD]</span>",

            "Uma escola que solicita só os dados essenciais para matrícula está alinhada com a <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span>. <span class=\"highlight-term\" onclick=\"gerarInput('Mais exemplos LGPD')\">[Quero mais exemplos]</span>",

            "Um app que permite baixar todos os dados que você forneceu é um ótimo exemplo da <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span> em ação. <span class=\"highlight-term\" onclick=\"gerarInput('Exemplos LGPD')\">[Mostrar mais]</span>",

            "Ao receber um e-mail pedindo consentimento para continuar armazenando seus dados, isso mostra respeito à <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span>. <span class=\"highlight-term\" onclick=\"gerarInput('Outros exemplos LGPD')\">[Ver outros exemplos]</span>",

            "Quando um formulário explica exatamente por que cada dado é solicitado, temos um bom exemplo de <span class=\"highlight-term\" onclick=\"gerarInput('LGPD')\">LGPD</span> sendo aplicada. <span class=\"highlight-term\" onclick=\"gerarInput('Mais exemplos LGPD')\">[Ver mais exemplos]</span>"
        ]

    }
}







@app.route("/api/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    history = request.json.get("history", [])
    model_input = request.json.get("model", "groq/llama-3.1-8b-instant") #default is the fastest (that ive tried)

    messages = [system_prompt] + history + [{"role": "user", "content": user_input}]

    #sem acento, minúsculo
    input_normalizado = unidecode(user_input.lower())

    for tema, variacoes in decision_tree_respostas.items():
        if tema in input_normalizado:
            # Verifica se há algum modificador específico
            for modificador in variacoes:
                if modificador != "default" and modificador in input_normalizado:
                    resposta_pronta = random.choice(variacoes[modificador])
                    break
            else:
                resposta_pronta = random.choice(variacoes["default"])

            return jsonify({
                "choices": [
                    {"message": {"content": resposta_pronta}}
                ]
            })



    # usa Groq com llama (rapido)
    if model_input.startswith("groq/"):
        model_name = model_input.replace("groq/", "")
        try:
            groq_response = client_groq.chat.completions.create(
                messages=messages,
                model=model_name
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

    # fallback no openrouter
    elif model_input.startswith("openrouter/"):
        model_name = model_input.replace("openrouter/", "")
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model_name,
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



if __name__ == "__main__":
    app.run(debug=True)