from typing import Optional

from talon.experimental.textarea import (
    TextArea,
    Span,
    DarkThemeLabels
)


class DraftManager():
    """
    API to the draft window
    """

    def __init__(self):
        self.area = TextArea()
        self.area.title = "Talon Draft"
        self.area.theme = DarkThemeLabels(
            text_size=20,
            label_size=20
        )
        self.area.value = ''
        self.area.register('label', self._update_labels)

    def show(self, text: Optional[str]=None):
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

    def get_rect(self) -> 'talon.types.Rect':
        """
        Get the Rect for the window
        """

        return self.area.rect

    def reposition(
            self,
            xpos: Optional[int]=None,
            ypos: Optional[int]=None,
            width: Optional[int]=None,
            height: Optional[int]=None):
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

    def select_text(self, start_anchor, end_anchor=None, include_trailing_whitespace=False):
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
        anchors_data = self._calculate_anchors(self._get_visible_text())
        for loop_anchor, start_index, end_index, last_space_index in anchors_data:
            if anchor == loop_anchor:
                return (start_index, end_index, last_space_index)

        raise RuntimeError(f"Couldn't find anchor {anchor}")

    def change_case(self, anchor, case):
        """
        Positions the caret before the given anchor. If after=True position it directly after.
        """

        start_index, end_index, _ = self.anchor_to_range(anchor)
        text = self.area.value[start_index:end_index]
        if case == 'lower':
            updated_text = text.lower()
        elif case == 'upper':
            updated_text = text.upper()
        elif case == 'title':
            updated_text = text[0].upper() + text[1:]
        else:
            raise AssertionError("Invalid case")

        self.area.replace(Span(start_index, end_index), updated_text)

    @staticmethod
    def _iterate_anchor_labels():
        characters = [chr(i) for i in range(ord('a'), ord('z') + 1)]
        for c in characters:
            yield c

        for c in characters:
            for d in characters:
                yield f"{c}{d}"


    @classmethod
    def _calculate_anchors(cls, text):
        """
        Produces an iterator of (anchor, start_word_index, end_word_index, last_space_index)
        tuples from the given text. Each tuple indicates a particular point you may want to 
        reference when editing along with some useful ranges you may want to operate on.

        - *index is just a character offset from the start of the string (e.g. the first character is at index 0)
        - anchor is a short piece of text you can use to identify it (e.g. 'a', or '1').
        """

        line_idx = 1
        char_idx = 0
        word_start_index = None
        word_end_index = None
        anchor_labels = cls._iterate_anchor_labels()

        state = 'newline'

        for curr_index, character in enumerate(text):
            next_state = {
                ' ': 'space',
                '\n': 'newline'
            }.get(character, 'word')

            # space -> word, space -> newline, word -> newline should yield
            should_yield = (
                word_start_index is not None and
                (next_state == 'newline' or (state == 'space' and next_state != 'space'))
            )
            if should_yield:
                yield (
                    next(anchor_labels),
                    word_start_index,
                    word_end_index or curr_index,
                    curr_index
                )
                word_start_index = None
                word_end_index = None
                last_space_index = None

            if state != 'word' and next_state == 'word':
                word_start_index = curr_index

            if state == 'word' and next_state != 'word':
                word_end_index = curr_index

            if next_state == 'newline':
                line_idx += 1
                char_idx = 0
            else:
                char_idx += 1
            state = next_state

        if word_start_index is not None:
            yield (
                next(anchor_labels),
                word_start_index,
                len(text),
                len(text)
            )

    def _update_labels(self, _visible_text):
        """
        Updates the position of the labels displayed on top of each word
        """

        anchors_data = self._calculate_anchors(self._get_visible_text())
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
    draft_manager.show("This is some text\nand another line of text and some more text so that the line gets so long that it wraps a bit.\nAnd a final sentence")
    draft_manager.reposition(xpos=100, ypos=100)
    draft_manager.select_text('c')
