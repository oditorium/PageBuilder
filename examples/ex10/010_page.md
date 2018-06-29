:title:                 Inline Templates
:heading:               Documents with inline templates

:texth|md:              **texth.**
                        This is the explanatory text that will appear before
                        the horizontal table (a _horizontal table_ is a
                        table where the top row is rendered with `th` tags
                        and everything else using `td` tags).

:tableh|tblh:           Col 1,      Col 2,      Col 3
                        10,         20,         30
                        11,         21,         31
                        12,         22,         32

:textv|md:              **textv.**
                        This text will appear before the vertical table (a
                        _vertical table_ is a table where the first column
                        is rendered using `th` tags and everything else
                        using `td` tags)

:tablev|tblv:           Row 1,      10,     11,     12,     13
                        Row 2,      20,     21,     22,     23
                        Row 3,      30,     31,     32,     33
                        Row 4,      40,     41,     42,     43

:text1|md:              **text1.**
                        This text will appear before the regular table (a
                        _regular table_ is a table where the first column
                        and the first row are rendered using `th` tags and
                        everything else using `td` tags).

                        In this case the table is rendered into a field
                        called `table1` which means that in the template it
                        can be accessed as `{table1}`. The `table` tag
                        itself has classes `parsetablehtml` and `<tagname>`
                        (in this case `table1`) that can be used styling it

:table1|tbl:            ,           Col 1,  Col 2,  Col 3,  Col4
                        Row 1,      10,     11,     12,     13
                        Row 2,      20,     21,     22,     23
                        Row 3,      30,     31,     32,     33
                        Row 4,      40,     41,     42,     43

:texttd|md:             **texttd.**
                        This text will appear before the td table (a
                        _td table_ is a table where  everything is rendered
                        using `td` tags)

:tabletd|tbltd:         10,     11,     12,     13
                        20,     21,     22,     23
                        30,     31,     32,     33
                        40,     41,     42,     43


:_sectiontemplate:      <h2> {heading} </h2>

                        {text1|md}
                        {table1|tbl}
                        {texth|md}
                        {tableh|tblh}
                        {textv|md}
                        {tablev|tblv}
                        {texttd|md}
                        {tabletd|tbltd}
                        {body}


**body.**
This is the body text. It is always interpreted as markdown and rendered
into a tag called `:body:`. It will only appear on this page if the
`_sectiontemplate` contains a reference to `{body}`. For reference, the
template used for rendering this page is

    :_sectiontemplate:      <h2> {heading} </h2>

                            {text1|md}
                            {table1|tbl}
                            {texth|md}
                            {tableh|tblh}
                            {textv|md}
                            {tablev|tblv}
                            {texttd|md}
                            {tabletd|tbltd}
                            {body}
