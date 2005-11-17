# This file consists of renpy functions that aren't expected to be
# touched by the user too much. We reserve the _ prefix for names
# defined in the library.

# It's strongly reccomended that you don't edit this file, as future
# releases of Ren'Py will probably change this file to include more
# functionality.

# It's also strongly recommended that you leave this file in the
# game directory, so its functionality is included in your game.



init -500:
    python:

        # These are settings that the user can tweak to control the
        # look of the main menu and the load/save/escape screens.

        # Used to store library settings.
        library = object()

        # The minimum version of the module we work with. Don't change
        # this unless you know what you're doing.
        library.module_version = 4008002

        # Should we warn the user if the module is missing or has a bad
        # version?
        library.module_warning = False

        # Used to translate strings in the library.
        library.translations = { }

        # True if the skip indicator should be shown.
        library.skip_indicator = True

        # This is updated to give the user an idea of where a save is
        # taking place.
        save_name = ''

        def _button_factory(label,
                            type=None,
                            selected=None,
                            disabled=False,
                            clicked=None,
                            **properties):
            """
            This function is called to create the various buttons used
            in the game menu. By overriding this function, one can
            (for example) replace the default textbuttons with image buttons.
            When it is called, it's expected to add a button to the screen.

            @param label: The label of this button, before translation. 

            @param type: The type of the button. One of "mm" (main menu),
            "gm_nav" (game menu), "file_picker_nav", "yesno", or "prefs".

            @param selected: True if the button is selected, False if not,
            or None if it doesn't matter.

            @param disabled: True if the button is disabled, False if not.

            @param clicked: A function that should be executed when the
            button is clicked.

            @param properties: Addtional layout properties.
            """

            style = type

            if selected and not disabled:
                style += "_selected"

            if disabled:
                clicked = None

            style = style + "_button"
            text_style = style + "_text"

            ui.textbutton(_(label), style=style, text_style=text_style, clicked=clicked, **properties)

        def _label_factory(label, type, **properties):
            """
            This function is called to create a new label. It can be
            overridden by the user to change how these labels are created.

            @param label: The label of the box.

            @param type: "prefs" or "yesno". 

            @param properties: This may contain position properties.
            """

            ui.text(_(label), style=type + "_label", **properties)

        # The function that's used to translate strings in the game menu.
        def _(s):
            """
            Translates s into another language or something.
            """
            
            if s in library.translations:
                return library.translations[s]
            else:
                return s

        # Are the windows currently hidden?
        _windows_hidden = False

    # Set up the default keymap.    
    python hide:

        # Called to make a screenshot happen.
        def screenshot():
            renpy.screenshot("screenshot.bmp")

        def invoke_game_menu():
            renpy.play(library.enter_sound)
            renpy.call_in_new_context('_game_menu')

        def toggle_skipping():
            config.skipping = not config.skipping
            renpy.restart_interaction()

        # The default keymap.
        km = renpy.Keymap(
            rollback = renpy.rollback,
            screenshot = screenshot,
            toggle_fullscreen = renpy.toggle_fullscreen,
            toggle_music = renpy.toggle_music,
            toggle_skip = toggle_skipping,
            game_menu = invoke_game_menu,
            hide_windows = renpy.curried_call_in_new_context("_hide_windows"),
            launch_editor = renpy.launch_editor,
            )

        config.underlay = [ km ]


    # The skip indicator.
    python hide:

        def skip_indicator():

            ### skip_indicator default
            # (text) The style and placement of the skip indicator.            

            if config.skipping and library.skip_indicator:
                ui.text(_("Skip Mode"), style='skip_indicator')

        config.overlay_functions.append(skip_indicator)

    return

label _hide_windows:

    if _windows_hidden:
        return

    python:
        _windows_hidden = True
        ui.saybehavior()
        ui.interact(suppress_overlay=True)
        _windows_hidden = False

    return



    
##############################################################################
# 
# Code for the game menu.



# This code here handles check for the correct version of the Ren'Py module.

label _check_module:

    if not library.module_warning:
        return

    python hide:
        module_info = _("While Ren'Py games are playable without the _renpy module, some features may be disabled. For more information, read the module/README.txt file or go to http://www.bishoujo.us/renpy/.")

        if renpy.module_version() == 0:
            _show_exception(_("_renpy module not found."),
                            _("The _renpy module could not be loaded on your system.") + "\n\n" + module_info)
        elif renpy.module_version() < library.module_version:
            _show_exception(_("Old _renpy module found."),
                            _("An old version (%d) of the Ren'Py module was found on your system, while this game requires version %d.") % (renpy.module_version(), library.module_version) + "\n\n" + module_info)

    return
                         


# Random nice things to have.
init:
    $ centered = Character(None, what_style="centered_text", window_style="centered_window")
    image text = renpy.ParameterizedText(style="centered_text")
    
        
