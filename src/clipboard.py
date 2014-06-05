# -*- coding: utf-8 -*-
import os
import process


class Clipboard(object):
    """
    Clipboard class
    ===============
    """
    @classmethod
    def get_clipboard(cls):
        if 'Darwin' in os.uname(): return MacClipboard()
        raise Exception('Not Supported Error')

    def _read_clipboard(self):
        raise NotImplementedError()

    def _write_clipboard(self, value):
        raise NotImplementedError()

    def read(self):
        return self._read_clipboard()

    def write(self, value):
        self._write_clipboard(value)


class MacClipboard(Clipboard):
    """
    Clipboard class for Mac
    ========================
    * pbcopy and pbpaste are required.
    """
    def _read_clipboard(self):
        return process.execute('pbpaste')[0]

    def _write_clipboard(self, value):
        process.execute('pbcopy', process_input=value)

