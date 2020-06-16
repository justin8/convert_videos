from dataclasses import dataclass
import os
import shutil
import tempfile
import logging
import traceback
from enum import Enum, auto

from stringcase import titlecase, lowercase
from video_utils import Video

from .ffmpeg_converter import FFmpegConverter
from .settings import AudioSettings, VideoSettings

log = logging.getLogger(__name__)


class Status(Enum):
    # Successful conversion
    CONVERTED = auto()

    # If a file is already converted with renaming
    # (e.g. appending the output codec) and this is that converted file
    ALREADY_PROCESSED = auto()

    # Force can override already in desired format, but not if both original and converted files already exist
    FORCE_CONVERTED = auto()

    # The file is already using the target format, can be overridden with --force
    IN_DESIRED_FORMAT = auto()

    FAILED = auto()

    def __str__(self):
        return titlecase(lowercase(self.name))


@dataclass
class VideoProcessor:
    video: Video
    video_settings: VideoSettings
    audio_settings: AudioSettings
    container: str
    force: bool = False
    dry_run: bool = False
    in_place: bool = False
    extra_ffmpeg_input_args: str = ""
    extra_ffmpeg_output_args: str = ""
    temp_directory: str = None

    def _create_temp_file(self):
        return tempfile.mkstemp(dir=self.temp_directory, suffix=f".{self.container}")[1]

    def __str__(self):
        return f"Video: {self.video.full_path}, format: {self.video.codec.pretty_name}, quality: {self.video.quality}"

    def process(self):
        if self.video.codec == self.video_settings.codec:
            print(f"{self.video.name} is already in the desired format")
            if not self.force:
                return Status.IN_DESIRED_FORMAT
            print(f"Forcing conversion anyway (--force is enabled)")

        if self.already_processed():
            return Status.ALREADY_PROCESSED

        try:
            self.temp_file = self._create_temp_file()
            converter = FFmpegConverter(
                source_file_path=self.video.full_path,
                destination_file_path=self.temp_file,
                extra_ffmpeg_input_args=self.extra_ffmpeg_input_args,
                extra_ffmpeg_output_args=self.extra_ffmpeg_output_args,
                video_settings=self.video_settings,
                audio_settings=self.audio_settings,
                dry_run=self.dry_run,
            )
            converter.process()
            self._move_output_video()
            return Status.CONVERTED
        except Exception as e:
            print(f"Failed to convert {self.video.full_path}. Exception:")
            print(e)
            traceback.print_exc()
            print()
            return Status.FAILED

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
        print(f"Moving file from temporary storage back to original folder")
        if not self.dry_run:
            shutil.move(self.temp_file, self.renamed_path())
        if self.in_place:
            if self.dry_run:
                print(f"DRY-RUN: Would replace original file {self.video.full_path}")
                return
            print(f"Replacing original file {self.video.full_path}")
            os.remove(self.video.full_path)
            shutil.move(self.renamed_path(), self.in_place_file_path())
