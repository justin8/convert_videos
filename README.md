# Convert Videos

![Test Status](https://github.com/justin8/convert_videos/workflows/Workflow/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/justin8/convert_videos/branch/master/graph/badge.svg)](https://codecov.io/gh/justin8/convert_videos)

This tool allows bulk conversion of videos using ffmpeg.

By default it will append the codec name to the file, e.g. `Best Movie Ever.avi` -> `Best Movie Ever - x265.mkv`. This can be optionally overridden using the `--in-place` flag.

Videos are only converted if they do not already match the desired codec, allowing you to process a folder of mixed format files and only convert the ones you desire. This can optionally be overridden.

## File output

### Container

The default output container is `mkv` format. This can be changed with the `--container` flag to anything that is supported by FFMPEG and the chosen video and audio codecs

## Video output

Default settings is HEVC/x265 at quality of 23

### Codecs

Currently only HEVC (x265) and AVC (h264) are supported for video codecs.

### Resizing

Videos can be resized automatically by providing a width. Height is automatically calculated to ensure that the aspect ratio is maintained.

### Hardware Acceleration

Hardware acceleration is supported on nVidia and Intel devices.

Caveats for nVidia:
- Conversions use constqp mode for the quality setting instead of CRF, as nvenc does not support CRF
- b-frames are not currently supported; nvenc itself supports them on 20xx+ series graphics cards.


Caveats for Intel:
- Conversions use global_quality mode as CRF isn't supported on Intel hardware. ICQ and LA-ICQ are apparently better, but only supported on Windows
- Look-ahead is only supported on x264 (not HEVC)


## Audio output

Default settings is 160kbps 2 channel AAC.

All audio streams will be included by default unless a language filter is specified with `--audio-language`.


## Subtitles

All subtitles will be copied from the source if they exist unless a language filter is specified with `--subtitle-language`.

## Usage

```
Usage: convert-videos [OPTIONS] DIRECTORIES...

Options:
  -i, --in-place                  Replace the original files instead of
                                  appending the new codec name

  -f, --force                     Force conversion even if the format of the
                                  file already matches the desired format

  --video-codec TEXT              A target video codec. Supported codecs:
                                  HEVC, AVC  [default: HEVC]

  -q, --quality INTEGER           The quantizer quality level to use.
                                  [default: 24]

  -p, --preset TEXT               FFmpeg preset to use.  [default: medium]
  -w, --width INTEGER             Specify a new width to enable resizing of
                                  the video

  --extra-input-args TEXT         Specify any extra arguments you would like
                                  to pass to FFMpeg input here

  --extra-output-args TEXT        Specify any extra arguments you would like
                                  to pass to FFMpeg output here

  --audio-codec TEXT              A target audio codec  [default: AAC]
  --audio-channels INTEGER        The number of channels to mux sound in to
                                  [default: 2]

  --audio-bitrate INTEGER         The bitrate to use for the audio codec
                                  [default: 160]

  --temp-dir TEXT                 Specify a temporary directory to use during
                                  conversions instead of the system default

  -v, --verbose                   Enable verbose log output
  --container TEXT                Specify a video container to convert the
                                  videos in to  [default: mkv]

  --dry-run                       Do not make actual changes
  --encoder [software|nvidia|intel]
                                  Optionally use a harwdare encoder to speed
                                  things up.  [default: software]

  --audio-language TEXT           Only include audio streams in this language
  --subtitle-language TEXT        Only include subtitle streams in this
                                  language

  -h, --help                      Show this message and exit.
```
