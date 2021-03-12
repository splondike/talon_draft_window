from typing import Optional

from talon import ui, settings, Module, Context
from .draft_ui import DraftManager

mod = Module()

# ctx is for toggling the draft_window_showing variable
# which lets you execute actions whenever the window is visible.
ctx = Context()

# ctx_focused is active only when the draft window is focussed. This
# lets you execute actions under that condition.
ctx_focused = Context()
ctx_focused.matches = r"""
title: Talon Draft
"""

mod.tag("draft_window_showing", desc="Tag set when draft window showing")
setting_theme = mod.setting(
    "draft_window_theme",
    type=str,
    default="dark",
    desc="Sets the main colors of the window, one of 'dark' or 'light'"
)
setting_label_size = mod.setting(
    "draft_window_label_size",
    type=int,
    default=20,
    desc="Sets the size of the word labels used in the draft window"
)
setting_label_color = mod.setting(
    "draft_window_label_color",
    type=str,
    default=None,
    desc=(
        "Sets the color of the word labels used in the draft window. "
        "E.g. 00ff00 would be green"
    )
)
setting_text_size = mod.setting(
    "draft_window_text_size",
    type=int,
    default=20,
    desc="Sets the size of the text used in the draft window"
)


draft_manager = DraftManager()

# Update the styling of the draft window dynamically as user settings change
def _update_draft_style(*args):
    draft_manager.set_styling(
        **{
            arg: setting.get()
            for setting, arg in (
                (setting_theme, 'theme'),
                (setting_label_size, 'label_size'),
                (setting_label_color, 'label_color'),
                (setting_text_size, 'text_size'),
            )
        }
    )
settings.register("", _update_draft_style)


@ctx_focused.action_class("user")
class ContextSensitiveDictationActions:
    """
    Override these actions to assist 'Smart dictation mode'.
    see https://github.com/knausj85/knausj_talon/pull/356
    """
    def dictation_peek_left(clobber=False):
        area = draft_manager.area
        return area[max(0, area.sel.left - 50) : area.sel.left]

    def dictation_peek_right():
        area = draft_manager.area
        return area[area.sel.right : area.sel.right + 50]


@ctx_focused.action_class("edit")
class EditActions:
    """
    Make default edit actions more efficient.
    """

    def selected_text() -> str:
        area = draft_manager.area
        if area.sel:
            result = area[area.sel.left : area.sel.right]
            return result
        return ""


@mod.action_class
class Actions:
    def draft_show(text: Optional[str] = None):
        """
        Shows draft window
        """

        draft_manager.show(text)
        ctx.tags = ["user.draft_window_showing"]

    def draft_hide():
        """
        Hides draft window
        """

        draft_manager.hide()
        ctx.tags = []

    def draft_select(
        start_anchor: str, end_anchor: str = "", include_trailing_whitespace: int = 0
    ):
        """
        Selects text in the draft window
        """

        draft_manager.select_text(
            start_anchor,
            end_anchor=None if end_anchor == "" else end_anchor,
            include_trailing_whitespace=include_trailing_whitespace == 1,
        )

    def draft_position_caret(anchor: str, after: int = 0):
        """
        Positions the caret in the draft window
        """

        draft_manager.position_caret(anchor, after=after == 1)

    def draft_get_text() -> str:
        """
        Returns the text in the draft window
        """

        return draft_manager.get_text()

    def draft_resize(width: int, height: int):
        """
        Resize the draft window.
        """

        draft_manager.reposition(width=width, height=height)

    def draft_named_move(name: str, screen_number: Optional[int] = None):
        """
        Lets you move the window to the top, bottom, left, right, or middle
        of the screen.
        """

        screen = ui.screens()[screen_number or 0]
        window_rect = draft_manager.get_rect()
        xpos = (screen.width - window_rect.width) / 2
        ypos = (screen.height - window_rect.height) / 2

        if name == "top":
            ypos = 50
        elif name == "bottom":
            ypos = screen.height - window_rect.height - 50
        elif name == "left":
            xpos = 50
        elif name == "right":
            xpos = screen.width - window_rect.width - 50
        elif name == "middle":
            # That's the default values
            pass

        draft_manager.reposition(xpos=xpos, ypos=ypos)


# Some capture groups we need


@mod.capture(rule="{self.letter}+")
def draft_anchor(m) -> str:
    """
    An anchor (string of letters)
    """
    return "".join(m)


@mod.capture(rule="(top|bottom|left|right|middle)")
def draft_window_position(m) -> str:
    """
    One of the named positions you can move the window to
    """

    return "".join(m)
