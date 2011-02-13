from lepl.stream.core import DUMMY_HELPER

# The contents of this file are subject to the Mozilla Public License
# (MPL) Version 1.1 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License
# at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
# the License for the specific language governing rights and
# limitations under the License.
#
# The Original Code is LEPL (http://www.acooke.org/lepl)
# The Initial Developer of the Original Code is Andrew Cooke.
# Portions created by the Initial Developer are Copyright (C) 2009-2010
# Andrew Cooke (andrew@acooke.org). All Rights Reserved.
#
# Alternatively, the contents of this file may be used under the terms
# of the LGPL license (the GNU Lesser General Public License,
# http://www.gnu.org/licenses/lgpl.html), in which case the provisions
# of the LGPL License are applicable instead of those above.
#
# If you wish to allow use of your version of this file only under the
# terms of the LGPL License and not to allow others to use your version
# of this file under the MPL, indicate your decision by deleting the
# provisions above and replace them with the notice and other provisions
# required by the LGPL License.  If you do not delete the provisions
# above, a recipient may use your version of this file under either the
# MPL or the LGPL License.

'''
Tests for the lepl.matchers.support module
'''

#from logging import basicConfig, DEBUG
from unittest import TestCase

from lepl.matchers.support import function_matcher_factory, function_matcher, \
    sequence_matcher_factory, sequence_matcher
    

@function_matcher
def char(support, stream):
    (head, offset, helper) = stream
    if offset < len(head): 
        return ([head[offset]], (head, offset+1, helper))

@function_matcher_factory()
def char_in(chars):
    def match(support, stream):
        (head, offset, helper) = stream
        if offset < len(head) and head[offset] in chars:
            return ([head[offset]], (head, offset+1, helper))
    return match

@sequence_matcher
def any_char(support, stream):
    (head, offset, helper) = stream
    while offset < len(head):
        yield ([head[offset]], (head, offset+1, helper))
        offset += 1

@sequence_matcher_factory()
def any_char_in(chars):
    def match(support, stream):
        (head, offset, helper) = stream
        while offset < len(head):
            if head[offset] in chars:
                yield ([head[offset]], (head, offset+1, helper))
            offset += 1
    return match


def mks(head, offset):
    return (head, offset, DUMMY_HELPER)


class DecoratorTest(TestCase):
    
    def test_char(self):
        #basicConfig(level=DEBUG)
        matcher = char()
        matcher.config.no_full_first_match()
        result = list(matcher.match_null('ab'))
        assert result == [(['a'], mks('ab', 1))], result
        matcher = char()[2:,...]
        matcher.config.no_full_first_match()
        result = list(matcher.match_null('abcd'))
        assert result == [(['abcd'], mks('abcd', 4)), 
                          (['abc'], mks('abcd', 3)), 
                          (['ab'], mks('abcd', 2))], result
        assert char()[:,...].parse('ab') == ['ab']
        
    def test_char_in(self):
        #basicConfig(level=DEBUG)
        matcher = char_in('abc')
        matcher.config.no_full_first_match()
        result = list(matcher.match_null('ab'))
        assert result == [(['a'], mks('ab', 1))], result
        result = list(matcher.match_null('pqr'))
        assert result == [], result
        matcher = char_in('abc')[2:,...]
        matcher.config.no_full_first_match()
        result = list(matcher.match_null('abcd'))
        assert result == [(['abc'], mks('abcd', 3)), 
                          (['ab'], mks('abcd', 2))], result
        
    def test_any_char(self):
        #basicConfig(level=DEBUG)
        matcher = any_char()
        # with this set we have an extra eos that messes things up
        matcher.config.no_full_first_match()
        result = list(matcher.match_null('ab'))
        assert result == [(['a'], mks('ab', 1)), 
                          (['b'], mks('ab', 2))], result
        matcher = any_char()[2:,...]
        matcher.config.no_full_first_match()
        result = list(matcher.match_null('abcd'))
        assert result == [(['abcd'], mks('abcd', 4)), 
                          (['abc'], mks('abcd', 3)), 
                          (['abd'], mks('abcd', 4)), 
                          (['ab'], mks('abcd', 2)), 
                          (['acd'], mks('abcd', 4)), 
                          (['ac'], mks('abcd', 3)), 
                          (['ad'], mks('abcd', 4)), 
                          (['bcd'], mks('abcd', 4)), 
                          (['bc'], mks('abcd', 3)), 
                          (['bd'], mks('abcd', 4)), 
                          (['cd'], mks('abcd', 4))], result
        
    def test_any_char_in(self):
        matcher = any_char_in('abc')
        matcher.config.no_full_first_match()
        result = list(matcher.match_null('ab'))
        assert result == [(['a'], mks('ab', 1)), 
                          (['b'], mks('ab', 2))], result
        result = list(matcher.match_null('pqr'))
        assert result == [], result
        matcher = any_char_in('abc')[2:,...]
        matcher.config.no_full_first_match()
        result = list(matcher.match_null('abcd'))
        assert result == [(['abc'], mks('abcd', 3)), 
                          (['ab'], mks('abcd', 2)), 
                          (['ac'], mks('abcd', 3)), 
                          (['bc'], mks('abcd', 3))], result
    
    def test_bad_args(self):
        #basicConfig(level=DEBUG)
        try:
            char(foo='abc')
            assert False, 'expected error'
        except TypeError:
            pass
        try:
            char('abc')
            assert False, 'expected error'
        except TypeError:
            pass
        try:
            char_in()
            assert False, 'expected error'
        except TypeError:
            pass
        try:
            @function_matcher
            def foo(a): return
            assert False, 'expected error'
        except TypeError:
            pass
            

class FunctionMatcherBugTest(TestCase):
    
    def test_bug(self):
        #basicConfig(level=DEBUG)
        from string import ascii_uppercase
        @function_matcher
        def capital(support, stream):
            (head, offset, helper) = stream
            if head[offset] in ascii_uppercase:
                return ([head[offset]], (head, offset+1, helper))
        parser = capital()[3]
        assert parser.parse_string('ABC')
        