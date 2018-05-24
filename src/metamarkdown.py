"""
parses a metamarkdown file

USAGE

    import metamarkdown as mm
    fieldParsers = {
        'date':     mm.parse_date_ymd,
        'author':   mm.parse_str,
        'tags':     mm.parse_csv,
        'numrefs':  int,
    }

    mm_text = "" "
    :author:    Stefan LOESCH
    :date:      2020-03-14
    :tags:      coding, python
    :numrefs:   31415

    # Lorem Ipsum

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer
    pellentesque justo varius ante tincidunt, eget malesuada nisl ullamcorper.
    Quisque mollis euismod est, sit amet placerat erat cursus posuere.
    "" "

    result = mm.parsemd(mm_text, fieldParsers)
    print(result.html)              # <h1>Lorem ipsum...
    print(result.body)              # # Lorem ipsum...
    print(result.meta['author'])    # Stefan LOESCH
    print(result.meta['tags'])      # ('coding', 'python')


(c) Copyright Stefan LOESCH 2018. All rights reserved.
Licensed under the MIT License
<https://opensource.org/licenses/MIT>
"""
__version__ = "0.2.1"


import re
import Markdown as mdwn
from collections import OrderedDict
from types import SimpleNamespace
from datetime import datetime


################################################################################
## RST PARSERS
################################################################################
def parse_date_ymd(s):
    """
    rst parser for a date field (format Ymd)
    """
    try: return datetime.strptime(s, '%Y-%m-%d').date()
    except ValueError: return "ERR({})".format(s)

def parse_csvs(s):
    """
    rst parser for comma separated string fields (returns frozenset)
    """
    return frozenset(map(lambda ss: ss.strip(), s.split(',')))

def parse_csv(s):
    """
    rst parser for comma separated string fields (returns tuple)
    """
    return tuple(map(lambda ss: ss.strip(), s.split(',')))

def parse_lines(s):
    """
    rst parser for string fields split by lines (returns tuple)
    """
    return tuple(map(lambda ss: ss.strip(), s.split('\n')))

def parse_table(s):
    """
    rst parser table (rows as lines, comma separated within; returns tuple)
    """
    return tuple(map(lambda s2: tuple(map(lambda s3: s3.strip(), s2.split(','))), s.strip().split('\n')))

def parse_dict(s, sep=None):
    """
    rst parser for (ordered) dicts; default separator is ':='
    """
    try: return OrderedDict(map (lambda s2: tuple(map(lambda s3: s3.strip(), s2.split(':='))), s.split(",")))
    except: return None

def parse_str(s):
    """
    rst parser for string (can also just use `str`)
    """
    return s

def parse_markdown(s):
    """
    rst parser for markdown
    """
    return mdwn.markdown(_replace_emdash(s))


################################################################################
## FILTERS
################################################################################

def _replace_emdash(s, execute=True):
    """
    replace -- with em-dash
    """
    if not execute: return s
    return re.sub("[\s]*--[\s]*", "—", s)

def _increase_heading_level(s, increase=0):
    """
    increase heading level by `increase` steps
    """
    if increase <= 0: return s
    repl = "#"*(increase+1)
    return re.subn("^#", repl, s, flags=re.MULTILINE)[0]

def _removeLineComments(s, execute=True):
    """
    removes comments (`//` to end of line)
    """
    if not execute: return s
    return re.subn("^[\s]*//.*$", "", s, flags=re.MULTILINE)[0]

def _removeComments(s, execute=0):
    """
    removes line comments (lines starting with `//`)
    """
    if not execute: return s
    return re.subn("\s//.*$", "", s, flags=re.MULTILINE)[0]

def _definitionsOnly(s, execute=0):
    """
    removes all text lines (only keeps definition of the form [name]:url)
    """
    if not execute: return s
    return "\n".join(re.findall("^\s*[[].*[\]]:.*$", s, re.MULTILINE))


################################################################################
## HELPER FUNCTIONS
################################################################################

def _starts_with_space(line, return_on_blank=True):
    """
    returns true if line starts with space (return_on_blank if empty)
    """
    try: return line[0] == ' '
    except IndexError: return return_on_blank

def _ziprange(alist, ix):
    """
    returns zip of the list, and the one with ix added at the end and first element dropped

    Example
    -------

    ::
        alist = [2,4,7]
        _ziprange (alist, 10)

        -->

        zip([2,4,7], [4,7,10]) -> (2,4), (4,7), (7,10)

    """
    blist = alist.copy()
    blist.append(ix)
    del blist[0]
    return zip(alist, blist)

def _num_leading_spaces(line):
    """
    returns the number of leading spaces in a line
    """
    try:
        ix = 0
        while line[ix] == ' ': ix += 1
        return ix

    except IndexError:
        return len(line)

def _remove_leading_spaces(lines):
    """
    removes leading spaces from group of lines (the number removed depends on first line)
    """
    if not lines: return lines
    num_leading_spaces = _num_leading_spaces(lines[0])
    return [l[num_leading_spaces:] for l in lines]



