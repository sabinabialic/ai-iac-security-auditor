import os
from huggingface_hub import InferenceClient

# The token is automatically read from your HUGGING_FACE_HUB_TOKEN environment variable
client = InferenceClient()

messages = [
    {"role": "user", "content": "Finish the story: Once upon a time, in a land far, far away,"}
]

response = client.chat_completion(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    messages=messages,
    max_tokens=50 # Note: The parameter is max_tokens for this method
)

print(response.choices[0].message.content)