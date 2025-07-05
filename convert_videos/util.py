import subprocess
from prettytable import PrettyTable


def check_hardware_acceleration_support():
    support = {"intel_quicksync": False, "nvidia_nvenc": False}

    lsmod_output = subprocess.run(["lsmod"], capture_output=True, text=True)

    if "i915" in lsmod_output.stdout:
        support["intel_quicksync"] = True
    if "nvidia" in lsmod_output.stdout:
        support["nvidia_nvenc"] = True

    return support


def format_duration(duration_ms):
    """Format duration from milliseconds to human readable format like '42m' or '1h5m'"""
    total_minutes = duration_ms // 1000 // 60
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours > 0:
        return f"{hours}h{minutes}m" if minutes > 0 else f"{hours}h"
    return f"{minutes}m"


def print_conversion_results(results):
    table = PrettyTable(
        ["Video", "Duration", "Current Size", "Original Codec", "Status"]
    )

    for result in results:
        codec = result["video"].codec.pretty_name
        if codec is None:
            codec = "Unknown"
        table.add_row(
            [
                result["video"].name,
                format_duration(result["video"].duration),
                str(result["video"].size_b // (1024 * 1024)) + " MB",
                codec,
                result["status"].colour(),
            ]
        )
    print(table)
