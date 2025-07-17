import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

# Carrega a chave da API do Gemini
GEMINI_KEY = os.getenv("GEMINI_KEY")

if not GEMINI_KEY:
    print("Erro: Chave GEMINI_KEY não configurada no arquivo .env.")
    print("Por favor, verifique se seu arquivo .env contém GEMINI_KEY='SUA_CHAVE_AQUI'")
else:
    try:
        genai.configure(api_key=GEMINI_KEY)

        print("Listando modelos disponíveis do Gemini:")
        for m in genai.list_models():
            # Filtra apenas modelos que suportam a geração de conteúdo de texto
            if 'generateContent' in m.supported_generation_methods:
                print(f"  Nome: {m.name}")
                print(f"  Descrição: {m.description}")
                print(f"  Métodos Suportados: {m.supported_generation_methods}")
                print("-" * 30)

    except Exception as e:
        print(f"Ocorreu um erro ao listar os modelos: {e}")

