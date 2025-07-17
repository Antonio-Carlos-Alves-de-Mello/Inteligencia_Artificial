# === Carrega chaves da .env ===
import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai # Importa a biblioteca do Gemini

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

app = Flask(__name__)

# === Carrega chaves da .env ===
# ATENÇÃO: As chaves de API devem ser carregadas APENAS do ambiente
# Nunca coloque o valor da chave diretamente aqui, apenas o nome da variável de ambiente.
OPENAI_KEY = os.getenv("OPENAI_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY") # Chave da API do Gemini

# === Função para OpenAI ===
def usar_openai(pergunta):
    if not OPENAI_KEY:
        return "Erro: Chave OPENAI_KEY não configurada."

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",  # Ou outro modelo válido que você tenha acesso
        "messages": [{"role": "user", "content": pergunta}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Lança um erro para códigos de status HTTP ruins (4xx ou 5xx)
        resposta_json = response.json()
    except requests.exceptions.RequestException as e:
        return f"Erro de requisição à OpenAI: {str(e)}"
    except ValueError as e: # Erro ao decodificar JSON
        return f"Erro ao processar JSON da OpenAI: {str(e)}. Resposta bruta: {response.text}"

    # Se resposta contiver erro explícito da API
    if "error" in resposta_json:
        return f"Erro da API OpenAI: {resposta_json['error'].get('message', 'Erro desconhecido')}"

    # Se tudo estiver ok
    try:
        return resposta_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return f"Resposta inválida da OpenAI: {resposta_json}"

# === Função para DeepSeek ===
def usar_deepseek(pergunta):
    if not DEEPSEEK_KEY:
        return "Erro: Chave DEEPSEEK_KEY não configurada."

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": pergunta}],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Lança um erro para códigos de status HTTP ruins (4xx ou 5xx)
        resposta_json = response.json()
        
        # Verifica primeiro se há erro explícito da API
        if "error" in resposta_json:
            return f"Erro da API DeepSeek: {resposta_json['error'].get('message', 'Erro desconhecido')}"
            
        # Nova estrutura da resposta (observada na documentação atual) ou estrutura tradicional
        if "content" in resposta_json:  # Caso a resposta venha direta (menos comum para chat completions)
            return resposta_json["content"]
        elif "choices" in resposta_json and len(resposta_json["choices"]) > 0:  # Estrutura tradicional
            return resposta_json["choices"][0]["message"]["content"]
        else:
            return f"Resposta inesperada da API DeepSeek: {resposta_json}"

    except requests.exceptions.RequestException as e:
        return f"Erro de requisição à DeepSeek: {str(e)}"
    except ValueError as e: # Erro ao decodificar JSON
        return f"Erro ao processar JSON da DeepSeek: {str(e)}. Resposta bruta: {response.text}"

# === Função para Gemini ===
def usar_gemini(pergunta):
    if not GEMINI_KEY:
        return "Erro: Chave GEMINI_KEY não configurada."
    
    try:
        genai.configure(api_key=GEMINI_KEY)
        # Você pode especificar um modelo diferente se desejar, como 'gemini-1.5-flash'
        model = genai.GenerativeModel('gemini-1.5-flash-8b') 
        
        # Para interações de chat mais complexas, você pode usar model.start_chat()
        # Mas para uma única pergunta, generate_content é suficiente.
        response = model.generate_content(pergunta)
        
        # A resposta do Gemini pode ter diferentes estruturas, 
        # response.text é a forma mais comum de obter o texto gerado.
        return response.text
    except Exception as e:
        return f"Erro ao chamar API Gemini: {str(e)}"

# === Rota principal ===
@app.route("/", methods=["GET", "POST"])
def index():
    resposta = None

    if request.method == "POST":
        pergunta = request.form.get("pergunta")
        modelo = request.form.get("modelo")

        if not pergunta or not modelo:
            resposta = "Parâmetros 'pergunta' e 'modelo' são obrigatórios"
        else:
            if modelo == "gpt-3.5-turbo":
                resposta = usar_openai(pergunta)
            elif modelo == "deepseek-chat":
                resposta = usar_deepseek(pergunta)
            elif modelo == "gemini-pro":
                resposta = usar_gemini(pergunta)
            else:
                resposta = "Modelo não suportado"

    return render_template("index.html", resposta=resposta)


if __name__ == "__main__":
    # Use debug=True apenas para desenvolvimento. Desative em produção.
    app.run(debug=True)