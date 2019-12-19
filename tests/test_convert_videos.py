import convert_videos


def test_change_extension_name():
    assert convert_videos.changeExtensionTo("asdf.mov", "mkv") == "asdf.mkv"
    assert convert_videos.changeExtensionTo("/foo/bar/baz.mov", "mkv") == "/foo/bar/baz.mkv"
    assert convert_videos.changeExtensionTo("asdf.mov", "avi") == "asdf.avi"
    assert convert_videos.changeExtensionTo("/foo/bar/baz.mov", "mp4") == "/foo/bar/baz.mp4"
