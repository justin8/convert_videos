from dataclasses import dataclass

from video_utils import Codec


@dataclass
class AudioSettings:
    codec: Codec
    channels: int
    bitrate: int

    def __str__(self):
        output = ""
        output += f" -acodec {self.codec.get_ffmpeg_name()}"
        output += f" -ab {self.bitrate}k"
        output += f" -ac {self.channels}"
        output += f" -map 0:a"  # Include all audio channels
        return output


@dataclass
class VideoSettings:
    codec: Codec
    quality: int
    preset: str
    width: int = None  # Or None
    encoder: str = "software"

    def __str__(self):
        output = self._get_stream_settings()
        output += f" -vcodec {self._get_ffmpeg_codec()}"
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
        else:
            output = f" -crf {self.quality}"
        return output

    def _get_codec_settings(self):
        output = ""
        if self.codec == Codec("HEVC"):
            output += f" -strict -2"
        return output

    def _get_stream_settings(self):
        output = " -map 0:v:0"  # Include first video stream
        output += " -map 0:s?"  # Include all subtitle streams, if they exist
        output += " -c:s copy"
        return output

    def _get_ffmpeg_codec(self):
        ffmpeg_codec = None
        if self.codec.format_name == "copy":
            ffmpeg_codec = "copy"
        else:
            ffmpeg_codec = self.codec.get_ffmpeg_name(self.encoder)
        if not ffmpeg_codec:
            raise Exception("Failed to find the desired codec!")
        return ffmpeg_codec
