# Convert Videos
![Python 3.7 Status](https://github.com/justin8/convert_videos/workflows/Python%203.7/badge.svg?branch=master)
![Python 3.8 Status](https://github.com/justin8/convert_videos/workflows/Python%203.8/badge.svg?branch=master)

This tool allows bulk conversion of videos using ffmpeg


## Usage
usage: convert-videos [-h] [-v] [-f] [-w WIDTH] [-q QUALITY] [-p PRESET] [-e EXTRA_ARGS] [-c CONTAINER] [-i] [--temp-dir TEMP_DIR] [--video-codec VIDEO_CODEC] [--audio-codec AUDIO_CODEC] [--audio-bitrate AUDIO_BITRATE] [--audio-channels AUDIO_CHANNELS] directory

positional arguments:
  directory             The directory to read files from

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Print more verbose messages (default: False)
  -f, --force           Force to run even if the specified videos are already in the expected format (default: False)
  -w WIDTH, --width WIDTH
                        Set the width if you would like to resize the video (default: None)
  -q QUALITY, --quality QUALITY
                        Quality quantizer (default: 22)
  -p PRESET, --preset PRESET
                        Encoding preset to use (default: medium)
  -e EXTRA_ARGS, --extra-args EXTRA_ARGS
                        Any extra arguments to pass to ffmpeg (default: )
  -c CONTAINER, --container CONTAINER
                        The container format to output in (default: mkv)
  -i, --in-place        Replace files in-place instead of appending ' x265' to the end (default: False)
  --temp-dir TEMP_DIR   The temp dir to store files in during conversion (default: /var/folders/w0/2mq4qtgs4_sd22tlblwzs2f9h0_kwk/T)
  --video-codec VIDEO_CODEC
                        The video codec to use for encoding (default: libx265)
  --audio-codec AUDIO_CODEC
                        The audio codec to use for encoding (default: aac)
  --audio-bitrate AUDIO_BITRATE
                        The bitrate of the audio codec (default: 160k)
  --audio-channels AUDIO_CHANNELS
                        The number of audio channels to use (default: 2)
