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
        output += f" -ab {self.bitrate}"
        output += f" -ac {self.channels}"
        return output


@dataclass
class VideoSettings:
    codec: Codec
    quality: int
    preset: str
    width: int = None  # Or None

    def __str__(self):
        output = f" -vcodec {self.codec.ffmpeg_name}"
        if self.codec.ffmpeg_name == "copy":
            return output

        output += f" -crf {self.quality}"
        output += f" -preset {self.preset}"

        if self.codec == Codec("HEVC"):
            output += f" -strict -2"

        if self.width:
            output += f" -vf scale={self.width}:-2"

        return output
