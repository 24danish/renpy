# This file mediates access to the _renpy module, which is a C module that
# allows us to enhance the feature set of pygame in a renpy specific way.

import pygame
from pygame.constants import *

import sys

try:
    import _renpy
    version = _renpy.version()

    if version < 5003003:
        print >>sys.stderr, "The _renpy module was found, but is out of date.\nPlease read module/README.txt for more information."
        
except:
    # If for any reason we can't import the module, we have a version
    # number of 0.

    print >>sys.stderr, "The _renpy module was not found. Please read module/README.txt for"
    print >>sys.stderr, "more information."

    version = 0


def convert_and_call(function, src, dst, *args):
    """
    This calls the function with the source and destination
    surface. The surfaces must have the same alpha.

    If the surfaces are not 24 or 32 bits per pixel, or don't have the
    same format, they are converted and then converted back.
    """

    if (dst.get_masks()[3] != 0) != (src.get_masks()[3] != 0):
        raise Exception("Surface alphas do not match.")

    dstsize = dst.get_bitsize()

    if dst.get_bitsize() in (24, 32):
        target = dst
    else:
        if dst.get_masks()[3]:
            target = pygame.Surface(dst.get_size(), SRCALPHA, 32)
        else:
            target = pygame.Surface(dst.get_size(), 0, 24)

    if src.get_bitsize() == target.get_bitsize():
        source = src
    else:
        source = src.convert(target)
    
    function(source, target, *args)

    if target is not dst:
        dst.blit(target, (0, 0))


if version >= 4008002:

    can_pixellate = True

    def pixellate(src, dst, avgwidth, avgheight, outwidth, outheight):
        """
        This pixellates the source surface. First, every pixel in the
        source surface is projected onto a virtual surface, such that
        the average value of every avgwidth x avgheight pixels becomes
        one virtual pixel. It then gets projected back onto the
        destination surface at a ratio of one virtual pixel to every
        outwidth x outheight destination pixels.

        If either src or dst is not a 24 or 32 bit surface, they are
        converted... but that may be a significant performance hit.
        
        The two surfaces must either have the same alpha or no alpha.
        """

        convert_and_call(_renpy.pixellate,
                         src, dst,
                         avgwidth, avgheight,
                         outwidth, outheight)

    
    def scale(s, size):
        """
        Scales down the supplied pygame surface by the given X and Y
        factors.

        Always works, but may not be high quality.
        """

        width, height = s.get_size()

        dx, dy = size

        if s.get_flags() & SRCALPHA:
            d = pygame.Surface((dx, dy), SRCALPHA)
        else:
            d = pygame.Surface((dx, dy), 0)

        pixellate(s, d, width / dx, height / dy, 1, 1)

        return d

else:

    can_pixellate = False

    def scale(s, size):

        return pygame.transform.scale(s, size)

# def slow_endian_order(shifts, masks, r, g, b, a):

#     has_alpha = masks[3]

#     if not has_alpha:

#         l = zip(shifts, (r, g, b))
#         l.sort()

#         if sys.byteorder == 'big':
#             l.reverse()

#         return [ j for i, j in l] + [ a ]

    
#     l = zip(shifts, (r, g, b, a))
#     l.sort()

#     if sys.byteorder == 'big':
#         l.reverse()

#     return [ j for i, j in l]

    
# endian_order_cache = { }


# def endian_order(src, r, g, b, a):
#     """
#     Returns the four arguments, in endian-order.
#     """

#     shifts = src.get_shifts()

#     try:
#         func = endian_order_cache[shifts]

#     except KeyError:
#         masks = src.get_masks()
#         order = slow_endian_order(shifts, masks, 'r', 'g', 'b', 'a')
#         func = eval( "lambda r, g, b, a : (" + ", ".join(order) + ")")
#         endian_order_cache[shifts] = func

#     return func(r, g, b, a)
        

if version >= 4008005:

    can_map = True

    def map(src, dst, rmap, gmap, bmap, amap):
        """
        This maps the colors between two surfaces. The various map
        parameters must be 256 character long strings, with the value
        of a character at a given offset being what a particular pixel
        component value is mapped to.
        """

        convert_and_call(_renpy.map,
                         src, dst,
                         *endian_order(dst, rmap, gmap, bmap, amap))


else:

    can_map = False


# Okay, what we have here are a pair of tables mapping masks to byte offsets
# for 24 and 32 bpp modes. We represent 0xff000000 as positive and negative
# numbers so that it doesn't yield a warning, and so that it works on
# 32 and 64 bit platforms.
if sys.byteorder == 'big':
    bo24 = { 255 : 2, 65280 : 1, 16711680 : 0, }
    bo32 = { 255 : 3, 65280 : 2, 16711680 : 1, 4278190080 : 0, -16777216 : 0, }
else:
    bo24 = { 255 : 0, 65280 : 1, 16711680 : 2, }
    bo32 = { 255 : 0, 65280 : 1, 16711680 : 2, 4278190080 : 3, -16777216 : 3, }


def byte_offset(src):
    """
    Given the surface src, returns a 4-tuple giving the byte offsets
    for the red, green, blue, and alpha components of the pixels in
    the surface. If a component doesn't exist, None is returned.
    """

    if src.get_bytesize() == 3:
        bo = bo24
    else:
        bo = bo32

    return [ bo.get(i, None) for i in src.get_masks() ]



if version >= 4008007:

    can_munge = True

    def alpha_munge(src, dst, amap):
        """
        This samples the red channel from src, maps it through amap, and
        place it into the alpha channel of amap.
        """

        if src.get_size() != dst.get_size():
            return

        red = byte_offset(src)[0]
        alpha = byte_offset(dst)[3]

        if red is not None and alpha is not None:
            _renpy.alpha_munge(src, dst, red, alpha, amap)        

else:

    can_munge = False

    def alpha_munge(src, dst, amap):
        return
