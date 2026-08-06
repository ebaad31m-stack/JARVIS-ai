import requests


OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_ai(prompt):

    data = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=data
        )

        result = response.json()

        return result.get("response", "")


    except Exception as error:

        return f"AI error: {error}"