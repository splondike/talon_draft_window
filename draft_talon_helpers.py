from typing import Optional

from talon import Module
from .draft_ui import DraftManager

mod = Module()

draft_manager = DraftManager()

@mod.action_class
class Actions:
    # TODO:
    # * The window doesn't work perfectly with all the standard editor commands. Particularly
    #   'undo that' doesn't always behave how it should.

    def draft_show(text: Optional[str]=None):
        """
        Shows draft window
        """

        draft_manager.show(text)

    def draft_hide():
        """
        Hides draft window
        """

        draft_manager.hide()

    def draft_select(
            start_anchor: str,
            end_anchor: str="",
            include_trailing_whitespace: int=0):
        """
        Selects text in the draft window
        """

        draft_manager.select_text(
            start_anchor,
            end_anchor=None if end_anchor == "" else end_anchor,
            include_trailing_whitespace=include_trailing_whitespace == 1
        )

    def draft_position_caret(anchor: str, after: int=0):
        """
        Positions the caret in the draft window
        """

        draft_manager.position_caret(
            anchor,
            after=after == 1
        )

    def draft_change_case(anchor: str, case: str):
        """
        Positions the caret in the draft window
        """

        draft_manager.change_case(
            anchor,
            case
        )

    def draft_get_text() -> str:
        """
        Returns the text in the draft window
        """

        return draft_manager.get_text()


# Some capture groups we need

@mod.capture(rule="{self.letter}+")
def anchor1(m) -> str:
    """
    An anchor (string of letters)
    """
    return "".join(m)


@mod.capture(rule="{self.letter}+")
def anchor2(m) -> str:
    """
    An anchor (string of letters)
    """

    return "".join(m)
