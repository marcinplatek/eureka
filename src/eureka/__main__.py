import hashlib
import io
import os
import tempfile
from typing import Iterator, TypeVar

import pyperclip
import tiktoken
import typer
import whisper
from joblib import Memory
from pydub import AudioSegment

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "audio_processor")


class AudioProcessor:
    def __init__(self):
        self.model = whisper.load_model("base")
        self.memory = Memory(CACHE_DIR, verbose=0)

    def process_audio(self, audio_file: io.BytesIO) -> str:
        audio_bytes = audio_file.read()
        audio_hash = hashlib.md5(audio_bytes).hexdigest()

        @self.memory.cache  # type: ignore
        def hacky_cached_process_audio(audio_hash: str) -> str:
            with tempfile.NamedTemporaryFile() as tmp:
                tmp.write(audio_bytes)

                result = self.model.transcribe(tmp.name)  # type: ignore

                return result["text"]  # type: ignore

        return hacky_cached_process_audio(audio_hash)


def convert_and_concatenate_m4a_to_mp3(filepaths: list[str]) -> io.BytesIO:
    concatenated_audio = AudioSegment.empty()
    for filepath in filepaths:
        audio = AudioSegment.from_file(filepath, format="m4a")  # type: ignore
        concatenated_audio += audio  # type: ignore

    mp3_buffer = io.BytesIO()
    concatenated_audio.export(mp3_buffer, format="mp3")  # type: ignore
    mp3_buffer.seek(0)

    return mp3_buffer


def process_concatenated_audio_files(
    filepaths: list[str], audio_processor: AudioProcessor
) -> str:
    mp3_buffer = convert_and_concatenate_m4a_to_mp3(filepaths)
    process_audio_cached = audio_processor.process_audio
    return process_audio_cached(mp3_buffer)  # type: ignore


T = TypeVar("T")


def chunked(a: list[T], n: int) -> Iterator[list[T]]:
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(a), n):
        yield a[i : i + n]


def split_tokens(text: str, chunk_size: int) -> list[str]:
    enc = tiktoken.encoding_for_model("gpt-4")

    tokens = enc.encode(text)

    chunked_tokens = chunked(tokens, chunk_size)

    return [enc.decode(chunk) for chunk in chunked_tokens]


def _main(filepaths: list[str] = typer.Argument(..., help="list of filepaths")):
    typer.echo("Processing audio files...")
    result = process_concatenated_audio_files(filepaths, AudioProcessor())

    typer.echo("Processing complete!")

    chunked_result = split_tokens(result, 3500)

    for chunk in chunked_result:
        print("val:", f"{chunk[:70]}...")
        typer.prompt("Ready?")
        pyperclip.copy(chunk)  # type: ignore

    typer.echo("Done!")


def main():
    typer.run(_main)


if __name__ == "__main__":
    main()
