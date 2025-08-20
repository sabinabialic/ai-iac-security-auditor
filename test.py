import os
from huggingface_hub import InferenceClient

# 1. Initialize the client
# The token is automatically read from your HUGGING_FACE_HUB_TOKEN environment variable
client = InferenceClient()

# 2. Define your prompt as a list of messages for a conversation
messages = [
    {"role": "user", "content": "Finish the story: Once upon a time, in a land far, far away,"}
]

# 3. Use the chat_completion method instead of text_generation
response = client.chat_completion(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    messages=messages,
    max_tokens=50 # Note: The parameter is max_tokens for this method
)

# 4. Print the generated text from the response object
print(response.choices[0].message.content)