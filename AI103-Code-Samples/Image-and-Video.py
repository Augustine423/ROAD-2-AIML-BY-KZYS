# SLIDE 59
# ============================================================
# AZURE OPENAI - TEXT TO IMAGE GENERATION
# Generates an image from a text prompt and saves the resulting image to a local file.
# ============================================================

import base64

# GENERATE AN IMAGE
img_results = client.images.generate(
    model="FLUX.1-Kontext-pro",
    prompt="A robot eating a cheeseburger.",
    n=1,
    size="1024x1024",
)

# SAVE THE GENERATED IMAGE
image_data = base64.b64decode(
    img_results.data[0].b64_json
)

with open("image.png", "wb") as image_file:
    image_file.write(image_data)

print("Image saved as image.png")



# SLIDE 60
# ============================================================
# AZURE OPENAI - IMAGE TO TEXT (RESPONSES API)
# Sends an image and a text prompt to a multimodal model and receives a text response describing or analyzing the image.
# ============================================================

import base64
from pathlib import Path

# LOAD IMAGE FROM LOCAL FILE
image_path = Path("dragon-fruit.jpeg")
image_format = "jpeg"

with open(image_path, "rb") as image_file:
    image_data = base64.b64encode(
        image_file.read()
    ).decode("utf-8")

# Create a data URL from the image (You can also use a public web URL instead)
data_url = (
    f"data:image/{image_format};base64,{image_data}"
)

# SEND IMAGE TO THE MODEL
response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "developer",
            "content": "You are an AI assistant for chefs planning recipes."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "What desserts could I make with this?"
                },
                {
                    "type": "input_image",
                    "image_url": data_url
                }
            ]
        }
    ]
)

# DISPLAY THE RESPONSE - The model analyzes the image and answers the question using both the image and text prompt.

print(response.output_text)



# SLIDE 60
# ============================================================
# AZURE OPENAI - IMAGE TO TEXT (CHAT COMPLETIONS API)
# Sends an image and a text prompt to a multimodal model using the Chat Completions API.
# ============================================================

import base64
from pathlib import Path

# LOAD IMAGE FROM LOCAL FILE
image_path = Path("orange.jpeg")
image_format = "jpeg"

with open(image_path, "rb") as image_file:
    image_data = base64.b64encode(
        image_file.read()
    ).decode("utf-8")

# Create a data URL from the image (You can also use a public web URL instead)
data_url = (
    f"data:image/{image_format};base64,{image_data}"
)

# SEND IMAGE TO THE MODEL
response = client.chat.completions.create(
    model="Phi-4-multimodal-instruct",
    messages=[
        {
            "role": "system",
            "content": (
                "You are an AI assistant for chefs "
                "planning recipes."
            )
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What can I make with this fruit?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_url
                    }
                }
            ]
        }
    ]
)

# DISPLAY THE RESPONSE - The model analyzes the image and answers the question using both the image and text prompt.
print(response.choices[0].message.content)



# SLIDE 61
# ============================================================
# AZURE OPENAI - TEXT TO VIDEO GENERATION
# Generates a video from a text prompt using a video model, monitors the job status, and downloads the completed video.
# ============================================================

import time

# CREATE A VIDEO GENERATION JOB
video = client.videos.create(
    model="sora-2",
    prompt= "A robot walks through a rainy city street at dusk, neon signs reflecting in puddles",
    size="1280x720",
    seconds=4,
    input_reference=open("landscape.png", "rb")
)

print(f"Video creation started. ID: {video.id}")

# POLL UNTIL THE VIDEO IS COMPLETE
while video.status not in [
    "completed",
    "failed",
    "cancelled"
]:

    print(f"Status: {video.status}. Waiting...")

    time.sleep(20)

    video = client.videos.retrieve(
        video.id
    )

# DOWNLOAD THE COMPLETED VIDEO
if video.status == "completed":

    content = client.videos.download_content(
        video.id,
        variant="video"
    )

    content.write_to_file("output.mp4")

    print("Video saved to output.mp4")



# SLIDE 62
# ============================================================
# AZURE OPENAI - VIDEO REMIXING
# Creates a new version of an existing video by modifying it with a new prompt.
# ============================================================

# REMIX AN EXISTING VIDEO

video = client.videos.remix(
    video_id="video_abc123",
    prompt="Change the color palette to warm sunset tones"
)

print(f"Remix started. Video ID: {video.id}")