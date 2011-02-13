
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

# pylint: disable-msg=W0401,C0111,W0614,W0622,C0301,C0321,C0324,C0103,R0201,R0903
#@PydevCodeAnalysisIgnore
# (the code style is for documentation, not "real")

'''
Examples from the documentation.
'''

#from logging import basicConfig, DEBUG

from lepl import *
from lepl._example.support import Example


class Tutorial1Example(Example):
    
    def run_parse(self):
        return Real().parse('123')
    
    def run_match_error(self):
        return Real().parse('cabbage')
    
    def run_parse_all(self):
        return Real().parse_all('123')
    
    def run_parse_all_list(self):
        return list(Real().parse_all('123'))
    
    def run_sum(self):
        add = Real() & Literal('+') & Real()
        return add.parse('12+30')
    
    def run_real(self):
        number = Real() >> float
        return number.parse('12')
  
    def run_real_2(self):
        number = Real() >> float
        add = number & ~Literal('+') & number
        return add.parse('12+30')

    def run_real_3(self):
        add = (Real() & Drop(Literal('+')) & Real()) >> float
        return add.parse('12+30')
    
    def run_sum2(self):
        number = Real() >> float
        add = number & ~Literal('+') & number > sum
        return add.parse('12+30')

    def test_all(self):
        self.examples([
(self.run_parse,
"""['123']"""),
(self.run_match_error,
"""FullFirstMatchException: The match failed in <string> at 'cabbage' (line 1, character 1).
"""),
# fails for python 2 (get a list) so exclude
#(self.run_parse_all,
#"""<map object at 0xdf45d0>"""),
(self.run_parse_all_list,
"""[['123'], ['12'], ['1']]"""),
(lambda: Integer().parse('1'),
"""['1']"""),
(lambda: Integer().parse('1.2'),
"""FullFirstMatchException: The match failed at '.2',
Line 1, character 1 of str: '1.2'.
"""),
(lambda: Float().parse('1'),
"""FullFirstMatchException: The match failed at '',
Line -1, character 0 of str: '1'.
"""),
(lambda: Float().parse('1.2'),
"""['1.2']"""),
(lambda: Real().parse('1'),
"""['1']"""),
(lambda: Real().parse('1.2'),
"""['1.2']"""),
(self.run_sum,
"""['12', '+', '30']"""),
(self.run_real,
"""[12.0]"""),
(self.run_real_2,
"""[12.0, 30.0]"""),
(self.run_real_3,
"""[12.0, 30.0]"""),
(self.run_sum2,
"""[42.0]"""),
])
        
