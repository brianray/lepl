#LICENCE

from unittest import TestCase

from lepl.rxpy.alphabet.digits import Digits
from lepl.rxpy.graph.opcode import Character


class CharacterTest(TestCase):
    
    def do_test_str(self, intervals, target):
        result = str(Character(intervals, alphabet=Digits()))
        assert result == target, result
    
    def test_str(self):
        self.do_test_str([], '[]')
        self.do_test_str([('0','0')], '[0]')
        self.do_test_str([('0','1')], '[01]')
        self.do_test_str([('0','2')], '[0-2]')
        self.do_test_str([('0','0'), ('1', '1')], '[01]')
       
    def test_coallesce(self):
        self.do_test_str([('0','0'), ('2', '2')], '[02]')
        self.do_test_str([('0','0'), ('1', '2')], '[0-2]')
        self.do_test_str([('0','1'), ('0', '2')], '[0-2]')
        self.do_test_str([('0','1'), ('1', '2')], '[0-2]')
        self.do_test_str([('0','2'), ('2', '2')], '[0-2]')
        self.do_test_str([('1','2'), ('0', '1')], '[0-2]')
        self.do_test_str([('2','2'), ('0', '0')], '[02]')
        self.do_test_str([('0','2'), ('6', '9')], '[0-26-9]')
        self.do_test_str([('1','2'), ('6', '9')], '[126-9]')
        self.do_test_str([('1','2'), ('0', '9')], '[0-9]')
    
    def test_reversed(self):
        self.do_test_str([('2','0')], '[0-2]')
        self.do_test_str([('1','0')], '[01]')
        self.do_test_str([('1','0'), ('1', '2')], '[0-2]')
    
    def test_contains(self):
        assert 0 not in Character([('1', '1')], Digits())
        assert 1 in Character([('1', '1')], Digits())
        assert 2 not in Character([('1', '1')], Digits())
        assert 0 in Character([('0', '1')], Digits())
        assert 1 in Character([('0', '1')], Digits())
        assert 2 not in Character([('0', '1')], Digits())
        assert 0 in Character([('0', '2')], Digits())
        assert 1 in Character([('0', '2')], Digits())
        assert 2 in Character([('0', '2')], Digits())
        assert 0 in Character([('0', '1'), ('1', '2')], Digits())
        assert 1 in Character([('0', '1'), ('1', '2')], Digits())
        assert 2 in Character([('0', '1'), ('1', '2')], Digits())
        assert 0 in Character([('0', '0'), ('2', '2')], Digits())
        assert 1 not in Character([('0', '0'), ('2', '2')], Digits())
        assert 2 in Character([('0', '0'), ('2', '2')], Digits())
