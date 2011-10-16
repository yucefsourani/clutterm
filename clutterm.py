#!/usr/bin/env python
from gi.repository import Clutter, ClutterX11
from clutterm.ui import Clutterm
from log_colorizer import make_colored_stream_handler
import logging
import sys
log = logging.getLogger('clutterm')
log.addHandler(make_colored_stream_handler())
log.setLevel(logging.DEBUG if 'debug' in sys.argv else logging.INFO)
debug = False
debugArgs = ['--clutter-debug=all', '--cogl-debug=all']

ClutterX11.set_use_argb_visual(True)

if debug:
    Clutter.init(debugArgs)
else:
    Clutter.init(sys.argv)
app = Clutterm()
app.interact()

Clutter.main()