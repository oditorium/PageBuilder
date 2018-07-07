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
__version__ = "1.2"


import re
import markdown as mdwn
from collections import OrderedDict
from collections import namedtuple
from types import SimpleNamespace
from datetime import datetime


################################################################################
## PARSERS
################################################################################
# TODO: convert to objects?

def parse_date_ymd(s):
    """
    parser for a date field (format Ymd)

    :s:         the input string to parse, which should be of the format
                    2002-12-31
    :returns:   datetime object
    """
    try: return datetime.strptime(s, '%Y-%m-%d').date()
    except ValueError: return "ERR({})".format(s)

def parse_csvs(s):
    """
    parser for comma separated string fields, returning frozenset

    :s:         the input string to parse, which should be of the format
                    string 1, string 2, string 3
    :returns:   frozenset('string 1', ...)
    """
    return frozenset(map(lambda ss: ss.strip(), s.split(',')))

def parse_csv(s):
    """
    parser for comma separated string fields, returning tuple

    :s:         the input string to parse, which should be of the format
                    string 1, string 2, string 3
    :returns:   tuple('string 1', ...)
    """
    return tuple(map(lambda ss: ss.strip(), s.split(',')))

def parse_lines(s):
    """
    parser for line-separated string fields

    :s:         the input string to parse, which should be of the format
                    string 1
                    string 2
                    string 3
    :returns:   tuple('string 1', ...)
    """
    return tuple(map(lambda ss: ss.strip(), s.split('\n')))

def parse_table(s):
    """
    parser for csv table

    :s:         the input string to parse, which should be of the format
                    v11, v12, v13, v14
                    v21, v22, v23, v24
                    v31, v32, v33, v34
    :returns:   tuple(('v11', 'v12', 'v13', 'v14'), ...)
    """
    return tuple(map(lambda s2: tuple(map(lambda s3: s3.strip(), s2.split(','))), s.strip().split('\n')))

def parse_table_html(s, first_row_th=True, first_col_th=False, cls=None):
    """
    parser for csv table, creates html

    :s:             the input string to parse, which should be of the format
                        v11, v12, v13, v14
                        v21, v22, v23, v24
                        v31, v32, v33, v34
    :first_row_th:  if True, use th for first row tags
    :first_col_th:  if True, use td for first col tags
    :returns:       table html
    """
    if cls is None: cls = ""
    tag_r1 = "th" if first_row_th else "td"
    tag_c1 = "th" if first_col_th else "td"
    tag_r1c1 = "th" if first_row_th or first_col_th else "td"

    s_tuple = parse_table(s)
    #print(s_tuple)
    #print(tuple(enumerate(s_tuple)))
    rows = (
               (
                    row,                                      # row
                    tag_r1c1 if rownum == 0 else tag_c1,      # tag col1
                    tag_r1   if rownum == 0 else "td",        # tag col not 1
                )
                for rownum, row in enumerate(s_tuple)
    )
    #print(tuple(rows))
    #return "QQQ"

    def row_html(row_tuple, tagc1, tagnc1):
        """
        converts tuple of fields into html

        :row_tuple: the per-field data
        :tagc1: the tag to use for column 1
        :tagnc1: the tag to use for the other columns
        """
        fields = (
           "<{tag}>{content}</{tag}>".format(
               tag = tagc1 if colnum==0 else tagnc1,
               content = field)

            for colnum, field in enumerate(row_tuple)
        )
        return "<tr>\n{}\n</tr>".format("\n".join(fields))

    rows = (
        row_html(*r)
        for r in rows
    )
    html = "<table class='parsetablehtml {1}'>\n{0}\n</table>".format("\n".join(rows), cls)
    #print(html)
    return html



def parse_dict(s, sep=None):
    """
    parser for (ordered) dicts

    :s:         the input string to parse, which should be of the format
                    key1 :=     value1,
                    key2 :=     value2,
                    key3 :=     value3,
                where the last comma is optional
    :sep:       separator (default is ':=')
    :returns:   OrderedDict(('key1', 'value1'), ...)
    """
    if sep is None: sep = ":="

    # deal with the comma on the last line
    s_split = s.split(",")
    if re.match("^\s*$", s_split[-1]):
        del s_split[-1]

    # now deal with the dict
    try: return OrderedDict(
                    map (
                        lambda s2: tuple(map(
                                            # split at
                                            lambda s3: s3.strip(),
                                            s2.split(sep)
                        )),
                        s_split
                    )
                )
    except:
        raise
        return OrderedDict()

def parse_str(s):
    """
    parser for (stripped) string

    :s:         the input string to parse
    :returns:   the string, stripped of leading and trailing whitespace
    """
    return s.strip()

def parse_markdown(s):
    """
    parser for markdown

    :s:         the input string to parse which should be valid markdown
    :returns:   the html associated with the markdown
                (also replaces '--' with em-dash)
    """
    return mdwn.markdown(_replace_emdash(s))

def parse_breaks(s):
    """
    parser for text with line breaks but that should not be parsed into p tags

    :s:         the input string to parse
    :returns:   the string with \n\n replace with <br/> and \n with space

    NOTE: to parse text into p tags simply parse as markdown.
    """
    return s.strip().replace("\n\n", "\n<br/>\n").replace("\n", " ")

from datetime import datetime

