from fastapi import FastAPI, HTTPException
import redis
import httpx
import json
import os

# Initialisation de FastAPI
app = FastAPI()

# Connexion à Redis (via les variables d'environnement du Docker Compose)
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_client = redis.Redis(host=redis_host, port=int(redis_port), db=0, decode_responses=True)

# URLs des services basées sur Docker Compose
MODEL_TRAINING_URL = "http://model-training:5000"
MODEL_SERVING_URL = "http://model-serving:5000"
DATA_PROCESSING_URL = "http://data-processing:5000"
EXPERIMENTS_URL = "http://experiments:5000"

# ---------------- API PRINCIPALE ----------------

@app.get("/")
def read_root():
    return {"message": "API Centrale - Orchestration des Services IA"}

# ----------------- PRÉTRAITEMENT -----------------

@app.post("/preprocess/")
async def preprocess_data(data: dict):
    """
    Envoie les données au service data-processing et stocke le résultat en cache.
    """
    cache_key = f"preprocess:{json.dumps(data)}"
    cached_result = redis_client.get(cache_key)

    if cached_result:
        return json.loads(cached_result)  # Retourne la version en cache

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{DATA_PROCESSING_URL}/preprocess", json=data)

    if response.status_code == 200:
        result = response.json()
        redis_client.set(cache_key, json.dumps(result), ex=3600)  # Cache avec expiration 1h
        return result
    else:
        raise HTTPException(status_code=response.status_code, detail="Erreur prétraitement")

# ----------------- ENTRAÎNEMENT DU MODÈLE -----------------

@app.post("/train/")
async def train_model():
    """
    Déclenche l'entraînement du modèle via model-training.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MODEL_TRAINING_URL}/train")

    if response.status_code == 200:
        return {"message": "Entraînement lancé avec succès"}
    else:
        raise HTTPException(status_code=response.status_code, detail="Erreur lors de l'entraînement")

# ----------------- INFÉRENCE (PRÉDICTION) -----------------

@app.post("/predict/")
async def predict(prompt: dict):
    """
    Envoie un prompt au service model-serving et stocke le résultat en cache.
    """
    cache_key = f"predict:{json.dumps(prompt)}"
    cached_result = redis_client.get(cache_key)

    if cached_result:
        return json.loads(cached_result)  # Retourne la version en cache

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MODEL_SERVING_URL}/predict", json=prompt)

    if response.status_code == 200:
        result = response.json()
        redis_client.set(cache_key, json.dumps(result), ex=600)  # Cache pendant 10 min
        return result
    else:
        raise HTTPException(status_code=response.status_code, detail="Erreur d'inférence")

# ----------------- EXPÉRIMENTATION -----------------

@app.get("/experiments/")
async def run_experiments():
    """
    Exécute un test sur le modèle avec des hyperparamètres expérimentaux.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{EXPERIMENTS_URL}/run_tests")

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Erreur dans l'expérimentation")

# ----------------- CACHE REDIS -----------------

@app.get("/cache/{key}")
def get_cached_value(key: str):
    """
    Récupère une valeur en cache depuis Redis.
    """
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    else:
        raise HTTPException(status_code=404, detail="Clé non trouvée dans le cache")

@app.delete("/cache/{key}")
def delete_cached_value(key: str):
    """
    Supprime une valeur du cache Redis.
    """
    redis_client.delete(key)
    return {"message": f"Cache supprimé pour la clé {key}"}
