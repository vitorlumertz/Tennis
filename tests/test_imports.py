import importlib
import sys
import unittest


class ImportOrderTests(unittest.TestCase):
    def test_import_match_before_tennis_helper(self):
        # Regressão do import circular: importar `match` antes de `tennisHelper`
        # lançava ImportError. Reimporta do zero para validar a ordem.
        for name in ("match", "tennisHelper"):
            sys.modules.pop(name, None)
        match = importlib.import_module("match")
        tennisHelper = importlib.import_module("tennisHelper")
        self.assertTrue(hasattr(match, "Match"))
        self.assertTrue(hasattr(tennisHelper, "IsValidScore"))


if __name__ == "__main__":
    unittest.main()
