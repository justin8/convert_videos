import logging

import click
from prettytable import PrettyTable
from video_utils import Codec

from convert_videos.util import check_hardware_acceleration_support

from .processor import AudioSettings, Processor, VideoSettings

CONTEXT_SETTINGS = dict(help_option_names=["--help", "-h"])
LOG_FORMATTER = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")


def configure_logger(verbose):
    global log
    log_level = logging.INFO
    if verbose:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)
    log = logging.getLogger()
    log.handlers[0].setFormatter(LOG_FORMATTER)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("directories", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "--in-place",
    "-i",
    is_flag=True,
    help="Replace the original files instead of appending the new codec name",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force conversion even if the format of the file already matches the desired format",
)
@click.option(
    "--video-codec",
    default="HEVC",
    show_default=True,
    help="A target video codec. Supported codecs: HEVC, AVC",
)
@click.option(
    "--quality",
    "-q",
    type=int,
    default=24,
    show_default=True,
    help="The quantizer quality level to use.",
)
@click.option(
    "--preset", "-p", default="medium", show_default=True, help="FFmpeg preset to use."
)
@click.option(
    "--width",
    "-w",
    type=int,
    help="Specify a new width to enable resizing of the video",
)
@click.option(
    "--extra-input-args",
    default="",
    help="Specify any extra arguments you would like to pass to FFMpeg input here",
)
@click.option(
    "--extra-output-args",
    default="",
    help="Specify any extra arguments you would like to pass to FFMpeg output here",
)
@click.option(
    "--audio-codec", default="AAC", show_default=True, help="A target audio codec"
)
@click.option(
    "--audio-channels",
    default=2,
    show_default=True,
    type=int,
    help="The number of channels to mux sound in to",
)
@click.option(
    "--audio-bitrate",
    default=160,
    show_default=True,
    type=int,
    help="The bitrate to use for the audio codec",
)
@click.option(
    "--temp-dir",
    help="Specify a temporary directory to use during conversions instead of the system default",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose log output")
@click.option(
    "--container",
    default="mkv",
    show_default=True,
    help="Specify a video container to convert the videos in to",
)
@click.option("--dry-run", is_flag=True, help="Do not make actual changes")
@click.option(
    "--encoder",
    type=click.Choice(["auto-detect", "software", "nvidia", "intel"]),
    default="auto-detect",
    show_default=True,
    help="Optionally use a hardware encoder to speed things up.",
)
@click.option("--audio-language", help="Only include audio streams in this language")
@click.option(
    "--subtitle-language", help="Only include subtitle streams in this language"
)
@click.option(
    "--minimum-size",
    type=int,
    default=0,
    help="Skip processing videos if they are below the specified size",
)
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
    encoder,
    audio_language,
    subtitle_language,
    minimum_size,
):
    configure_logger(verbose)

    if encoder == "auto-detect":
        log.debug("Auto detecting hardware acceleration support")
        hardware_support = check_hardware_acceleration_support()
        encoder = "software"
        if hardware_support["intel_quicksync"]:
            encoder = "intel"
        if hardware_support["nvidia_nvenc"]:
            encoder = "nvidia"
        log.debug(f"Using encoder: {encoder}")

    video_settings = VideoSettings(
        codec=Codec(video_codec),
        quality=quality,
        preset=preset,
        width=width,
        encoder=encoder,
        subtitle_language=subtitle_language,
    )
    audio_settings = AudioSettings(
        codec=Codec(audio_codec),
        channels=audio_channels,
        bitrate=audio_bitrate,
        language=audio_language,
    )

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
            minimum_size_b=minimum_size * 1024 * 1024,
        ).start()

    _print_conversion_results(results)


def _print_conversion_results(results):
    table = PrettyTable(["Video", "Original Codec", "Current Size", "Status"])

    for result in results:
        codec = result["video"].codec.pretty_name
        if codec is None:
            codec = "Unknown"
        table.add_row(
            [
                result["video"].full_path,
                codec,
                str(result["video"].size_b // (1024 * 1024)) + " MB",
                result["status"].colour(),
            ]
        )
    print(table)
