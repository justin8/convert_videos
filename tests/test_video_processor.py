import pytest
from convert_videos import video_processor
from convert_videos.video_processor import VideoProcessor, Status
from convert_videos.settings import AudioSettings, VideoSettings
from video_utils import Video, Codec
from mock import patch


@pytest.fixture
def target():
    audio_settings = AudioSettings(codec=Codec("AAC"), channels=2, bitrate=120)

    video_settings = VideoSettings(
        codec=Codec("HEVC"), quality=25, preset="slow", encoder="software"
    )

    return VideoProcessor(
        video=Video("bar.mkv", "/asdf/foo"),
        video_settings=video_settings,
        audio_settings=audio_settings,
        container="asdf",
        in_place=False,
        dry_run=False,
    )


@patch("tempfile.mkstemp", autospec=True)
def test_create_temp_file_default(mock_mkstemp, target):
    target._create_temp_file()
    mock_mkstemp.assert_called_with(dir=None, suffix=".asdf")


@patch("tempfile.mkstemp", autospec=True)
def test_create_temp_file_new_dir(mock_mkstemp, target):
    target.temp_directory = "/foo/bar"
    target._create_temp_file()
    mock_mkstemp.assert_called_with(dir="/foo/bar", suffix=".asdf")


@patch.object(video_processor, "FFmpegConverter")
@patch.object(VideoProcessor, "_move_output_video")
@patch.object(VideoProcessor, "_create_temp_file", return_value="/foo")
def test_process(
    mock_create_temp_file, mock_move_output_video, mock_ffmpeg_converter, target
):
    target.process()
    mock_ffmpeg_converter.assert_called_with(
        audio_settings=target.audio_settings,
        video_settings=target.video_settings,
        extra_ffmpeg_input_args="",
        extra_ffmpeg_output_args="",
        destination_file_path="/foo",
        source_file_path="/asdf/foo/bar.mkv",
        dry_run=False,
    )
    mock_ffmpeg_converter().process.assert_called()
    mock_move_output_video.assert_called()


@patch.object(video_processor, "FFmpegConverter")
@patch.object(VideoProcessor, "_move_output_video")
@patch.object(VideoProcessor, "_create_temp_file", return_value="/foo")
def test_process_dry_run(
    mock_create_temp_file, mock_move_output_video, mock_ffmpeg_converter, target
):
    target.dry_run = True
    target.process()
    mock_ffmpeg_converter.assert_called_with(
        audio_settings=target.audio_settings,
        video_settings=target.video_settings,
        extra_ffmpeg_input_args="",
        extra_ffmpeg_output_args="",
        destination_file_path="/foo",
        source_file_path="/asdf/foo/bar.mkv",
        dry_run=True,
    )
    mock_ffmpeg_converter().process.assert_called()
    mock_move_output_video.assert_called()


@patch.object(VideoProcessor, "renamed_path")
@patch("os.path.exists", return_value=True)
def test_already_processed_renamed_file_exists(mock_exists, mock_renamed_path, target):
    result = target.already_processed()
    assert result is True


@patch.object(VideoProcessor, "renamed_path")
@patch("os.path.exists", return_value=False)
def test_already_processed_container_matches(mock_exists, mock_renamed_path, target):
    target.video.name = "bar - x265.mkv"
    result = target.already_processed()
    assert result is True


@patch.object(VideoProcessor, "renamed_path")
@patch("os.path.exists", return_value=False)
def test_already_processed_false(mock_exists, mock_renamed_path, target):
    result = target.already_processed()
    assert result is False


def test_renamed_path(target):
    result = target.renamed_path()
    assert result == "/asdf/foo/bar - x265.asdf"


def test_in_place_file_path(target):
    result = target.in_place_file_path()
    assert result == "/asdf/foo/bar.asdf"


@patch("shutil.move")
@patch("os.remove")
def test_move_output_video(mock_remove, mock_move, target):
    target.temp_file = "/foo/bar/baz"
    target._move_output_video()
    mock_move.assert_called_with("/foo/bar/baz", "/asdf/foo/bar - x265.asdf")
    mock_remove.assert_not_called()


@patch("shutil.move")
@patch("os.remove")
def test_move_output_video_dry_run(mock_remove, mock_move, target):
    target.dry_run = True
    target.temp_file = "/foo/bar/baz"
    target._move_output_video()
    mock_move.assert_not_called()
    mock_remove.assert_not_called()


@patch("shutil.move")
@patch("os.remove")
def test_move_output_video_in_place(mock_remove, mock_move, target):
    target.temp_file = "/foo/bar/baz"
    target.in_place = True
    target._move_output_video()
    mock_move.assert_any_call("/foo/bar/baz", "/asdf/foo/bar - x265.asdf")
    mock_remove.assert_called_with("/asdf/foo/bar.mkv")
    mock_move.assert_any_call("/asdf/foo/bar - x265.asdf", "/asdf/foo/bar.asdf")


@patch("shutil.move")
@patch("os.remove")
def test_move_output_video_in_place_dry_run(mock_remove, mock_move, target):
    target.dry_run = True
    target.temp_file = "/foo/bar/baz"
    target.in_place = True
    target._move_output_video()
    mock_move.assert_not_called()
    mock_remove.assert_not_called


def test_in_desired_format(target):
    target.video.codec = Codec("HEVC")
    target.video_settings.codec = Codec("HEVC")
    response = target.process()
    assert response == Status.IN_DESIRED_FORMAT


@patch.object(VideoProcessor, "already_processed", return_value=True)
def test_already_processed(mock_already_processed, target):
    response = target.process()
    assert response == Status.ALREADY_PROCESSED


@patch.object(VideoProcessor, "already_processed", return_value=False)
@patch.object(VideoProcessor, "_create_temp_file")
@patch("convert_videos.video_processor.FFmpegConverter")
@patch.object(VideoProcessor, "_move_output_video")
def test_converted(m1, m2, m3, m4, target):
    response = target.process()
    assert response == Status.CONVERTED


@patch.object(VideoProcessor, "already_processed", return_value=False)
@patch.object(VideoProcessor, "_create_temp_file")
@patch("convert_videos.video_processor.FFmpegConverter", side_effect=Exception)
@patch.object(VideoProcessor, "_move_output_video")
def test_failed(m1, m2, m3, m4, target):
    response = target.process()
    assert response == Status.FAILED


@patch.object(VideoProcessor, "_is_below_minimum_size", return_value=True)
def test_below_minimum_size(mock_is_below_minimum_size, target):
    response = target.process()
    assert response == Status.BELOW_MINIMUM_SIZE


@patch("os.path.getsize", return_value=100 * 1024 * 1024)
def test_is_below_minimum_size_true(mock_getsize, target):
    target.minimum_size = 200
    result = target._is_below_minimum_size()
    assert result is True


@patch("os.path.getsize", return_value=300 * 1024 * 1024)
def test_is_below_minimum_size_false(mock_getsize, target):
    target.minimum_size = 200
    result = target._is_below_minimum_size()
    assert result is False


@patch("os.path.getsize", return_value=300 * 1024 * 1024)
def test_is_below_minimum_size_zero(mock_getsize, target):
    target.minimum_size = 0
    result = target._is_below_minimum_size()
    assert result is False
