#!/usr/bin/env python3
"""
creates a self-contained HTML page from a metamarkdown file

(c) Copyright Stefan LOESCH 2018. All rights reserved.
Licensed under the MIT License
<https://opensource.org/licenses/MIT>
"""
__version__ = "2.1"

import metamarkdown as mm
import markdown as mdwn
from transformer import contract
from collections import namedtuple
from collections import OrderedDict
import json
import yaml
import re

########################################################################################
## STRING CONSTANTS

_TEMPLATE = """
<html>

    <head>

        <title>{title}</title>

        <meta charset="UTF-8">
        {metatags}

        <style>
        {style}
        </style>

        <base target="_blank">

    </head>

    <body>

        <div id='body'>
        {body}
        </div>

    </body>

</html>
""".strip()

_SECTIONTEMPLATE_DEFAULT="""
// This is the `default` section template that is applied to all files that
// not explicitly define a section type using the :sectiontype:  meta tag
// (or that use `:sectiontype: default`)

{body}
"""

_SECTIONTEMPLATE_CLEAN="""
// This is the `clean` section template. It can not usually be changed
// unless explitly overwritten in the `_SECTIONTEMPLATES` (plural) file, and
// it is meant to be a template that only renders the body text of a  meta
// markdown file. It can be applied using the `:sectiontype: clean` meta
// tag, and is mostly useful when the default section template has been
// changed because of the presence `_SECTIONTEMPLATE` (singular) file.

{body}
"""

_SECTIONTEMPLATES="""
This is the preamble of the _SECTIONTEMPLATES file, ie the section before
the first divider. This section is discarded, so it can contain arbitrary
text and comments.

The _SECTIONTEMPLATES file can also contain comment lines, starting with '//'.

The different templates in the file are separated by divider lines like the
one below. The rule is:

    [BEGINLINE][\space or =]* SECTIONTYPE: sectionname [\space or =]* [ENDLINE]

The difference between the _SECTIONTEMPLATES (plural) and the _SECTIONTEMPLATE (singular)
files is as follows:

- _SECTIONTEMPLATE changes the `default` template, meaning it is applied to
  all files that do not explicitly specify another template using the
  `:sectiontype:` type, eg `:sectiontype: clean`

- _SECTIONTEMPLATES changes other named templates. They have to explicitly
  activated in a files using the `:sectiontype: <type>` meta tag, where
  `<type>` corresponds to the term after SECTIONTYPE in the dividers below

- The _SECTIONTEMPLATES file can define the `default` template by using
  `== SECTIONTYPE: default ==`; if also a _SECTIONTEMPLATE file is present
  the result is undefined



========================== SECTIONTYPE: titlepage  ==========================
// SECTIONTYPE:         title
// FIELDS:              doctitle, docauthor, docdate, docabstract
// DESCRIPTION:         renders a title page for the documents; note that
//                      the body content is not rendered at all and can
//                      for example be used for comments

<h1>{doctitle}</h1>

<div class='title title-author'>    {docauthor}     </div>
<div class='title title-date'>      {docdate}       </div>
<div class='title title-abstract'>{docabstract}     </div>



=========================== SECTIONTYPE: chapter  ===========================
// SECTIONTYPE:         chapter
// FIELDS:              body, heading
// DESCRIPTION:         renders a document chapter, starting with an h2
//                      heading from the field :heading:

<h2>{heading}</h2>

{body}
"""

