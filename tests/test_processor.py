import pickle
from os import path

import pytest
from mock import NonCallableMagicMock, patch
from video_utils import Codec, Video

from convert_videos import AudioSettings, Processor, VideoSettings, processor
from convert_videos.video_processor import Status


@pytest.fixture
def target():
    audio_settings = AudioSettings(codec=Codec("AAC"), channels=2, bitrate=120)

    video_settings = VideoSettings(
        codec=Codec("HEVC"),
        quality=25,
        preset="slow",
        encoder="software",
    )

    return Processor(
        directory="/tmp/foo",
        force=False,
        video_settings=video_settings,
        audio_settings=audio_settings,
        in_place=False,
        container="mkv",
    )


@pytest.fixture
def file_map_fixture():
    current_dir = path.dirname(path.abspath(__file__))
    test_data_dir = path.join(current_dir, "testData")
    filemap_file = path.join(test_data_dir, "filemap.pickle")
    with open(filemap_file, "rb") as f:
        return pickle.load(f)


@patch.object(Processor, "_load_file_map", autospec=True)
@patch.object(Processor, "_convert_all", autospec=True)
def test_processor_start(mock_convert_all, mock_load_file_map, target):
    target.results = "foo"
    result = target.start()
    mock_convert_all.assert_called()
    mock_load_file_map.assert_called()
    assert result == "foo"


@patch.object(processor, "FileMap")
def test_load_file_map(mock_file_map, target):
    target._load_file_map()
    mock_file_map.assert_called_with("/tmp/foo")
    mock_file_map().load.assert_called()


@patch.object(processor, "VideoProcessor", autospec=True)
def test_get_video_processor(mock_video_processor, target):
    result = target._get_video_processor(Video("bar.mkv", "/tmp/foo"))
    mock_video_processor.assert_called()
    assert isinstance(result, NonCallableMagicMock)


@patch.object(Processor, "_convert_files_in_directory", return_value=["some-response"])
def test_convert_all(mock_convert_files_in_directory, target, file_map_fixture):
    target._file_map = file_map_fixture
    target._convert_all()
    assert mock_convert_files_in_directory.call_count == 2

    # The pickle file contains paths from the original system, so we check for those
    mock_convert_files_in_directory.assert_any_call(
        "/Users/jdray/git/home/convert_videos/tests/testData/foo"
    )
    mock_convert_files_in_directory.assert_any_call(
        "/Users/jdray/git/home/convert_videos/tests/testData/bar"
    )

    # Confirm we return the results from convert_files_in_directory in a list
    assert target.results == ["some-response", "some-response"]


@patch.object(Processor, "_get_video_processor")
@patch("video_utils.video.Video.get_current_size", return_value=1000)
def test_convert_files_in_directory_status_passthrough(
    mock_get_current_size, mock_get_video_processor, target, file_map_fixture
):
    mock_get_video_processor().process.return_value = {"status": Status.FAILED}
    target._file_map = file_map_fixture

    # Use the path from the pickle file
    response = target._convert_files_in_directory(
        "/Users/jdray/git/home/convert_videos/tests/testData/foo"
    )

    failures = [x for x in response if x["status"] == Status.FAILED]

    assert len(failures) == 6


@patch.object(processor, "VideoProcessor", autospec=True)
def test_get_video_processor_with_minimum_size_per_hour(mock_video_processor, target):
    target.minimum_size_per_hour_mb = 100
    video = Video("test.mkv", "/tmp")
    result = target._get_video_processor(video)

    mock_video_processor.assert_called_with(
        video=video,
        video_settings=target.video_settings,
        audio_settings=target.audio_settings,
        container=target.container,
        extra_ffmpeg_input_args=target.extra_ffmpeg_input_args,
        extra_ffmpeg_output_args=target.extra_ffmpeg_output_args,
        temp_directory=target.temp_directory,
        in_place=target.in_place,
        dry_run=target.dry_run,
        force=target.force,
        minimum_size_per_hour_mb=100,
    )
    assert isinstance(result, NonCallableMagicMock)
