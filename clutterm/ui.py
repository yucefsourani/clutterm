from gi.repository import Clutter
from .shell import Shell
from .shader import shaders
from .lex import lex
import logging
log = logging.getLogger('clutterm')

# Define some standard colors to make basic color assigments easier
colorWhite = Clutter.Color.new(255, 255, 255, 255)
colorRed = Clutter.Color.new(255, 0, 0, 255)
colorBlack = Clutter.Color.new(0, 0, 0, 200)


class Clutterm(object):

    def __init__(self):
        """
        Build the user interface.
        """
        self.mainStage = Clutter.Stage.new()
        self.mainStage.set_title("Clutterminal")
        self.mainStage.set_size(800, 600)
        self.mainStage.set_reactive(True)
        self.mainStage.set_use_alpha(True)
        self.mainStage.set_opacity(0)

        # Create lines layout
        self.linesBoxManager = Clutter.BoxLayout()
        self.linesBoxManager.set_vertical(True)
        self.linesBoxManager.set_homogeneous(False)
        self.linesBoxManager.set_pack_start(False)

        # Globals
        self.radix = ''
        self.line = None
        self.stay = False

        # Create the lines box
        self.linesBox = Clutter.Box.new(self.linesBoxManager)
        self.linesBox.set_color(colorBlack)
        self.mainStage.add_actor(self.linesBox)

        # Make the main window fill the entire stage
        mainGeometry = self.mainStage.get_geometry()
        self.linesBox.set_geometry(mainGeometry)

        # Present the main stage (and make sure everything is shown)
        self.mainStage.show_all()

    def interact(self):
        self.shell = Shell(end_callback=self.destroy)
        self.new_line()

        def update(read):
            self.write(self.shell.read())

        # This is so bad...
        # Really need to find a way to put a thread or an asyncore
        # Without clutter threading problems
        # Polling for now
        self.reader = Clutter.Timeline.new(10)
        self.reader.set_loop(True)
        self.reader.connect('completed', update)
        self.reader.start()

        # Setup some key bindings on the main stage
        self.mainStage.connect_after("key-press-event", self.onKeyPress)

    def write(self, text):
        if text == '':
            return

        text = ''.join((self.radix, text))
        remaining = text
        self.radix = remaining
        while remaining:
            string, remaining = lex(remaining, self.shell.cols, self.set_title)
            self.set_line(''.join(string))
            if remaining is not None:
                self.radix = remaining
                self.new_line()

        # text = re.sub(csi_char_attr, '', text)

        # text = re.sub(csi_useless, '', text)
        # osc_match = osc.search(text)
        # text = re.sub(osc, '', text)

    def set_title(self, text):
        self.mainStage.set_title(text)

    def set_line(self, text):
        log.debug("D %r" % text)
        self.line.set_markup('<span>%s</span>' % text)

    def new_line(self):
        children = Clutter.Container.get_children(self.linesBox)
        if len(children) > self.shell.rows:
            children[0].destroy()

        self.line = Clutter.Text()
        self.line.set_font_name("Mono 10")
        self.line.set_color(colorWhite)
        self.linesBoxManager.set_alignment(self.line, 0, 0)
        self.linesBox.add_actor(self.line)

    def destroy(self):
        Clutter.main_quit()

    def onKeyPress(self, actor=None, event=None, data=None):
        """
        Basic key binding handler
        """
        uval = event.key.unicode_value
        kval = event.key.keyval
        log.debug('u %r v %d' % (uval, kval))

        if uval != '':
            self.shell.write(uval)
        else:
            if kval in shaders:
                shaders[kval](self.linesBox)