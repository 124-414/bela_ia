from openai import OpenAI
import os

client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_image(prompt):

    img=client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    return img.data[0].url