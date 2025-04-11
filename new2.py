API_KEY = "AIzaSyBZEgzKt0gYQLjKnZeDW8F9Ixe9AMFRKzY"

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

client = genai.Client(api_key=API_KEY)
image = Image.open('caucal2.jpeg')
prompt = ("make business suit on this man, of olive green color with background blurred, full body shoot")

response = client.models.generate_content(
    model="gemini-2.0-flash-exp-image-generation",
    contents=[prompt,image],
    config=types.GenerateContentConfig(
        response_modalities=['text', 'image']
    )
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = Image.open(BytesIO(base64.b64decode(part.inline_data.data)))
        image.save("edited-image.png")
        image.show()
