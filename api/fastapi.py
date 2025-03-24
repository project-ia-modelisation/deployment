from fastapi import FastAPI, HTTPException
from llama_cpp import Llama
import requests

app = FastAPI()

# Charger un modèle LLaMA 2 (ex : Mistral, Llama 3, Phi-2)
model_path = "models/mistral-7b.Q4_K_M.gguf"  # Chemin vers ton modèle local
llm = Llama(model_path=model_path, n_ctx=2048)

# URL de ton API de modélisation
MODELING_API_URL = "http://localhost:5000/generate_model"

@app.post("/generate-response/")
async def generate_response(prompt: str):
    try:
        # 1️⃣ Envoi du prompt à l'IA de modélisation
        response = requests.post(MODELING_API_URL, json={"prompt": prompt})
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Erreur avec l'API de modélisation")

        model_data = response.json()  # Récupération des infos 3D/2D

        # 2️⃣ Génération de la réponse textuelle basée sur les données reçues
        full_prompt = f"""
        Tu es une IA spécialisée en modélisation 3D et 2D.
        Voici un prompt utilisateur : "{prompt}"
        Voici les données techniques générées par ton IA de modélisation :
        {model_data}

        Fournis une réponse claire et détaillée.
        """

        response = llm(full_prompt)
        return {"response": response["choices"][0]["text"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
