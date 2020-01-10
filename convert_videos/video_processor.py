from dataclasses import dataclass
import os
import shutil
import tempfile
import logging

from video_utils import Video

from .ffmpeg_converter import FFmpegConverter
from .settings import AudioSettings, VideoSettings

log = logging.getLogger(__name__)


@dataclass
class VideoProcessor:
    video: Video
    video_settings: VideoSettings
    audio_settings: AudioSettings
    container: str
    in_place: bool = False
    extra_ffmpeg_args: str = ""
    temp_directory: str = None

    # def __post__init__(self):
    #     self.temp_file = self._create_temp_file()

    def _create_temp_file(self):
        return tempfile.mkstemp(dir=self.temp_directory, suffix=f".{self.container}")[1]

    def __str__(self):
        return f"Video: {self.video.full_path}, format: {self.video.codec.pretty_name}, quality: {self.video.quality}"

    def process(self):
        self.temp_file = self._create_temp_file()
        converter = FFmpegConverter(
            source_file_path=self.video.full_path,
            destination_file_path=self.temp_file,
            extra_ffmpeg_args=self.extra_ffmpeg_args,
            video_settings=self.video_settings,
            audio_settings=self.audio_settings
        )
        converter.process()
        self._move_output_video()

    def already_processed(self):
        renamed_path = self.renamed_path()
        if os.path.exists(renamed_path):
            print(
                f"File {self.video.name} appears to have already been converted to {renamed_path} exists. Skipping")
            return True

        split_filename = os.path.splitext(self.video.name)
        codec_name = self.video_settings.codec.pretty_name
        if split_filename[0].endswith(codec_name):
            print(
                f"File {self.video.name} already matches the renaming format. Skipping")
            return True

        return False

    def renamed_path(self):
        split_filename = os.path.splitext(self.video.full_path)
        codec_name = self.video_settings.codec.pretty_name
        return f"{split_filename[0]} - {codec_name}.{self.container}"

    def in_place_file_path(self):
        split_filename = os.path.splitext(self.video.full_path)
        return f"{split_filename[0]}.{self.container}"

    def _move_output_video(self):
        shutil.move(self.temp_file, self.renamed_path())
        if self.in_place:
            print(f"Replacing original file {self.video.full_path}")
            os.remove(self.video.full_path)
            shutil.move(self.renamed_path(), self.in_place_file_path())
