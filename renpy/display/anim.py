# This file contains support for state-machine controlled animations.

import renpy
import pygame
import random

class State(object):
    """
    This creates a state that can be used in a SMAnimation.
    """


    def __init__(self, name, image, *atlist, **properties):
        """
        @param name: A string giving the name of this state.

        @param image: The displayable that is shown to the user while
        we are in (entering) this state. For convenience, this can
        also be a string or tuple, which is interpreted with Image.

        image should be None when this State is used with motion,
        to indicate that the image will be replaced with the child of
        the motion.

        @param atlist: A list of functions to call on the image. (In
        general, if something can be used in an at clause, it can be
        used here as well.)

        If any keyword arguments are given, they are used to construct a
        Position object, that modifies the position of the image.
        """

        if image and not isinstance(image, renpy.display.core.Displayable):
            image = renpy.display.image.Image(image)

        self.name = name
        self.image = image
        self.atlist = atlist
        self.properties = properties


    def add(self, sma):
        sma.states[self.name] = self

    def get_image(self):
        rv = self.image

        for i in self.atlist:
            rv = i(rv)

        if self.properties:
            rv = renpy.display.layout.Position(rv, **properties)

        return rv

    def motion_copy(self, child):

        if self.image is not None:
            child = self.mage

        return State(self.name, child, *self.atlist)
    

class Edge(object):
    """
    This creates an edge that can be used with a SMAnimation.
    """

    def __init__(self, old, delay, new, trans=None, prob=1):
        """
        @param old: The name (a string) of the state that this transition is from.

        @param delay: The number of seconds that this transition takes.

        @param new: The name (a string) of the state that this transition is to.

        @param trans: The transition that will be used to show the
        image found in the new state. If None, the image is show
        immediately.

        When used with an SMMotion, the transition should probably be
        move.

        @param prob: The number of times this edge is added. This can
        be used to make a transition more probable then others. For
        example, if one transition out of a state has prob=5, and the
        other has prob=1, then the one with prob=5 will execute 5/6 of
        the time, while the one with prob=1 will only occur 1/6 of the
        time. (Don't make this too large, as memory use is proportional to
        this value.)
        """

        self.old = old
        self.delay = delay
        self.new = new
        self.trans = trans
        self.prob = prob

    def add(self, sma):
        for i in range(0, self.prob):
            sma.edges.setdefault(self.old, []).append(self)


