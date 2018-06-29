:title:                 Table 1 - BROKEN
:sectiontemplate:       element

:pre|md:                The text in the `pre` field will be rendered
                        _before_ the element from the `element` field.

                        ### TD Table

:element|tbltd:         1,  2,  3
                        4,  5,  6
                        7,  8,  9

:post|md:               The text in the `post` field will be rendered
                        _after_ the element from the `element` field.

                        The above table is a _td table_ (ie it has no headings
                        and everything is rendered as td);  it is rendered
                        using the `tblh` filter.


The body text, if present, will be rendered last.

**THIS EXAMPLE BROKE WHEN THE RAW TEXT WAS RENDERED INTO THE BASE TAG
AND THE FILTERED TEXT INTO THE FILTERED TAG. THIS TEMPLATE ASSUMES THAT
PRE / ELEMENT / POST CONTAIN THE FILTERED TEXT**
