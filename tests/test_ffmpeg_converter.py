from mock import patch, mock_open
import pytest

from video_utils import Codec
from convert_videos.settings import AudioSettings, VideoSettings

from convert_videos.ffmpeg_converter import FFmpegConverter
from convert_videos import ffmpeg_converter


@pytest.fixture
def target():
    audio_settings = AudioSettings(codec=Codec("AAC"), channels=2, bitrate=120)

    video_settings = VideoSettings(codec=Codec("HEVC"), quality=25, preset="slow", encoder="software")

    return FFmpegConverter(
        source_file_path="/asdf/foo/bar.mkv",
        video_settings=video_settings,
        audio_settings=audio_settings,
        destination_file_path="/asdf/temp/path.mkv",
        extra_ffmpeg_input_args="",
        extra_ffmpeg_output_args="",
        dry_run=False,
    )


@patch.object(FFmpegConverter, "_generate_ffmpeg_settings", return_value="12345")
@patch.object(ffmpeg_converter, "ffmpy")
def test_process(mock_ffmpy, mock_settings, target):
    target.process()
    mock_ffmpy.FFmpeg.assert_called_with(inputs={"/asdf/foo/bar.mkv": "12345"}, outputs={"/asdf/temp/path.mkv": "12345"})
    mock_ffmpy.FFmpeg().run.assert_called()


def test_generate_ffmpeg_output_settings(target):
    result = target._generate_ffmpeg_settings("output")
    assert (
        result
        == "-y -threads 0 -map 0:v:0 -map 0:s? -c:s copy -vcodec libx265 -preset slow -crf 25 -strict -2 -acodec aac -ab 120k -ac 2 -map 0:a "
    )


def test_extra_output_args(target):
    target.extra_ffmpeg_output_args = "-foo"
    result = target._generate_ffmpeg_settings("output")
    assert (
        result
        == "-y -threads 0 -map 0:v:0 -map 0:s? -c:s copy -vcodec libx265 -preset slow -crf 25 -strict -2 -acodec aac -ab 120k -ac 2 -map 0:a -foo"
    )


def test_generate_ffmpeg_input_settings(target):
    result = target._generate_ffmpeg_settings("input")
    assert result == " "


def test_generate_ffmpeg_input_settings_nvidia_hw(target):
    target.video_settings.encoder = "nvidia"
    result = target._generate_ffmpeg_settings("input")
    assert result == " -hwaccel cuvid"


def test_extra_input_args(target):
    target.extra_ffmpeg_input_args = "-foo"
    result = target._generate_ffmpeg_settings("input")
    assert result == " -foo"


@patch("os.path.exists", return_value=True)
@patch("os.path.isfile", return_value=True)
@patch("os.access", return_value=True)
@patch("os.path.isdir")
@patch("os.remove")
def test_validate_destination_happy_path_exists(mock_remove, mock_isdir, mock_access, mock_isfile, mock_exists, target):
    result = target._validate_destination()
    assert result is True


@patch("os.path.exists", return_value=True)
@patch("os.path.isfile", return_value=True)
@patch("os.access", return_value=False)
@patch("os.path.isdir")
@patch("os.remove")
def test_validate_destination_unwritable(mock_remove, mock_isdir, mock_access, mock_isfile, mock_exists, target):
    with pytest.raises(IOError):
        target._validate_destination()


@patch("os.path.exists", return_value=True)
@patch("os.path.isfile", return_value=False)
@patch("os.access")
@patch("os.path.isdir", return_falue=True)
@patch("os.remove")
def test_validate_destination_is_dir(mock_remove, mock_isdir, mock_access, mock_isfile, mock_exists, target):
    with pytest.raises(IOError):
        target._validate_destination()


@patch("os.path.exists", return_value=False)
@patch("os.path.isfile")
@patch("os.access")
@patch("os.path.isdir")
@patch("os.remove")
def test_validate_destination_doesnt_exist(mock_remove, mock_isdir, mock_access, mock_isfile, mock_exists, target):
    m = mock_open()
    with patch("builtins.open", m):
        result = target._validate_destination()
        assert result is True


@patch("os.path.exists", return_value=False)
@patch("os.path.isfile")
@patch("os.access")
@patch("os.path.isdir")
@patch("os.remove")
def test_validate_destination_invalid_path(mock_remove, mock_isdir, mock_access, mock_isfile, mock_exists, target):
    m = mock_open()
    m.side_effect = FileNotFoundError
    with patch("builtins.open", m):
        with pytest.raises(FileNotFoundError):
            target._validate_destination()
