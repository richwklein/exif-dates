from pathlib import Path

from exif_dates import has_exiftool, insensitive_glob


def test_has_exiftool_returns_bool():
    assert isinstance(has_exiftool(), bool)


class TestInsensitiveGlob:
    def test_matches_lowercase_extension(self, tmp_path):
        (tmp_path / "photo.jpg").touch()
        assert tmp_path / "photo.jpg" in [Path(p) for p in insensitive_glob(tmp_path, "jpg")]

    def test_matches_uppercase_extension(self, tmp_path):
        (tmp_path / "photo.JPG").touch()
        result = insensitive_glob(tmp_path, "jpg")
        assert len(result) == 1

    def test_matches_mixed_case_extension(self, tmp_path):
        (tmp_path / "clip.Mp4").touch()
        result = insensitive_glob(tmp_path, "mp4")
        assert len(result) == 1

    def test_no_match_returns_empty(self, tmp_path):
        (tmp_path / "document.txt").touch()
        result = insensitive_glob(tmp_path, "jpg")
        assert result == []

    def test_excludes_subdirectory_files(self, tmp_path):
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "photo.jpg").touch()
        result = insensitive_glob(tmp_path, "jpg")
        assert result == []

    def test_multiple_matches(self, tmp_path):
        (tmp_path / "a.jpg").touch()
        (tmp_path / "b.JPG").touch()
        (tmp_path / "c.Jpg").touch()
        result = insensitive_glob(tmp_path, "jpg")
        assert len(result) == 3
