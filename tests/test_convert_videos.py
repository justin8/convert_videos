from convert_videos import processor, Processor, AudioSettings, VideoSettings
from video_utils import Codec, Video
import pytest
from mock import patch, NonCallableMagicMock
from os import path
import pickle


@pytest.fixture
def target():
    audio_settings = AudioSettings(
        codec=Codec("AAC"),
        channels=2,
        bitrate=120
    )

    video_settings = VideoSettings(
        codec=Codec("HEVC"),
        quality=25,
        preset="slow"
    )

    return Processor(
        directory="/tmp/foo",
        force=False,
        video_settings=video_settings,
        audio_settings=audio_settings,
        in_place=False,
        container="mkv"
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
    target.start()
    mock_convert_all.assert_called()
    mock_load_file_map.assert_called()


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


@patch.object(Processor, "_convert_files_in_directory")
def test_convert_all(mock_convert_files_in_directory, target, file_map_fixture):
    target._file_map = file_map_fixture
    target._convert_all()
    assert mock_convert_files_in_directory.call_count == 2
    mock_convert_files_in_directory.assert_any_call(
        "/Users/jdray/git/home/convert_videos/tests/testData/foo", [])
    mock_convert_files_in_directory.assert_any_call(
        "/Users/jdray/git/home/convert_videos/tests/testData/bar", [])


@patch.object(Processor, "_get_video_processor")
def test_convert_files_in_directory_one_item(mock_get_video_processor, target, file_map_fixture):
    mock_get_video_processor().already_processed.return_value = False
    target._file_map = file_map_fixture
    failures = []
    target._convert_files_in_directory(
        "/Users/jdray/git/home/convert_videos/tests/testData/foo", failures)

    assert mock_get_video_processor().process.call_count == 1


@patch.object(Processor, "_get_video_processor")
def test_convert_files_in_directory_all_already_processed(mock_get_video_processor, target, file_map_fixture):
    mock_get_video_processor().already_processed.return_value = True
    target._file_map = file_map_fixture
    failures = []
    target._convert_files_in_directory(
        "/Users/jdray/git/home/convert_videos/tests/testData/foo", failures)

    assert mock_get_video_processor().process.call_count == 0


@patch.object(Processor, "_get_video_processor")
def test_convert_files_in_directory_failure_handling(mock_get_video_processor, target, file_map_fixture):
    mock_get_video_processor().already_processed.return_value = False
    mock_get_video_processor().process.side_effect = Exception
    target._file_map = file_map_fixture
    failures = []
    target._convert_files_in_directory(
        "/Users/jdray/git/home/convert_videos/tests/testData/foo", failures)

    assert len(failures) == 1
