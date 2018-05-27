# Page Builder

_convert (meta) markdown into a self-contained html document_


## Meta Markdown

Markdown is ideal for writing nicely formatted text. However, one drawback
of markdown is that there is often a need for meta data associated with
text, and there is no way of adding this meta data to a markdown file.
_MetaMarkdown_ addresses this by allowing markdown files to have an
rst-style pre-amble that can contain arbitrary meta data. For example this
would be a valid MetaMarkdown file:

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

Pagebuilder is first and foremost a python module that can be used with the
import statement. The central object is the `PageBuilder` object which for
ease of use is instantiated using default parameters as `pagebuilder`. Basic
usage is as follows. For details, please see the module doc strings.

    from pagebuilder import pagebuilder, PageBuilder

    metamarkdown = """..."""

    mybuilder = PageBuilder(basefontsize="20px")
    html1 = pagebuilder(metamarkdown)               # using defaults
    html2 = mybuilder(metamarkdown)                 # using personal setting


## Page Builder Executable
### Installation

In order to install PageBuilder, Python 3 must be installed on the system
and `pagebuilder.py` must be executable and in the system path.
`metamarkdown.py` and `transformer.py` can either be in the same directory,
or somewhere else on the the python path.

A simple installation script is provided, which copies the files into
`~/bin` and creates a symlink without the `.py` extension for the
executable.


### Usage

The executable relies on `argparse`, so use the `--help` flag to the
specific usage instructions. To get started, you can use the
`--save-templates` flag to save the page and style templates as well as a
meta markdown file locally.

    pagebuilder.py --save-templates

The executable will use the template files in the local directory if
available, so if you change them you can control layout and style.

    pagebuilder.py *.md


There are also a number of examples to get started, and that demonstrate the
various usage patterns for this tool. Those examples are all located under
the `examples` directory.

- **Example 1 -- Separate Documents:** This example shows how do convert
  multiple, unrelated meta-markdown files into html files. It also shows how
  to work with standard meta data fields, and how the settings file can be
  used to provide defaults.

- **Example 2 -- Single Document:** This example shows how to create a
  document that is generated from multiple constituent meta-markdown files.

- **Example 3 -- Section Template:** This example show how to create a
  single document from consituent files, where each file can be formatted
  using the *section template*, for example integrating meta data into the
  text output in the section.

- **Example 4 -- Field Filters:** This example shows how meta data fields can
  be converted before being used in a section template. For example, this
  allows using markdown in the meta data fields, or the text can be wrapped
  in a pre, or a div for additional CSS styling.

- **Example 5 -- Multiple Section Templates:** This example shows how multiple
  section templates can be used within the same overall document.

- **Example 6 -- Title page and Chapter template:** This example shows how
  how to use the built-in section templates for title pages and chapters.


## License

See LICENSE file and license information in the specific files.