################################################################################
## CLASS PARSER
################################################################################
class Parser():
    """
    parse a metamarkdown file


    Filters

    :increaseHeadingLevel:          increase heading level (eg 1: # -> ##, ## -> ### etc)
    :replaceEmDash:                 replace -- with em dash
    :removeComments:                remove all comments (`//` to end of line)
    :removeLineComments:            remove line comments (lines starting with `//`)
    :definitionsOnly:               only keeps definition lines (starting with `[`)
    """


    _filters = {
            "increaseHeadingLevel":     _increase_heading_level,
            "replaceEmDash":            _replace_emdash,
            "removeComments":           _removeComments,
            "removeLineComments":       _removeLineComments,
            "definitionsOnly":          _definitionsOnly,
    }


    ######################################################################
    ## CONSTRUCTOR
    def __init__(s, fieldParsers=None, createHtml=True, **filterSettings):
        s.fieldParsers      = fieldParsers
        s.createHtml        = createHtml
        s.filterSettings    = filterSettings


    ######################################################################
    ## APPLY FILTERS
    def _applyFilters(s, doc):
        """
        applies all selected filters
        """
        for afilter, aparam in s.filterSettings.items():
            try:
                filterf = s._filters[afilter]
                doc = filterf(doc, aparam)
            except:
                raise
        return doc


    ######################################################################
    ## _PARSE
    def _parse(s, doc):
        """
        parses meta markdown document into a custom structure


        Document Definition
        -------------------

        ::
            :field1:   content1
                       content1 cont'd
            :field2:   content2
                       ....

            Body Area


        :Returns: tuple(tags, body)

            tags       - OrderedDict of tags and raw (text) values
            body       - body text


        """

        # split the document in individual lines
        doclines = doc.split("\n")

        # loop over the lines
        ix = 0          # loopindex
        taglines = []   # collects the ix numbers of tag lines
        tags = []       # collects that tags
        while True:

            # get the current line
            try: line = doclines[ix]
            except IndexError: break

            # check whether is starts with space or is empty
            if not _starts_with_space(line):

                # yes: check whether it is start of a tag
                m = re.match("^(:[a-zA-Z0-9]*:)", line)
                if m:

                    # yes: remember index
                    taglines.append(ix)
                    thetag = m.group(0)[1:-1]
                    tags.append(thetag.lower())


                else:
                    # no, not start of a tag: check whether we already have found tags
                    if taglines:

                        # yes: this means we are done here, we've found the body
                        # at this point, line == docline[ix] is the first body line
                        break

                    else:
                        # no: this means we are still parsing the title area
                        pass


            # next line
            ix += 1

        # when we leave the loop, ix will be the first body line


        if taglines:
            # general case: we have tags, so title pre tags, body post tags
            title = "\n".join([doclines[i] for i in range(0, taglines[0])])
            body = "\n".join([doclines[i] for i in range(ix, len(doclines))])
        else:
            # otherwise we set title to None, and the whole text is just put into body
            title, body = "", "\n".join(l for l in doclines)

        # we remove the tags themselves from the doclines, and replace them with spaces
        for i,tagi in zip (taglines, tags):
            leni = len(tagi)+2
            doclines[i] = " " * leni + doclines[i][leni:]

        # now we collect all lines that belong to the tags
        # if taglines is (3,7,10,...) then _ziprange is ( (3,7), (7, 10), ...)
        taglist = [[doclines[i] for i in range(start, end)] for start, end in _ziprange(taglines, ix)]

        # now we remove the leading spaces from the taglines (determined by first indent)
        taglist = [_remove_leading_spaces(tl) for tl in taglist]

        # now pack this all into an OrderedDict and merge the lines again
        tags_dict = OrderedDict(
            ((tagi, "\n".join(taglinesi)) for tagi, taglinesi in zip(tags, taglist))
        )

        return (tags_dict, body)



    ######################################################################
    ## PARSE
    def parse (s, doc, fieldParsers=None, createHtml=True):
        """
        parses a meta-markdown document (starts with rst-like meta data, then markdown)

        :doc:               the meta-markdown document
        :fieldParsers:      dict fieldName: fieldParser
        :createHtml:        if True (default), create html from markdown
        :returns:           the function returns a SimpleNamespace where the meta fields
                            are in `.meta` and the raw body is in `.body`. If html is
                            created this is in `.html`

        Document Definition
        -------------------

        ::
            :field1:   content1
                       content1 cont'd
            :field2:   content2
                       ....

            body


        Field definitions *must* start in column 0. A field is considered to
        end where either the next field or the body starts. The start of the
        body is the first line that starts at col 0 where there is no field
        definition following.
        """

        if fieldParsers is None: fieldParsers = s.fieldParsers;
        if fieldParsers is None: fieldParsers = {}

        # parse the document into a tags dict and a markdown body
        tags, body = s._parse(doc)

        # parse the tags using the respective field parsers
        meta = OrderedDict()
        for tagi, tagdatai in tags.items():
            if tagi in fieldParsers: parse = fieldParsers[tagi]
            else:               parse = str
            meta[tagi] = parse(tagdatai)

        # apply all selected filters to the markdown
        body = s._applyFilters(body)

            # TODO: increase headinglevels is a bit complex because
            # the info whether to increase or not is contained _in_
            # the file so either this must be read done here, or the
            # file must be scanned twice...

        # convert the markdown to html (if desired)
        if s.createHtml and createHtml:
            html = mdwn.markdown(body)
        else:
            html = None

        return SimpleNamespace(
            meta        = meta,
            body        = body,
            html        = html,
        )


    ######################################################################
    ## __CALL__
    def __call__(s, *args, **kwargs):
        """
        alias for `parse`
        """
        return s.parse(*args, **kwargs)



parsemd         = Parser()
metamarkdown    = parsemd

parsetext       = Parser(createHtml=False)
text            = parsetext
