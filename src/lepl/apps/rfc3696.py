
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
Matchers for validating URIs and related objects, taken from RFC3696.

IMPORTANT - the emphasis here is on validation of user input.
These matchers are not exact matches for the underlying specs - they are
just useful practical approximations.  Read RFC3696 to see what I mean
(or the quotes from that doc in the source below).
'''

from re import compile as compile_
from string import ascii_letters, digits, printable, whitespace

from lepl import *


def _guarantee_bool(function):
    '''
    A decorator that guarantees a true/false response.
    '''
    def wrapper(*args, **kargs):
        try:
            return bool(function(*args, **kargs))
        except:
            return False
    return wrapper


def _matcher_to_validator(factory):
    '''
    Generate a validator based on the given matcher factory.
    '''
    matcher = factory()
    matcher.config.compile_to_re()
    
    @_guarantee_bool
    def validator(value):
        for char in '\n\r':
            assert char not in value
        return matcher.parse(value)
    
    return validator
        

def _LimitLength(matcher, length):
    return PostCondition(matcher, lambda results: len(results[0]) <= length)

def _RejectRegexp(matcher, pattern):
    regexp = compile_(pattern)
    return PostCondition(matcher, lambda results: not regexp.match(results[0]))


def _PreferredFullyQualifiedDnsName():
    '''
    Any characters, or combination of bits (as octets), are permitted in
    DNS names.  However, there is a preferred form that is required by
    most applications.  This preferred form has been the only one
    permitted in the names of top-level domains, or TLDs.  In general, it
    is also the only form permitted in most second-level names registered
    in TLDs, although some names that are normally not seen by users obey
    other rules.  It derives from the original ARPANET rules for the
    naming of hosts (i.e., the "hostname" rule) and is perhaps better
    described as the "LDH rule", after the characters that it permits.
    The LDH rule, as updated, provides that the labels (words or strings
    separated by periods) that make up a domain name must consist of only
    the ASCII [ASCII] alphabetic and numeric characters, plus the hyphen.
    No other symbols or punctuation characters are permitted, nor is
    blank space.  If the hyphen is used, it is not permitted to appear at
    either the beginning or end of a label.  There is an additional rule
    that essentially requires that top-level domain names not be all-
    numeric.
    [...]
    Most internet applications that reference other hosts or systems
    assume they will be supplied with "fully-qualified" domain names,
    i.e., ones that include all of the labels leading to the root,
    including the TLD name.  Those fully-qualified domain names are then
    passed to either the domain name resolution protocol itself or to the
    remote systems.  Consequently, purported DNS names to be used in
    applications and to locate resources generally must contain at least
    one period (".") character.
    [...]
    [...]It is
    likely that the better strategy has now become to make the "at least
    one period" test, to verify LDH conformance (including verification
    that the apparent TLD name is not all-numeric), and then to use the
    DNS to determine domain name validity, rather than trying to maintain
    a local list of valid TLD names.
    [...]
    A DNS label may be no more than 63 octets long.  This is in the form
    actually stored; if a non-ASCII label is converted to encoded
    "punycode" form (see Section 5), the length of that form may restrict
    the number of actual characters (in the original character set) that
    can be accommodated.  A complete, fully-qualified, domain name must
    not exceed 255 octets.
    '''
    ld = Any(ascii_letters + digits)
    ldh = ld | '-'
    label = ld + Optional(ldh[:] + ld)
    short_label = _LimitLength(label, 63)
    tld = _RejectRegexp(short_label, r'[0-9]+')
    any_name = short_label[1:, r'\.', ...] + '.' + tld
    non_numeric = _RejectRegexp(any_name, r'[0-9\.]+')
    short_name = _LimitLength(non_numeric, 255)
    return short_name


def _EmailLocalPart():
    '''
    Contemporary email addresses consist of a "local part" separated from
    a "domain part" (a fully-qualified domain name) by an at-sign ("@").
    The syntax of the domain part corresponds to that in the previous
    section.  The concerns identified in that section about filtering and
    lists of names apply to the domain names used in an email context as
    well.  The domain name can also be replaced by an IP address in
    square brackets, but that form is strongly discouraged except for
    testing and troubleshooting purposes.
    
    The local part may appear using the quoting conventions described
    below.  The quoted forms are rarely used in practice, but are
    required for some legitimate purposes.  Hence, they should not be
    rejected in filtering routines but, should instead be passed to the
    email system for evaluation by the destination host.
    
    The exact rule is that any ASCII character, including control
    characters, may appear quoted, or in a quoted string.  When quoting
    is needed, the backslash character is used to quote the following
    character.
    [...]
    In addition to quoting using the backslash character, conventional
    double-quote characters may be used to surround strings.
    [...]
    Without quotes, local-parts may consist of any combination of
    alphabetic characters, digits, or any of the special characters
    
    ! # $ % & ' * + - / = ?  ^ _ ` . { | } ~
    
    period (".") may also appear, but may not be used to start or end the
    local part, nor may two or more consecutive periods appear.  Stated
    differently, any ASCII graphic (printing) character other than the
    at-sign ("@"), backslash, double quote, comma, or square brackets may
    appear without quoting.  If any of that list of excluded characters
    are to appear, they must be quoted.
    [...]
    In addition to restrictions on syntax, there is a length limit on
    email addresses.  That limit is a maximum of 64 characters (octets)
    in the "local part" (before the "@") and a maximum of 255 characters
    (octets) in the domain part (after the "@") for a total length of 320
    characters.  Systems that handle email should be prepared to process
    addresses which are that long, even though they are rarely
    encountered.
    '''
    unescaped_chars = ascii_letters + digits + "!#$%&'*+-/=?^_`.{|}~"
    escapable_chars = unescaped_chars + r'@\",[] '
    quotable_chars = unescaped_chars + r'@\,[] '
    unquoted_string = (('\\' + Any(escapable_chars)) 
                       | Any(unescaped_chars))[1:, ...]
    quoted_string = '"' + Any(quotable_chars)[1:, ...] + '"'
    local_part = quoted_string | unquoted_string
    no_extreme_dot = _RejectRegexp(local_part, r'"?\..*\."?')
    no_double_dot = _RejectRegexp(no_extreme_dot, r'.*\."*\..*')
    short_local_part = _LimitLength(no_double_dot, 64)
    return short_local_part


def _Email():
    return _EmailLocalPart() + '@' + _PreferredFullyQualifiedDnsName()


def Email():
    '''
    Returns a validator for emails, according to RFC3696, which returns True
    if the email is valid, and False otherwise.
    '''
    return _matcher_to_validator(_Email)
    

def _HttpUrl():
    '''
    The following characters are reserved in many URIs -- they must be
    used for either their URI-intended purpose or must be encoded.  Some
    particular schemes may either broaden or relax these restrictions
    (see the following sections for URLs applicable to "web pages" and
    electronic mail), or apply them only to particular URI component
    parts.
    
       ; / ? : @ & = + $ , ?
    
    In addition, control characters, the space character, the double-
    quote (") character, and the following special characters
    
       < > # %
    
    are generally forbidden and must either be avoided or escaped, as
    discussed below.
    [...]
    When it is necessary to encode these, or other, characters, the
    method used is to replace it with a percent-sign ("%") followed by
    two hexidecimal digits representing its octet value.  See section
    2.4.1 of [RFC2396] for an exact definition.  Unless it is used as a
    delimiter of the URI scheme itself, any character may optionally be
    encoded this way; systems that are testing URI syntax should be
    prepared for these encodings to appear in any component of the URI
    except the scheme name itself.
    [...]
    Absolute HTTP URLs consist of the scheme name, a host name (expressed
    as a domain name or IP address), and optional port number, and then,
    optionally, a path, a search part, and a fragment identifier.  These
    are separated, respectively, by a colon and the two slashes that
    precede the host name, a colon, a slash, a question mark, and a hash
    mark ("#").  So we have
    
       http://host:port/path?search#fragment
    
       http://host/path/
    
       http://host/path#fragment
    
       http://host/path?search
    
       http://host
    
    and other variations on that form.  There is also a "relative" form,
    but it almost never appears in text that a user might, e.g., enter
    into a form.  See [RFC2616] for details.
    [...]
    The characters
    
       / ; ?
    
    are reserved within the path and search parts and must be encoded;
    the first of these may be used unencoded, and is often used within
    the path, to designate hierarchy.
    '''
    path_chars = ''.join(set(printable).difference(set(whitespace))
                                       .difference('/;?<>#%'))
    other_chars = path_chars + '/'
    hex = digits + 'abcdef' + 'ABCDEF'
    path_string = ('%' + Any(hex)[2, ...] | Any(path_chars))[1:, ...]
    other_string = ('%' + Any(hex)[2, ...] | Any(other_chars))[1:, ...]
    
    url = 'http://' + _PreferredFullyQualifiedDnsName() + \
            Optional(':' + Any(digits)[1:, ...]) + \
            Optional('/' + 
                     Optional(path_string[1:, '/', ...] + Optional('/')) +
                     Optional('?' + other_string) +
                     Optional('#' + other_string))

    return url


def HttpUrl():
    '''
    Returns a validator for HTTP URLs, according to RFC3696, which returns True
    if the email is valid, and False otherwise.
    '''
    return _matcher_to_validator(_HttpUrl)


def MailToUrl():
    '''
    The following characters may appear in MAILTO URLs only with the
    specific defined meanings given.  If they appear in an email address
    (i.e., for some other purpose), they must be encoded:
    
       :       The colon in "mailto:"
    
       < > # " % { } | \ ^ ~ `
    
       These characters are "unsafe" in any URL, and must always be
       encoded.
    
    The following characters must also be encoded if they appear in a
    MAILTO URL
    
       ? & =
          Used to delimit headers and their values when these are encoded
          into URLs.
    ----------
    The RFC isn't that great a guide here.  The best approach, I think, is
    to check the URL for "forbidden" characters, then decode it, and finally
    validate the decoded email.  So we implement the validator directly (ie
    this is not a matcher).
    '''
    
    MAIL_TO = 'mailto:'
    encoded_token = compile_('(%.{0,2})')
    email = _Email()
    email.config.compile_to_re()
    
    @_guarantee_bool
    def validator(url):
        assert url.startswith(MAIL_TO)
        url = url[len(MAIL_TO):]
        for char in r':<>#"{}|\^~`':
            assert char not in url
        def unpack(chunk):
            if chunk.startswith('%'):
                assert len(chunk) == 3
                return chr(int(chunk[1:], 16))
            else:
                return chunk
        url = ''.join(unpack(chunk) for chunk in encoded_token.split(url))
        assert url
        return email.parse(url)

    return validator
