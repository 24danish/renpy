#!/usr/bin/env python


import distutils.core
import os
import os.path
import platform
import sys

try:
    import bdist_mpkg
except:
    pass

# This environment variable should have the full path to the installed
# Ren'Py dependencies.
install = os.environ.get("RENPY_DEPS_INSTALL", "/home/tom/ab/deps/install")

# Check to see if that's the case.
if not os.path.isdir(install):
    print "The Ren'Py dependencies install directory:"
    print
    print install
    print
    print "does not exist. Please set RENPY_DEPS_INSTALL to the correct"
    print "location of the Ren'Py dependencies install directory, and "
    print "re-run this script."
    sys.exit(-1)

# Default compile arguements for everybody.
include_dirs = [ install + "/include", install + "/include/SDL" ]
library_dirs = [ install + "/lib" ]
extra_compile_args = [ "-O3" ]
extra_link_args = [ ]
sdl_libraries = [ 'SDL' ]
sound_libraries = [ 'SDL_sound', 'smpeg', 'vorbisfile', 'vorbis', 'ogg', 'modplug', 'speex', 'stdc++', ]

# The following turn on optional modules.
nativemidi = None
winmixer = None
linmixer = None

# Detect win32.
if platform.win32_ver()[0]:
    nativemidi = [ 'nativemidi.c', 'native_midi_win32.c', 'native_midi_common.c', 'rwobject.c' ]
    nativemidi_libs = [ 'winmm', 'SDL' ]
    winmixer = True

# Detect mac.
if platform.mac_ver()[0]:
    nativemidi = [ 'nativemidi.c', 'native_midi_mac.c', 'native_midi_common.c', 'rwobject.c' ]
    nativemidi_libs = [ 'SDL' ]

# Detect OSS.
try:
    import ossaudiodev
    linmixer = True
except:
    pass

extensions = [ ]
py_modules = [ ]

rpe = distutils.core.Extension(
    "_renpy",
    [ "core.c", "_renpy.c" ],
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    libraries=sdl_libraries,
    )

extensions.append(rpe)

psse = distutils.core.Extension(
    "pysdlsound",
    [ "pss.c", "rwobject.c", "pysdlsound.c" ],
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    libraries=sound_libraries + sdl_libraries,
    )

extensions.append(psse)

if nativemidi:
    nme = distutils.core.Extension(
        "nativemidi",
        nativemidi,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        extra_compile_args=extra_compile_args,
        libraries=nativemidi_libs,
        extra_link_args=extra_link_args,
        )

    extensions.append(nme)

if winmixer:
    wme = distutils.core.Extension(
        "winmixer",
        [ 'winmixer.c' ],
        libraries=['winmm'],
        )

    extensions.append(wme)

if linmixer:
    py_modules.append('linmixer')

distutils.core.setup(
    name = "renpy_module",
    version = "5.4.1",
    ext_modules = extensions,
    py_modules = py_modules,
    )

