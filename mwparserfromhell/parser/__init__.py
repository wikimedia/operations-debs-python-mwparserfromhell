# -*- coding: utf-8  -*-
#
# Copyright (C) 2012-2014 Ben Kurtovic <ben.kurtovic@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This package contains the actual wikicode parser, split up into two main
modules: the :py:mod:`~.tokenizer` and the :py:mod:`~.builder`. This module
joins them together under one interface.
"""

class ParserError(Exception):
    """Exception raised when an internal error occurs while parsing.

    This does not mean that the wikicode was invalid, because invalid markup
    should still be parsed correctly. This means that the parser caught itself
    with an impossible internal state and is bailing out before other problems
    can happen. Its appearance indicates a bug.
    """
    def __init__(self, extra):
        msg = "This is a bug and should be reported. Info: {0}.".format(extra)
        super(ParserError, self).__init__(msg)


from .builder import Builder
from .tokenizer import Tokenizer
try:
    from ._tokenizer import CTokenizer
    use_c = True
except ImportError:
    CTokenizer = None
    use_c = False

__all__ = ["use_c", "Parser", "ParserError"]

class Parser(object):
    """Represents a parser for wikicode.

    Actual parsing is a two-step process: first, the text is split up into a
    series of tokens by the :py:class:`.Tokenizer`, and then the tokens are
    converted into trees of :py:class:`.Wikicode` objects and
    :py:class:`.Node`\ s by the :py:class:`.Builder`.

    Instances of this class or its dependents (:py:class:`.Tokenizer` and
    :py:class:`.Builder`) should not be shared between threads.
    :py:meth:`parse` can be called multiple times as long as it is not done
    concurrently. In general, there is no need to do this because parsing
    should be done through :py:func:`mwparserfromhell.parse`, which creates a
    new :py:class:`.Parser` object as necessary.
    """

    def __init__(self):
        if use_c and CTokenizer:
            self._tokenizer = CTokenizer()
        else:
            self._tokenizer = Tokenizer()
        self._builder = Builder()

    def parse(self, text, context=0, skip_style_tags=False):
        """Parse *text*, returning a :py:class:`~.Wikicode` object tree.

        If given, *context* will be passed as a starting context to the parser.
        This is helpful when this function is used inside node attribute
        setters. For example, :py:class:`~.ExternalLink`\ 's
        :py:attr:`~.ExternalLink.url` setter sets *context* to
        :py:mod:`contexts.EXT_LINK_URI <.contexts>` to prevent the URL itself
        from becoming an :py:class:`~.ExternalLink`.

        If *skip_style_tags* is ``True``, then ``''`` and ``'''`` will not be
        parsed, but instead will be treated as plain text.

        If there is an internal error while parsing, :py:exc:`.ParserError`
        will be raised.
        """
        tokens = self._tokenizer.tokenize(text, context, skip_style_tags)
        code = self._builder.build(tokens)
        return code
