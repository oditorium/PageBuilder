:title:                 Format 1
:heading:               Example Page Format 1
:sectiontemplate:       myformat1

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


Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque ut leo
tincidunt, tincidunt neque nec, fermentum tellus. Morbi commodo maximus sem,
non mattis mi tempor id. Suspendisse turpis ipsum, commodo ut vehicula sit
amet, efficitur ultricies sapien. Curabitur vulputate orci a facilisis
consectetur. Fusce ullamcorper massa ut nisl auctor, ac commodo lorem
sodales. Praesent ut feugiat quam. Pellentesque pretium gravida elit vel
aliquam. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eu
orci ac dui ultrices consectetur sit amet vitae augue. Duis a tellus
ullamcorper, vehicula justo sit amet, dictum risus. Integer dapibus metus
aliquet laoreet congue. Ut elementum aliquet ex ut commodo. Vivamus mattis
nibh sed rhoncus aliquam.

Ut rutrum fringilla elementum. Interdum et malesuada fames ac ante ipsum
primis in faucibus. Nulla faucibus sodales suscipit. Suspendisse massa odio,
vestibulum at ligula sed, consequat volutpat tellus. Integer pretium magna
vitae nunc semper, non tincidunt purus vehicula. Nam vestibulum turpis eget
orci fermentum lobortis. Morbi a ante sit amet dui tincidunt dictum. Mauris
in ex a elit dignissim consectetur. Praesent et massa consectetur, aliquet
enim lacinia, lobortis diam. Sed vitae magna ornare, finibus enim vitae,
commodo sapien.

Donec imperdiet congue lacus at posuere. Maecenas eleifend non velit quis
porttitor. Vivamus vestibulum pretium venenatis. In hac habitasse platea
dictumst. Phasellus magna nunc, pretium eget blandit a, scelerisque laoreet
nisl. Etiam molestie ipsum quam, at finibus erat tempor non. Praesent
sagittis, ante eu ornare fringilla, ex mi placerat dui, pretium malesuada
sapien augue non tellus. Nulla mattis tortor vel augue placerat, ut blandit
purus facilisis. Proin metus velit, maximus finibus condimentum vitae,
venenatis sit amet ipsum. Ut sit amet tortor vitae felis gravida euismod.
Praesent et ipsum augue. Morbi commodo leo nec lorem porttitor, vel ultrices
urna rhoncus. Etiam ipsum sapien, scelerisque non nunc aliquet, feugiat
eleifend dolor. Sed consequat leo varius tellus pharetra, a porta ipsum
auctor. Quisque venenatis turpis condimentum rutrum aliquam. Donec aliquet
sapien sed risus tempus, viverra pellentesque felis dignissim.
