"""Unit tests for the curriculum module."""

from textype.curriculum import LESSONS, SENTENCES, LessonDict


class TestCurriculum:
    """Tests the structure and content of the curriculum data."""

    def test_lessons_structure(self):
        """Tests that LESSONS is a list of dictionaries."""
        assert isinstance(LESSONS, list)
        assert all(isinstance(lesson, dict) for lesson in LESSONS)

    def test_lesson_keys(self):
        """Ensures each lesson has the required keys."""
        required_keys = LessonDict.__annotations__.keys()
        for lesson in LESSONS:
            assert all(key in lesson for key in required_keys)

    def test_lesson_data_types(self):
        """Verifies the data types of the values in each lesson dictionary."""
        for lesson in LESSONS:
            assert isinstance(lesson["name"], str)
            assert isinstance(lesson["algo"], str)
            assert isinstance(lesson["row"], str)
            assert isinstance(lesson["target_acc"], int)
            assert isinstance(lesson["target_wpm"], int)
            assert isinstance(lesson["shift_mode"], str)
            assert lesson["shift_mode"] in ["off", "mixed", "always"]

    def test_sentences_structure(self):
        """Tests that SENTENCES is a list of strings."""
        assert isinstance(SENTENCES, list)
        assert all(isinstance(sentence, str) for sentence in SENTENCES)

    def test_no_empty_sentences(self):
        """Ensures there are no empty strings in the SENTENCES list."""
        assert all(len(sentence) > 0 for sentence in SENTENCES)
