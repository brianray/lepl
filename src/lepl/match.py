

from lepl.stream import Stream


class MatchMixin():
    '''
    Helper functions that forward to __call__.
    '''
    
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
    
    def match_string(self, text, **options):
        '''
        Parse a string.  For options, see __do_match here or lepl.core.Core.
        '''
        return self(Stream.from_string(text, **options))

    def match_path(self, path, **options):
        '''
        Parse a file from a given path.  
        For options, see __do_match here or lepl.core.Core.
        '''
        return self(Stream.from_path(path, **options))

    def match_list(self, list_, **options):
        '''
        Parse a list of values.  
        For options, see __do_match here or lepl.core.Core.
        '''
        return self(Stream.from_list(list_, **options))

    def match_file(self, file_, **options):
        '''
        Parse a file.  For options, see __do_match here or lepl.core.Core.
        '''
        return self(Stream.from_string(file_, **options))
