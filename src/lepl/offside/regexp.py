
# Copyright 2009 Andrew Cooke

# This file is part of LEPL.
# 
#     LEPL is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published 
#     by the Free Software Foundation, either version 3 of the License, or
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
Extend regular expressions to be aware of additional tokens for line start
and end.
'''

from lepl.offside.support import LineAwareError
from lepl.regexp.core import Character
from lepl.regexp.str import StrAlphabet, make_str_parser
from lepl.support import format, str


# pylint: disable-msg=W0105
# epydoc standard
START = 'SOL'
'''
Extension to represent start of line.
'''

END = 'EOL'
'''
Extension to represent end of line.
'''


# pylint: disable-msg=R0903
# using __ methods

class Marker(object):
    '''
    Used like a character, but represents start/end of line.
    '''
    
    def __init__(self, text, high):
        '''
        If high is true this is ordered after other letters, otherwise it is
        ordered before.
        '''
        self.text = text
        self.high = high
    
    def __gt__(self, other):
        return other is not self and self.high

    def __ge__(self, other):
        return other is self or self.high
    
    def __eq__(self, other):
        return other is self

    def __lt__(self, other):
        return other is not self and not self.high

    def __le__(self, other):
        return other is self or not self.high
    
    def __str__(self):
        return self.text
    
    def __hash__(self):
        return hash(repr(self))
    
    def __repr__(self):
        return format('Marker({0!r},{1!r})', self.text, self.high)
    
    def __len__(self):
        return 1

def as_extension(x):
    return format('(*{0})', x)


SOL = Marker(as_extension(START), False)
'''
Marker to represent the start of a line.
'''

EOL = Marker(as_extension(END), True)
'''
Marker to represent the end of a line.
'''


# pylint: disable-msg=E1002
# pylint can't find ABCs
class LineAwareAlphabet(StrAlphabet):
    '''
    Extend an alphabet to include SOL and EOL tokens.
    '''
    
    def __init__(self, alphabet):
        if not isinstance(alphabet, StrAlphabet):
            raise LineAwareError(
                format('Only StrAlphabet subclasses supported: {0}/{1}',
                       alphabet, type(alphabet).__name__))
        super(LineAwareAlphabet, self).__init__(SOL, EOL,
                                parser_factory=make_str_parser)
        self.base = alphabet
        self.extensions = {START: SOL, END: EOL}
        
    def before(self, char):
        '''
        Append SOL before the base character set.
        '''
        if char == self.max:
            return self.base.max
        if char > self.base.min:
            return self.base.before(char)
        return self.min
    
    def after(self, char):
        '''
        Append EOL after the base character set.
        '''
        if char == self.min:
            return self.base.min
        if char < self.base.max:
            return self.base.after(char)
        return self.max
    
    def extension(self, text):
        '''
        Supply the extensions.
        '''
        if text in self.extensions:
            extn = self.extensions[text]
#            return Character([(extn, extn)], self)
# TODO
            return (extn, extn)
        else:
            return super(LineAwareAlphabet, self).extension(text)
        
    def join(self, chars):
        '''
        Join characters together.
        '''
        return super(LineAwareAlphabet, self).join(
                    filter(lambda x: x not in (SOL, EOL), chars))
            