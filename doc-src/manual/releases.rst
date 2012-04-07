
Release History
===============


Summary
-------

==========  =======  ===========
Date        Version  Description
==========  =======  ===========
2009-01-29  1.0b1    Fighting with setuptools etc.
----------  -------  -----------
2009-01-29  1.0b2    Now with source, documentation and inline licence.
----------  -------  -----------
2009-01-30  1.0b3    Fixed version number confusion (was 0.1bx in some places).
----------  -------  -----------
2009-01-31  1.0rc1   With support.
----------  -------  -----------
2009-02-04  1.0      No significant changes from rc1.
----------  -------  -----------
2009-02-23  2.0b1    New trampolining core; matcher graph rewriting; memoisation.
----------  -------  -----------
2009-03-04  2.0b2    Fixed major bug in LMemo for 2.6; general tidying.
----------  -------  -----------
2009-03-05  2.0      Improved documentation.
----------  -------  -----------
2009-03-05  2.0.1    Fixed stupid bug introduced at last minute in 2.0.
----------  -------  -----------
2009-03-06  2.0.2    A few more small bug fixes.
----------  -------  -----------
2009-03-08  2.1b     Improved efficiency.
----------  -------  -----------
2009-03-08  2.1      Minor bugfixes and documentation.
----------  -------  -----------
2009-03-12  2.1.1    Fix flatten() and compose_transforms(); remove GeneratorManager from default configuration.
----------  -------  -----------
2009-03-27  2.2      Added >=, String(), regexp framework.
----------  -------  -----------
2009-04-05  2.3      Compilation to regular expressions.
----------  -------  -----------
2009-04-05  2.3.1    Fix regexp packaging.
----------  -------  -----------
2009-04-05  2.3.2    Fix regexp packaging.
----------  -------  -----------
2009-04-28  2.3.3    Fix regexp packaging.
----------  -------  -----------
2009-04-28  2.3.4    Fix regexp packaging.
----------  -------  -----------
2009-04-28  2.3.5    Make all classes new style in 2.6.
----------  -------  -----------
2009-05-02  2.4      Added lexer.
----------  -------  -----------
2009-06-27  3.0a1    New tutorial; bin package; modified Nodes, `*args` (general clean-up of API).
----------  -------  -----------
2009-07-04  3.0a2    Various small fixes via pylint.
----------  -------  -----------
2009-07-07  3.0b1    Smart separators.
----------  -------  -----------
2009-07-07  3.0b2    Fix packaging issues with b1.
----------  -------  -----------
2009-07-16  3.0b3    More packaging issues (switched to distutils; bundling tests and examples).
----------  -------  -----------
2009-07-16  3.0      New tutorial; bin package; smart separators; modified Nodes, `*args` (general clean-up of API).
----------  -------  -----------
2009-08-19  3.1      Rewritten streams.
----------  -------  -----------
2009-09-05  3.2      Clone bugfix.
----------  -------  -----------
2009-09-09  3.2.1    Clone bugfix bugfix.
----------  -------  -----------
2009-09-13  3.3b1    Whitespace sensitive parsing (no documentation).
----------  -------  -----------
2009-09-23  3.3      Whitespace sensitive parsing.
----------  -------  -----------
2009-11-22  3.3.1    Regexp bugfixes.
----------  -------  -----------
2009-11-22  3.3.2    Regexp bugfixes (correct self-test).
----------  -------  -----------
2009-12-10  3.3.3    Various small tweaks based on user feedback.
----------  -------  -----------
2010-04-03  4.0b1    Broad revision, simplification.
----------  -------  -----------
2010-04-16  4.0      Broad revision, simplification.
----------  -------  -----------
2010-04-18  4.0.1    Small bugfix for left-recursive, whitespace sensitive grammars (hash).
----------  -------  -----------
2010-04-18  4.0.2    Small bugfix for left-recursive, whitespace sensitive grammars (equality).
----------  -------  -----------
2010-04-20  4.0.3    Small bugfix for kargs of user-defined matchers; dropped Python 3 specific test.
----------  -------  -----------
2010-04-24  4.1      Major bugfix related to coercion of matcher arguments.
----------  -------  -----------
2010-05-02  4.2      RFC 3696 validation; better regexp rewriting.
----------  -------  -----------
2010-05-02  4.2.1    Small bugfix for top level DNS names that start with a digit.
----------  -------  -----------
2010-05-20  4.2.2    Small bugfix in regexp rewriting.
----------  -------  -----------
2010-05-31  4.2.3    Extra offside example; improved handling of regexps in tokens.
----------  -------  -----------
2010-06-10  4.3      Simplified line aware parsing.
----------  -------  -----------
2010-06-11  4.3.1    Small bugfix to support SOL and EOL.
----------  -------  -----------
2010-06-11  4.3.2    Small bugfix to support Python 2.7.
----------  -------  -----------
2010-10-12  4.3.3    Bugfixes for offside handling of errors.
----------  -------  -----------
2010-11-28  4.3.4    Small bugfix for printing empty List.
----------  -------  -----------
2011-01-25  4.3.5    Bugfix for NFA regexps with multiple choices;
                     add ``Rational()`` matchers.
