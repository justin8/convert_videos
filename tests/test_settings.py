from convert_videos.settings import AudioSettings, VideoSettings
from video_utils import Codec


def test_audio_settings():
    target = AudioSettings(Codec("AAC"), 2, 128)
    assert str(target) == " -map 0:a -acodec aac -ab 128k -ac 2"


def test_audio_copy():
    target = AudioSettings(Codec("copy"), 2, 128)
    assert str(target) == " -map 0:a -acodec copy"


def test_audio_language_filter_fullname():
    target = AudioSettings(Codec("AAC"), 2, 128, "english")
    assert str(target) == " -map 0:a:m:language:eng -acodec aac -ab 128k -ac 2"


def test_audio_language_filter_shortcode():
    target = AudioSettings(Codec("AAC"), 2, 128, "jpn")
    assert str(target) == " -map 0:a:m:language:jpn -acodec aac -ab 128k -ac 2"


def test_video_settings_avc():
    target = VideoSettings(Codec("AVC"), 25, "slow")
    assert (
        str(target) == " -map 0:v -map 0:s? -c:s copy -vcodec h264 -preset slow -crf 25"
    )


def test_video_settings_avc_nvidia():
    target = VideoSettings(Codec("AVC"), 25, "slow", encoder="nvidia")
    assert (
        str(target)
        == " -map 0:v -map 0:s? -c:s copy -vcodec h264_nvenc -preset slow -rc constqp -qp 25 -b:v 0"
    )


def test_video_settings_avc_intel():
    target = VideoSettings(Codec("AVC"), 25, "slow", encoder="intel")
    assert (
        str(target)
        == " -map 0:v -map 0:s? -c:s copy -vcodec h264_qsv -preset slow -global_quality 25 -look_ahead 1 -g:v 120"
    )


def test_video_settings_hevc():
    target = VideoSettings(Codec("HEVC"), 25, "slow", None)  # type: ignore
    assert (
        str(target)
        == " -map 0:v -map 0:s? -c:s copy -vcodec libx265 -preset slow -crf 25 -strict -2"
    )


def test_video_settings_hevc_nvidia():
    target = VideoSettings(Codec("HEVC"), 25, "slow", encoder="nvidia")
    assert (
        str(target)
        == " -map 0:v -map 0:s? -c:s copy -vcodec hevc_nvenc -preset slow -rc constqp -qp 25 -b:v 0 -strict -2"
    )


def test_video_settings_hevc_intel():
    target = VideoSettings(Codec("HEVC"), 25, "slow", encoder="intel")
    assert (
        str(target)
        == " -map 0:v -map 0:s? -c:s copy -vcodec hevc_qsv -preset slow -global_quality 25 -g:v 120 -strict -2"
    )


def test_video_settings_width():
    target = VideoSettings(
        codec=Codec("AVC"), quality=25, preset="slow", width=720, encoder="software"
    )
    assert (
        str(target)
        == " -map 0:v -map 0:s? -c:s copy -vcodec h264 -preset slow -crf 25 -vf scale=720:-2"
    )


def test_video_copy():
    target = VideoSettings(Codec("copy"), 25, "slow")
    assert str(target) == " -map 0:v -map 0:s? -c:s copy -vcodec copy"


def test_video_language_filter_fullname():
    target = VideoSettings(Codec("AVC"), 25, "slow", subtitle_language="english")
    assert (
        str(target)
        == " -map 0:v -map 0:s:m:language:eng? -c:s copy -vcodec h264 -preset slow -crf 25"
    )


def test_video_language_filter_shortcode():
    target = VideoSettings(Codec("AVC"), 25, "slow", subtitle_language="jpn")
    assert (
        str(target)
        == " -map 0:v -map 0:s:m:language:jpn? -c:s copy -vcodec h264 -preset slow -crf 25"
    )
