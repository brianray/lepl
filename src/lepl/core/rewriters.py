
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
Rewriters modify the graph of matchers before it is used to generate a 
parser.
'''

from lepl.support.graph import Visitor, preorder, loops, order, NONTREE, \
    dfs_edges, LEAF
from lepl.matchers.matcher import Matcher, is_child, FactoryMatcher, \
    matcher_type, MatcherTypeException, matcher_map
from lepl.matchers.support import NoTrampolineTransformableWrapper
from lepl.support.lib import lmap, format, basestring, document


def clone(node, args, kargs):
    '''
    Clone including matcher-specific attributes.
    '''
    from lepl.support.graph import clone as old_clone
    copy = old_clone(node, args, kargs)
    copy_standard_attributes(node, copy)
    return copy


def copy_standard_attributes(node, copy, describe=True, transform=True):
    '''
    Handle the additional attributes that matchers may have.
    '''
    from lepl.matchers.support import Transformable
    if isinstance(node, Transformable) and transform:
        copy.function = node.function
    if describe:
        copy.describe = node.describe 
    if isinstance(node, FactoryMatcher):
        copy.factory = node.factory


class DelayedClone(Visitor):    
    '''
    A version of `Clone()` that uses `Delayed()` rather
    that `Proxy()` to handle circular references.  Also caches results to
    avoid duplications.
    '''
    
    def __init__(self, clone_=clone):
        super(DelayedClone, self).__init__()
        self._clone = clone_
        self._visited = {}
        self._loops = set()
        self._node = None
    
    def loop(self, node):
        '''
        This is called for nodes that are involved in cycles when they are
        needed as arguments but have not themselves been cloned.
        '''
        # delayed import to avoid dependency loops
        from lepl.matchers.core import Delayed
        if node not in self._visited:
            self._visited[node] = Delayed()
            self._loops.add(node)
        return self._visited[node]
    
    def node(self, node):
        '''
        Store the current node.
        '''
        self._node = node
        
    def constructor(self, *args, **kargs):
        '''
        Clone the node, taking care to handle loops.
        '''
        # delayed import to avoid dependency loops
        if self._node not in self._visited:
            self._visited[self._node] = self.__clone_node(args, kargs)
        # if this is one of the loops we replaced with a delayed instance,
        # then we need to patch the delayed matcher
        elif self._node in self._loops and \
                not self._visited[self._node].matcher:
            self._visited[self._node] += self.__clone_node(args, kargs)
        return self._visited[self._node]
    
    def __clone_node(self, args, kargs):
        '''
        Before cloning, drop any Delayed from args and kargs.  Afterwards,
        check if this is a Delaed instance and, if so, return the contents.
        This helps keep the number of Delayed instances from exploding.
        '''
        args = lmap(self.__drop, args)
        kargs = dict((key, self.__drop(kargs[key])) for key in kargs)
        return self.__drop(self._clone(self._node, args, kargs))
    
    @staticmethod
    def __drop(node):
        '''
        Filter `Delayed` instances where possible (if they have the matcher
        defined and are nor transformed).
        '''
        # delayed import to avoid dependency loops
        from lepl.matchers.core import Delayed
        from lepl.matchers.transform import Transformable
        if isinstance(node, Delayed) and node.matcher and \
                not (isinstance(node, Transformable) and node.function):
            return node.matcher
        else:
            return node
    
    def leaf(self, value):
        '''
        Leaf values are unchanged.
        '''
        return value
    
    
def post_clone(function):
    '''
    Generate a clone function that applies the given function to the newly
    constructed node, except for Delayed instances (which are effectively
    proxies and so have no functionality of their own) (so, when used with 
    `DelayedClone`, effectively performs a map on the graph).
    '''
    from lepl.matchers.core import Delayed
    def new_clone(node, args, kargs):
        '''
        Apply function as well as clone.
        '''
        copy = clone(node, args, kargs)
        # ignore Delayed since that would (1) effectively duplicate the
        # action and (2) they come and go with each cloning.
        if not isinstance(node, Delayed):
            copy = function(copy)
        return copy
    return new_clone


def flatten(graph):
    '''
    A rewriter that flattens `And` and `Or` lists.
    '''
    from lepl.matchers.combine import And, Or
    def new_clone(node, old_args, kargs):
        '''
        The flattening cloner.
        '''
        table = matcher_map({And: '*matchers', Or: '*matchers'})
        new_args = []
        type_ = matcher_type(node, fail=False)
        if type_ in table:
            attribute_name = table[type_]
            for arg in old_args:
                if matcher_type(arg, fail=False) is type_ \
                        and not arg.function \
                        and not node.function:
                    if attribute_name.startswith('*'):
                        new_args.extend(getattr(arg, attribute_name[1:]))
                    else:
                        new_args.append(getattr(arg, attribute_name))
                else:
                    new_args.append(arg)
        if not new_args:
            new_args = old_args
        return clone(node, new_args, kargs)
    return graph.postorder(DelayedClone(new_clone), Matcher)


def compose_transforms(graph):
    '''
    A rewriter that joins adjacent transformations into a single
    operation, avoiding trampolining in some cases.
    '''
    from lepl.matchers.transform import Transform, Transformable
    def new_clone(node, args, kargs):
        '''
        The joining cloner.
        '''
        # must always clone to expose the matcher (which was cloned earlier - 
        # it is not node.matcher)
        copy = clone(node, args, kargs)
        if isinstance(copy, Transform) \
                and isinstance(copy.matcher, Transformable):
            return copy.matcher.compose(copy)
        else:
            return copy
    return graph.postorder(DelayedClone(new_clone), Matcher)


def memoize(memoizer):
    '''
    A rewriter that adds the given memoizer to all nodes in the matcher
    graph.
    '''
    def rewriter(graph):
        '''
        Embed the memoizer within the cloner.
        '''
        return graph.postorder(DelayedClone(post_clone(memoizer)), Matcher)
    return document(rewriter, memoize, 
                    format('memoize({0})', memoizer.__name__))


def auto_memoize(conservative=None, full=False):
    '''
    Generate an all-purpose memoizing rewriter.  It is typically called after
    flattening and composing transforms.
    
    This rewrites the matcher graph to:
    1 - rewrite recursive `Or` calls so that terminating clauses are
    checked first.
    2 - add memoizers as appropriate
    
    This rewriting may change the order in which different results for
    an ambiguous grammar are returned.
    
    If ``conservative`` is not specified then `optimize_or(False)` and
    `context_memoize(True)` are used.  This gives conservative memoisation 
    with minimal rewriting of alternatives.
    '''
    def rewriter(graph):
        '''
        Apply the two sub-rewriters in turn.
        '''
        graph = optimize_or(False if conservative is None 
                            else conservative)(graph)
        graph = context_memoize(True if conservative is None 
                                else conservative, full)(graph)
        return graph
    return document(rewriter, auto_memoize)


def left_loops(node):
    '''
    Return (an estimate of) all left-recursive loops from the given node.
    
    We cannot know for certain whether a loop is left recursive because we
    don't know exactly which parsers will consume data.  But we can estimate
    by assuming that all matchers eventually (ie via their children) consume
    something.  We can also improve that slightly by ignoring `Lookahead`.
    
    So we estimate left-recursive loops as paths that start and end at
    the given node, and which are first children of intermediate nodes
    unless the node is `Or`, or the preceding matcher is a
    `Lookahead`.  
    
    Each loop is a list that starts and ends with the given node.
    '''
    from lepl.matchers.combine import Or
    from lepl.matchers.core import Lookahead
    stack = [[node]]
    known = set([node]) # avoid getting lost in embedded loops
    while stack:
        ancestors = stack.pop()
        parent = ancestors[-1]
        if isinstance(parent, Matcher):
            for child in parent:
                family = list(ancestors) + [child]
                if child is node:
                    yield family
                else:
                    if child not in known:
                        stack.append(family)
                        known.add(child)
                if not is_child(parent, Or, fail=False) and \
                        not is_child(child, Lookahead, fail=False):
                    break
    
                    
def either_loops(node, conservative):
    '''
    Select between the conservative and liberal loop detection algorithms.
    '''
    if conservative:
        return loops(node, Matcher)
    else:
        return left_loops(node)
    

def optimize_or(conservative=True):
    '''
    Generate a rewriter that re-arranges `Or` matcher contents for
    left--recursive loops.
    
    When a left-recursive rule is used, it is much more efficient if it
    appears last in an `Or` statement, since that forces the alternates
    (which correspond to the terminating case in a recursive function)
    to be tested before the LMemo limit is reached.
    
    This rewriting may change the order in which different results for
    an ambiguous grammar are returned.
    
    `conservative` refers to the algorithm used to detect loops; False
    may classify some left--recursive loops as right--recursive.
    '''
    from lepl.matchers.core import Delayed
    from lepl.matchers.combine import Or
    def rewriter(graph):
        '''
        The Or-rewriting rewriter.
        '''
        for delayed in [x for x in preorder(graph, Matcher) 
                        if isinstance(x, Delayed)]:
            for loop in either_loops(delayed, conservative):
                for i in range(len(loop)):
                    if is_child(loop[i], Or, fail=False):
                        # we cannot be at the end of the list here, since that
                        # is a Delayed instance
                        # copy from tuple to list
                        loop[i].matchers = list(loop[i].matchers)
                        matchers = loop[i].matchers
                        target = loop[i+1]
                        # move target to end of list
                        index = matchers.index(target)
                        del matchers[index]
                        matchers.append(target)
        return graph
    return document(rewriter, optimize_or)


def context_memoize(conservative=True, full=False):
    '''
    Generate a memoizer that only applies LMemo to left recursive loops.
    Everything else can use the simpler RMemo.
    
    `conservative` refers to the algorithm used to detect loops; False
    may classify some left--recursive loops as right--recursive.
    '''
    from lepl.matchers.core import Delayed
    from lepl.matchers.memo import LMemo, RMemo
    def rewriter(graph):
        '''
        Detect loops and clone appropriately.
        '''
        dangerous = set()
        for head in order(graph, NONTREE, Matcher):
            for loop in either_loops(head, conservative):
                for node in loop:
                    dangerous.add(node)
        def new_clone(node, args, kargs):
            '''
            Clone with the appropriate memoizer 
            (cannot use post_clone as need to test original)
            '''
            copy = clone(node, args, kargs)
            if isinstance(node, Delayed):
                # no need to memoize the proxy (if we do, we also break 
                # rewriting, since we "hide" the Delayed instance)
                return copy
            elif node in dangerous:
                return LMemo(copy)
            elif not full:
                return copy
            else:
                return RMemo(copy)
        return graph.postorder(DelayedClone(new_clone), Matcher)
    return document(rewriter, context_memoize,
                    format('context_memoize({0})', conservative))


def set_arguments(type_, **extra_kargs):
    '''
    Add/replace named arguments while cloning.
    '''
    def rewriter(graph):
        '''
        Rewrite with some arguments fixed.
        '''
        def new_clone(node, args, kargs):
            '''
            As clone, but add in any extra kargs if the node is an instance
            of the given type.
            '''
            if isinstance(node, type_):
                for key in extra_kargs:
                    kargs[key] = extra_kargs[key]
            return clone(node, args, kargs)
        return graph.postorder(DelayedClone(new_clone), Matcher)
    return document(rewriter, set_arguments,
                    format('set_arguments({0})', extra_kargs))


def function_only(spec):
    '''
    Replace given matchers if all arguments are FunctionWrapper instances.
    
    `spec` is a map from original matcher type to ([attributes], replacement)
    where attributes are attribute names to check for functions and 
    replacement is a new class with the same signature as the original.
    '''

    def rewriter(graph):
        def type_ok(value):
            return isinstance(value, basestring) \
                or isinstance(value, NoTrampolineTransformableWrapper)
        def new_clone(node, args, kargs):
            ok = False
            for type_ in spec:
                if is_child(node, type_):
                    (attributes, replacement) = spec[type_]
                    for attribute in attributes:
                        if attribute.startswith('*'):
                            values = getattr(node, attribute[1:])
                            for value in values:
                                # this is *not* is_child, because we are
                                # looking at the wrapper class directly
                                ok = type_ok(value)
                                if not ok:
                                    break
                        else:
                            value = getattr(node, attribute)
                            ok = type_ok(value)
                        if not ok:
                            break
                    if ok:
                        type_ = replacement
                        break
            if not ok:
                type_ = type(node)
            try:
                copy = type_(*args, **kargs)
                copy_standard_attributes(node, copy)
                return copy
            except TypeError as err:
                raise TypeError(format('Error cloning {0} with ({1}, {2}): {3}',
                                       type_, args, kargs, err))
        return graph.postorder(DelayedClone(new_clone), Matcher)
    return document(rewriter, function_only)


class NodeStats(object):
    '''
    Provide statistics and access by type to nodes.
    '''
    
    def __init__(self, matcher=None):
        self.loops = 0
        self.leaves = 0
        self.total = 0
        self.others = 0
        self.duplicates = 0
        self.unhashable = 0
        self.types = {}
        self.__known = set()
        if matcher is not None:
            self.add_all(matcher)
        
    def add(self, type_, node):
        '''
        Add a node of a given type.
        '''
        try:
            node_type = matcher_type(node)
        except MatcherTypeException:
            node_type = type(node)
        if type_ & LEAF:
            self.leaves += 1
        if type_ & NONTREE and is_child(node_type, Matcher, fail=False):
            self.loops += 1
        try:
            if node not in self.__known:
                self.__known.add(node)
                if node_type not in self.types:
                    self.types[node_type] = set()
                self.types[node_type].add(node)
                if is_child(node_type, Matcher):
                    self.total += 1
                else:
                    self.others += 1
            else:
                self.duplicates += 1
        except:
            self.unhashable += 1
            
    def add_all(self, matcher):
        '''
        Add all nodes.
        '''
        for (_parent, child, type_) in dfs_edges(matcher, Matcher):
            self.add(type_, child)

    def __str__(self):
        counts = format('total:      {total:3d}\n'
                        'leaves:     {leaves:3d}\n'
                        'loops:      {loops:3d}\n'
                        'duplicates: {duplicates:3d}\n'
                        'others:     {others:3d}\n'
                        'unhashable: {unhashable:3d}\n', **self.__dict__)
        keys = list(self.types.keys())
        keys.sort(key=repr)
        types = '\n'.join([format('{0:40s}: {1:3d}', key, len(self.types[key]))
                           for key in keys])
        return counts + types
