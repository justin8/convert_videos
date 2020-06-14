from convert_videos.settings import AudioSettings, VideoSettings
from video_utils import Codec


def test_audio_settings():
    target = AudioSettings(Codec("AAC"), 2, 128)
    assert str(target) == " -acodec aac -ab 128k -ac 2"


def test_video_settings_avc():
    target = VideoSettings(Codec("AVC"), 25, "slow", None)
    assert str(target) == " -vcodec h264 -crf 25 -preset slow"


def test_video_settings_avc_nvidia():
    target = VideoSettings(Codec("AVC"), 25, "slow", hw_accel="nvidia")
    assert str(target) == " -vcodec h264_nvenc -hwaccel cuvid -crf 25 -preset slow"


def test_video_settings_hevc():
    target = VideoSettings(Codec("HEVC"), 25, "slow", None)
    assert str(target) == " -vcodec libx265 -crf 25 -preset slow -strict -2"


def test_video_settings_hevc_nvidia():
    target = VideoSettings(Codec("HEVC"), 25, "slow", hw_accel="nvidia")
    assert str(target) == " -vcodec hevc_nvenc -hwaccel cuvid -crf 25 -preset slow -strict -2"


def test_video_settings_width():
    target = VideoSettings(
        codec=Codec("AVC"),
        quality=25,
        preset="slow",
        width=720,
        hw_accel=None)
    assert str(target) == " -vcodec h264 -crf 25 -preset slow -vf scale=720:-2"
