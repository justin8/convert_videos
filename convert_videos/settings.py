from dataclasses import dataclass

from video_utils import Codec


@dataclass
class AudioSettings:
    codec: Codec
    channels: int
    bitrate: int

    def __str__(self):
        output = ""
        output += f" -acodec {self.codec.ffmpeg_name}"
        output += f" -ab {self.bitrate}k"
        output += f" -ac {self.channels}"
        return output


@dataclass
class VideoSettings:
    codec: Codec
    quality: int
    preset: str
    hw_accel: str
    width: int = None  # Or None

    def __str__(self):
        output = f" -vcodec {self._get_ffmpeg_codec()}"
        if self.codec.ffmpeg_name == "copy":
            return output

        output += f" -crf {self.quality}"
        output += f" -preset {self.preset}"

        if self.codec == Codec("HEVC"):
            output += f" -strict -2"

        if self.width:
            output += f" -vf scale={self.width}:-2"

        return output

    def _get_ffmpeg_codec(self):
        ffmpeg_codec = None
        if self.codec.format_name == "copy":
            ffmpeg_codec = "copy"
        elif self.hw_accel == "nvidia":
            if self.codec.format_name == "HEVC":
                ffmpeg_codec = "hevc_nvenc"
            if self.codec.format_name == "AVC":
                ffmpeg_codec = "h264_nvenc"
        else:
            ffmpeg_codec = self.codec.ffmpeg_name
        if not ffmpeg_codec:
            raise Exception("Failed to find the desired codec!")
        return ffmpeg_codec
