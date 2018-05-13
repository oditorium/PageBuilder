# Page Builder

_convert (meta) markdown into a self-contained web-page_

## Meta Markdown

Markdown is ideal for writing nicely formatted text.
However, one drawback of markdown is that there is often a
need for meta data associated with text, and there is no way
of adding this meta data to a markdown file. _MetaMarkdown_
addresses this by allowing markdown files to have an
rst-style pre-amble that can contain arbitrary meta data.
For example this would be a valid MetaMarkdown file:

    :title:         Lorem Ipsum | Stefan LOESCH
    :meta:          author  :=  Stefan LOESCH,
                    license :=  MIT
    :tags:          lorem, ipsum

    # Lorem Ipsum

    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Suspendisse ultricies euismod nunc, at fermentum nisl
    scelerisque semper. 
    
    - Sed a enim quam. 
    - Sed et sem eget.
    
    Nulla efficitur iaculis. Fusce rhoncus convallis ligula,
    consectetur bibendum ante tincidunt ac. Sed volutpat
    quam condimentum magna ornare pulvinar. 

The MetaMarkdown code is in `metamarkdown.py`

## Page Builder Module
Pagebuilder is first and foremost a python module that can
be used with the import statement. The central object is the
`PageBuilder` object which for ease of use is instantiated
using default parameters as `pagebuilder`. Basic usage is as
follows. For details, please see the module doc strings.

    from pagebuilder import pagebuilder, PageBuilder

    metamarkdown = """..."""

    mybuilder = PageBuilder(basefontsize="20px")
    html1 = pagebuilder(metamarkdown)               # using defaults
    html2 = mybuilder(metamarkdown)                 # using personal setting

## Page Builder Executable

### Installation

In order to install PageBuilder, Python 3 must be installed
on the system and `pagebuilder.py` must be executable and in
the system path. `metamarkdown.py` can either be in the same
directory, or somewhere else on the the python path.

A simple installation script is provided, which copies the
two files into `~/bin` and creates a symlink without the
`.py` extension for the executable.

### Usage

The executable relies on `argparse`, so use the `--help`
flag to the specific usage instructions. To get started, you
can use the `--save-templates` flag to save the page and
style templates as well as a meta markdown file locally.

    pagebuilder.py --save-templates

The executable will use the template files in the local
directory if available, so if you change them you can
control layout and style. 

    pagebuilder.py *.md

## License

See LICENSE file and license information in the specific
files.
