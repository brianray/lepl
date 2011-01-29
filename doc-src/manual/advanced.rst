
Advanced Use
============

.. index:: configuration, .config
.. _configuration:

Configuration
-------------

Configuration for Lepl 4 has been completely revised.  Instead of using a
separate configuration object, a ``.config`` attribute on the matcher is used.
This means that you can explore the available options at the Python prompt
(and perhaps via some IDEs).

For example::

  >>> dir(matcher.config)
  [... 'add_monitor', 'add_rewriter', 'alphabet', 'auto_memoize', 'blocks', 
  'changed', 'clear', 'compile_to_dfa', 'compile_to_nfa', ...]
  >>> help(matcher.config.compile_to_dfa)
  Help on method compile_to_dfa in module lepl.core.config:
  compile_to_dfa(self, force=False, alphabet=None) method of lepl.core.config.ConfigBuilder instance
      Compile simple matchers to DFA regular expressions.  This improves
      efficiency but may change the parser semantics slightly (DFA regular
      expressions do not provide backtracking / alternative matches).

Also, note that configuration methods can be chained together, making
configuration code more compact::

  >>> matcher.config.clear().lexer()

The various options available are described in the following sections.  In
addition, :ref:`this example <config_example>` shows the effect of different
options on parsing times.

.. index:: default(), clear(), default_line_aware()

Common, Packaged Actions
~~~~~~~~~~~~~~~~~~~~~~~~

`.config.default() <api/redirect.html#lepl.core.config.ConfigBuilder.default>`_

  This sets the default configuration.  It is not needed when first using a
  matcher, but can be useful to "reset" a matcher to the default state.

  The default configuration is now (since Lepl 4) close to optimal; for many
  parsers no additional configuration is necessary.

`.config.clear() <api/redirect.html#lepl.core.config.ConfigBuilder.clear>`_

  This empties the current configuration (for example, removing the default
  settings).  If this is *not* used then any alterations are *relative* to the
  default settings.

`.config.default_line_aware() <api/redirect.html#lepl.core.config.ConfigBuilder.default_line_aware>`_

  This sets the default configuration when using line aware (block indented;
  offside rule) parsing.  See :ref:`offside`.

.. index:: lexer(), line_aware(), blocks()

Other Packaged Actions
~~~~~~~~~~~~~~~~~~~~~~

`.config.lexer() <api/redirect.html#lepl.core.config.ConfigBuilder.lexer>`_ `.config.no_lexer() <api/redirect.html#lepl.core.config.ConfigBuilder.no_lexer>`_

  Detect the use of `Token()` and modify the parser to use the
  lexer. Typically this is called indirectly via `.config.default()
  <api/redirect.html#lepl.core.config.ConfigBuilder.default>`_ (above).

`.config.line_aware() <api/redirect.html#lepl.core.config.ConfigBuilder.line_aware>`_

  Enable line aware parsing.  Typically this is called indirectly by
  `.config.default_line_aware()
  <api/redirect.html#lepl.core.config.ConfigBuilder.default_line_aware>`_
  (above).

`.config.blocks() <api/redirect.html#lepl.core.config.ConfigBuilder.blocks>`_

  Enable offisde rule parsing.  Typically this is called indirectly by setting
  ``block_policy`` or ``block_start`` on `.config.default_line_aware()
  <api/redirect.html#lepl.core.config.ConfigBuilder.default_line_aware>`_
  (above).

.. index:: full_first_match(), no_full_first_match(), trace(), record_deepest()

Debug Actions
~~~~~~~~~~~~~

`.config.full_first_match()
<api/redirect.html#lepl.core.config.ConfigBuilder.full_first_match>`_
`.config.no_full_first_match()
<api/redirect.html#lepl.core.config.ConfigBuilder.no_full_first_match>`_

  Enable or disable the automatic generation of an error if the first match
  fails.

