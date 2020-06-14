from dataclasses import dataclass
import logging
import os

import ffmpy

from .settings import AudioSettings, VideoSettings


log = logging.getLogger(__name__)


@dataclass
class FFmpegConverter:
    source_file_path: str
    destination_file_path: str
    extra_ffmpeg_args: str
    dry_run: bool
    video_settings: VideoSettings
    audio_settings: AudioSettings

    def __post__init__(self):
        self._validate_destination()

    def process(self):
        output_settings = self._generate_ffmpeg_settings()

        ff = ffmpy.FFmpeg(
            inputs={self.source_file_path: None},
            outputs={self.destination_file_path: output_settings})
        if self.dry_run:
            print(f"DRY-RUN: Would start conversion. Command: '{ff.cmd}'")
        else:
            log.info(f"Starting conversion. Command: '{ff.cmd}'")
            ff.run()

    def _generate_ffmpeg_settings(self):
        output_settings = "" + \
            "-y" + \
            " -threads 0" + \
            str(self.video_settings) + \
            str(self.audio_settings) + \
            " " + self.extra_ffmpeg_args
        return output_settings

    def _validate_destination(self):
        if os.path.exists(self.destination_file_path):
            if os.path.isfile(self.destination_file_path):
                if os.access(self.destination_file_path, os.W_OK):
                    return True
                raise IOError(
                    f"Destination file {self.destination_file_path} exists but is not writable")
            if os.path.isdir(self.destination_file_path):
                raise IOError(
                    f"Destination file {self.destination_file_path} is a directory, and not a file")
        else:
            try:
                with open(self.destination_file_path, 'w') as f:
                    f.writelines("test")
            finally:
                os.remove(self.destination_file_path)
            return True