def parse_now(s):
    """
    parses Python data format and returns the current datetime in that format

    :s:         the input string to parse (datetime format string)
    :returns:   the current datetime formatted according the format string in s

    For Python date format see
    <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior>

    Interesting ones are (details might depend on the system)

        %a, %A, %w      weekday abbreviated / full / number
        %d, %e          day of the month zero/blank padded
        %b, %B          month as name abbreviated / full
        %Y, %y          year with/without century
        %H, %I          zero-padded hour in 24/12 hour format
        %k, %l          blank-padded hour in 24/12 hour format
        %p, %P          am/pm indicator in lowercase/uppercase
        %M, %S          minutes and seconds
        %c, %x, %X      full datetime / date / time according to locale
        %F              iso date format
        %Z, %z          time zone name / UTC offset
    """
    s = s.strip()
    if s == "-": s = "%a %e %b %Y, %k:%M"
    return datetime.now().strftime(s)




################################################################################
## FILTERS
################################################################################

# Filters are functions that take a string (possible also some additional
# parameters) and that return a modification of that string; for example,
# a the `_replace_emdash` filter replaces all double-hyphens `--` with
# em-dashes `—`

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
## ANALYSIS FUNCTIONS
################################################################################

# Analysis Functions are similar to filters in that they take a string, the
# string being the text that is being converted. Contrary to filters however
# they do not modify the text -- and therefore they dont return it -- but they
# perform some analysis on the text, and they return a struct representing
# the result of this analysis

_Reference = namedtuple('Reference', ['ref', 'url'])

def _extract_references(md, arg=None):
    """
    scan a markown string for link definitions

    :md:        the markdown text to be scanned
    :arg:       dummy argument
    :returns:   tuple(r1, r2, ...)
                where rx = _Reference(refx, urlx)

    NOTES
    - link definitions are of the form `[ref]:url`
    - references are returned as named tuples `Reference(ref, url)`
    """
    pattern = "\[([\w]*)\]:([\w:\/\.-]*)\s"
    result = re.findall(pattern, md)
    return {"references": tuple( _Reference(*ref) for ref in result)}


################################################################################
## HELPER FUNCTIONS
################################################################################

def _starts_with_space(line, return_on_blank=True):
    """
    returns true if line starts with space

    :line:                  the line to be examined
    :return_on_blank:       what to return if line == ""
    :returns:               True if starts with space, False else
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
    number of leading spaces

    :line:          the line to be examined
    :returns:       number of leading spaces in line
    """
    try:
        ix = 0
        while line[ix] == ' ': ix += 1
        return ix

    except IndexError:
        return len(line)

def _remove_leading_spaces(lines):
    """
    removes leading spaces from group of lines

    :lines:         an iterable of lines
    :returns:       lines with leading spaces removed (number of spaces
                    removed depends on spaces in first line)
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

    _analysers = {
            "extractReferences":        _extract_references,
    }


    ######################################################################
    ## CONSTRUCTOR
    def __init__(s, fieldParsers=None, createHtml=True, filters=None, analysers=None):
        s.fieldParsers      = fieldParsers
        s.createHtml        = createHtml
        s.filterSettings    = filters if not filters is None else {}
        s.analyserSettings  = analysers if not analysers is None else {}


    ######################################################################
    ## APPLY FILTERS
    def _applyFilters(s, doc):
        """
        applies all selected filters to document

        :doc:           the document
        :returns:       the document with filters applied
        """
        for afilter, aparam in s.filterSettings.items():
            if aparam is False: continue
            try:
                filterf = s._filters[afilter]
                doc = filterf(doc, aparam)
            except:
                raise
        return doc

    ######################################################################
    ## APPLY ANALYSERS
    def _applyAnalysers(s, doc):
        """
        applies all selected analysers to document

        :doc:           the document
        :returns:       a single dict, aggregating all dicts that have been
                        returned by the analysers selected
        """
        result = {}
        for ananalyser, aparam in s.analyserSettings.items():
            if aparam is False: continue
            try:
                analyserf = s._analysers[ananalyser]
                result.update(analyserf(doc, aparam))
            except:
                raise
        return result


    ######################################################################
    ## _PARSE
    def _parse(s, doc):
        """
        parses meta markdown document into a custom structure

        :doc:           the document to parse
        :returns:       tuple(tags, body)
        :tags:          OrderedDict of tags and raw (text) values
        :body:          body text


        Document Definition
        -------------------

        ::
            :field1:   content1
                       content1 cont'd
            :field2:   content2
                       ....

            Body Area



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
                m = re.match("^(:[a-zA-Z0-9_|]*:)", line)
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
            else:                    parse = parse_str
            meta[tagi] = parse(tagdatai)

        # apply all selected filters to the markdown
        body = s._applyFilters(body)

            # TODO: increase headinglevels is a bit complex because
            # the info whether to increase or not is contained _in_
            # the file so either this must be read done here, or the
            # file must be scanned twice...

        # apply the selected analysers to the markdown
        analysis = s._applyAnalysers(body)

        # convert the markdown to html (if desired)
        if s.createHtml and createHtml:
            html = mdwn.markdown(body)
        else:
            html = None


        #print ("ANALYSIS MM", analysis)
        return SimpleNamespace(
            meta        = meta,
            analysis    = analysis,
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
