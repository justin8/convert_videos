from dataclasses import dataclass
import logging
import os

import ffmpy

from .colour import colour
from .settings import AudioSettings, VideoSettings


log = logging.getLogger(__name__)


@dataclass
class FFmpegConverter:
    source_file_path: str
    destination_file_path: str
    extra_ffmpeg_input_args: str
    extra_ffmpeg_output_args: str
    dry_run: bool
    video_settings: VideoSettings
    audio_settings: AudioSettings

    def __post_init__(self):
        self._validate_destination()

    def process(self):
        input_settings = self._generate_ffmpeg_settings("input")
        output_settings = self._generate_ffmpeg_settings("output")

        ff = ffmpy.FFmpeg(
            inputs={self.source_file_path: input_settings},
            outputs={self.destination_file_path: output_settings},
        )
        if self.dry_run:
            log.info(
                colour("blue", f"DRY-RUN: Would start conversion. Command: '{ff.cmd}'")
            )
        else:
            log.info(colour("blue", f"Starting conversion. Command: '{ff.cmd}'"))
            ff.run()
            log.info(colour("green", "Successfully finished conversion!"))

    def _generate_ffmpeg_settings(self, mode):
        if mode == "input":
            output = " " + self.extra_ffmpeg_input_args
            if self.video_settings.encoder == "nvidia":
                output = " -hwaccel cuvid"
            if self.video_settings.encoder == "intel":
                output = " -hwaccel qsv -hwaccel_output_format qsv"
            return output

        output = (
            ""
            + "-y"
            + " -threads 0"
            + str(self.video_settings)
            + str(self.audio_settings)
            + " "
            + self.extra_ffmpeg_output_args
        )
        return output

    def _validate_destination(self):
        if os.path.exists(self.destination_file_path):
            if os.path.isfile(self.destination_file_path):
                if os.access(self.destination_file_path, os.W_OK):
                    return True
                raise IOError(
                    f"Destination file {self.destination_file_path} exists but is not writable"
                )
            if os.path.isdir(self.destination_file_path):
                raise IOError(
                    f"Destination file {self.destination_file_path} is a directory, and not a file"
                )
        else:
            try:
                with open(self.destination_file_path, "w") as f:
                    f.writelines("test")
            finally:
                os.remove(self.destination_file_path)
            return True
