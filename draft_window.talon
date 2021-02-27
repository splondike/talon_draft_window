title:/Talon Buffer/
-
# Replace a single word with a phrase
^replace <user.anchor1> with <user.text>$:
  user.draft_select("{anchor1}")
  result = user.formatted_text(text, "NOOP")
  insert(result)

# Position cursor before word
^cursor <user.anchor1>:
  user.draft_position_caret("{anchor1}")

# Position cursor after word
^cursor after <user.anchor1>:
  user.draft_position_caret("{anchor1}", 1)

# Select a whole word
^select <user.anchor1>:
  user.draft_select("{anchor1}")

# Select a range of words
^select <user.anchor1> until <user.anchor2>:
  user.draft_select("{anchor1}", "{anchor2}")

# Delete a word
^clear <user.anchor1>:
  user.draft_select("{anchor1}", "", 1)
  key(backspace)

# Delete a range of words
^clear <user.anchor1> until <user.anchor2>:
  user.draft_select("{anchor1}", "{anchor2}", 1)
  key(backspace)

# Make a word title case
^word title <user.anchor1>:
    user.draft_change_case("{anchor1}", "title")

# Make a word lower case
^word lower <user.anchor1>:
    user.draft_change_case("{anchor1}", "lower")

# Make a word all caps case
^word upper <user.anchor1>:
    user.draft_change_case("{anchor1}", "upper")
