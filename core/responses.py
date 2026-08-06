def get_response(message):

    responses = {
        "hello": "Hello. How can I assist you?",
        "good morning": "Good morning. Ready when you are.",
        "who are you": "I am JARVIS, your personal AI assistant."
    }

    return responses.get(message.lower())