from unittest.mock import patch
from convert_videos.util import format_duration


class TestFormatDuration:
    def test_format_duration_minutes_only(self):
        # 42 minutes in milliseconds
        duration_ms = 42 * 60 * 1000
        assert format_duration(duration_ms) == "42m"

    def test_format_duration_hours_and_minutes(self):
        # 1 hour 5 minutes in milliseconds
        duration_ms = (1 * 60 + 5) * 60 * 1000
        assert format_duration(duration_ms) == "1h5m"

    def test_format_duration_hours_only(self):
        # Exactly 2 hours in milliseconds
        duration_ms = 2 * 60 * 60 * 1000
        assert format_duration(duration_ms) == "2h"

    def test_format_duration_zero_minutes(self):
        # 0 minutes
        duration_ms = 0
        assert format_duration(duration_ms) == "0m"

    def test_format_duration_less_than_minute(self):
        # 30 seconds (should round down to 0 minutes)
        duration_ms = 30 * 1000
        assert format_duration(duration_ms) == "0m"

    def test_format_duration_multiple_hours(self):
        # 3 hours 42 minutes in milliseconds
        duration_ms = (3 * 60 + 42) * 60 * 1000
        assert format_duration(duration_ms) == "3h42m"


class TestCLI:
    def test_cli_help_includes_amd(self):
        from click.testing import CliRunner
        from convert_videos.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "amd" in result.output

    @patch("convert_videos.cli.Processor")
    @patch("convert_videos.cli.print_conversion_results")
    def test_cli_explicit_amd_encoder(
        self, mock_print_results, mock_processor, tmp_path
    ):
        from click.testing import CliRunner
        from convert_videos.cli import main

        mock_processor.return_value.start.return_value = []
        runner = CliRunner()
        result = runner.invoke(main, ["--encoder", "amd", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_processor.call_args[1]["video_settings"].encoder == "amd"

    @patch("convert_videos.cli.check_hardware_acceleration_support")
    @patch("convert_videos.cli.Processor")
    @patch("convert_videos.cli.print_conversion_results")
    def test_cli_auto_detect_amd(
        self, mock_print_results, mock_processor, mock_check_hw, tmp_path
    ):
        from click.testing import CliRunner
        from convert_videos.cli import main

        mock_check_hw.return_value = {
            "intel_quicksync": False,
            "nvidia_nvenc": False,
            "amd_vaapi": True,
        }
        mock_processor.return_value.start.return_value = []
        runner = CliRunner()
        result = runner.invoke(main, ["--encoder", "auto-detect", str(tmp_path)])
        assert result.exit_code == 0
        assert mock_processor.call_args[1]["video_settings"].encoder == "amd"
