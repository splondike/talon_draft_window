# These are available when the draft window is open, but not necessarily focussed
tag: user.draft_window_showing
-
draft hide: user.draft_hide()

draft submit:
  content = user.draft_get_text()
  user.draft_hide()
  user.paste(content)
