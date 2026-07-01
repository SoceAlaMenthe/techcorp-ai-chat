# Preuves d'exécution - INFRA (serveur Ollama réel)

## ollama --version
ollama version is 0.31.1

## ollama list
NAME                       ID              SIZE      MODIFIED      
techcorp-finance:latest    ccc4de04894b    2.2 GB    2 minutes ago    
phi3.5:latest              61819fb370a3    2.2 GB    2 minutes ago    

## Health-check (python healthcheck.py)
[1/3] Version API (http://localhost:11434/api/version) ... OK - ollama 0.31.1
[2/3] Modele 'techcorp-finance' charge ... OK
[3/3] Inference de test ... OK - 5.6s - reponse: "READY\n\nNote: I'm an AI language model with no access to sens"

RESULTAT : SERVEUR OPERATIONNEL

## Requête API réelle (/api/generate)
```json
{
  "model": "techcorp-finance",
  "response": "Compound interest refers to the addition of interest to the principal sum of a deposit or loan so that the added interest also earns interest during subsequent periods. This results in exponential growth of the investment over time, as each period'thy interest is calculated on an increasingly larger amount due to previous interests being included with the initial sum.",
  "total_duration_s": 9.18
}
```