`.config.trace() <api/redirect.html#lepl.core.config.ConfigBuilder.trace>`_

  Add a monitor to trace results.  See `TraceResults() <api/redirect.html#lepl.core.trace.TraceResults>`_.  Removed by
  `.config.remove_all_monitors()
  <api/redirect.html#lepl.core.config.ConfigBuilder.remove_all_monitors>`_ or
  `.config.clear() <api/redirect.html#lepl.core.config.ConfigBuilder.clear>`_.

`.config.record_deepest()
<api/redirect.html#lepl.core.config.ConfigBuilder.record_deepest>`_

  Add a monitor to record deepest match.  See `RecordDeepest() <api/redirect.html#lepl.core.trace.RecordDeepest>`_. Removed by
  `.config.remove_all_monitors()
  <api/redirect.html#lepl.core.config.ConfigBuilder.remove_all_monitors>`_ or
  `.config.clear() <api/redirect.html#lepl.core.config.ConfigBuilder.clear>`_.

.. index:: flatten(), no_flatten(), compile_to_dfa(), compile_to_nfa(), compile_to_re(), no_compile_to_regexp(), optimize_or(), no_optimize_or(), direct_eval(), no_direct_eval(), compose_transforms(), no_compose_transforms(), auto_memoize(), left_memoize(), right_memoize(), no_memoize(), manage()
    
Optimisation Actions
~~~~~~~~~~~~~~~~~~~~

`.config.flatten()
<api/redirect.html#lepl.core.config.ConfigBuilder.flatten>`_
`.config.no_flatten()
<api/redirect.html#lepl.core.config.ConfigBuilder.no_flatten>`_

  Combined nested `And() <api/redirect.html#lepl.matchers.combine.And>`_ and
  `Or() <api/redirect.html#lepl.matchers.combine.Or>`_ matchers.

  Nested matchers typically occur because each ``&`` and ``|`` operator
  generates a new matcher, so a sequence of matchers separated by ``&``, for
  example, generates several `And()
  <api/redirect.html#lepl.matchers.combine.And>`_ functions.  This rewriter
  moves them into a single matcher, as might be expected from reading the
  grammar.  This should not change the "meaning" of the grammar or the results
  returned.

`.config.compile_to_dfa()
<api/redirect.html#lepl.core.config.ConfigBuilder.compile_to_dfa>`_
`.config.compile_to_nfa()
<api/redirect.html#lepl.core.config.ConfigBuilder.compile_to_nfa>`_
`.config.compile_to_re()
<api/redirect.html#lepl.core.config.ConfigBuilder.compile_to_re>`_
`.config.no_compile_to_regexp()
<api/redirect.html#lepl.core.config.ConfigBuilder.no_compile_to_regexp>`_

  Compile simple matches to regular expressions.

  There are various restrictions about which matchers can be translated to
  regular expressions.  The most important are that regular expressions cannot
  include recursive loops or transformations.  So rewriting of regular
  expressions is typically restricted to those parts of the parser that
  recognise individual words.

  .. warning::

     `.config.compile_to_re()
     <api/redirect.html#lepl.core.config.ConfigBuilder.compile_to_re>`_ uses
     the Python `re` library, which cannot handle streams of data in the same
     way as Lepl.  This means that matching using that library is restricted
     to single lines of text, and this option should only be used in very
     special circumstances (typically when the input is guaranteed to be only
     a single line of text).

`.config.optimize_or()
<api/redirect.html#lepl.core.config.ConfigBuilder.optimize_or>`_
`.config.no_optimize_or()
<api/redirect.html#lepl.core.config.ConfigBuilder.no_optimize_or>`_

  Rearrange arguments to `Or() <api/redirect.html#lepl.matchers.combine.Or>`_
  so that left-recursive matchers are tested last.  This improves efficiency,
  but may alter the parser semantics (the ordering of multiple results with
  ambiguous grammars may change).

  The ``conservative`` parameter supplied to this rewriter indicates how
  left--recursive rules are detected.  If true, all recursive paths are
  assumed to be left recursive.  If false then only those matchers that are in
  the left--most position of multiple arguments are used (except for `Or()
  <api/redirect.html#lepl.matchers.combine.Or>`_).

