try:
    import talon.experimental.textarea
    running_in_talon = True
except ModuleNotFoundError:
    # Some shenanigans to stub out the Talon imports
    import imp, sys
    name = "talon.experimental.textarea"
    module = imp.new_module(name)
    sys.modules[name] = module
    exec(
        "\n".join([
            "TextArea = 1",
            "Span = 1",
            "DarkThemeLabels = 1",
            "LightThemeLabels = 1"
        ]),
        module.__dict__
    )
    running_in_talon = False

from unittest import TestCase
from functools import wraps

from .draft_ui import calculate_text_anchors


class CalculateAnchorsTest(TestCase):
    """
    Tests calculate_text_anchors
    """

    def test_finds_anchors(self):
        examples = [
            ("one-word", [("a", 0, 7, 7)]),
            ("two words", [("a", 0, 2, 3), ("b", 4, 8, 8)]),
            ("two\nwords", [("a", 0, 2, 3), ("b", 4, 8, 8)]),
        ]
        for text, expected in examples:
            # Given an example

            # When we calculate the result and turn it into a list
            result = list(calculate_text_anchors(text))

            # Then it matches what we expect
            self.assertEqual(result, expected, text)
