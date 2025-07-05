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
