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

:dictfield|dct:         key1 := value1,
                        key2 := value2,
                        key3 := value3,
