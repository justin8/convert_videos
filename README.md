# Convert Videos

![Test Status](https://github.com/justin8/convert_videos/workflows/Tests/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/justin8/convert_videos/branch/master/graph/badge.svg)](https://codecov.io/gh/justin8/convert_videos)

This tool allows bulk conversion of videos using ffmpeg.

By default it will append the codec name to the file, e.g. `Best Movie Ever.avi` -> `Best Movie Ever - x265.mkv`. This can be optionally overridden.

Videos are only converted if they do not already match the desired codec, allowing you to process a folder of mixed format files and only convert the ones you desire. This can optionally be overridden.

Videos can also be resized automatically by providing a width. Height is automatically calculated to ensure that the aspect ratio is maintained.

Default settings:
Audio: 160bps 2 channel AAC
Video: HEVC/x265 at quality of 22

## Usage

```
Usage: convert-videos [OPTIONS] DIRECTORY

Options:
  -i, --in-place            Replace the original files instead of appending
                            the new codec name
  -f, --force               Force conversion even if the format of the file
                            already matches the desired format
  --video-codec TEXT        A target video codec  [default: HEVC]
  -q, --quality INTEGER     The quantizer quality level to use  [default: 22]
  -p, --preset TEXT         FFmpeg preset to use  [default: medium]
  -w, --width INTEGER       Specify a new width to enable resizing of the
                            video
  -e, --extra-args TEXT     Specify any extra arguments you would like to pass
                            to FFMpeg here
  --audio-codec TEXT        A target audio codec  [default: AAC]
  --audio-channels INTEGER  The number of channels to mux sound in to
                            [default: 2]
  --audio-bitrate INTEGER   The bitrate to use for the audio codec  [default:
                            160]
  --temp-dir TEXT           Specify a temporary directory to use during
                            conversions instead of the system default
  -v, --verbose             Enable verbose log output
  --container TEXT          Specify a video container to convert the videos in
                            to  [default: mkv]
  -h, --help                Show this message and exit.

```
