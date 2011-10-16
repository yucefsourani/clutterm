import io
import os
import pty
import sys
import fcntl
import struct
import termios
import logging
from subprocess import Popen
log = logging.getLogger('clutterm')


class Shell(object):
    shell = os.getenv('SHELL')

    def __init__(self, rows=40, cols=100, end_callback=None):
        self.rows = rows
        self.cols = cols
        self.end_callback = end_callback
        self.fork()

    def read(self):
        try:
            read = self.reader.read(65535)
        except IOError as e:
            log.info('Got an io error %r, must be the end, quitting' % e)
            if self.end_callback:
                self.end_callback()
            sys.exit(0)
        if read:
            log.info('R<%r>' % read)

        return read

    def write(self, text):
        log.info('W     <%r>' % text)
        self.writer.write(text)
        self.writer.flush()

    def fork(self):
        pid, fd = pty.fork()
        if pid == 0:
            # Child
            try:
                fd_list = [int(i) for i in os.listdir('/proc/self/fd')]
            except OSError:
                fd_list = xrange(256)
            # Close all file descriptors other than
            # stdin, stdout, and stderr (0, 1, 2)
            for i in [i for i in fd_list if i > 2]:
                try:
                    os.close(i)
                except OSError:
                    pass
            self.env = {}
            self.env["COLUMNS"] = str(self.cols)
            self.env["LINES"] = str(self.rows)
            self.env["TERM"] = "xterm"
            self.env["COLORTERM"] = "clutterm"
            self.env["SHELL"] = self.shell
            p = Popen(self.shell, env=self.env)
            p.wait()
            sys.exit(0)
        else:
            # Parent
            log.debug('pty forked pid: %d fd: %d' % (pid, fd))
            fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)

            # Set the size of the terminal window:
            s = struct.pack("HHHH", self.rows, self.cols, 0, 0)
            fcntl.ioctl(fd, termios.TIOCSWINSZ, s)

            self.fd = fd
            self.pid = pid

            self.reader = io.open(
                self.fd,
                'rt',
                buffering=1024,
                newline="",
                encoding='UTF-8',
                closefd=False,
                errors='handle_special'
            )
            self.writer = io.open(
                self.fd,
                'wt',
                buffering=1024,
                newline="",
                encoding='UTF-8',
                closefd=False
            )

            return fd