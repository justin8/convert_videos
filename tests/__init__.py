import unittest
import convert_videos
import mock

class testConvertVideos(unittest.TestCase):


    def testChangeExtensionToMKV(self):
        self.assertEqual(convert_videos.changeExtensionToMKV("asdf.mov"), "asdf.mkv")
        self.assertEqual(convert_videos.changeExtensionToMKV("/foo/bar/baz.mov"), "/foo/bar/baz.mkv")
