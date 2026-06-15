import unittest

from tennis_manager.tennisExceptions import (
    CategoryNotFound,
    PlayerNotFound,
    AddingDoubleInSingleCategory,
    DuplicatedCategory,
    DuplicatedTeam,
    DrawingDoublesError,
)


class ExceptionMessageTests(unittest.TestCase):
    def test_category_not_found(self):
        self.assertEqual(str(CategoryNotFound("X")), "Category (X) does not exist.")

    def test_player_not_found(self):
        self.assertEqual(
            str(PlayerNotFound("P", "C")),
            "Player (P) not found in category (C).",
        )

    def test_adding_double_in_single(self):
        self.assertEqual(
            str(AddingDoubleInSingleCategory("D", "C")),
            "Trying to add double (D) in single category (C).",
        )

    def test_duplicated_category(self):
        self.assertEqual(
            str(DuplicatedCategory("C")),
            "Trying to add category (C), but it already exists.",
        )

    def test_duplicated_team(self):
        self.assertEqual(
            str(DuplicatedTeam("T", "C")),
            "Trying to add team (T) in category (C), but it already exists.",
        )

    def test_drawing_doubles_error(self):
        self.assertEqual(
            str(DrawingDoublesError("C")),
            "Error drawing doubles in category (C).",
        )


if __name__ == "__main__":
    unittest.main()
