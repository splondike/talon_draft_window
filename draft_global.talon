mode: command
-
^draft show$: user.draft_show()

^draft hide$: user.draft_hide()

^draft edit$:
    text = edit.selected_text()
    key(backspace)
    user.draft_show(text)
^draft edit all$:
    edit.select_all()
    text = edit.selected_text()
    key(backspace)
    user.draft_show(text)

^draft empty$: user.draft_show("")

^draft submit$:
  content = user.draft_get_text()
  user.draft_hide()
  sleep(100ms)
  insert(content)
