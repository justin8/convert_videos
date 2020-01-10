from convert_videos.settings import AudioSettings, VideoSettings
from video_utils import Codec


def test_audio_settings():
    target = AudioSettings(Codec("AAC"), 2, 128)
    assert str(target) == " -acodec aac -ab 128 -ac 2"


def test_video_settings_generic():
    target = VideoSettings(Codec("AVC"), 25, "slow")
    assert str(target) == " -vcodec h264 -crf 25 -preset slow"


def test_video_settings_hevc():
    target = VideoSettings(Codec("HEVC"), 25, "slow")
    assert str(target) == " -vcodec libx265 -crf 25 -preset slow -strict -2"


def test_video_settings_width():
    target = VideoSettings(Codec("AVC"), 25, "slow", 720)
    assert str(target) == " -vcodec h264 -crf 25 -preset slow -vf scale=720:-2"