class SMAnimation(renpy.display.core.Displayable):
    """
    This creates a state-machine animation. Such an animation is
    created by randomly traversing the edges between states in a
    defined state machine. Each state corresponds to an image shown to
    the user, with the edges corresponding to the amount of time an
    image is shown, and the transition it is shown with.

    Images are shown, perhaps with a transition, when we are
    transitioning into a state containing that image.
    """
    
    def __init__(self, initial, *args, **properties):
        """
        @param initial: The name (a string) of the initial state we
        start in.

        @param showold: If the keyword parameter showold is True, then
        the old image is shown instead of the new image when in an
        edge.

        @param anim_timebase: If True, we use the animation
        timebase. If False, we use the displayable timebase.

        This accepts as additional arguments the anim.State and
        anim.Edge objects that are used to make up this state
        machine.
        """

        if 'delay' in properties:
            self.delay = properties['delay']
            del properties['delay']
        else:
            self.delay = None

        if 'showold' in properties:
            self.showold = properties['showold']
            del properties['showold']
        else:
            self.showold = False

        if 'anim_timebase' in properties:
            self.anim_timebase = properties['anim_timebase']
            del properties['anim_timebase']
        else:
            self.anim_timebase = True

        super(SMAnimation, self).__init__(**properties)

        self.properties = properties

        # The initial state.
        self.initial = initial

        # A map from state name to State object.
        self.states = { }

        # A map from state name to list of Edge objects.
        self.edges = { }

        for i in args:
            i.add(self)

        # The time at which the current edge started. If None, will be
        # set to st by render.
        self.edge_start = None

        # A cache for what the current edge looks like when rendered.
        self.edge_cache = None

        # The current edge.
        self.edge = None

        # The state we're in.
        self.state = None

    def predict(self, callback):
        for i in self.states.itervalues():
            i.image.predict(callback)

    def pick_edge(self, state):
        """
        This randomly picks an edge out of the given state, if
        one exists. It updates self.edge if a transition has
        been selected, or returns None if none can be found. It also
        updates self.image to be the new image on the selected edge.
        """

        if state not in self.edges:
            self.edge = None
            return

        edges = self.edges[state]
        self.edge = random.choice(edges)
        self.state = self.edge.new
        
    def update_cache(self):
        """
        Places the correct Displayable into the edge cache, based on
        what is contained in the given edge. This takes into account
        the old and new states, and any transition that is present.
        """


        if self.edge.trans:
            im = self.edge.trans(old_widget=self.states[self.edge.old].get_image(),
                                 new_widget=self.states[self.edge.new].get_image())
        elif self.showold:
            im = self.states[self.edge.old].get_image()
        else:
            im = self.states[self.edge.new].get_image()

        self.edge_cache = im

    def get_placement(self):

        if self.edge_cache:
            return self.edge_cache.get_placement()

        if self.state:
            return self.states[self.state].get_image().get_placement()

        return super(SMAnimation, self).get_placement()

    def render(self, width, height, st, at):

        if self.anim_timebase:
            t = at
        else:
            t = st

        if self.edge_start is None or t < self.edge_start:
            self.edge_start = t
            self.edge_cache = None
            self.pick_edge(self.initial)

        while self.edge and t > self.edge_start + self.edge.delay:
            self.edge_start += self.edge.delay
            self.edge_cache = None
            self.pick_edge(self.edge.new)

        # If edge is None, then we have a permanent, static picture. Deal
        # with that.

        if not self.edge:
            im = renpy.display.render.render(self.states[self.state].get_image(),
                                             width, height,
                                             st - self.edge_start, at)


        # Otherwise, we have another edge.

        else:
            if not self.edge_cache:
                self.update_cache()

            im = renpy.display.render.render(self.edge_cache, width, height, t - self.edge_start, at)

            renpy.display.render.redraw(self.edge_cache, self.edge.delay - (t - self.edge_start))


        iw, ih = im.get_size()

        rv = renpy.display.render.Render(iw, ih)
        rv.blit(im, (0, 0))

        return rv
    
    def __call__(self, child=None, new_widget=None, old_widget=None):
        """
        Used when this SMAnimation is used as a SMMotion. This creates
        a duplicate of the animation, with all states containing None
        as the image having that None replaced with the image that is provided here.
        """

        if child is None:
            child = new_widget

        args = [ ]

        for state in self.states.itervalues():
            args.append(state.motion_copy(child))

        for edges in self.edges.itervalues():
            args.extend(edges)

        return SMAnimation(self.initial, delay=self.delay, *args, **self.properties)


class Animation(renpy.display.core.Displayable):
    """
    A Displayable that draws an animation, which is a series of images
    that are displayed with time delays between them.
    """

    def __init__(self, *args, **properties):
        """
        Odd (first, third, fifth, etc.) arguments to Animation are
        interpreted as image filenames, while even arguments are the
        time to delay between each image. If the number of arguments
        is odd, the animation will stop with the last image (well,
        actually delay for a year before looping). Otherwise, the
        animation will restart after the final delay time.

        @param anim_timebase: If True, the default, use the animation
        timebase. Otherwise, use the displayable timebase.
        """

        properties.setdefault('style', 'animation')
        self.anim_timebase = properties.pop('anim_timebase', True)

        super(Animation, self).__init__(**properties)

        self.images = [ ]
        self.delays = [ ]

        for i, arg in enumerate(args):

            if i % 2 == 0:
                self.images.append(renpy.display.im.image(arg, loose=True))
            else:
                self.delays.append(arg)

        if len(self.images) > len(self.delays):
            self.delays.append(365.25 * 86400.0) # One year, give or take.
                
    def render(self, width, height, st, at):

        if self.anim_timebase:
            t = at % sum(self.delays)
        else:
            t = st % sum(self.delays)

        for image, delay in zip(self.images, self.delays):
            if t < delay:
                renpy.display.render.redraw(self, delay - t)

                im = renpy.display.render.render(image, width, height, st, at)
                width, height = im.get_size()
                rv = renpy.display.render.Render(width, height)
                rv.blit(im, (0, 0))

                return rv
            
            else:
                t = t - delay

    def predict(self, callback):
        for i in self.images:
            i.predict(callback)