----------  -------  -----------
2011-01-30  4.4      Rename `Float() <api/redirect.html#lepl.support.warn.Float>`_, `Real() <api/redirect.html#lepl.matchers.derived.Real>`_; add `Limit() <api/redirect.html#lepl.matchers.combine.Limit>`_.
----------  -------  -----------
2011-03-20  5.0      Rewrite of streams and related functionality.  Simplified core code.
----------  -------  -----------
2012-01-08  5.0.1    Tokens + iterables bugfix.
----------  -------  -----------
2012-03-17  5.0.2    Made String() more string-specific.
----------  -------  -----------
2012-03-18  5.1      Add Reduce() (makes String() more general again).
----------  -------  -----------
2012-04-07  5.1.1    Added lepl.core.dynamic.IntVar.
==========  =======  ===========

5.1
---

The addition of `Reduce` simplified `String` and resolved some long-standing
issues about empty sequences.

5.0
---

See :ref:`lepl5`.

Stream handling and line--aware parsing were simplified.  Resource management
was improved.

.. release_4_4:

4.4
---

The `Float() <api/redirect.html#lepl.support.warn.Float>`_ matcher now excludes integers.  For the old behaviour, which
included them, use `Real() <api/redirect.html#lepl.matchers.derived.Real>`_.  More control over search has been added with
`Limit() <api/redirect.html#lepl.matchers.combine.Limit>`_.


.. release_4_3:

4.3, 4.3.5
----------

After user feedback the line-aware (but not offside) parsing was simplified
slightly.  ``Eol()`` was changed to ``LineAwareEol()``, a similar matcher for
start of line was added, and rewriting of matchers inside tokens was improved.

The bug fixed in 4.3.5 may have affected some complex character-set matches
(like floating point numbers).  It is unlikely to have been common, since
regular expression compilation is restricted to "leaf" matchers, which are not
normally so complex.


.. release_4_2:

4.2, 4.2.3
----------

Includes a new module for validating email addresses and URLs according to
:ref:`rfc3696`.  Rewriting to regular expressions has also been improved.

.. release_4_0:

4.0, 4.1
--------

See :ref:`lepl4`.

4.1 addresses a significant error which could cause problems during
optimisation of the parser (even with the default configuration).


.. release_3_3:

3.3, 3.3.3
----------

This supports :ref:`line--aware <offside>` parsing.  3.3.3 includes various
small improvements based on user-feedback.


.. release_3_2:

3.2, 3.2.1
----------

A bugfix release to correct a problem with cloning matchers.  3.2 is a minor
release (rather than a 3.1.1 bugfix release) because it also includes
significant internal changes as I work towards supporting
whitespace-significant ("offside rule") parsing.


.. release_3_1:

3.1
---

A fairly small set of changes, focussed on the :ref:`streams <streams>` that
can be used to "wrap" input (instead of parsing a string or list directly).
These have a clearer design (although remain, unfortunately, complex), are
better documented, with clearer interfaces (abstract classes), and will (I
hope) support handling the "offside rule" in a later release.

.. warning::

  Although this is a minor release, some of the "public" has API changed.
  These changes are generally in areas that I believe are not commonly used,
  but you should check that code still runs after upgrading.  Perhaps the most
  likely problem is that `parse_list()` has become ``parse_items()`` to emphasise
  that it is for sequences of "characters" (in contrast, for example, to parse
  a list of "lines", use ``parse_lines()``; characters
  and lines refer to whether `Any() <api/redirect.html#lepl.matchers.core.Any>`_
  should match all or part of an entity, respectively).


.. release_3_0:

3.0
---

This release is based on two quite separate themes, both of which have
required modifications to the Lepl core code to the extent that a new major
version is necessary.

First, the handling of whitespace has been revised, extended, and documented.
The preferred approach in most cases, using the :ref:`lexer`, is described in
detail in a new :ref:`tutorial <tutorial>`.  In addition, for those cases
where spaces are significant, :ref:`columns <table_example>` and two new
:ref:`"smart separators" <spaces>` have been added.

The separator work highlighted a source of confusion in the standard matchers:
many used ``&`` and ``[]``, which are modified by separators.  As a
consequence, the library was revised to remove all these uses.  Separators
should now only affect spaces in a clearly predictable way (there is a small
trade-off between usefulness and predictability; the library is now more
predictable, which is probably for the best).

The second theme is the parsing of :ref:`binary data <binary>`.  This is
somewhat obscure, but provides some fairly original functionality (with room
for significant expansion in future releases).

While writing the binary parser I needed to revisit and revise core routines
related to graphs.  Various internal interfaces have been simplified; the most
visible being the `Node() <api/redirect.html#lepl.support.node.Node>`_ class, which is now more "Pythonesque".
