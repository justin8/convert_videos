from convert_videos.settings import AudioSettings, VideoSettings
from video_utils import Codec


def test_audio_settings():
    target = AudioSettings(Codec("AAC"), 2, 128)
    assert str(target) == " -acodec aac -ab 128k -ac 2 -map 0:a"


def test_video_settings_avc():
    target = VideoSettings(Codec("AVC"), 25, "slow", None)
    assert str(target) == " -map 0:v:0 -map 0:s? -c:s copy -vcodec h264 -preset slow -crf 25"


def test_video_settings_avc_nvidia():
    target = VideoSettings(Codec("AVC"), 25, "slow", hw_accel="nvidia")
    assert str(target) == " -map 0:v:0 -map 0:s? -c:s copy -vcodec h264_nvenc -preset slow -rc constqp -qp 25 -b:v 0"


def test_video_settings_hevc():
    target = VideoSettings(Codec("HEVC"), 25, "slow", None)
    assert str(target) == " -map 0:v:0 -map 0:s? -c:s copy -vcodec libx265 -preset slow -crf 25 -strict -2"


def test_video_settings_hevc_nvidia():
    target = VideoSettings(Codec("HEVC"), 25, "slow", hw_accel="nvidia")
    assert str(target) == " -map 0:v:0 -map 0:s? -c:s copy -vcodec hevc_nvenc -preset slow -rc constqp -qp 25 -b:v 0 -strict -2"


def test_video_settings_width():
    target = VideoSettings(
        codec=Codec("AVC"),
        quality=25,
        preset="slow",
        width=720,
        hw_accel=None)
    assert str(target) == " -map 0:v:0 -map 0:s? -c:s copy -vcodec h264 -preset slow -crf 25 -vf scale=720:-2"