`.config.direct_eval()
<api/redirect.html#lepl.core.config.ConfigBuilder.direct_eval>`_
`.config.no_direct_eval()
<api/redirect.html#lepl.core.config.ConfigBuilder.no_direct_eval>`_

  Combine simple matchers so that they are evaluated without trampolining.

`.config.compose_transforms()
<api/redirect.html#lepl.core.config.ConfigBuilder.compose_transforms>`_
`.config.no_compose_transforms()
<api/redirect.html#lepl.core.config.ConfigBuilder.no_compose_transforms>`_

  Combine transforms (functions applied to results) with matchers.
        
  The `Transform() <api/redirect.html#lepl.functions.Transform>`_ matcher is
  the "workhorse" that underlies `Apply()
  <api/redirect.html#lepl.matchers.derived.Apply>`_, ``>``, etc.  It changes
  the results returned by other functions.

  Because transforms are not involved in the work of matching --- they just
  modify the final results --- the effects of adjacent instances can be
  combined into a single operation.  In some cases they can also be merged
  into the operation of another matcher.  This is done by the
  `compose_transforms <api/redirect.html#lepl.rewriters.compose_transforms>`_
  rewriter.

  These operations should not change the "meaning" of the grammar or the
  results returned, but should improve performance by reducing the amount of
  :ref:`trampolining` made by the parser.

`.config.auto_memoize()
<api/redirect.html#lepl.core.config.ConfigBuilder.auto_memoize>`_
`.config.left_memoize()
<api/redirect.html#lepl.core.config.ConfigBuilder.left_memoize>`_
`.config.right_memoize()
<api/redirect.html#lepl.core.config.ConfigBuilder.right_memoize>`_
`.config.no_memoize()
<api/redirect.html#lepl.core.config.ConfigBuilder.no_memoize>`_

  Remember previous inputs and results for matchers so that work is not
  repeated.  See :ref:`memoisation`.

`.config.manage() <api/redirect.html#lepl.core.config.ConfigBuilder.manage>`_

  Add a monitor to manage resources.  See ``GeneratorManager()``. Removed by
  `.config.remove_all_monitors()
  <api/redirect.html#lepl.core.config.ConfigBuilder.remove_all_monitors>`_ or
  `.config.clear() <api/redirect.html#lepl.core.config.ConfigBuilder.clear>`_.

.. index:: add_rewriter(), remove_rewriter(), remove_all_rewriters(), add_monitor(), remove_all_monitors(), stream_factory(), alphabet()

Low Level Actions
~~~~~~~~~~~~~~~~~

These methods are used internally.  They may also be useful if you are
developing a completely new functionality that is not supported by the "higher
level" actions described above.

`.config.add_rewriter()
<api/redirect.html#lepl.core.config.ConfigBuilder.add_rewriter>`_
`.config.remove_rewriter()
<api/redirect.html#lepl.core.config.ConfigBuilder.remove_rewriter>`_
`.config.remove_all_rewriters()
<api/redirect.html#lepl.core.config.ConfigBuilder.remove_all_rewriters>`_

  Add or remove a rewriter, or remove all rewriters (possibly of a given
  type).  Rewriters manipulate the matchers before the parser is used.  This
  allows Lepl to use some of the techniques that make "compiled" parsers more
  efficient --- but it can also introduce quite subtle errors.  The addition
  of user--defined rewriters is not encouraged unless you are *very* familiar
  with Lepl.

`.config.add_monitor()
<api/redirect.html#lepl.core.config.ConfigBuilder.add_monitor>`_
`.config.remove_all_monitors()
<api/redirect.html#lepl.core.config.ConfigBuilder.remove_all_monitors>`_

  Add a monitor, or remove all monitors.  Monitors implement a callback
  interface that receives information about how Lepl is working.  They can be
  used to share state across matchers, or to generate debugging information,
  for example.