_STYLE = """
:defaults:      baseFont        := sans-serif,
                baseFontsize    := 28px,
                baseLineheight  := 1.5,
                baseWidth       := 900px

#body {{
    width: {baseWidth};
    margin-left: 50px;
    margin-top: 50px;
    font-family: {baseFont};
    font-size: {baseFontsize};
    line-height: {baseLineheight};
}}

h1 {{font-size: 200%;}}
h2 {{font-size: 130%;}}
h3 {{font-size: 110%; text-decoration: underline; }}
h4 {{font-size: 100%; font-style: italic;}}
h5 {{font-size: 80%; font-weight: normal; font-style: italic;}}

h1 {{text-align: center;}}
h2 {{
    border-bottom: 3px solid black; border-top: 3px solid black;
    background-color: #eee;
    page-break-before: always;
}}

a {{font-size: 75%;}}
blockquote {{
    font-size: 80%;
    font-style: italic;
    border-left: 3px solid #aaa;
    padding-left: 10px;
    margin-left: 100px;
}}
code {{
    display: inline-block;
    padding: 1px 5px;
    background-color: #eee;
    font-size: 70%;
}}
pre {{
    background-color: #eee;
    font-size: 75%;
}}
table.section {{border-collapse: separate; width: 90%; border-spacing: 10px; }}
table.section td, table.section th {{font-size: 120%; text-align: left; }}
table.section td{{padding-left: 20px; border-left: 5px solid #ccc; }}
.title {{text-align: center;}}
.ff-docabstract h1 {{font-size: 100%; }}
div.ff-docabstract {{font-size: 80%; padding: 50px 20%;}}
""".strip()

_SETTINGS = """
:meta:          author  :=  Stefan LOESCH,
                license :=  MIT

[google]:https://www.google.com
"""

_EXAMPLE = """
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
""".strip()

_META = """
<meta {field}="{value}">
""".strip()

_INDEX = """
# Index

_NOTE: not all those links will work, depending on whether the command line
settings mean those files are generated. Also, currently this file assumes
default file names and will not pick up changes eg with the `:jointfilename:`
tag_

## Aggregate Files
- joint document [document](document.html)
- composite meta data [yaml](document.yaml) [json](document.json)
- raw meta data [yaml](document.r.yaml) [json](document.r.json)

## Component Files
{}
"""
_INDEXLINE = """- [{0[0]}]({0[2]})"""


########################################################################################
## HELPER FUNCTIONS

from itertools import zip_longest

