:title:                 Example 4

:textfield:             This field is not being formatted at all.

                        It will be passed as is into the template.

                        In this example the line endings will be ignored.

:mdfield|md:            This field is passed through a markdown converter.

                        It is then wrapped in a div of types `ff`, `ff-md`
                        and `ff-md-<fieldname>` ie here `ff-md-mdfield`.

                        The type of the div can be used to attach css
                        formatting to the field.

:mdfield2|md:           Lorem ipsum dolor sit amet, consectetur
                        adipiscing elit. Aenean fermentum viverra ligula,
                        nec scelerisque nisl volutpat et. [lipsum][lipsum]

                        - Nullam consectetur viverra urna tempus pharetra. Donec quis    
                          augue id ante mollis vehicula id nec tellus. Sed
                          placerat eros at sem aliquet finibus. Suspendisse
                          ipsum est, dictum commodo arcu nec, pulvinar
                          bibendum quam.

                        - Aenean a elit ultricies, iaculis nulla at, tempor
                          leo. Suspendisse potenti. Maecenas sed quam
                          tortor. Ut elementum enim in massa ultrices
                          faucibus. Cras condimentum enim nec iaculis
                          volutpat.

                        [lipsum]:https://lipsum.com/

:prefield|pre:          This field is formatted as a pre.

                                ￣￣￣￣￣￣￣
                                |  HIYA    |
                                | ＿＿＿＿___|
                                (\__/) ||
                                (•ㅅ•) ||
                                / 　 づ

                                1
                                 2
                                  3
                                   4
                                    5

                        The pre has types `ff`, `ff-pre`
                        and `ff-<fieldname>` ie here `ff-prefield`.

:divfield|div:          This field is simply wrapped in a div.

                        Like in a regular textfield no processing is applied.

                        But in an html file all formatting will be ignored

                        (it can of course contain <strong>tags</strong>)

:divfield2|div:         This field is simply wrapped in a div.

                        Like in a regular textfield no processing is applied.

                        But in an html file all formatting will be ignored

                        (it can of course contain <strong>tags</strong>)

:dictfield|dct:         key1 => value1,
                        key2 => value2,
                        key3 => value3,

:linefield|ln:          this is line 1
                        this is line 2

:csvfield|csv:          item 1, item 2, item 3,
                        item 4, item 5, and
                        item 6

:brkfield|brk:          The break field converts single line breaks in simple
                        spaces, but preserves (double) line breaks, or rather,
                        converts them into br tags.

                        This means that, when converted to html, paragraphs
                        can be distinguished.

:nowfield|now:          -

:nowfield1|now:         %e %B %Y

:nowsplainer|pre:       %a, %A, %w      weekday abbreviated / full / number
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

:tablefield|tbl:        ,   c1, c2, c3
                        r1, 1,  2,  3
                        r2, 4,  5,  6
                        r3, 7,  8,  9

:tablefieldh|tblh:      c1,     c2,     c3
                        4,      5,      6
                        7,      8,      9

:tablefieldv|tblv:      r1, 1,  4,  7
                        r2, 2,  5,  8
                        r3, 3,  6,  9

:tablefieldtd|tbltd:    1,  2,  3
                        4,  5,  6
                        7,  8,  9
