import unittest
import convert_videos
import mock

class tv_episode_parser_tests(unittest.TestCase):

    def test_get_codec_from_format(self):
        self.assertEqual(convert_videos.get_codec_from_format("HEVC"), "libx265")
        self.assertEqual(convert_videos.get_codec_from_format("AVC"), "h264")
        self.assertEqual(convert_videos.get_codec_from_format("foobar"), "Unknown")


    def test_change_extension_to_mkv(self):
        self.assertEqual(convert_videos.change_extension_to_mkv("asdf.mov"), "asdf.mkv")
        self.assertEqual(convert_videos.change_extension_to_mkv("/foo/bar/baz.mov"), "/foo/bar/baz.mkv")