def _grouper(iterable, n=2, fillvalue=None):
    """
    groups iterable into chunks of size n

    :iterable:  the iterable to be chunked
    :n:         the size of the chunks
    :fillvalue:    the value filling the last chunk
    :returns:      chunked iterable

    USAGE

        grouper("ABCDE") # -> (("A", "B"), ("C", "D"), ("E", None))
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)




########################################################################################
## CLASS PAGE BUILDER

class PageBuilder():
    """
    converts metamarkdown files into self-contained and styled html files
    """

    _fieldParsers = {
        "title":            mm.parse_str,
        "tags":             mm.parse_csv,
        "keywords":         mm.parse_csv,
        "meta":             mm.parse_dict,
        "headinglevel":     int,
    }

    _default_parameters = {
        "title":                        "Document",
        "_template":                    _TEMPLATE,
        "sectiontemplate":              "default",
        "_sectiontemplate_default":     _SECTIONTEMPLATE_DEFAULT,
        "_sectiontemplate_clean":       _SECTIONTEMPLATE_CLEAN,
        "_sectiontemplates":            _SECTIONTEMPLATES,
        "_style":                       _STYLE,
        "_meta":                        _META,
        "_settings":                    "",
        "_replaceEmDash":               True,
        "_removeComments":              True,
        "_removeLineComments":          False,
        #"_definitionsOnly":            False,
    }

    def __init__(s, **kwargs):
        s.p = {} # parameter

        # read the paramters from kwargs or, if not present there, from _default_parameters
        for param, value in s._default_parameters.items():
            try:
                s.p[param] = kwargs[param]
            except KeyError:
                s.p[param] = value

        # process the section templates
        s.p['_sectiontemplate_default'] = s._processSectionTemplates(s.p['_sectiontemplate_default'])
        s.p['_sectiontemplate_clean']   = s._processSectionTemplates(s.p['_sectiontemplate_clean'])
            # removes the comment lines from those templates
        templates_dict = s._processSectionTemplates(s.p['_sectiontemplates'])
            # returns OrderedDict ( template_name: template_string )
        for k,v in templates_dict.items(): s.p['_sectiontemplate_'+k] = v
        s.p['_sectiontemplatenames'] = tuple(['default', 'clean'] + [k for k in templates_dict])


        s._parse = mm.Parser(
                        fieldParsers            = s._fieldParsers,
                        replaceEmDash           = s.p['_replaceEmDash'],
                        removeComments          = s.p['_removeComments'],
                        removeLineComments      = s.p['_removeLineComments'],
                        #definitionsOnly         = s.p['_definitionsOnly'],
        )
        s._readSettings(s.p['_settings']);

    def updateParameters(s, **kwargs):
        """
        update the parameters from `kwargs` (only those in kwargs)

        :kwargs:          parameters in the form `n1=v1, n2=b2, ...`
                          use `**{n1:v1, n2:v2}` to pass dicts
        """
        for param, value in kwargs.items():
            if not param in s._parameters:
                pass
                #raise ValueError("Unknown parameter", param, tuple(s.p.keys()))
            s.p[param] = value

    @staticmethod
    def _processSectionTemplates(sectionTemplates):
        """
        processes the SECTIONTEMPLATES file

        :sectionsTemplate:      the sections template file
        :returns:               OrderedDict(templateName: template_str)     if bona fide sectionS file
                                template_str                                if no dividers present

        The sections template has the following format:

            preamble text that is discarded

            ================== SECTIONTYPE: sectionname1 =======================
            // comment lines
            <content of section sectionname1>

            ================== SECTIONTYPE: sectionname2 =======================
            <content of section sectionname2>
        """

        # remove comment lines
        sectionTemplates = re.sub("^//.*$", "", sectionTemplates, flags=re.MULTILINE)

        # split along the divider lines
        regex = "^[\s=]+SECTIONTYPE:\s*([a-zA-Z_0-9]*?)[\s=]+$"
        sectionTemplates = re.split(regex, sectionTemplates, flags=re.MULTILINE)
            # this returns a list of the following form
            #
            #     [preamable, sectionName1, sectionTemplate1, sectionName2, ...]
            #
            # where preamble is the text before the first divider and might or
            # might not be present

        # no dividers found? -> must be a flat section file
        if len(sectionTemplates) == 1:
            return sectionTemplates[0]

        # otherwise discard the preamble
        if len(sectionTemplates) % 2 == 1: del sectionTemplates[0]

        # convert to OrderedDict
        sectionTemplates = OrderedDict(_grouper(sectionTemplates, 2))

        return sectionTemplates


    def _processMetaMarkdown(s, md, createHtml=True):
        """
        processes one markdown file
        """
        return s._parse(md, createHtml=createHtml)


    def _processTemplate(s, template_name, specific_params=None):
        """
        processes template strings eg for the page template or style

        :template_name:     key of the template in `s.p`
        :specific_params:   parameters specific to the file rendered (eg
                            the body html for rendering a page template)
        :returns:           the template with defaults filled in
        """
        if specific_params is None: specific_params = {}

        # process the :defaults: tag
        try:
            result = mm.parsetext(s.p[template_name], fieldParsers={"defaults": mm.parse_dict})
        except KeyError as e:
            missing_template_name = str(e).rsplit("_", maxsplit=1)[1][:-1]
            print ("\nMISSING-TEMPLATE ERROR\n======================")
            print ("missing:  ", missing_template_name)
            print ("defined: ", s.p['_sectiontemplatenames'])
            print ()
            return "ERROR: Missing Sectiontemplate {}".format(missing_template_name)
        template = result.body
        
        # overwrite the parameters in the template with those in s.p if defined there
        params = result.meta.get("defaults", {})
        #if params is None: params = {}
        params = {
            k: s.p[k] if k in s.p else v
            for k,v in params.items()
        }

        # overwrite / amend the parameters from the page-specific paramters
        params.update(specific_params)
        if params:
            try:
                template = template.format(**params)
            except KeyError as e:
                #print("QQQQQ PARAMS KEYS", params.keys())
                #raise
                print ("\nTEMPLATE ERROR\n==============")
                print ("missing:  ", e)
                print ("defined: ", tuple(params.keys()))
                print ()
                template = "KEY ERROR: {} ".format(e)
        return template

    def _readSettings(s, settings):
        """
        process the settings file (overwrites current settings)

        :settings:          the (text from) the settings file
        """
        s._settings_body = ""
        s._settings_meta = {}
        processed = mm.Parser(
                        fieldParsers=s._fieldParsers,
                        definitionsOnly=True,
                        removeLineComments=False,
                        removeComments=False)(settings)
        s._settings_body = processed.body
        s._settings_meta = processed.meta

    @property
    def _style(s):
        """
        processes the internal style template

        :returns:   the style to be used with all parameters resolved
        """
        return s._processTemplate("_style")

    def _template(s, **params):
        """
        processes the full-page template, returning a complete page including <html>, <head> and <body> tags

        :params:    keyword arguments corresponding to the fields the
                    template expect to be filled from the file data,
                    such as body text and style
        :returns:   the final page HTML including <html>, <head> and <body> tags
        """
        return s._processTemplate("_template", params)

    def applyFilters(s, params):
        """
        applies filters to all fields of form 'name|filter'

        :params:        all template parameters
        :returns:       new parameter dict with filters applied

        EXAMPLE

            _applyFilters({'f1|md': 'lorem _ipsum_ dolor'})
            -> {
                'f1|md':    as above,
                'f1':       '<p>lorem <em>ipsum</em></p>', # markdown expanded
            }
        """
        params1 = {} # can't update the paramter dict during iteration
        for k,v in params.items():

            # markdown filter -> convert from markdown, wrap in div
            if k[-3:] == "|md":
                params1[k[0:-3]] = \
                    "<div class='ff ff-md ff-{1}'>{0}</div>".format(mm.parse_markdown(v),k[0:-3])

            # pre filter -> wrap in pre
            elif k[-4:] == "|pre":
                params1[k[0:-4]] = \
                    "<pre class='ff ff-pre ff-{1}'>{0}</pre>".format(v, k[0:-4])

            # pre filter -> wrap in div
            elif k[-4:] == "|div":
                params1[k[0:-4]] = \
                    "<div class='ff ff-div ff-{1}'>{0}</div>".format(v, k[0:-4])

            # dict filter -> interpret as (ordered) dict
            elif k[-4:] == "|dct":
                params1[k[0:-4]] = mm.parse_dict(v)

            # dict filter -> interpret as table (tuple of tuples)
            elif k[-4:] == "|tbl":
                params1[k[0:-4]] = mm.parse_table(v)

            # lines filter -> split string by lines
            elif k[-3:] == "|ln":
                params1[k[0:-3]] = mm.parse_lines(v)

            # csv filter -> split at commas
            elif k[-4:] == "|csv":
                params1[k[0:-4]] = mm.parse_csv(v)

        params.update(params1)
        return params

    def _sectionTemplate(s, **params):
        """
        processes section template, returning the html for the section

        :params:    keyword arguments corresponding to the fields the
                    template expect to be filled from the file data
        :returns:   the section html
        """
        sectionTemplateName = params.get("sectiontemplate", "default")
        sectionTemplateName = "_sectiontemplate_"+sectionTemplateName.strip()
            # params['_sectiontemplate'] contains the (short) name of the template
            # this is prepended with "_sectiontemplate_" to get the key under which it is stored
            # eg the default template will be under "_sectiontemplate_default"

        # process all meta data fields, applying filters
        # for example :fieldname|md: applies the markdown filter to the contents
        # of the field, and stores the result as :fieldname:

        return s._processTemplate(sectionTemplateName, params)

    def createHtmlPageFromHtmlAndMeta(s, bodyHtml, meta=None):
        """
        creates an entire HtmlPage based on the bodyHtml and meta data
        """
        if meta is None: meta = {}
        #print(meta)

        title = meta.get("title", "")
        metaTags = (
                s.p['meta'].format(field=field, value=value)
                for field, value in meta.get("_meta", {}).items()
        )

        return s._template(
            body        = bodyHtml,
            metatags    = "\n".join(metaTags), # that's html meta tags
            style       = s._style,
            **meta                          # that's meta data that might be rendered
        )

    def createHtmlPageFromMetaMarkdown(s, metaMarkdown):
        """
        creates an entire HtmlPage based on the meta markdown

        :returns:   Namedtuple(html, innerHtml, metaData, metaDataRaw)
        """

        # process the meta markdown file with the settings body (links!)
        processed = s._processMetaMarkdown(metaMarkdown+s._settings_body)

        # combine the meta data with the settings meta data (former has priority)
        metaData = contract([s._settings_meta, processed.meta])

        # apply filters
        metaData = s.applyFilters(metaData)

        # apply the section template
        sectionHtml = s._sectionTemplate(body=processed.html, **metaData)

        # apply the main template
        html = s.createHtmlPageFromHtmlAndMeta(bodyHtml=sectionHtml, meta=metaData)

        # return the results
        MMD = namedtuple("mmdData", "pageHtml sectionHtml metaData metaDataRaw")
        metaData['_body'] = processed.body
            # also store the body as a meta data field
            # TODO: should this happen in the meta markdown class?
        return MMD(html, sectionHtml, metaData, processed.meta)

    def __call__(s, *args, **kwargs):
        """
        alias for `createHtmlPageFromMetaMarkdown`
        """
        return s.createHtmlPageFromMetaMarkdown(*args, **kwargs)


pagebuilder = PageBuilder()



########################################################################################
## CLASS BUILDER MAIN

import http.server as hs
import sys
import os
import argparse


class PageBuilderMain():
    """
    wrapper around data and functions for the PageBuilder object

    :main:          entry point that can be called directly in a python shell script
    :run:           entry point that expects all parameters in kwargs

    USAGE

    in a python module, reading arguments from argparse

        if __name__ == "__main__":
            PageBuilderMain().main()

    from other python code, getting arguments from parameters

        params = ...
        PageBuilderMain().run(**params)


    """

    STYLE               = _STYLE
    SETTINGS            = _SETTINGS
    TEMPLATE            = _TEMPLATE
    SECTIONTEMPLATE     = _SECTIONTEMPLATE_DEFAULT
    SECTIONTEMPLATES    = _SECTIONTEMPLATES
    INDEX               = _INDEX
    INDEXLINE           = _INDEXLINE
    EXAMPLE             = _EXAMPLE

    FNSTYLE             = "_STYLE.css"
    FNSETTINGS          = "_SETTINGS"
    FNTEMPLATE          = "_TEMPLATE.html"
    FNSECTIONTEMPLATE   = "_SECTIONTEMPLATE.html"
    FNSECTIONTEMPLATES  = "_SECTIONTEMPLATES.html"
    FNEXAMPLE           = "EXAMPLE.md"

    DESCRIPTION = """