`.config.stream_factory()
<api/redirect.html#lepl.core.config.ConfigBuilder.stream_factory>`_

  Set the stream factory.  This changes the class used to generate the stream
  for the parser, given some input (for example, `matcher.parse_string()
  <api/redirect.html#lepl.core.config.ParserMixin.parse_string>`_ will call
  the ``from_string()`` method on this factory, to convert the string into a
  suitable stream).

`.config.alphabet()
<api/redirect.html#lepl.core.config.ConfigBuilder.alphabet>`_

  Set the alphabet, used by rgegular expressions.  The default alphabet is
  suitable for Unicode data.

.. index:: set_arguments(), no_set_arguments(), set_alphabet_arg(), set_block_policy_arg()

Argument Actions
~~~~~~~~~~~~~~~~

Sometimes the same argument must be set on many matchers.  Rather that setting
each matcher individually, it is possible to set them all, via the
configuration.  These are used internally, to implement packaged actions;
end-users should not need to call these methods in "normal" use.

`.config.set_arguments()
<api/redirect.html#lepl.core.config.ConfigBuilder.set_arguments>`_
`.config.no_set_arguments()
<api/redirect.html#lepl.core.config.ConfigBuilder.no_set_arguments>`_

  Set an argument, or clear all such settings.

`.config.set_alphabet_arg()
<api/redirect.html#lepl.core.config.ConfigBuilder.set_alphabet_arg>`_

  Set the ``alphabet=...`` argument.  If no value is given then the value
  given earlier to `.config.argument()
  <api/redirect.html#lepl.core.config.ConfigBuilder.argument>`_ (or, if no
  value was given, the default Unicode alphabet) is used.

`.config.set_block_policy_arg()
<api/redirect.html#lepl.core.config.ConfigBuilder.set_block_policy_arg>`_

  Set the block policy on all ``Block()`` instances.

.. index:: search, backtracking
.. _backtracking:

Search and Backtracking
-----------------------

Since Lepl supports full backtracking via generators it is possible to request
all the alternative parses for a given input::

  >>> from lepl import *

  >>> any = Any()[:,...]
  >>> split = any & any & Eos()
  >>> match = split.match_string()

  >>> [pair[0] for pair in match('****')]
  [['****'], ['***', '*'], ['**', '**'], ['*', '***'], ['****']]

This shows that successive parses match less of the input with the first
matcher, indicating that the matching is *greedy*.

*Non-greedy* (generous?) matching is achieved by specifying an array slice
increment of ``'b'`` (or `BREADTH_FIRST
<api/redirect.html#lepl.matchers.operators.BREADTH_FIRST>`_)::

  >>> any = Any()[::'b',...]
  >>> split = any & any & Eos()
  >>> match = split.match_string()

  >>> [pair for (pair, stream) in match('****')]
  [['****'], ['*', '***'], ['**', '**'], ['***', '*'], ['****']]

The greedy and non--greedy repetitions are implemented by depth (default,
``'d'``, or `DEPTH_FIRST
<api/redirect.html#lepl.matchers.operators.DEPTH_FIRST>`_), and breadth--first
searches (``'b'`` or `BREADTH_FIRST
<api/redirect.html#lepl.matchers.operators.BREADTH_FIRST>`_), respectively.

In addition, by specifying a slice increment of ``'g'`` (`GREEDY
<api/redirect.html#lepl.matchers.operators.GREEDY>`_), you can request a
*guaranteed greedy* match.  This evaluates all possibilities, before returning
them in reverse length order.  Typically this will be identical to
depth--first search, but it is possible for backtracking to produce a longer
match in complex cases --- this final option, by evaluating all cases,
re--orders the results as necessary.

Specifying ``'n'`` (`NON_GREEDY
<api/redirect.html#lepl.matchers.operators.NON_GREEDY>`_) gets the reverse
ordering.

The tree implicit in the descriptions "breadth--first" and "depth--first" is
not the AST, nor the tree of matchers, but a tree based on matchers and
streams.  In the case of a single, repeated, match this is easy to visualise:
at any particular node the child nodes are generated by applying the matcher
to the various streams returned by the current match (none if this is a final
node, one for a simple match, several if the matcher backtracks).