class Blink(renpy.display.core.Displayable):
    """
    """

    def __init__(self, image, on=0.5, off=0.5, rise=0.5, set=0.5,
                 high=1.0, low=0.0, offset=0.0, anim_timebase=False, **properties):

        """
        This takes as an argument an image or widget, and blinks that image
        by varying its alpha. The sequence of phases is
        on - set - off - rise - on - ... All times are given in seconds, all
        alphas are fractions between 0 and 1.

        @param image: The image or widget that will be blinked.

        @param on: The amount of time the widget spends on, at high alpha.

        @param off: The amount of time the widget spends off, at low alpha.

        @param rise: The amount time the widget takes to ramp from low to high alpha.

        @param set: The amount of time the widget takes to ram from high to low.

        @param high: The high alpha.

        @param low: The low alpha.

        @param offset: A time offset, in seconds. Use this to have a
        blink that does not start at the start of the on phase.

        @param anim_timebase: If True, use the animation timebase, if false, the displayable timebase.
        """
        
        super(Blink, self).__init__(**properties)

        self.image = renpy.display.im.image(image, loose=True)
        self.on = on
        self.off = off
        self.rise = rise
        self.set = set
        self.high = high
        self.low = low
        self.offset = offset
        self.anim_timebase = anim_timebase

        self.cycle = on + set + off + rise


    def predict(self, callback):
        self.image.predict(callback)

    def render(self, height, width, st, at):

        if self.anim_timebase:
            t = at
        else:
            t = st

        time = (self.offset + t) % self.cycle
        alpha = self.high

        if 0 <= time < self.on:
            delay = self.on - time
            alpha = self.high

        time -= self.on

        if 0 <= time < self.set:
            delay = 0            
            frac = time / self.set
            alpha = self.low * frac + self.high * (1.0 - frac)

        time -= self.set

        if 0 <= time < self.off:
            delay = self.off - time
            alpha = self.low

        time -= self.off

        if 0 <= time < self.rise:
            delay = 0
            frac = time / self.rise 
            alpha = self.high * frac + self.low * (1.0 - frac)


        rend = renpy.display.render.render(self.image, height, width, st, at)

        if not renpy.display.module.can_map:
            return rend

        w, h = rend.get_size()
        rv = renpy.display.render.Render(w, h)

        if alpha:

            oldsurf = rend.pygame_surface()

            if not (oldsurf.get_masks()[3]):
                oldsurf = oldsurf.convert_alpha()

            newsurf = pygame.Surface(oldsurf.get_size(), oldsurf.get_flags(), oldsurf)

            amap = renpy.display.im.ramp(0, int(alpha * 255.0))
            identity = renpy.display.im.identity

            renpy.display.module.map(oldsurf, newsurf,
                                     identity, identity, identity, amap)

            renpy.display.render.mutated_surface(newsurf)

            rv.blit(newsurf, (0, 0))

        rv.depends_on(rend)
        renpy.display.render.redraw(self, delay)

        return rv


def Filmstrip(image, framesize, gridsize, delay, frames=None, loop=True, **properties):
    """
    This creates an animation from a single image. This image
    must consist of a grid of frames, with the number of columns and
    rows in the grid being taken from gridsize, and the size of each
    frame in the grid being taken from framesize. This takes frames
    and sticks them into an Animation, with the given delay between
    each frame. The frames are taken by going from left-to-right
    across the first row, left-to-right across the second row, and
    so on until all frames are consumed, or a specified number of
    frames are taken.

    @param image: The image that the frames must be taken from.

    @param framesize: A (width, height) tuple giving the size of
    each of the frames in the animation.

    @param gridsize: A (columns, rows) tuple giving the number of
    columns and rows in the grid.

    @param delay: The delay, in seconds, between frames.

    @param frames: The number of frames in this animation. If None,
    then this defaults to colums * rows frames, that is, taking
    every frame in the grid.

    @param loop: If True, loop at the end of the animation. If False,
    this performs the animation once, and then stops.

    Other keyword arguments are as for anim.SMAnimation.
    """

    width, height = framesize
    cols, rows = gridsize

    if frames is None:
        frames = cols * rows

    i = 0

    # Arguments to Animation
    args = [ ]

    for r in range(0, rows):
        for c in range(0, cols):

            x = c * width
            y = r * height

            args.append(renpy.display.im.Crop(image, x, y, width, height))
            args.append(delay)

            i += 1
            if i == frames:
                break

        if i == frames:
            break
            
    if not loop:
        args.pop()

    return Animation(*args, **properties)
