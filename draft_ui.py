import threading
import tkinter
import tkinter.font


class LabelledText(tkinter.Text):
    """
    Textarea widget which displays anchor labels on each word and allows text selection
    based on those anchors.

    Standard keyboard shortcuts apply: copy (ctrl+c), cut (ctrl+x), paste (ctrl+v),
    select all (ctrl+a), undo (ctrl+z), redo (ctrl+shift+z)

    Useful docs for Tkinter:
    https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/text-methods.html
    """

    # TODO:
    # * The anchors should group around the caret position so closer things are easier
    #   to access.
    # * Handle long passages; scrolling or resizing text maybe? Label positioning should
    #   take this into account.
    # * The label positioning is a bit finnicky and can overlap letters, could probably
    #   improve this.

    def __init__(self, parent, **kwargs):
        self.font = tkinter.font.nametofont("TkFixedFont").actual()
        defaults = {
            'spacing1': 15,
            'spacing2': 15,
            'spacing3': 30,
            'wrap': 'word',
            'undo': True,
            'font': (self.font['family'], 30),
            'relief': 'flat',
            'highlightbackground': '#fff',
            'highlightcolor': '#fff'
        }
        defaults.update(kwargs)

        super().__init__(parent, **defaults)

        self.change_sentinel = False
        self.change_debounce_id = None
        self.bind("<<Modified>>", self._on_change)
        self.bind("<Configure>", lambda event: self._update_labels_debounced())

        self.master.bind('<Control-a>', self._action_select_all)

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

        # This sets the selection
        self.tag_remove(tkinter.SEL, '1.0', 'end')
        self.tag_add(tkinter.SEL, start_index, end_index)
        # This must be adjacent to the selection for overwrite to occur
        self.mark_set(tkinter.INSERT, end_index)

    def position_caret(self, anchor, after=False):
        """
        Positions the caret before the given anchor. If after=True position it directly after.
        """

        start_index, end_index, _ = self.anchor_to_range(anchor)
        index = end_index if after else start_index

        self.tag_remove(tkinter.SEL, '1.0', 'end')
        self.mark_set(tkinter.INSERT, index)

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
        text = self.get(start_index, end_index)
        self.delete(start_index, end_index)
        if case == 'lower':
            updated_text = text.lower()
        elif case == 'upper':
            updated_text = text.upper()
        elif case == 'title':
            updated_text = text[0].upper() + text[1:]
        else:
            raise AssertionError("Invalid case")

        self.insert(start_index, updated_text)

    def _on_change(self, event):
        if self.change_sentinel:
            return

        self.change_sentinel = True
        try:

            # Set 'modified' to 0.  This will also trigger the <<Modified>>
            # virtual event which is why we need the sentinel.
            self.tk.call(event.widget._w, 'edit', 'modified', 0)
        finally:
            # Clean the sentinel.
            self.change_sentinel = False

        if self.change_debounce_id:
            self.after_cancel(self.change_debounce_id)

        self._update_labels_debounced()

    def _update_labels_debounced(self):
        def _update_labels_inner(text_input):
            self.change_debounce_id = None
            self._update_labels()

        self.change_debounce_id = self.after(
            300,
            _update_labels_inner,
            self
        )

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

        - *index is a Tkinter style index (i.e. <line number>.<character pos>)
        - anchor is a short piece of text you can use to identify it (e.g. 'a', '1').
        """

        line_idx = 1
        char_idx = 0
        word_start_index = None
        word_end_index = None
        anchor_labels = cls._iterate_anchor_labels()

        state = 'newline'

        for character in text:
            next_state = {
                ' ': 'space',
                '\n': 'newline'
            }.get(character, 'word')
            curr_index = f"{line_idx}.{char_idx}"

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
                'end',
                'end'
            )

    def _get_visible_text(self):
        # Ensure text position is recalculated
        self.update_idletasks()

        return self.get('1.0', 'end')

    def _update_labels(self):
        """
        Updates the position of the labels displayed on top of each word
        """

        # Destroy old labels
        for child in self.winfo_children():
            child.destroy()

        anchors_data = self._calculate_anchors(self._get_visible_text())
        for anchor, start_index, a, b in anchors_data:
            label = tkinter.Label(
                self,
                background="#fff",
                foreground="#aaaaaa",
                font=(self.font['family'], 10),
                height=1,
                width=2,
                text=anchor,
                borderwidth=0
            )

            # character bounding box
            x, _, _, _ = self.bbox(start_index)
            # line bounding box
            _, y, _, _, _ = self.dlineinfo(start_index)
            label.place(x=x, y=y - 6)

    def _action_select_all(self, event):
        self.tag_add(tkinter.SEL, '1.0', 'end')
        self.mark_set(tkinter.INSERT, 'end')


class DraftManager():
    """
    Controls a floating text input window. The main interface class to the system.
    """

    # TODO:
    # * Make this file reloadable; kill the thread on reload

    def __init__(self):
        threading.Thread(target=self.spawn, daemon=False).start()

    def spawn(self):
        while True: # recreate the window when closed
            self.gui = tkinter.Tk()
            self.gui.title("Talon Draft")
            w = self.gui.winfo_screenwidth()
            h = self.gui.winfo_screenheight()

            self.gui.geometry(f"{int(w*0.5)}x{int(h*0.5)}+{int(w*0.1)}+{int(h*0.15)}")
            self.text = LabelledText(self.gui)
            self.text.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

            self.gui.withdraw()
            self.gui.mainloop()

    def show(self, text=""):
        if text is not None:
            self.text.delete("1.0", "end")
            self.text.insert('end', text)

        self.gui.deiconify()
        self.gui.lift()
        self.gui.focus_force()
        self.text.focus()

    def hide(self):
        self.gui.withdraw()

    def select_text(self, start_anchor, end_anchor=None, include_trailing_whitespace=False):
        self.text.select_text(
            start_anchor,
            end_anchor=end_anchor,
            include_trailing_whitespace=include_trailing_whitespace
        )

    def position_caret(self, anchor, after=False):
        self.text.position_caret(anchor, after=after)

    def get_text(self):
        return self.text.get("1.0", "end").strip()

    def change_case(self, anchor, case):
        self.text.change_case(anchor, case)


if __name__ == "__main__":
    # For testing outside of Talon
    import time
    draft_manager = DraftManager()
    time.sleep(1) # Give the thread a chance
    draft_manager.show("hello world")
    draft_manager.change_case("a", "title")
