from dataclasses import dataclass

from .video_processor import VideoProcessor, VideoSettings, AudioSettings
from video_utils import FileMap
import traceback

# TODO: Use logging module everywhere


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
    temp_directory: str = None
    container: str = "mkv"

    def start(self):
        self._load_file_map()
        self._convert_all()

    def _load_file_map(self):
        self._file_map = FileMap(self.directory)
        self._file_map.load()

    def _convert_all(self):
        failures = []

        for directory in self._file_map.contents:
            print(f"Working in directory {directory}")
            self._convert_files_in_directory(directory, failures)
        print(f"Finished converting all videos!")
        if failures:
            print(f"The below files failed to convert correctly")
            for failure in failures:
                print(failure)

    def _convert_files_in_directory(self, directory, failures):
        videos_processed = []
        total_videos = len(self._file_map.contents[directory])
        for video in self._file_map.contents[directory]:
            item = self._get_video_processor(video)
            print(
                f"Processing video {video.full_path} ({len(videos_processed)}/{total_videos})")
            videos_processed.append(video)

            if video.codec == self.video_settings.codec:
                print(f"{video.name} is already in the desired format")
                if not self.force:
                    continue
                print(f"Forcing conversion anyway (--force is enabled)")

            if item.already_processed():
                continue

            try:
                item.process()
            except Exception as e:
                failures.append(item)
                print(f"Failed to convert {video.full_path}. Exception:")
                print(e)
                traceback.print_exc()
                print()
        print(f"Finished converting files in directory {directory}")

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
        )