So far so good.  Unfortunately the process is more complicated for `And()
<api/redirect.html#lepl.matchers.combine.And>`_ and `Or()
<api/redirect.html#lepl.matchers.combine.Or>`_.

In the case of `And() <api/redirect.html#lepl.matchers.combine.And>`_, the
first matcher is matched first.  The child nodes correspond to the various
(with backtracking) results of this match.  At each child node, the second
matcher is applied, generating new children.  This repeats until the scope of
the `And() <api/redirect.html#lepl.matchers.combine.And>`_ terminates at a
depth in the tree corresponding to the children of the last matcher.  Since
`And() <api/redirect.html#lepl.matchers.combine.And>`_ fails unless all
matchers match, only the final child nodes are possible results.  As a
consequence, both breadth and depth first searches would return the same
ordering.  The `And() <api/redirect.html#lepl.matchers.combine.And>`_ match is
therefore unambiguous and the implementation has no way to specify the
(essentially meaningless) choice between the two searches.

In the case of `Or() <api/redirect.html#lepl.matchers.combine.Or>`_ we must
select both the matcher and the result from the results available for that
matcher.  A natural approach is to assign the first generation of children to
the choice of matcher, and the second level to the choice of result for the
(parent) matcher.  Again, this results in no ambiguity between breadth and
depth--first results.

However, there is also an intuitively attractive argument that breadth--first
search would return the first results of the different matches, in series,
before considering backtracking.  At the moment I do not see a "natural" way
to form such a tree, and so this is not implemented.  Feedback is appreciated.

.. index:: First(), Limit()

Restricting Search
~~~~~~~~~~~~~~~~~~

Lepl's ability to backtrack is powerful, but sometimes it is inefficient.
To improve efficiency you can restrict backtracking in two ways.

First, by using `First() <api/redirect.html#lepl.matchers.combine.First>`_, you can stop search with the first matcher in a
list.  This gives results similar to `Or() <api/redirect.html#lepl.matchers.combine.Or>`_, but stops at the first
successful matcher.  It can be used in--line with the operator ``%``.

Second, by using `Limit() <api/redirect.html#lepl.matchers.combine.Limit>`_, you can restrict search within a single
matcher.  In the simplest form ``Limit(matcher)`` will take only the first match
from a matcher.  A different maximum number of matches can be specified with
the optional `count` argument.

`Limit() <api/redirect.html#lepl.matchers.combine.Limit>`_ can also be applied to repetition by specifying the count
(normally 1) as a "slice" value.  So, ``Limit(matcher)`` is equivalent to
``matcher[1:1:1]``:

  >>> list(Real().parse_all('1.2'))
  >>> list(Limit(Real()).parse_all('1.2'))
  >>> list(Real()[1:1:1].parse_all('1.2'))
  >>> list(Limit(Real(), count=2).parse_all('1.2'))
  >>> list(Real()[1:1:2].parse_all('1.2'))

.. index:: Difference()

Excluding Matches
~~~~~~~~~~~~~~~~~

Closely related to restricting search, it is possible to exclude certain
matches.  This typically does not improve efficiency (the excluded matches
have to be made anyway), but can simply the logic of a complex parser.

The `Difference() <api/redirect.html#lepl.matchers.combine.Difference>`_ matcher takes two matchers as arguments.  The first is
matched as normal, but any matches that would also have been matched by the
second matcher are excluded.

