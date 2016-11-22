#!/usr/bin/env python3

from multiprocessing.pool import ThreadPool
import argparse
import os
import re
import shutil
import tempfile
import time

import ffmpy
from pymediainfo import MediaInfo
from colorama import Fore, Back, Style, init

# Init colorama
init()

valid_codecs = {
        "HEVC": "libx265",
        "AVC": "h264",
        "MPEG-4 Visual": "mpeg4"
    }


def cprint(colour, message):
    colours = {
            "green": Fore.GREEN,
            "blue": Fore.BLUE,
            "red": Fore.RED
            }
    print(colours[colour] + str(message) + Style.RESET_ALL)


def get_codec_from_format(format_string):
    if format_string in valid_codecs.values():
        return valid_codecs[format_string]
    return "Unknown"


def get_unconverted_items(codec_map, desired_codec):
    output_list = []
    for file_path, codec in codec_map.items():
        if codec != desired_codec:
            output_list.append(file_path)

    print()
    cprint("green", "### Files that are not in x265: ")
    cprint("blue", output_list)

    return output_list


def get_codec_map(directory):
    videos = get_videos_in_dir(directory)
    codec_map = get_codecs_of_files(videos)

    cprint("green", "### Map of files and codecs:")
    cprint("blue", codec_map)
    return codec_map


# TODO: This needs to cache the results of all HVEC files somewhere so we don't re-check those. Should make this much faster
def get_codecs_of_files(videos):
    cprint("green", "### Checking codecs used in remaining videos")
    pool = ThreadPool(processes=4)
    t0 = time.time()
    temp_codec_map = pool.map(get_codec, videos)
    cprint("blue", "Gathering list of codecs in files took %s seconds" % (time.time() - t0))

    # Recombine the list of dicts in to a dict
    codec_map = {}
    for item in temp_codec_map:
        for k, v in item.items():
            codec_map[k] = v
    return codec_map


# This speeds things up, no point checking if converted videos already exist
def remove_converted_videos_from_list(videos):
    output = []
    cprint("green", "###  Checking if any videos found have already been converted")
    for video in videos:
        if not re.match(".* - x265\.mkv", video):
            if not os.path.exists(get_renamed_video_name(video)):
                cprint("blue", "%s may not have already been convered" % video)
                output.append(video)
            else:
                cprint("blue", "%s has a renamed file in the same folder" % video)
        else:
            cprint("blue", "%s is a converted and renamed file" % video)
    return output


def get_renamed_video_name(filename):
    split_filename = os.path.splitext(filename)
    return "%s - x265.mkv" % split_filename[0]


def change_extension_to_mkv(filename):
    split_filename = filename.split('.')
    return "%s.mkv" % split_filename[0]


# TODO: Change to os.walk
def get_videos_in_dir(directory):
    files = (os.path.abspath(os.path.join(directory, filename)) for filename in os.listdir(directory))
    raw_videos = []
    cprint("green", "### Testing to see if files are videos...")
    for f in files:
        if is_video(f):
            raw_videos.append(f)

    videos = remove_converted_videos_from_list(raw_videos)
    return videos


def is_video(f):
    result = re.match(".*\.(avi|mkv|mp4|m4v|mpg|mpeg|mov|flv|ts|wmv)", f, re.IGNORECASE)
    if result:
        cprint("blue", "File '%s' is a video" % f)
    else:
        cprint("blue", "File '%s' is NOT a video" % f)
    return result


def get_codec(file_path):
    metadata = MediaInfo.parse(os.path.join(file_path))
    for track in metadata.tracks:
        if track.track_type == "Video":
            ffmpeg_codec = get_codec_from_format(track.format)
            return {file_path: ffmpeg_codec}
    raise Exception("No video track found")


def validate_target_video_codec(codec):
    if codec not in valid_codecs.values():
        raise Exception("Unsupported codec requested")


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--verbose",
                        help="Print more verbose messages",
                        action="store_true")
    parser.add_argument("-w", "--width",
                        help="Set the width if you would like to resize the video",
                        action="store")
    parser.add_argument("-q", "--quality",
                        help="Quality quantizer",
                        default=21,
                        action="store")
    parser.add_argument("-p", "--preset",
                        help="Encoding preset to use",
                        default="slow",
                        action="store")
    parser.add_argument("-e", "--extra-args",
                        help="Any extra arguments to pass to ffmpeg",
                        default="",
                        action="store")
    parser.add_argument("-i", "--in-place",
                        help="Replace files in-place instead of appending ' x265' to the end",
                        action="store_true")
    parser.add_argument("--video-codec",
                        help="The video codec to use for encoding",
                        default="libx265",
                        action="store")
    parser.add_argument("--audio-codec",
                        help="The audio codec to use for encoding",
                        default="libfdk_aac",
                        action="store")
    parser.add_argument("--audio-bitrate",
                        help="The bitrate of the audio codec",
                        default="160k",
                        action="store")
    parser.add_argument("--audio-channels",
                        help="The number of audio channels to use",
                        default="2",
                        action="store")
    parser.add_argument("directory",
                        help="The directory to read files from",
                        action="store")

    args = parser.parse_args()

    global VERBOSE
    VERBOSE = args.verbose

    validate_target_video_codec(args.video_codec)

    codec_map = get_codec_map(args.directory)
    unconverted_items = get_unconverted_items(codec_map, args.video_codec)

    failures = []
    scale = "-vf scale=%s:-2" % args.width if args.width else ""

    if not unconverted_items:
        cprint("green", "No files found that were not already x265")
    for infile in unconverted_items:
        cprint("green", "######################################")
        cprint("green", "### Starting to convert '%s'" % infile)
        outfile = tempfile.mkstemp(suffix=".mkv")[1]
        ff = ffmpy.FFmpeg(
                inputs={infile: None},
                outputs={outfile: "-y -threads 0 -vcodec %s -strict -2 -crf %s %s %s -preset %s -acodec %s -ab %s -ac %s" % (args.video_codec, args.quality, scale, args.extra_args, args.preset, args.audio_codec, args.audio_bitrate, args.audio_channels)})

        try:
            renamed_file = get_renamed_video_name(infile)
            cprint("blue", "Testing if the output folder is writable...")
            with open(renamed_file, 'w') as f:
                f.writelines("test")
            os.remove(renamed_file)
            cprint("blue", "Running ffmpeg command: '%s'" % ff.cmd)
            ff.run()
            cprint("green", "######################################")
            cprint("green", "Successfully converted '%s'" % infile)
            cprint("blue", "Moving to '%s'..." % renamed_file)
            shutil.move(outfile, renamed_file)
            if args.in_place:
                new_filename = change_extension_to_mkv(infile)
                cprint("blue", "Removing original file '%s'" % infile)
                os.remove(infile)
                cprint("blue", "Renaming to '%s'" % new_filename)
                shutil.move(renamed_file, new_filename)
        except Exception as e:
            cprint("red", "ffmpeg failed! No files will be overwritten")
            failures.append(infile)
            print(e)
        if os.path.exists(outfile):
            os.remove(outfile)
    cprint("green", "### Finished converting all videos!")
    if failures:
        cprint("red", "### The below files failed to convert correctly. Please check the output above for more details:")
        for failure in failures:
            cprint("blue", failure)


if __name__ == "__main__":
    main()
