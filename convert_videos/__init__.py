#!/usr/bin/env python3

from multiprocessing.pool import ThreadPool
import argparse
import os
import re
import shutil
import logging
import tempfile
import time

import ffmpy
from pymediainfo import MediaInfo
from colorama import Fore, Back, Style, init
import video_utils

# Init colorama
init()

log = logging.getLogger()


def cprint(colour, message):
    colours = {
            "green": Fore.GREEN,
            "blue": Fore.BLUE,
            "red": Fore.RED
            }
    print(colours[colour] + str(message) + Style.RESET_ALL)


def getRenamedVideoName(filename):
    splitFilename = os.path.splitext(filename)
    return "%s - x265.mkv" % splitFilename[0]


def changeExtensionToMKV(filename):
    splitFilename = filename.split('.')
    return "%s.mkv" % splitFilename[0]


def checkIfWritable(filePath):
    log.info("Checking if %s is writable" % filePath)
    try:
        with open(filePath, 'w') as f:
            f.writeline("test")
    finally:
        os.remove(filePath)


def convertVideo(filePath, args):
    tempVideo = tempfile.mkstemp(suffix=".mkv")
    cprint("green", "Starting to convert %s" % filePath)
    scale = "-vf scale=%s:-2" % args.width if args.width else ""
    ff = ffmpy.FFmpeg(
            inputs={filePath: None},
            outputs={tempVideo: "-y -threads 0 -vcodec %s -strict -2 -crf %s %s %s -preset %s -acodec %s -ab %s -ac %s" % (args.video_codec, args.quality, scale, args.extra_args, args.preset, args.audio_codec, args.audio_bitrate, args.audio_channels)})
    ff.run()
    return tempVideo


def convertRemainingVideos(fileMap, args):
    failures = []
    for directory in fileMap:
        cprint("green", "Working in directory %s" % directory)
        i = 0
        for filename, metadata in fileMap[directory]:
            i += 1
            cprint("green", "Parsing video %s (%s/%s)" % (filename, i, len(fileMap[directory])))
            if video_utils.getCodecFromFormat(metadata['format']) == args.video_codec:
                continue

            try:
                filePath = os.path.join(directory, filename)
                renamedFilePath = getRenamedVideoName(filePath)
                checkIfWritable(renamedFilePath)
                tempVideo = convertVideo(filePath, args)
                os.shutil.move(tempVideo, renamedFilePath)
                if args.in_place:
                    os.remove(filePath)
                    shutil.move(renamedFilePath, changeExtensionToMKV(filePath))
            except Exception as e:
                cprint("red", "Failed to convert %s" % filePath)
                failures.append(filePath)
                print(e)
            finally:
                if os.path.exists(tempVideo):
                    os.remove(tempVideo)

        cprint("green", "Finished converting all videos in %s" % directory)
    cprint("green", "Finished converting all videos!")
    if failures:
        cprint("red", "The below files failed to convert correctly:")
        for failure in failures:
            log.error(failure)


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

    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)

    fileMap = videoUtils.getFileMap(directory)

    convertRemainingVideos(fileMap, args)


if __name__ == "__main__":
    main()
