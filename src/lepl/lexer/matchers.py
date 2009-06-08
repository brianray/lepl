
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     LEPL is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public License
#     along with LEPL.  If not, see <http://www.gnu.org/licenses/>.

'''
Generate and match a stream of tokens that are identified by regular expressions.
'''

from abc import ABCMeta

from lepl.context import Namespace, NamespaceMixin, Scope
from lepl.error import syntax_error_kargs
from lepl.lexer.stream import lexed_simple_stream, lexed_location_stream
from lepl.matchers \
    import OperatorMatcher, BaseMatcher, coerce, Any, Literal, Lookahead, \
    Regexp, And, Add, Or, Apply, Drop, KApply, Repeat, raise_error, First, Map
from lepl.operators \
    import Matcher, ADD, AND, OR, APPLY, APPLY_RAW, NOT, KARGS, RAISE, \
    REPEAT, FIRST, MAP
from lepl.parser import tagged
from lepl.regexp.matchers import BaseRegexp, Regexp
from lepl.regexp.rewriters import regexp_rewriter
from lepl.regexp.unicode import UnicodeAlphabet
from lepl.stream import LocationStream


TOKENS = 'tokens'
'''
The namespace used for global per-thread data for matchers defined here. 
'''

NonToken = ABCMeta('NonToken', (object, ), {})
'''
ABC used to identify matchers that actually consume from the stream.  These
are the "leaf" matchers that "do the real work" and they cannot be used at
the same level as Tokens, but must be embedded inside them.

This is a purely informative interface used, for example, to generate warnings 
for the user.  Not implementing this interface will not block any functionality.  
'''

NonToken.register(Any)
NonToken.register(Literal)
NonToken.register(Lookahead)
NonToken.register(Regexp)


class LexerError(Exception):
    '''
    Errors associated with the lexer
    '''
    pass


class TokenNamespace(Namespace):
    '''
    A modified version of the usual ``DefaultNamespace`` without handling of
    spaces (since that is handled by the lexer), allowing Tokens and other
    matchers to be configured separately (because they process different 
    types).
    
    At one point this also defined alphabet and skip, used by the rewriter,
    but because those are global values it makes mosre sense to supply them
    directly to the rewriter.
    '''
    
    def __init__(self):
        super(TokenNamespace, self).__init__({
            ADD:       lambda a, b: Add(And(a, b)),
            AND:       And,
            OR:        Or,
            APPLY:     Apply,
            APPLY_RAW: lambda a, b: Apply(a, b, raw=True),
            NOT:       Drop,
            KARGS:     KApply,
            RAISE:     lambda a, b: KApply(a, raise_error(b)),
            REPEAT:    Repeat,
            FIRST:     First,
            MAP:       Map,
        })
        

class Token(OperatorMatcher):
    '''
    Introduce a token that will be recognised by the lexer.  A Token instance
    can be specialised to match particular contents by calling as a function.
    '''
    
    __count = 0
    
    def __init__(self, regexp, content=None, id=None, alphabet=None,
                  complete=True, compiled=False):
        '''
        Define a token that will be generated by the lexer.
        
        regexp is the regular expression that the lexer will use to generate
        appropriate tokens.
        
        content is the optional matcher that will be invoked on the value
        of the token.  It is usually set via (), which clones this instance
        so that the same token can be used more than once.
        
        id is an optional unique identifier that will be given an integer
        value if left empty.
        
        alphabet is the alphabet associated with the regexp.  It should be
        set by the lexer rewiter, so that all instances share the same
        value (it appears in the constructor so that Tokens can be cloned).
        
        complete indicates whether any sub-matcher must completely exhaust
        the contents when matching.  It can be over-ridden for a particular
        sub-matcher via __call__().
        
        compiled should only be used internally.  It is a flag indicating
        that the Token has been processed by the rewriter (see below).
        
        A Token must be "compiled" --- this completes the configuration
        using a given alphabet and is done by the lexer_rewriter.  Care is taken
        to allow a Token to be cloned before or after compilation.
        '''
        super(Token, self).__init__(name=TOKENS, namespace=TokenNamespace)
        self._arg(regexp=regexp)
        self._arg(content=content)
        if id is None:
            id = Token.__count
            Token.__count += 1
        self._arg(id=id)
        self._arg(alphabet=alphabet)
        self._arg(complete=complete)
        self._arg(compiled=compiled)
        
    def compile(self, alphabet=None):
        '''
        Convert the regexp if necessary. 
        '''
        if alphabet is None:
            alphabet = UnicodeAlphabet.instance()
        if self.alphabet is None:
            self.alphabet = alphabet
        self.regexp = self.__to_regexp(self.regexp, self.alphabet)
        self.compiled = True
    
    @staticmethod
    def  __to_regexp(regexp, alphabet):
        '''
        The regexp may be a matcher; if so we try to convert it to a regular
        expression and extract the equivalent text.
        '''
        if isinstance(regexp, Matcher):
            rewriter = regexp_rewriter(alphabet)
            rewrite = rewriter(regexp)
            if isinstance(rewrite, BaseRegexp):
                regexp = str(rewrite.regexp)
            else:
                raise LexerError('A Token was specified with a matcher, '
                                 'but the matcher could not be converted to '
                                 'a regular expression: {0}'.format(rewrite))
        return regexp
        
    def __call__(self, content, complete=None):
        '''
        If complete is specified as True of False it overrides the value
        set in the constructor.  If True the content matcher must complete 
        match the Token contents.
        '''
        complete = self.complete if complete is None else complete
        return Token(self.regexp, coerce(content), self.id, self.alphabet, 
                     complete, self.compiled)
    
    @tagged
    def _match(self, stream):
        '''
        On matching we first assert that the token type is correct and then
        delegate to the content.
        '''
        if not self.compiled:
            raise LexerError('A Token has not been compiled. '
                             'You must use the lexer_rewriter with Tokens. '
                             'This can be done by using Configuration.tokens().')
        if stream:
            (tokens, contents) = stream[0]
            if self.id in tokens:
                if self.content is None:
                    yield ([contents], stream[1:])
                else:
                    generator = self.content._match(contents)
                    try:
                        while True:
                            (value, stream_out) = yield generator
                            if not stream_out or not self.complete:
                                yield (value, stream[1:])
                    except StopIteration:
                        return
        
    def __str__(self):
        return '{0}: {1!r}'.format(self.id, self.regexp)
    
    def __repr__(self):
        return '<Token({0!s})>'.format(self)
    
    @classmethod
    def reset_ids(cls):
        '''
        Reset the ID counter.  This should not be needed in normal use.
        '''
        cls.__count = 0
        
        
