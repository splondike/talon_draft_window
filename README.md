This reposiory is a [Talon](https://talonvoice.com/) script that allows you to more easily edit prose style text via a task-specific UI.

# Usage

The `draft_window.talon` file depends on functions and lists defined by the [knausj\_talon](https://github.com/knausj85/knausj_talon) repo. Once you have knausj set up you can just drop this folder in next to it in the Talon user scripts directory (~/.talon/user/ under Linux). Alternatively you can edit the `draft_window.talon` file for your needs.

Once that's set up, an example voice command session might go like:

    draft show left # Show the window on the left of your screen
    sentence how are you # Types this in to the window, this is knausj
    replace cap with your family # Replaces the word corresponding to 'c' ('you') with 'your family'
    word lower air # Make the word corresponding to 'a' (how) lowercase
    cursor after bat # Put the text input cursor after the word corresponding to 'b'
    draft submit # Hide the draft window and type the contents in to the previously focussed widget

## Customising

If you want to change the display of the window you can do by adding some settings to one of your .talon files. See `settings.talon.example` for more details.
