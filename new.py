from google import genai
from google.genai import types
import requests
import mimetypes
import os
from IPython.display import display, Markdown, Image
import pathlib
import base64

client = genai.Client(api_key="AIzaSyBZEgzKt0gYQLjKnZeDW8F9Ixe9AMFRKzY")

def display_response(response):
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            display(Markdown(part.text))
        elif part.inline_data is not None:
            mime = part.inline_data.mime_type
            print(mime)
            data = part.inline_data.data
            display(Image(data=data))

def save_image(response, path):
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            continue
        elif part.inline_data is not None:
            mime = part.inline_data.mime_type
            data = part.inline_data.data
            decoded_data = base64.b64decode(data)
            pathlib.Path(path).write_bytes(decoded_data)

contents = 'Image of a car'

response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=contents,
    config=types.GenerateContentConfig(
        response_modalities=['text', 'image']
    )
)

display_response(response)
save_image(response, 'car.png')
