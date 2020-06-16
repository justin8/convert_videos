import click
import logging

from prettytable import PrettyTable
from video_utils import Codec

from .processor import Processor, AudioSettings, VideoSettings

# TODO: How do I set show_defaults on all commands?
CONTEXT_SETTINGS = dict(help_option_names=["--help", "-h"])


def set_log_level(verbose):
    log_level = logging.WARNING
    if verbose:
        log_level = logging.INFO
    logging.basicConfig(level=log_level)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("directories", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--in-place", "-i", is_flag=True, help="Replace the original files instead of appending the new codec name")
@click.option("--force", "-f", is_flag=True, help="Force conversion even if the format of the file already matches the desired format")
@click.option("--video-codec", default="HEVC", show_default=True, help="A target video codec. Supported codecs: HEVC, AVC")
@click.option("--quality", "-q", type=int, default=23, show_default=True, help="The quantizer quality level to use")
@click.option("--preset", "-p", default="medium", show_default=True, help="FFmpeg preset to use.")
@click.option("--width", "-w", type=int, help="Specify a new width to enable resizing of the video")
@click.option("--extra-input-args", default="", help="Specify any extra arguments you would like to pass to FFMpeg input here")
@click.option("--extra-output-args", default="", help="Specify any extra arguments you would like to pass to FFMpeg output here")
@click.option("--audio-codec", default="AAC", show_default=True, help="A target audio codec")
@click.option("--audio-channels", default=2, show_default=True, type=int, help="The number of channels to mux sound in to")
@click.option("--audio-bitrate", default=160, show_default=True, type=int, help="The bitrate to use for the audio codec")
@click.option("--temp-dir", help="Specify a temporary directory to use during conversions instead of the system default")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose log output")
@click.option("--container", default="mkv", show_default=True, help="Specify a video container to convert the videos in to")
@click.option("--dry-run", is_flag=True, help="Do not make actual changes")
@click.option("--nvidia-hw-accel", is_flag=True, help="Use Nvidia HW acceleration instead of software encoding")
def main(
    directories,
    force,
    in_place,
    video_codec,
    quality,
    preset,
    width,
    extra_input_args,
    extra_output_args,
    audio_codec,
    audio_channels,
    audio_bitrate,
    temp_dir,
    verbose,
    container,
    dry_run,
    nvidia_hw_accel,
):

    set_log_level(verbose)

    hw_accel = None
    if nvidia_hw_accel:
        hw_accel = "nvidia"

    video_settings = VideoSettings(codec=Codec(video_codec), quality=quality, preset=preset, width=width, hw_accel=hw_accel)
    audio_settings = AudioSettings(codec=Codec(audio_codec), channels=audio_channels, bitrate=audio_bitrate,)

    if video_settings.codec.ffmpeg_name is None:
        raise Exception("Invalid video codec specified")

    if audio_settings.codec.ffmpeg_name is None:
        raise Exception("Invalid audio codec specified")

    results = []
    for directory in directories:
        results += Processor(
            directory=directory,
            force=force,
            video_settings=video_settings,
            audio_settings=audio_settings,
            in_place=in_place,
            extra_ffmpeg_input_args=extra_input_args,
            extra_ffmpeg_output_args=extra_output_args,
            temp_directory=temp_dir,
            container=container,
            dry_run=dry_run,
        ).start()

    _print_conversion_results(results)


def _print_conversion_results(results):
    table = PrettyTable(["Video", "Status"])

    for result in results:
        table.add_row([result["video"].full_path, result["status"]])
    print(table)
