title:/Talon Draft/
-
# Replace a single word with a phrase
^replace <user.draft_anchor1> with <user.text>$:
  user.draft_select("{draft_anchor1}")
  result = user.formatted_text(text, "NOOP")
  insert(result)

# Position cursor before word
^cursor <user.draft_anchor1>:
  user.draft_position_caret("{draft_anchor1}")

^cursor before <user.draft_anchor1>:
  user.draft_position_caret("{draft_anchor1}")

# Position cursor after word
^cursor after <user.draft_anchor1>:
  user.draft_position_caret("{draft_anchor1}", 1)

# Select a whole word
^select <user.draft_anchor1>:
  user.draft_select("{draft_anchor1}")

# Select a range of words
^select <user.draft_anchor1> until <user.draft_anchor2>:
  user.draft_select("{draft_anchor1}", "{draft_anchor2}")

# Delete a word
^clear <user.draft_anchor1>:
  user.draft_select("{draft_anchor1}", "", 1)
  key(backspace)

# Delete a range of words
^clear <user.draft_anchor1> until <user.draft_anchor2>:
  user.draft_select("{draft_anchor1}", "{draft_anchor2}", 1)
  key(backspace)

# Make a word title case
^word title <user.draft_anchor1>:
    user.draft_change_case("{draft_anchor1}", "title")

# Make a word lower case
^word lower <user.draft_anchor1>:
    user.draft_change_case("{draft_anchor1}", "lower")

# Make a word all caps case
^word upper <user.draft_anchor1>:
    user.draft_change_case("{draft_anchor1}", "upper")
