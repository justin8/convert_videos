import logging
from dataclasses import dataclass

from video_utils import FileMap

from .settings import AudioSettings, VideoSettings
from .video_processor import Status, VideoProcessor

log = logging.getLogger()


@dataclass
class Processor:
    directory: str
    force: bool
    video_settings: VideoSettings
    audio_settings: AudioSettings
    dry_run: bool = False
    in_place: bool = False
    extra_ffmpeg_input_args: str = ""
    extra_ffmpeg_output_args: str = ""
    temp_directory: str = None  # type: ignore
    container: str = "mkv"
    minimum_size_b: int = 0  # Minimum file size in megabytes to process
    minimum_size_per_hour_mb: int = 0  # Minimum file size per hour in MB

    def start(self):
        self._load_file_map()
        self._convert_all()
        return self.results

    def _load_file_map(self):
        self._file_map = FileMap(self.directory)
        self._file_map.load()

    def _convert_all(self):
        self.results = []
        for directory in self._file_map.contents:
            self.results += self._convert_files_in_directory(directory)
        log.info(f"Finished processing all videos in {self.directory}")
        return self.results

    def _convert_files_in_directory(self, directory):
        videos_processed = []
        return_values = []
        total_videos = len(self._file_map.contents[directory])
        for video in self._file_map.contents[directory]:
            item = self._get_video_processor(video)
            log.debug(
                f"Processing video '{video.name}' ({len(videos_processed)}/{total_videos})"
            )
            log.debug(f"Video details: {video}")
            videos_processed.append(video)

            status = item.process()
            if status == Status.BELOW_MINIMUM_SIZE:
                log.debug(
                    f"Video '{video.name}' is below the minimum size ({self.minimum_size_b // (1024 * 1024)} MB) and will not be processed."
                )
            return_values.append({"video": video, "status": status})
        log.info(f"Finished processing files in directory {directory}")
        return return_values

    def _get_video_processor(self, video):
        return VideoProcessor(
            video=video,
            video_settings=self.video_settings,
            audio_settings=self.audio_settings,
            container=self.container,
            extra_ffmpeg_input_args=self.extra_ffmpeg_input_args,
            extra_ffmpeg_output_args=self.extra_ffmpeg_output_args,
            temp_directory=self.temp_directory,
            in_place=self.in_place,
            dry_run=self.dry_run,
            force=self.force,
            minimum_size_b=self.minimum_size_b,
            minimum_size_per_hour_mb=self.minimum_size_per_hour_mb,
        )
