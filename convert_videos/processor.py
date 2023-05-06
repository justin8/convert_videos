from dataclasses import dataclass
import logging

from video_utils import FileMap

from .video_processor import VideoProcessor
from .settings import VideoSettings, AudioSettings

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
            log.debug(f"Processing video '{video.name}' ({len(videos_processed)}/{total_videos})")
            videos_processed.append(video)

            status = item.process()
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
        )
