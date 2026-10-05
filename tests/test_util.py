from unittest.mock import MagicMock, patch
from video_utils import Codec, Video

from convert_videos.util import (
    check_hardware_acceleration_support,
    format_duration,
    format_filesize,
    print_conversion_results,
)
from convert_videos.video_processor import Status


class TestCheckHardwareAccelerationSupport:
    @patch("subprocess.run")
    def test_amd_amdgpu_support(self, mock_run):
        mock_run.return_value = MagicMock(stdout="amdgpu 12345 0\ndrm 123 1 amdgpu\n")
        support = check_hardware_acceleration_support()
        assert support == {
            "intel_quicksync": False,
            "nvidia_nvenc": False,
            "amd_vaapi": True,
        }

    @patch("subprocess.run")
    def test_amd_radeon_support(self, mock_run):
        mock_run.return_value = MagicMock(stdout="radeon 12345 0\n")
        support = check_hardware_acceleration_support()
        assert support == {
            "intel_quicksync": False,
            "nvidia_nvenc": False,
            "amd_vaapi": True,
        }

    @patch("subprocess.run")
    def test_intel_support(self, mock_run):
        mock_run.return_value = MagicMock(stdout="i915 12345 0\n")
        support = check_hardware_acceleration_support()
        assert support == {
            "intel_quicksync": True,
            "nvidia_nvenc": False,
            "amd_vaapi": False,
        }

    @patch("subprocess.run")
    def test_nvidia_support(self, mock_run):
        mock_run.return_value = MagicMock(stdout="nvidia 12345 0\n")
        support = check_hardware_acceleration_support()
        assert support == {
            "intel_quicksync": False,
            "nvidia_nvenc": True,
            "amd_vaapi": False,
        }

    @patch("subprocess.run")
    def test_no_hardware_support(self, mock_run):
        mock_run.return_value = MagicMock(stdout="some_module 12345 0\n")
        support = check_hardware_acceleration_support()
        assert support == {
            "intel_quicksync": False,
            "nvidia_nvenc": False,
            "amd_vaapi": False,
        }


class TestFormatDuration:
    def test_format_duration_minutes_only(self):
        duration_ms = 42 * 60 * 1000
        assert format_duration(duration_ms) == "42m"

    def test_format_duration_hours_and_minutes(self):
        duration_ms = (1 * 60 + 5) * 60 * 1000
        assert format_duration(duration_ms) == "1h5m"

    def test_format_duration_hours_only(self):
        duration_ms = 2 * 60 * 60 * 1000
        assert format_duration(duration_ms) == "2h"

    def test_format_duration_zero(self):
        assert format_duration(0) == "0m"


class TestFormatFilesize:
    def test_format_filesize_no_change(self):
        video = MagicMock(spec=Video)
        video.size_b = 100 * 1024 * 1024
        result = {"video": video, "status": Status.IN_DESIRED_FORMAT}
        assert format_filesize(result) == "100 MB (no change)"

    def test_format_filesize_converted(self):
        video = MagicMock(spec=Video)
        video.size_b = 100 * 1024 * 1024
        converted_video = MagicMock(spec=Video)
        converted_video.get_current_size.return_value = 50 * 1024 * 1024
        result = {
            "video": video,
            "status": Status.CONVERTED,
            "converted_video": converted_video,
        }
        assert format_filesize(result) == "100 MB -> 50 MB"


class TestPrintConversionResults:
    @patch("builtins.print")
    def test_print_conversion_results(self, mock_print):
        video = MagicMock(spec=Video)
        video.name = "test.mkv"
        video.duration = 60 * 1000
        video.size_b = 10 * 1024 * 1024
        video.codec = Codec("AVC")
        results = [
            {
                "video": video,
                "status": Status.CONVERTED,
                "converted_video": video,
            }
        ]
        video.get_current_size.return_value = 5 * 1024 * 1024
        print_conversion_results(results)
        mock_print.assert_called_once()
