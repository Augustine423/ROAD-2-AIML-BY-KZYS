
import os
import asyncio
import base64
import queue

import pyaudio
from dotenv import load_dotenv

from azure.identity.aio import AzureCliCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    InputAudioFormat,
    Modality,
    OutputAudioFormat,
    RequestSession,
    ServerEventType,
    AudioNoiseReduction,
    AudioEchoCancellation,
    AzureSemanticVadMultilingual,
    AzureStandardVoice,
)


class AudioProcessor:
    """Capture microphone audio and play audio from VoiceLive."""

    def __init__(self, connection):
        self.connection = connection
        self.loop = None
        self.audio = pyaudio.PyAudio()

        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 24000
        self.chunk_size = 1200

        self.input_stream = None
        self.output_stream = None
        self.playback_queue = queue.Queue()
        self.closed = False

    def start_capture(self):
        """Start microphone capture and send audio to VoiceLive."""

        if self.input_stream is not None:
            return

        self.loop = asyncio.get_running_loop()

        def capture_callback(in_data, frame_count, time_info, status):
            if self.closed:
                return (None, pyaudio.paComplete)

            audio_base64 = base64.b64encode(in_data).decode("utf-8")

            future = asyncio.run_coroutine_threadsafe(
                self.connection.input_audio_buffer.append(
                    audio=audio_base64
                ),
                self.loop,
            )

            # Retrieve asynchronous errors without blocking the audio thread.
            def report_error(fut):
                try:
                    fut.result()
                except Exception as exc:
                    print(f"⚠️ Audio upload failed: {exc}")

            future.add_done_callback(report_error)

            return (None, pyaudio.paContinue)

        self.input_stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=capture_callback,
        )

        print("🎤 Microphone started")

    def start_playback(self):
        """Start the speaker output stream."""

        if self.output_stream is not None:
            return

        remaining = bytearray()

        def playback_callback(in_data, frame_count, time_info, status):
            nonlocal remaining

            bytes_needed = (
                frame_count
                * self.channels
                * pyaudio.get_sample_size(self.format)
            )

            while len(remaining) < bytes_needed:
                try:
                    chunk = self.playback_queue.get_nowait()
                except queue.Empty:
                    break

                if chunk is None:
                    break

                remaining.extend(chunk)

            output = bytes(remaining[:bytes_needed])
            del remaining[:bytes_needed]

            if len(output) < bytes_needed:
                output += bytes(bytes_needed - len(output))

            return (output, pyaudio.paContinue)

        self.output_stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=playback_callback,
        )

        print("🔊 Speakers ready")

    def queue_audio(self, audio_data):
        """Queue decoded PCM audio bytes for playback."""
        if isinstance(audio_data, str):
            audio_data = base64.b64decode(audio_data)

        self.playback_queue.put(audio_data)

    def clear_playback_queue(self):
        """Discard audio that has not played yet."""
        while True:
            try:
                self.playback_queue.get_nowait()
            except queue.Empty:
                break

    def shutdown(self):
        """Stop and release audio resources."""

        if self.closed:
            return

        self.closed = True

        for stream in (self.input_stream, self.output_stream):
            if stream is not None:
                try:
                    if stream.is_active():
                        stream.stop_stream()
                except Exception:
                    pass

                try:
                    stream.close()
                except Exception:
                    pass

        self.audio.terminate()
        print("🔇 Audio stopped")


class VoiceAssistant:
    """Connect to a hosted Azure AI Foundry voice agent."""

    def __init__(
        self,
        endpoint,
        agent_name,
        project_name,
        credential,
    ):
        self.endpoint = endpoint
        self.agent_name = agent_name
        self.project_name = project_name
        self.credential = credential

        self.connection = None
        self.audio_processor = None

    async def start(self):
        print("\n" + "=" * 60)
        print("🎙️  AZURE VOICELIVE VOICE AGENT")
        print("=" * 60)

        try:
            async with connect(
                endpoint=self.endpoint,
                credential=self.credential,
                agent_name=self.agent_name,
                project_name=self.project_name,
            ) as connection:
                self.connection = connection
                self.audio_processor = AudioProcessor(connection)

                await self.setup_session()
                self.audio_processor.start_playback()

                print("\n✅ Connected. Start speaking!")
                print("Press Ctrl+C to exit.\n")

                await self.process_events()

        finally:
            if self.audio_processor is not None:
                self.audio_processor.shutdown()

    async def setup_session(self):
        """Configure audio and voice activity detection."""

        session_config = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            voice=AzureStandardVoice(
                name="en-US-Ava:DragonHDLatestNeural"
            ),
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,
            turn_detection=AzureSemanticVadMultilingual(),
            input_audio_echo_cancellation=AudioEchoCancellation(),
            input_audio_noise_reduction=AudioNoiseReduction(
                type="azure_deep_noise_suppression"
            ),
        )

        await self.connection.session.update(session=session_config)
        print("⚙️ Session configured")

    async def process_events(self):
        """Receive events from the VoiceLive service."""

        async for event in self.connection:
            await self.handle_event(event)

    async def handle_event(self, event):
        event_type = event.type

        if event_type == ServerEventType.SESSION_UPDATED:
            print("📡 Session updated")

            if self.audio_processor is not None:
                self.audio_processor.start_capture()

        elif (
            event_type
            == ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED
        ):
            print(f"👤 You: {event.get('transcript', '')}")

        elif event_type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE:
            print(f"🤖 Agent: {event.get('transcript', '')}")

        elif event_type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
            self.audio_processor.clear_playback_queue()
            print("🎤 Listening...")

        elif event_type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED:
            print("🤔 Thinking...")

        elif event_type == ServerEventType.RESPONSE_AUDIO_DELTA:
            self.audio_processor.queue_audio(event.delta)

        elif event_type == ServerEventType.RESPONSE_AUDIO_DONE:
            print("✓ Response complete\n")

        elif event_type == ServerEventType.ERROR:
            print(f"❌ VoiceLive error: {event.error.message}")


async def async_main():
    load_dotenv()

    endpoint = os.getenv("AZURE_VOICELIVE_ENDPOINT")
    agent_name = os.getenv("AZURE_VOICELIVE_AGENT_ID")
    project_name = os.getenv("AZURE_VOICELIVE_PROJECT_NAME")

    missing = [
        name
        for name, value in (
            ("AZURE_VOICELIVE_ENDPOINT", endpoint),
            ("AZURE_VOICELIVE_AGENT_ID", agent_name),
            ("AZURE_VOICELIVE_PROJECT_NAME", project_name),
        )
        if not value
    ]

    if missing:
        raise ValueError(
            "Missing environment variables: " + ", ".join(missing)
        )

    async with AzureCliCredential() as credential:
        assistant = VoiceAssistant(
            endpoint=endpoint,
            agent_name=agent_name,
            project_name=project_name,
            credential=credential,
        )

        await assistant.start()


def main():
    try:
        os.system("cls" if os.name == "nt" else "clear")
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as exc:
        print(f"\n❌ An error occurred: {exc}")


if __name__ == "__main__":
    main()
