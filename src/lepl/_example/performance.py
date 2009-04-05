
from logging import basicConfig, DEBUG, INFO
from timeit import timeit

from lepl import *
from lepl._example.support import Example

COUNT = 100

def build(config):
    
    #basicConfig(level=INFO)
    
    class Term(Node): pass
    class Factor(Node): pass
    class Expression(Node): pass
        
    expr   = Delayed()
    number = Float()                                > 'number'
    spaces = Drop(Regexp(r'\s*'))
    
    with Separator(spaces):
        term    = number | '(' & expr & ')'         > Term
        muldiv  = Any('*/')                         > 'operator'
        factor  = term & (muldiv & term)[:]         > Factor
        addsub  = Any('+-')                         > 'operator'
        expr   += factor & (addsub & factor)[:]     > Expression
        line    = Trace(expr) & Eos()
    
    parser = line.string_parser(config)
    return parser

def default(): return build(Configuration.default())
def managed(): return build(Configuration.managed())
def nfa(): return build(Configuration.nfa())
def dfa(): return build(Configuration.dfa())
def basic(): return build(Configuration())

def trace_only(): 
    return build(
        Configuration(monitors=[lambda: TraceResults(False)]))

def manage_only(): 
    return build(
        Configuration(monitors=[lambda: GeneratorManager(queue_len=0)]))

def memo_only(): 
    return build(
        Configuration(rewriters=[auto_memoize()]))

def nfa_only(): 
    return build(
        Configuration(rewriters=[
            regexp_rewriter(UnicodeAlphabet.instance(), False)]))

def dfa_only(): 
    return build(
        Configuration(rewriters=[
            regexp_rewriter(UnicodeAlphabet.instance(), False, DfaRegexp)]))

def parse_multiple(parser, count=COUNT):
    for i in range(count):
        parser('1.23e4 + 2.34e5 * (3.45e6 + 4.56e7 - 5.67e8)')[0]

def parse_default(): parse_multiple(default())
def parse_managed(): parse_multiple(managed())
def parse_nfa(): parse_multiple(nfa())
def parse_dfa(): parse_multiple(dfa())
def parse_basic(): parse_multiple(basic())
def parse_trace_only(): parse_multiple(trace_only())
def parse_manage_only(): parse_multiple(manage_only())
def parse_memo_only(): parse_multiple(memo_only())
def parse_nfa_only(): parse_multiple(nfa_only())
def parse_dfa_only(): parse_multiple(dfa_only())

def time(count, name):
    stmt = '{0}()'.format(name)
    setup = 'from __main__ import {0}'.format(name)
    return timeit(stmt, setup, number=count)

def analyse(func):
    name = func.__name__
    time1 = time(COUNT, name)
    time2 = time(1, 'parse_' + name)
    print('{0:>20s} {1:5.2f} {2:5.2f}'.format(name, time1, time2))

def main():
    print('{0:d} iterations; total time in s\n'.format(COUNT))
    for config in [default, managed, nfa, dfa]:
        analyse(config)
    print()
    for config in [basic, trace_only, manage_only,
                   memo_only, nfa_only, dfa_only]:
        analyse(config)

if __name__ == '__main__':
    main()

        
class PerformanceExample(Example):
    
    def test_parse(self):
    
        # run this to make sure nothing changes
        parsers = [default, managed, nfa, dfa,
                   basic, trace_only, manage_only,
                   memo_only, nfa_only, dfa_only]
        examples = [(lambda: parser()('1.23e4 + 2.34e5 * (3.45e6 + 4.56e7 - 5.67e8)')[0],
"""Expression
 +- Factor
 |   `- Term
 |       `- number '1.23e4'
 +- operator '+'
 `- Factor
     +- Term
     |   `- number '2.34e5'
     +- operator '*'
     `- Term
         +- '('
         +- Expression
         |   +- Factor
         |   |   `- Term
         |   |       `- number '3.45e6'
         |   +- operator '+'
         |   +- Factor
         |   |   `- Term
         |   |       `- number '4.56e7'
         |   +- operator '-'
         |   `- Factor
         |       `- Term
         |           `- number '5.67e8'
         `- ')'""") for parser in parsers]
        self.examples(examples)
        
