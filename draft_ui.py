from typing import Optional
import re

from talon.experimental.textarea import (
    TextArea,
    Span,
    DarkThemeLabels,
    LightThemeLabels
)


def iterate_anchor_labels():
    """
    Produces an iterator of possible anchor labels
    """

    characters = [chr(i) for i in range(ord("a"), ord("z") + 1)]
    for c in characters:
        yield c

    for c in characters:
        for d in characters:
            yield f"{c}{d}"

word_matcher = re.compile(r"([^\s]+)(\s*)")
def calculate_text_anchors(text):
    """
    Produces an iterator of (anchor, start_word_index, end_word_index, last_space_index)
    tuples from the given text. Each tuple indicates a particular point you may want to 
    reference when editing along with some useful ranges you may want to operate on.

    - *index is just a character offset from the start of the string (e.g. the first character is at index 0)
    - end_word_index is the index of the character after the last one included in the
      anchor. That is, you can use it with a slice directly like [start:end]
    - anchor is a short piece of text you can use to identify it (e.g. 'a', or '1').
    """
    anchor_labels = iterate_anchor_labels()

    for match in word_matcher.finditer(text):
        yield (
            next(anchor_labels),
            match.start(),
            match.end() - len(match.group(2)),
            match.end()
        )


class DraftManager:
    """
    API to the draft window
    """

    def __init__(self):
        self.area = TextArea()
        self.area.title = "Talon Draft"
        self.area.value = ""
        self.area.register("label", self._update_labels)
        self.set_styling()

    def set_styling(
        self,
        theme="dark",
        text_size=20,
        label_size=20,
        label_color=None
    ):
        """
        Allow settings the style of the draft window. Will dynamically
        update the style based on the passed in parameters.
        """

        area_theme = DarkThemeLabels if theme == "dark" else LightThemeLabels
        theme_changes = {
            "text_size": text_size,
            "label_size": label_size,
        }
        if label_color is not None:
            theme_changes["label"] = label_color
        self.area.theme = area_theme(**theme_changes)

    def show(self, text: Optional[str] = None):
        """
        Show the window. If text is None then keep the old contents,
        otherwise set the text to the given value.
        """

        if text is not None:
            self.area.value = text
        self.area.show()

    def hide(self):
        """
        Hide the window.
        """

        self.area.hide()

    def get_text(self) -> str:
        """
        Gets the context of the text area
        """

        return self.area.value

    def get_rect(self) -> "talon.types.Rect":
        """
        Get the Rect for the window
        """

        return self.area.rect

    def reposition(
        self,
        xpos: Optional[int] = None,
        ypos: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ):
        """
        Move the window or resize it without having to change all properties.
        """

        rect = self.area.rect
        if xpos is not None:
            rect.x = xpos

        if ypos is not None:
            rect.y = ypos

        if width is not None:
            rect.width = width

        if height is not None:
            rect.height = height

        self.area.rect = rect

    def select_text(
        self, start_anchor, end_anchor=None, include_trailing_whitespace=False
    ):
        """
        Selects the word corresponding to start_anchor. If end_anchor supplied, selects
        from start_anchor to the end of end_anchor. If include_trailing_whitespace=True
        then also selects trailing space characters (useful for delete).
        """

        start_index, end_index, last_space_index = self.anchor_to_range(start_anchor)
        if end_anchor is not None:
            _, end_index, last_space_index = self.anchor_to_range(end_anchor)

        if include_trailing_whitespace:
            end_index = last_space_index

        self.area.sel = Span(start_index, end_index)

    def position_caret(self, anchor, after=False):
        """
        Positions the caret before the given anchor. If after=True position it directly after.
        """

        start_index, end_index, _ = self.anchor_to_range(anchor)
        index = end_index if after else start_index

        self.area.sel = index

    def anchor_to_range(self, anchor):
        anchors_data = calculate_text_anchors(self._get_visible_text())
        for loop_anchor, start_index, end_index, last_space_index in anchors_data:
            if anchor == loop_anchor:
                return (start_index, end_index, last_space_index)

        raise RuntimeError(f"Couldn't find anchor {anchor}")

    def _update_labels(self, _visible_text):
        """
        Updates the position of the labels displayed on top of each word
        """

        anchors_data = calculate_text_anchors(self._get_visible_text())
        return [
            (Span(start_index, end_index), anchor)
            for anchor, start_index, end_index, _ in anchors_data
        ]

    def _get_visible_text(self):
        # Placeholder for a future method of getting this
        return self.area.value


if False:
    # Some code for testing, change above False to True and edit as desired
    draft_manager = DraftManager()
    draft_manager.show(
        "This is a line of text\nand another line of text and some more text so that the line gets so long that it wraps a bit.\nAnd a final sentence"
    )
    draft_manager.reposition(xpos=100, ypos=100)
    draft_manager.select_text("c")
