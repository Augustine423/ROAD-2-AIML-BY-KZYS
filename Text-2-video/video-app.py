
import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider,
)

# ============================================================
# 1. Load configuration
# ============================================================

load_dotenv()

endpoint = os.getenv("OPENAI_BASE_URL")
model_deployment = os.getenv("MODEL_DEPLOYMENT")

if not endpoint or not model_deployment:
    raise ValueError(
        "Missing configuration. Check OPENAI_BASE_URL "
        "and MODEL_DEPLOYMENT in your .env file."
    )

# ============================================================
# 2. Configure Azure authentication
# ============================================================

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default",
)

client = OpenAI(
    base_url=endpoint,
    api_key=token_provider,
    timeout=60.0,
    max_retries=2,
)


# ============================================================
# 3. Poll video generation status
# ============================================================

def poll_video_status(video_id):
    """Wait until the video completes or fails."""

    print(f"\nChecking video status: {video_id}")

    while True:
        video = client.videos.retrieve(video_id)

        print(
            f"Status: {video.status} | "
            f"Progress: {getattr(video, 'progress', 'N/A')}%"
        )

        if video.status == "completed":
            print("Video generation completed successfully!")
            return video

        if video.status in ("failed", "cancelled"):
            error = getattr(video, "error", None)
            raise RuntimeError(
                f"Video generation {video.status}. Error: {error}"
            )

        time.sleep(20)


# ============================================================
# 4. Download a completed video
# ============================================================

def download_video(video_id, output_filename="output.mp4"):
    """Download the generated video to a local file."""

    print(f"\nDownloading video: {video_id}")

    content = client.videos.download_content(
        video_id,
        variant="video",
    )

    content.write_to_file(output_filename)

    print(f"Video saved successfully: {os.path.abspath(output_filename)}")


# ============================================================
# 5. Generate a video from a text prompt
# ============================================================

def generate_video_from_text(
    prompt,
    output_filename="original_video.mp4",
    size="1280x720",
    seconds=4,
):
    """Generate a video from a text prompt."""

    print("\nStarting text-to-video generation...")

    video = client.videos.create(
        model=model_deployment,
        prompt=prompt,
        size=size,
        seconds=seconds,
    )

    print(f"Video ID: {video.id}")
    print(f"Initial status: {video.status}")

    video = poll_video_status(video.id)

    download_video(video.id, output_filename)

    return video


# ============================================================
# 6. Remix an existing video
# ============================================================

def remix_video(
    video_id,
    prompt,
    output_filename="remixed_video.mp4",
):
    """Remix a previously generated video."""

    print(f"\nStarting video remix: {video_id}")

    remixed = client.videos.remix(
        video_id=video_id,
        prompt=prompt,
    )

    print(f"Remix ID: {remixed.id}")
    print(f"Initial status: {remixed.status}")

    remixed = poll_video_status(remixed.id)

    download_video(remixed.id, output_filename)

    return remixed


# ============================================================
# 7. Generate a video from a reference image
# ============================================================

def generate_video_from_image(
    image_path,
    prompt,
    output_filename="image_reference_video.mp4",
    size="1280x720",
    seconds=8,
):
    """Generate a video using a local reference image."""

    if not os.path.isfile(image_path):
        raise FileNotFoundError(
            f"Reference image not found: {image_path}"
        )

    print(f"\nStarting image-to-video generation: {image_path}")

    with open(image_path, "rb") as image_file:
        video = client.videos.create(
            model=model_deployment,
            prompt=prompt,
            input_reference=image_file,
            size=size,
            seconds=seconds,
        )

    print(f"Video ID: {video.id}")
    print(f"Initial status: {video.status}")

    video = poll_video_status(video.id)

    download_video(video.id, output_filename)

    return video


# ============================================================
# 8. Main application menu
# ============================================================

def main():
    while True:
        print("\n====================================")
        print("     AZURE VIDEO GENERATION APP")
        print("====================================")
        print("1. Generate video from text")
        print("2. Remix an existing video")
        print("3. Generate video from a reference image")
        print("4. Exit")

        choice = input("\nSelect an option (1-4): ").strip()

        try:
            if choice == "1":
                prompt = input(
                    "\nEnter your video prompt: "
                ).strip()

                if not prompt:
                    print("Please enter a prompt.")
                    continue

                filename = input(
                    "Output filename [original_video.mp4]: "
                ).strip() or "original_video.mp4"

                video = generate_video_from_text(
                    prompt=prompt,
                    output_filename=filename,
                )

                print(f"\nCompleted video ID: {video.id}")

            elif choice == "2":
                video_id = input(
                    "\nEnter the ID of a completed video: "
                ).strip()

                prompt = input(
                    "Enter the changes for the remix: "
                ).strip()

                if not video_id or not prompt:
                    print("Video ID and prompt are required.")
                    continue

                filename = input(
                    "Output filename [remixed_video.mp4]: "
                ).strip() or "remixed_video.mp4"

                remixed = remix_video(
                    video_id=video_id,
                    prompt=prompt,
                    output_filename=filename,
                )

                print(f"\nCompleted remix ID: {remixed.id}")

            elif choice == "3":
                image_path = input(
                    "\nEnter reference image path: "
                ).strip().strip('"')

                prompt = input(
                    "Describe how the image should be animated: "
                ).strip()

                if not image_path or not prompt:
                    print("Image path and prompt are required.")
                    continue

                filename = input(
                    "Output filename [image_reference_video.mp4]: "
                ).strip() or "image_reference_video.mp4"

                video = generate_video_from_image(
                    image_path=image_path,
                    prompt=prompt,
                    output_filename=filename,
                )

                print(f"\nCompleted video ID: {video.id}")

            elif choice == "4":
                print("Exiting application.")
                break

            else:
                print("Invalid option. Please choose 1, 2, 3, or 4.")

        except Exception as ex:
            print(f"\nError: {ex}")


# ============================================================
# 9. Application entry point
# ============================================================

if __name__ == "__main__":
    main()
