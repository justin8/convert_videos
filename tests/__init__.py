import unittest
import convert_videos
import mock

class testConvertVideos(unittest.TestCase):


    def testChangeExtensionTo(self):
        self.assertEqual(convert_videos.changeExtensionTo("asdf.mov", "mkv"), "asdf.mkv")
        self.assertEqual(convert_videos.changeExtensionTo("/foo/bar/baz.mov", "mkv"), "/foo/bar/baz.mkv")
        self.assertEqual(convert_videos.changeExtensionTo("asdf.mov", "avi"), "asdf.avi")
        self.assertEqual(convert_videos.changeExtensionTo("/foo/bar/baz.mov", "mp4"), "/foo/bar/baz.mp4")
