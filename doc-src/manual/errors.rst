
.. _errors:

Error Reporting
===============


.. index:: errors

Introduction
------------

In some applications it is important not only to parse correctly structured
input, but also to give a helpful responses when the input is incorrectly
structured.

Lepl provides support for reporting errors in the input in three ways.

1. By checking when the entire input was consumed and, if not, reporting on
   the location of deepest match.

2. By allowing a matcher to directly raise an exception.

3. By creating a parse tree with nodes that represent errors; these error
   nodes can then be used, later, to raise exceptions.

The first approach is often the best compromise and is used by default (see
``.config.full_first_match()``,
:ref:`configuration <configuration>`).  However, it is limited to a single
match and gives little information about the underlying problem.

The second approach is simple, but doesn't play well with backtracking.

The third approach is probably best for more complex situations, but remains
relatively unexplored.  It may not scale well, for example.

.. index:: ^, make_error(), **, sexpr_throw(), node_throw(), Error()

Example
-------

Here is an example of the second and third approaches in use::

  >>> from lepl import *

  >>> class Term(List): pass
  >>> class Factor(List): pass
  >>> class Expression(List): pass

  >>> expr    = Delayed()
  >>> number  = Digit()[1:,...]
  >>> badChar = AnyBut(Space() | Digit() | '(')[1:,...]

  >>> with DroppedSpace():

  >>>     unopen   = number ** make_error('no ( before {out_rest!s}') & ')'
  >>>     unclosed = ('(' & expr & Eos()) ** make_error('no ) for {in_rest!s}')

  >>>     term    = Or(
  >>>                  (number | '(' & expr & ')')      > Term,
  >>>                  badChar                          ^ 'unexpected text: {results[0]}',
  >>>                  unopen,
  >>>                  unclosed
  >>>                  )
  >>>     muldiv  = Any('*/')
  >>>     factor  = (term & (muldiv & term)[:])         > Factor
  >>>     addsub  = Any('+-')
  >>>     expr   += (factor & (addsub & factor)[:])     > Expression
  >>>     line    = (Empty() & expr & Eos())            >> sexpr_throw

  >>> parser = line.get_parse()

  >>> parser('1 + 2 * (3 + 4 - 5')[0]
  [...]
    File "<string>", line 1
      1 + 2 * (3 + 4 - 5
	      ^
  lepl.matchers.error.Error: no ) for '(3 + 4 - 5'

  >>> parser('1 + 2 * 3 + 4 - 5)')[0]
    File "<string>", line 1
      1 + 2 * 3 + 4 - 5)
		      ^
  lepl.matchers.error.Error: no ( before ')'

  >>> parser('1 + 2 * (3 + four - 5)')[0]
    File "<string>", line 1
      1 + 2 * (3 + four - 5)
		   ^
  lepl.matchers.error.Error: unexpected text: four

  >>> parser('1 + 2 ** (3 + 4 - 5)')[0]
    File "<string>", line 1
      1 + 2 ** (3 + 4 - 5)
	     ^
  lepl.matchers.error.Error: unexpected text: *


.. note::

  This example follows the :ref:`applycase` and :ref:`complexor` patterns.

  Also, the parentheses around expressions that are sent to ``>>`` are
  critical.

.. index:: ^, Error(), SyntaxError()

Operators, Functions and Classes
--------------------------------

=============================================================================  ========  ========
Name                                                                           Type      Action
=============================================================================  ========  ========
``^``                                                                          Operator  Raises an exception, given a format string.  Formatting has the same named parameters as the ``KApply()`` matcher (results, stream_in, stream_out); implemented as KApply(``raise_error``)
-----------------------------------------------------------------------------  --------  --------
``raise_error()``           Function  See above.
-----------------------------------------------------------------------------  --------  --------
``Error()``                       Class     Creates a parse tree node that can be used to trigger a later exception (``Error`` is a subclass of both ``Node`` and ``SyntaxError``).
-----------------------------------------------------------------------------  --------  --------
``sexpr_throw()``             Function  Walks a ``List()``--based parse tree and raises the first ``Error`` found.
-----------------------------------------------------------------------------  --------  --------
``node_throw()``               Function  Walks a ``Node()``--based parse tree and raises the first ``Error`` found.
-----------------------------------------------------------------------------  --------  --------
``make_error()``             Function  Creates an ``Error`` node, given a format string.
=============================================================================  ========  ========
