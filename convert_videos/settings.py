from iso639 import to_iso639_2
from dataclasses import dataclass

from video_utils import Codec


@dataclass
class AudioSettings:
    codec: Codec
    channels: int
    bitrate: int
    language: str = None  # type: ignore

    def __post_init__(self):
        self.get_ffmpeg_codec()

    def __str__(self):
        output = ""
        if self.language:
            output = f" -map 0:a:m:language:{to_iso639_2(self.language)}"
        else:
            output += " -map 0:a"  # Include all audio channels

        output += f" -acodec {self.get_ffmpeg_codec()}"
        if self.get_ffmpeg_codec() == "copy":
            return output

        output += f" -ab {self.bitrate}k"
        output += f" -ac {self.channels}"
        return output

    def get_ffmpeg_codec(self):
        ffmpeg_codec = None
        if self.codec.format_name == "copy":
            ffmpeg_codec = "copy"
        else:
            ffmpeg_codec = self.codec.get_ffmpeg_name()
        if not ffmpeg_codec:
            raise Exception("Failed to find the desired audio codec!")
        return ffmpeg_codec


@dataclass
class VideoSettings:
    codec: Codec
    quality: int
    preset: str
    width: int = None  # type: ignore # Or None
    encoder: str = "software"
    subtitle_language: str = None  # type: ignore

    def __post_init__(self):
        self.get_ffmpeg_codec()

    def __str__(self):
        output = self._get_stream_settings()
        output += f" -vcodec {self.get_ffmpeg_codec()}"
        if self.codec.format_name == "copy":
            return output

        output += f" -preset {self.preset}"
        output += self._get_quality_settings()
        output += self._get_codec_settings()
        output += self._get_scaling_settings()

        return output

    def _get_scaling_settings(self):
        output = ""
        if self.width:
            output += f" -vf scale={self.width}:-2"
        return output

    def _get_quality_settings(self):
        if self.encoder == "nvidia":
            # nvenc doesn't support CRF; only CQ and QP modes.
            # QP consistently provides better quality output for the same bitrate on NVENC however, so we're using that
            output = f" -rc constqp -qp {self.quality}"
            output += " -b:v 0"  # Unless bitrate is set to 0, CQ is mostly ignored

            # b-frames are disabled by default, and only supported on Turing+ architectures. Need to auto-detect this
            # output += f" -rc-lookahead -b_ref_mode middle"
        elif self.encoder == "intel":
            # qsv doesn't support CRF either; they have their own methods at the link below
            # ICQ and LA-ICQ are apparently the gold standard; but only supported on windows (weird)
            # https://www.intel.com/content/www/us/en/developer/articles/technical/common-bitrate-control-methods-in-intel-media-sdk.html
            output = f" -global_quality {self.quality}"
            if self.codec.format_name == "AVC":
                # Look-ahead is supported for x264 and is preferable for better quality
                output += " -look_ahead 1"
        else:
            output = f" -crf {self.quality}"
        return output

    def _get_codec_settings(self):
        output = ""
        if self.codec == Codec("HEVC"):
            output += " -strict -2"
        return output

    def _get_stream_settings(self):
        output = " -map 0:v"  # Include first video stream
        if self.subtitle_language:
            output += f" -map 0:s:m:language:{to_iso639_2(self.subtitle_language)}?"
        else:
            output += " -map 0:s?"  # Include all subtitle streams, if they exist
        output += " -c:s copy"
        return output

    def get_ffmpeg_codec(self):
        ffmpeg_codec = None
        if self.codec.format_name == "copy":
            ffmpeg_codec = "copy"
        else:
            ffmpeg_codec = self.codec.get_ffmpeg_name(self.encoder)
        if not ffmpeg_codec:
            raise Exception("Failed to find the desired video codec!")
        return ffmpeg_codec
