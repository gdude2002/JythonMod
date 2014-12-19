#! /usr/bin/env python

"""reverb.py - Regular Expressions VERBose v2.0

This module is a wrapper around the standard re module that allows regular
expressions to be written in a more readable manner.  It was inspired by
some messages in comp.lang.python from early July, 1998, and by Ka-Ping Yee's
rxb module (basically the same idea, built on top of the older regex module).

reverb is on the Cheeseshop:

    http://pypi.python.org/pypi/reverb/2.0
"""

import re

def _prioritize(a, b, priority):
    a = '(?:%s)' % a.text if a.priority < priority else a.text
    b = '(?:%s)' % b.text if b.priority < priority else b.text
    return a, b

class Raw(object):
    text = None      # basic Regexp
    priority = 99    # priority (controls auto-added parentheses):
                     #  0 = | (least binding)
                     #  1 = concatenation (including ^, $)
                     #  2 = repetition (*, +, ?)
                     #  99 = atomic (charsets, parentheses, etc.)
    negated = None   # negated form of Regexp, if meaningful
    nongreedy = None # nongreedy form
    charset = None   # form usable in character set, if any

    def __init__(self, text, priority, **kw):
        self.text = text
        self.priority = priority
        self.__dict__.update(kw)
        if "nongreedy" in kw:
            self.minimal = self.nongreedy
        if kw.get('charset') == 1:
            self.charset = text

    def __or__(self, right):
        return Raw(self.text + '|' + Text(right).text, 0)

    def __ror__(self, left):
        return Raw(Text(left).text + '|' + self.text, 0)

    def __add__(self, right):
        self, right = _prioritize(self, Text(right), 1)
        return Raw(self + right, 1)

    __and__ = __add__

    def __radd__(self, left):
        self, left = _prioritize(self, Text(left), 1)
        return Raw(left + self, 1)

    __rand__ = __radd__

    def __neg__(self):
        if self.negated:
            return Raw(self.negated, self.priority,
                    negated = self.text)
        raise TypeError, 'Regexp cannot be negated'

    def __sub__(self, right):
        self, right = _prioritize(self, -Text(right), 1)
        return Raw(self + right, 1)

    def __rsub__(self, left):
        self, left = _prioritize(-self, Text(left), 1)
        return Raw(left + self, 1)

def Repeated(expr, min, max = None):
    expr = Text(expr)
    expr = '(?:%s)' % expr.text if expr.priority<2 else expr.text
    if min == None:
        min = 0
    if min == 0 and max == None:
        suffix = '*'
    elif min == 1 and max == None:
        suffix = '+'
    elif min == 0 and max == 1:
        suffix = '?'
    elif max == None:
        suffix = '{%d,}' % min
    else:
        suffix = '{%d,%d}' % (min, max)
    return Raw(expr + suffix, 2, nongreedy = Raw(expr + suffix + '?', 2))

def Optional(expr, max = None):
    return Repeated(expr, 0, max)

def Required(expr, max = None):
    return Repeated(expr, 1, max)

def Maybe(expr):
    return Repeated(expr, 0, 1)

def Group(expr, name = None):
    expr = Text(expr)
    if name:
        return Raw('(?P<%s>%s)' % (name, expr.text), 99)
    else:
        return Raw('(%s)' % expr.text, 99)

def Match(name):
    return Raw('(?P=%s)' % name, 99)

def FollowedBy(expr):
    expr = Text(expr).text
    return Raw('(?=%s)' % expr, 99, negated = '(?!%s)' % expr)

def _ischar(c):
    if not isinstance(c, basestring) or len(c) != 1:
        raise TypeError, 'single character required'

class Char:
    def __init__(self, start):
        _ischar(start)
        self.start = start

    def to(self, end):
        _ischar(end)
        temp = '%c-%c' % (self.start, end)
        return Raw('[%s]' % temp, 99, negated = '[^%s]'%temp, charset = temp)

def Set(*args):
    rv = [];
    for item in args:
        if isinstance(item, Raw):
            if item.charset:
                rv.append(item.charset)
            else:
                raise TypeError, "can't be used in charset"
        elif isinstance(item, str):
            rv.append(item)
        elif isninstance(item, int):
            rv.append(chr(item))
        else:
            raise TypeError, 'unsuitable value for charset'
    rv = "".join(rv)
    return Raw('[%s]' % rv, 99, negated = '[^%s]' % rv)


def Text(text):
    if isinstance(text, Raw):
        return text
    if isinstance(text, str):
        if len(text) == 1:
            return Raw(re.escape(text), 99)
        else:
            return Raw(re.escape(text), 1)
    raise TypeError, 'unsuitable value for Regexp'

def Matched(name):
    return r'\g<%s>' % name

Alphanum    = Raw('\\w', 99, negated = '\\W', charset = 1)
Any         = Raw('.', 99)
Digit       = Raw('\\d', 99, negated = '\\D', charset = 1)
Digits      = Digit
End         = Raw('$', 99)
EndString   = Raw('\\Z', 99)
Start       = Raw('^', 99)
StartString = Raw('\\A', 99)
Whitespace  = Raw('\\s', 99, negated = '\\S', charset = 1)
Wordbreak   = Raw('\\b', 99, negated = '\\B')

# re-constants

IGNORECASE  = re.IGNORECASE
LOCALE      = re.LOCALE
MULTILINE   = re.MULTILINE
DOTALL      = re.DOTALL

def Re(pat, flags = 0):
    return re.compile(Text(pat).text, flags)