A good example, is the emulation of `Float() <api/redirect.html#lepl.matchers.derived.Float>`_ using `Real() <api/redirect.html#lepl.matchers.derived.Real>`_ and
`Integer() <api/redirect.html#lepl.matchers.derived.Integer>`_ (remember that `Real() <api/redirect.html#lepl.matchers.derived.Real>`_ matches both float and integer
values):

  >>> myFloat = Difference(Real(), Integer())
  >>> list(myFloat.parse_all('1.2'))
  [['1.2'], ['1.']]
  >>> list(Real().parse_all('1.2))
  [['1.2'], ['1.'], ['1']]


.. index:: memoisation, RMemo(), LMemo(), memoize(), ambiguous grammars, left-recursion, context_memoize(), auto_memoize()
.. _memoisation:

Memoisation
-----------

A memoizer stores a matcher's results.  If it is called again in the same
context (during backtracking, for example), the stored result can be returned
without repeating the work needed to generate it.  This improves the
efficiency of the parser.

Lepl 2 has two memoizers.  The simplest is `RMemo()
<api/redirect.html#lepl.matchers.memo.RMemo>`_ which is a simple cache based
on the stream supplied.

For left--recursive grammars, however, things are more complicated.  The same
matcher can be called with the same stream at different "levels" of recursion
(for full details see :ref:`memoisation_impl`).  In this case, `LMemo()
<api/redirect.html#lepl.matchers.memo.LMemo>`_ must be used.

Memoizers can be specified directly in the grammar or they can be added via
several configuration options, described below.

When added directly to the grammar a memoizer only affects the given
matcher(s).  For example::

  >>> matcher = Any('a')[:] & Any('a')[:] & RMemo(Any('b')[4])
  >>> len(list(matcher.match('aaaabbbb')))
  5

Here the `RMemo() <api/redirect.html#lepl.matchers.memo.RMemo>`_ avoids re-matching of
the "bbbb", but has no effect on the matching of the "a"s.

.. _left_recursion:

To explicitly apply a memoizer to all matchers use `.config.left_memoize()
<api/redirect.html#lepl.core.config.ConfigBuilder.left_memoize>`_ or
`.config.right_memoize()
<api/redirect.html#lepl.core.config.ConfigBuilder.right_memoize>`_::

  >>> class VerbPhrase(Node): pass
  >>> class DetPhrase(Node): pass
  >>> class SimpleTp(Node): pass
  >>> class TermPhrase(Node): pass
  >>> class Sentence(Node): pass

  >>> verb        = Literals('knows', 'respects', 'loves')         > 'verb'
  >>> join        = Literals('and', 'or')                          > 'join'
  >>> proper_noun = Literals('helen', 'john', 'pat')               > 'proper_noun'
  >>> determiner  = Literals('every', 'some')                      > 'determiner'
  >>> noun        = Literals('boy', 'girl', 'man', 'woman')        > 'noun'
        
  >>> verbphrase  = Delayed()
  >>> verbphrase += verb | (verbphrase // join // verbphrase)      > VerbPhrase
  >>> det_phrase  = determiner // noun                             > DetPhrase
  >>> simple_tp   = proper_noun | det_phrase                       > SimpleTp
  >>> termphrase  = Delayed()
  >>> termphrase += simple_tp | (termphrase // join // termphrase) > TermPhrase
  >>> sentence    = termphrase // verbphrase // termphrase & Eos() > Sentence
    
  >>> p = sentence.left_memoize()
  >>> len(list(p('every boy or some girl and helen and john or pat knows '
  >>>            'and respects or loves every boy or some girl and pat or '
  >>>            'john and helen')))
  392

This example is left--recursive and very ambiguous.  With `LMemo()
<api/redirect.html#lepl.matchers.memo.LMemo>`_ added to all matchers it can be
parsed with no problems.

Because memoisation add extra overhead it is usually preferable --- and part
of the default configuration --- to use `.config.auto_memoize()
<api/redirect.html#lepl.core.config.ConfigBuilder.auto_memoize>`_.  This
improves efficiency by:

* Only adding `LMemo() <api/redirect.html#lepl.matchers.memo.LMemo>`_ to
  left--recursive matchers.
* Only adding `RMemo() <api/redirect.html#lepl.matchers.memo.RMemo>`_ to the
  remaining matchers if the ``full=True`` argument is given.

The detection of left--recursive matchers makes some assumptions about how
matchers work (in simple terms, that each matcher will consume some input); in
some unusual cases this may be incorrect and can be overriden by specifying
the argument ``conservative=True``.
