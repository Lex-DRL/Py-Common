"""
The module detecting which OS type we're running on.
"""
__author__ = 'Lex Darlog (DRL)'

from sys import platform as __pf
__pf_low = __pf.lower()

IS_WINDOWS = __pf_low.startswith('win')
IS_LINUX = __pf_low.startswith('linux')
IS_FREEBSD = __pf_low.startswith('freebsd')
IS_MACOS = __pf_low.startswith('darwin')
IS_UNIX = IS_LINUX or IS_FREEBSD or IS_MACOS

__all__ = ('IS_WINDOWS', 'IS_LINUX', 'IS_FREEBSD', 'IS_MACOS', 'IS_UNIX')