class RuntimeLexerError(LexerError):
    
    def __init__(self, stream):
        super(RuntimeLexerError, self).__init__(
            'Cannot lex "{filename}" at {lineno}/{offset}'.format(
                **syntax_error_kargs(stream, None, None)))


class Lexer(NamespaceMixin, BaseMatcher):
    '''
    This takes a set of regular expressions and provides a matcher that
    converts a stream into a stream of tokens, passing the new stream to 
    the embedded matcher.
    
    It is added to the matcher graph by the lexer_rewriter; it is not
    specified explicitly by the user.
    '''
    
    def __init__(self, matcher, tokens, alphabet, skip, 
                  error=None, t_regexp=None, s_regexp=None):
        '''
        matcher is the head of the original matcher graph, which will be called
        with a tokenised stream. 
        
        tokens is the set of `Token` instances that define the lexer.
        
        alphabet is the alphabet for which the regexps are defined.
        
        skip is the regular expression for spaces (which are silently
        dropped if not token can be matcher).
        
        error is the exception raised if skip fails to match.  It is passed
        the stream.
        
        t_regexp and s_regexp are internally compiled state, use in cloning,
        and should not be provided by non-cloning callers.
        '''
        super(Lexer, self).__init__(TOKENS, TokenNamespace)
        if t_regexp is None:
            for token in tokens:
                token.compile(alphabet)
            t_regexp = Regexp.multiple(alphabet, 
                                       [(t.id, t.regexp) for t in tokens]).dfa()
        if s_regexp is None:
            s_regexp = Regexp.single(alphabet, skip).dfa()
        error = RuntimeLexerError if error is None else error
        self._arg(matcher=matcher)
        self._arg(tokens=tokens)
        self._arg(alphabet=alphabet)
        self._arg(skip=skip)
        self._arg(error=error)
        self._arg(t_regexp=t_regexp)
        self._arg(s_regexp=s_regexp)
        
    def token_for_id(self, id):
        '''
        A utility that checks the known tokens for a given ID.  The ID is used
        internally, but is (by default) an unfriendly integer value.  Note that 
        a lexed stream associates a chunk of input with a list of IDs - more 
        than one regexp may be a maximal match (and this is a feature, not a 
        bug).
        '''
        for token in self.tokens:
            if token.id == id:
                return token
        
    @tagged
    def _match(self, stream):
        if isinstance(stream, LocationStream):
            tokens = lexed_location_stream(self.t_regexp, self.s_regexp,
                                           self.error, stream, self.alphabet)
        else:
            # might assert simple stream here?
            tokens = lexed_simple_stream(self.t_regexp, self.s_regexp, 
                                         self.error, stream, self.alphabet)
        generator = self.matcher._match(tokens)
        while True:
            (result, stream_out) = yield generator
            yield (result, stream_out)

        