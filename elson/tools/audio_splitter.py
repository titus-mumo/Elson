from re import A
from sys import getsizeof
from pydub import AudioSegment
from pydub.silence import split_on_silence
import concurrent.futures
from abc import ABC
from .logger import Logger


class AudioSplitter(ABC):
    def load_chunks(self) -> list[AudioSegment]:
        return []


class TimebasedAudioSplitter(AudioSplitter):
    def __init__(self, file: str, interval: int) -> None:
        self.file = file
        self.audio = AudioSegment.from_file(self.file)
        self.s = interval  # in secs
        self.ms = 1000 * self.s

    @Logger.log
    def load_chunks(self):
        return [
            self.audio[i * self.ms: i * self.ms + self.ms]
            for i in range(len(self.audio) // self.ms + 1)
        ]


class SilenceAudioSplitter(AudioSplitter):
    class AudioChunkGroup:
        def __init__(self, chunks):
            self.chunks = chunks
            self.size = len(self.chunks)
            self.av_size = self.get_average_size()
            self.is_valid = self.av_size > 0

        def get_average_size(self):
            size = len(self.chunks)
            if not size:
                return 0
            return getsizeof(self.chunks) / size

        def __str__(self) -> str:
            if self.av_size:
                return f"{self.av_size} bytes"
            return "Invalid"

    DEFAULT_OFFSET = 10
    DEFAULT_MIN_SILENCE_LEN = 1500
    DEFAULT_MAX_N_OF_CHUNKS = 15
    DEFAULT_MAX_CHUNK_SIZE = 60  # in bytes
    DEFAULT_MIN_CHUNK_SIZE = 20  # in bytes
    DEFAULT_MAX_N_OF_WORKERS = 5

    def __init__(self, file: str) -> None:
        self.file = file
        self.audio = AudioSegment.from_mp3(self.file)

    def _load_chunks(
        self,
        min_silence_len: int,
        silence_thresh: int,
        keep_silence=200,
    ) -> AudioChunkGroup:
        return SilenceAudioSplitter.AudioChunkGroup(
            split_on_silence(
                audio_segment=self.audio,
                min_silence_len=min_silence_len,
                silence_thresh=silence_thresh,
                keep_silence=keep_silence,
            )
        )

    @Logger.log
    def load_chunks(
        self, min_silence_len=DEFAULT_MIN_SILENCE_LEN, verbose=True
    ) -> list:
        """
        Splits mp3 files into chunks

        Parameters:
        offset (int): Increment for finding the best configuration
        min_silence_len (int): Minumum length of silence

        Returns:
        list[AudioSegment]
        """
        Logger.debug("Converting audio into chunks")
        best_chunk = None

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.DEFAULT_MAX_N_OF_WORKERS
        ) as executor:
            future_to_offset = {
                executor.submit(
                    self._load_chunks,
                    min_silence_len,
                    -offset,
                )
                for offset in range(1, 100, self.DEFAULT_OFFSET)
            }
            for i, future in enumerate(
                concurrent.futures.as_completed(future_to_offset)
            ):
                c = future.result()
                if not c.is_valid:
                    pass

                try:
                    Logger.debug(
                        f"Phase_{i+1}\nNumber of chunks: {c.size}.\nAverage chunk size: {c.av_size}.\n\n"
                    )
                    if c.av_size <= self.DEFAULT_MAX_N_OF_CHUNKS and (
                        not best_chunk or (c.av_size > best_chunk.size)
                    ):
                        best_chunk = c

                except Exception as exc:
                    Logger.warn(
                        f"Something went wrong while splitting chunks. See error msg: {exc}"
                    )

        if best_chunk:
            Logger.info(
                f"Audio splitting into chunks complete! Number of chunks: {best_chunk.size}"
            )

        return best_chunk.chunks if best_chunk else []
