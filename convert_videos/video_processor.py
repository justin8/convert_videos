import logging
import os
import shutil
import tempfile
import traceback
from dataclasses import dataclass
from enum import Enum, auto

from stringcase import lowercase, titlecase
from video_utils import Video

from .colour import colour
from .ffmpeg_converter import FFmpegConverter
from .settings import AudioSettings, VideoSettings

log = logging.getLogger()


class Status(Enum):
    # Successful conversion
    CONVERTED = auto()

    # The file would be converted, if we weren't running in dry-run mode
    WOULD_CONVERT = auto()

    # If a file is already converted with renaming
    # (e.g. appending the output codec) and this is that converted file
    ALREADY_PROCESSED = auto()

    # The file is already using the target format, can be overridden with --force
    IN_DESIRED_FORMAT = auto()

    # The file is below the minimum size and will not be processed
    BELOW_MINIMUM_SIZE = auto()

    FAILED = auto()

    def __str__(self):
        status_text = titlecase(lowercase(self.name))
        if self not in (Status.FAILED, Status.WOULD_CONVERT, Status.CONVERTED):
            return f"SKIPPING: {status_text}"
        return status_text

    def colour(self):
        c = "green"
        if self not in (Status.WOULD_CONVERT, Status.CONVERTED):
            c = "blue"
        if self == Status.FAILED:
            c = "red"
        return colour(c, str(self))


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
    temp_directory: str = None  # type: ignore
    minimum_size_b: int = 0  # Minimum file size in megabytes to process

    def _create_temp_file(self):
        return tempfile.mkstemp(dir=self.temp_directory, suffix=f".{self.container}")[1]

    def __str__(self):
        codec_name = (
            self.video.codec.pretty_name if self.video.codec is not None else "Unknown"
        )
        return f"Video: {self.video.full_path}, format: {codec_name}, quality: {self.video.quality}"

    def process(self):
        if self._is_below_minimum_size():
            return Status.BELOW_MINIMUM_SIZE

        if self.video.codec == self.video_settings.codec:
            log.debug(f"'{self.video.name}' is already in the desired format")
            if not self.force:
                return Status.IN_DESIRED_FORMAT
            log.debug("Forcing conversion anyway (--force is enabled)")

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
            if self.dry_run:
                return Status.WOULD_CONVERT
            return Status.CONVERTED
        except Exception as e:
            log.error(
                colour("red", f"Failed to convert {self.video.full_path}. Exception:")
            )
            log.error(e)
            traceback.print_exc()
            return Status.FAILED

    def _is_below_minimum_size(self):
        if self.minimum_size_b and self.video.size_b:
            if self.video.size_b < self.minimum_size_b:
                return True
        return False

    def already_processed(self):
        renamed_path = self.renamed_path()
        if os.path.exists(renamed_path):
            log.debug(
                f"File '{self.video.name}' appears to have already been converted to {renamed_path} exists. Skipping"
            )
            return True

        split_filename = os.path.splitext(self.video.name)
        codec_name = (
            self.video_settings.codec.pretty_name
            or self.video_settings.get_ffmpeg_codec()
        )
        if split_filename[0].endswith(codec_name):
            log.debug(
                f"File '{self.video.name}' already matches the renaming format. Skipping"
            )
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
        log.debug("Moving file from temporary storage back to original folder")
        if not self.dry_run:
            shutil.move(self.temp_file, self.renamed_path())
        if self.in_place:
            if self.dry_run:
                log.info(
                    colour(
                        "blue",
                        f"DRY-RUN: Would replace original file {self.video.full_path}",
                    )
                )
                return
            print(f"Replacing original file {self.video.full_path}")
            os.remove(self.video.full_path)
            shutil.move(self.renamed_path(), self.in_place_file_path())
