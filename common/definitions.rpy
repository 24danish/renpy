# This file contains a number of definitions of standard
# locations and transitions. We've moved them into the common
# directory so that it's easy for an updated version of all of these
# definitions.

init -425:

    # Positions ##############################################################

    # These are positions that can be used inside at clauses. We set
    # them up here so that they can be used throughout the program.
    $ left = Position(xpos=0.0, xanchor='left')
    $ center = Position()
    $ right = Position(xpos=1.0, xanchor='right')

    # Offscreen positions for use with the move transition. Images at
    # these positions are still shown (and consume
    # resources)... remember to hide the image after the transition.    
    $ offscreenleft = Position(xpos=0.0, xanchor='right')
    $ offscreenright = Position(xpos=1.0, xanchor='left')

    # Transitions ############################################################

    # Simple transitions.
    $ fade = Fade(.5, 0, .5) # Fade to black and back.
    $ dissolve = Dissolve(0.5)
    $ pixellate = Pixellate(1.0, 5)

    # Various uses of CropMove.    
    $ wiperight = CropMove(1.0, "wiperight")
    $ wipeleft = CropMove(1.0, "wipeleft")
    $ wipeup = CropMove(1.0, "wipeup")
    $ wipedown = CropMove(1.0, "wipedown")

    $ slideright = CropMove(1.0, "slideright")
    $ slideleft = CropMove(1.0, "slideleft")
    $ slideup = CropMove(1.0, "slideup")
    $ slidedown = CropMove(1.0, "slidedown")

    $ slideawayright = CropMove(1.0, "slideawayright")
    $ slideawayleft = CropMove(1.0, "slideawayleft")
    $ slideawayup = CropMove(1.0, "slideawayup")
    $ slideawaydown = CropMove(1.0, "slideawaydown")

    $ irisout = CropMove(1.0, "irisout")
    $ irisin = CropMove(1.0, "irisin")

    # This moves changed images to their new locations
    $ move = MoveTransition(0.5)

    # These shake the screen up and down for a quarter second.
    # The delay needs to be an integer multiple of the period.
    $ vpunch = Move((0, 10), (0, -10), .10, bounce=True, repeat=True, delay=.275)
    $ hpunch = Move((15, 0), (-15, 0), .10, bounce=True, repeat=True, delay=.275)

    # These use the ImageDissolve to do some nifty effects.
    $ blinds = ImageDissolve(im.Tile("blindstile.png"), 1.0, 8)
    $ squares = ImageDissolve(im.Tile("squarestile.png"), 1.0, 256)

    image black = Solid((0, 0, 0, 255))
    
