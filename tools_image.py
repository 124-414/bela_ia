import os
from openai import OpenAI
from dotenv import load_dotenv

def create_image(prompt):
    """
    Motor de geração de imagens da BELA.
    A chave é carregada apenas no momento da chamada.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("ERRO: API Key não encontrada.")
        return None
        
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Professional technical photography, high definition, cinematic: {prompt}",
            size="1024x1024",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        print(f"Erro na geração: {e}")
        return None