---------------------------------------
Convert (meta)markdown to html
---------------------------------------

Metamarkdown is like Markdown, except that the preamble of the file
can contain rst-like metadata, ie lines of the form

    :fieldname:         field value

and the converter algorithm uses those fields to control the outputs.
Also there are a few extra markdown filters, for example `--` is
converted to an em-dash. and `//` indicates a comment.

The executable looks for three special files in the directory, notably

- _TEMPLATE.html            -- the base template used
- _STYLE.css                -- style information
- _SETTINGS                 -- a settings file (meta markdown format)
- _SECTIONTEMPLATE.html     -- the file specifying the default section template
- _SECTIONTEMPLATES.html    -- the file specifying additional section templates

Example files can be generated using the `--save-templates` flag
(attention: files already present are overwritten without warning).

The settings file is prepended to each of the executed files, both in
terms of meta data and in terms of text (the latter is mostly useful
for link references). Meta data in the files intelligently overwrites
meta data from the templates. For example, the meta field `:meta:`
generates meta tags in the html. If we have in the settings file

    :meta:          field0 := value0, field1 := value0

and in the processed file

    :meta:          field1 := value1, field2 := value1

then the meta tags generated are

    <meta field0="value0">
    <meta field1="value1">
    <meta field2="value1">

---
Version v{}
""".format(__version__)

    def setupArgParse(s):
        """
        sets up argparse

        :returns:       the `argparse` module

        USAGE

        Simple usage

            args = s.setupArgParse().parse_args()


        Advanced usage

            ap = s.setupArgParse()
            ap.add_argument(...)
            ...
            args = ap.parse_args()



        """
        ap = argparse.ArgumentParser(description=s.DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
        ap.add_argument("mdfiles", nargs="*", help="metamarkdown file(s)")
        ap.add_argument("--save-templates", "-t", action="store_true", default=False,
                help="save the style and template files locally and exit")
        ap.add_argument("--no-style", action="store_true", default=False,
                help="do not include style information into the html output")
        ap.add_argument("--join", "-j", action="store_true", default=False,
                help="create joined up file of all the input files")
        ap.add_argument("--serve", action="store_true", default=False,
                help="run an http server (port 8314) on the current location")
        ap.add_argument("--version", "-v", action="store_true", default=False,
                help="print version number")

        return ap


    def readStyleTemplateSettings(s):
        """
        look for style, template and settings files on a number of locations

        :returns:       tuple(style, template, sectiontemplate, settings)
        """
        try:
            with open(s.FNSTYLE, "r") as f: style = f.read()
            print ("reading local", s.FNSTYLE)
        except FileNotFoundError:
            style = s.STYLE

        try:
            with open(s.FNTEMPLATE, "r") as f: template = f.read()
            print ("reading local", s.FNTEMPLATE)
        except FileNotFoundError:
            template = s.TEMPLATE

        try:
            with open(s.FNSECTIONTEMPLATE, "r") as f: sectiontemplate = f.read()
            print ("reading local", s.FNSECTIONTEMPLATE)
        except FileNotFoundError:
            sectiontemplate = s.SECTIONTEMPLATE

        try:
            with open(s.FNSECTIONTEMPLATES, "r") as f: sectiontemplates = f.read()
            print ("reading local", s.FNSECTIONTEMPLATES)
        except FileNotFoundError:
            sectiontemplates = s.SECTIONTEMPLATES

        try:
            with open(s.FNSETTINGS, "r") as f: settings = f.read()
            print ("reading local", s.FNSETTINGS)
        except FileNotFoundError:
            settings = ""

        return (style, template, sectiontemplate, sectiontemplates, settings)

    def runServer(s, port, bind=None, handler=None, server=None, protocol=None):
        """
        serve the local directory (called by `run`)

        :port:          at which port to serve
        :bind:          IP address to bind (typically 127.0.0.1 or 0.0.0.0)
        :handler:       handler class (default: SimpleHTTPRequestHandler)
        :server:        server class (default: HTTPServer)
        :protocol:      protocol (default "HTTP/1.0")

        Note: the code is taken out of http.server
        """
        if handler  is None: handler    = hs.SimpleHTTPRequestHandler
        if server   is None: server     = hs.HTTPServer
        if protocol is None: protocol   = "HTTP/1.0"
        if bind     is None: bind       = "127.0.0.1"

        server_address = (bind, port)
        handler.protocol_version = protocol
        #with server_class(server_address, handler) as httpd: # does not work in 3.4
        httpd = server(server_address, handler)
        sa = httpd.socket.getsockname()
        serve_message = "Serving HTTP on {host} port {port} (http://{host}:{port}/) ..."
        print(serve_message.format(host=sa[0], port=sa[1]))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            return
        #end with

    def saveTemplates(s):
        """
        saves the templates to the local director (called by `run`)
        """
        print ("Saving templates:")
        print ("Style               =>", s.FNSTYLE)
        print ("Template            =>", s.FNTEMPLATE)
        print ("Section Template    =>", s.FNSECTIONTEMPLATE)
        print ("Section Templates   =>", s.FNSECTIONTEMPLATES)
        print ("Settings            =>", s.FNSETTINGS)
        print ("Example             =>", s.FNEXAMPLE)
        with open(s.FNSTYLE, "w") as f:             f.write(s.STYLE)
        with open(s.FNTEMPLATE, "w") as f:          f.write(s.TEMPLATE)
        with open(s.FNSECTIONTEMPLATE, "w") as f:   f.write(s.SECTIONTEMPLATE)
        with open(s.FNSECTIONTEMPLATES, "w") as f:  f.write(s.SECTIONTEMPLATES)
        with open(s.FNSETTINGS, "w") as f:          f.write(s.SETTINGS)
        with open(s.FNEXAMPLE, "w") as f:           f.write(s.EXAMPLE)


    def readAndProcessInputFiles(s, mdfiles, builder, save=True):
        """
        reads and processes all mmd input files, saves individual outputs

        :mdfiles:       list of filenames for the meta markdown files
        :builder:       the builder object
        :save:          if True (default), save generated files
        :returns:       tuple(files, html, meta, metaRaw, fullMeta)
        :files:         list of filename tuples (filename, base_filename, html_filename)
        :html:          list of inner html segments per file
        :meta:          individual meta data (after aggreation with settings)
        :metaRaw:       individual meta data (before aggreation with settings)
        :fullMeta:      the aggregate meta data dict
        """
        files = []
        full_html = ""
        full_meta = {}
        html_list = []
        meta_data_list = []
        meta_data_raw_list = []

        for fn in mdfiles:
            fnbase, _ = os.path.splitext(fn)
            fnhtml = fnbase+".html"
            files.append( (fn, fnbase, fnhtml) )
            with open(fn, "r") as f: mmd = f.read()
            html, inner_html, meta_data, meta_data_raw = builder(mmd)
            html_list.append(inner_html)
            meta_data['_filename'] = fn
            meta_data['_filenamebase'] = fnbase
            meta_data_raw['_filename'] = fn
            meta_data_raw['_filenamebase'] = fnbase
            meta_data_list.append(meta_data)
            meta_data_raw_list.append(meta_data_raw)
            full_meta = contract([meta_data, full_meta])
                # this applies the meta data from the right, so oldest entry wins!
                # (in particular, settings always win!)
            if "filename" in meta_data: fnhtml = meta_data['filename'].strip()
            if save:
                print("converting {0} to html (output: {1})".format(fn, fnhtml))
                with open(fnhtml, "w") as f: f.write(html)

        return (files, html_list, meta_data_list, meta_data_raw_list, full_meta)

    def createJointDocument(s, builder, htmlList, meta, save=True):
        """
        creates the joint document, concatenating the html and meta from all files

        :html:          list of inner html per file
        :builder:       the builder object
        :meta:          the aggregate meta data of all files
        :save:          if True (default), save generated file
        :returns:       tuple(html)
        :html:          the entire-document html
        """
        full_html = "\n".join(htmlList)
        html = builder.createHtmlPageFromHtmlAndMeta(full_html, meta)
        if "jointfilename" in meta: fnhtml = meta['jointfilename'].strip()
        else: fnhtml = "document.html"

        if save:
            print("saving joined html file (output: {0})".format(fnhtml))
            with open(fnhtml, "w") as f: f.write(html)

        return (html,)

    def createIndexHtml(s, files, save=True):
        """
        creates the index file

        :files:         the list of file tuples
        :save:          if True (default), save generated files

        :returns:       tuple(html)
        :html:          the html of the index file
        """
        md = "\n".join(s.INDEXLINE.format(f) for f in files)
            # TODO: this is wrong if the file contains the `filename` directive
            # TODO: this does not link to the joined file
        md = _INDEX.format(md)
        html = s.TEMPLATE.format(
                    body=mdwn.markdown(md),
                    title="INDEX",
                    style="", metatags=""
        )
        if save:
            print ("saving index (output: index.html)")
            with open("index.html", "w") as f: f.write(html)

        return (html,)

    def saveMetaData(s, meta, metaRaw, saveYAML=True, saveJSON=True, saveAggr=True, saveRaw=True):
        """
        saves the list meta data in YAML and/or JSON format

        :meta:          list of aggregate meta data (including settings)
        :metaRaw:       list of raw meta data (excluding settings)
        :saveYAML:      save as YAML
        :saveJSON:      save as JSON
        :saveAggr:      save aggregated list
        :saveRaw:       save raw list
        """
        FNBASE = "document"
            # TODO: link output to flags

        if saveYAML:
            if saveAggr:
                print ("saving aggregate meta data (output: {0}.yaml)".format(FNBASE))
                with open("{}.yaml".format(FNBASE), "w") as f:
                    f.write(yaml.dump(meta, default_flow_style=False))
            if saveRaw:
                print ("saving raw meta data (output: {0}.r.yaml)".format(FNBASE))
                with open("{}.r.yaml".format(FNBASE), "w") as f:
                    f.write(yaml.dump(metaRaw, default_flow_style=False))

        if saveJSON:
            if saveAggr:
                print ("saving aggregate meta data (output: {0}.json)".format(FNBASE))
                with open("{}.json".format(FNBASE), "w") as f:
                    f.write(json.dumps(meta))
            if saveRaw:
                print ("saving raw meta data (output: {0}.r.json)".format(FNBASE))
                with open("{}.r.json".format(FNBASE), "w") as f:
                    f.write(json.dumps(metaRaw))

    def run(s, **kwargs):
        """
        actual execution when the module is called from the command line

        all parameters are passed in `kwargs`:

        :mdfiles:           iterable of metamarkdown file names
        :join:              if true, also generate joint output for html
        :no_style:          ignore style information
        :serve:             launch a server (see `port`)
        :port:              if server is given, that's the port, otherwise ignored
        :save_templates:    save template files in current directory, then exit

        NOTE: the split between `main` and `run` is that (a) `run` does not
        know about command line args, and (b) there is no non-trivial code
        in main. This allows to reuse the object in a non-command-line
        context.
        """
        if kwargs.get("serve", False):
            port = kwargs.get("port", 8000)
            s.runServer(port)
            return

        if kwargs.get("save_templates", False):
            s.saveTemplates()
            return

        mdfiles     = kwargs.get("mdfiles", [])
        no_style    = kwargs.get("no_style", False)
        join        = kwargs.get("join", False)

        style, template, sectiontemplate, sectiontemplates, settings = s.readStyleTemplateSettings()
        if no_style: style = ""
        builder = PageBuilder(
                    _style                      = style,
                    _template                   = template,
                    _sectiontemplate_default    = sectiontemplate,
                    _sectiontemplates           = sectiontemplates,
                    _settings                   = settings
        )
        print("Available section template names:", builder.p['_sectiontemplatenames'])

        files, html_list, meta_data_list, meta_data_raw_list, full_meta = \
                                    s.readAndProcessInputFiles(mdfiles, builder)

        if join or 'join' in full_meta or 'jointfilename' in full_meta:
            document_html, = s.createJointDocument(builder, html_list, full_meta)

        s.saveMetaData(meta_data_list, meta_data_raw_list,
            saveYAML=True, saveJSON=True, saveAggr=True, saveRaw=False)

        index_html, = s.createIndexHtml(files)



    def main(s):
        """
        the main execution entry point

        USAGE

            if __name__ == "__main__":
                PageBuilderMain().main()

        NOTE: the split between `main` and `run` is that (a) `run` does not
        know about command line args, and (b) there is no non-trivial code
        in main. This allows to reuse the object in a non-command-line
        context.
        """

        args = s.setupArgParse().parse_args()

        print("Version ", __version__)
        if args.version: sys.exit(0)

        if args.serve:
            s.run(serve=True, port=8000)
            sys.exit(0)

        if args.save_templates:
            s.run(save_templates=True)
            sys.exit(0)

        s.run(
            mdfiles     = args.mdfiles,
            join        = args.join,
            no_style    = args.no_style,
        )



#######################################################################
## MAIN


if __name__ == "__main__":
    PageBuilderMain().main()
