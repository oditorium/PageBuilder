#!/usr/bin/env python3
"""
creates a self-contained HTML page from a metamarkdown file

(c) Copyright Stefan LOESCH 2018. All rights reserved.
Licensed under the MIT License
<https://opensource.org/licenses/MIT>
"""
__version__ = "1.4"

import metamarkdown as mm
import markdown as mdwn
from transformer import contract
from collections import namedtuple
import json
import yaml


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

_STYLE = """
:parameters:    baseFont        := sans-serif,
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

## Aggregate File
-to come-

## Component Files
{}

## Meta Data
- actual [yaml](index.yaml) [json](index.json)
- raw [yaml](indexr.yaml) [json](indexr.json)


"""
_INDEX_LINE = """- [{0[0]}]({0[2]})"""


class PageBuilder():
    """
    converts metamarkdown files into self-contained and styled html files
    """

    _fieldParsers = {
        "title":            str,
        "tags":             mm.parse_csv,
        "keywords":         mm.parse_csv,
        "meta":             mm.parse_dict,
        "headinglevel":     int,
    }


    _parameters = {
        "template":                 _TEMPLATE,
        "style":                    _STYLE,
        "meta":                     _META,
        "settings":                 "",
        "replaceEmDash":            True,
        "removeComments":           True,
        "removeLineComments":       False,
        #"definitionsOnly":          False,
    }

    def __init__(s, **kwargs):
        s.p = {} # parameter
        for param, value in s._parameters.items():
            try:
                s.p[param] = kwargs[param]
            except KeyError:
                s.p[param] = value

        s._parse = mm.Parser(
                        fieldParsers            = s._fieldParsers,
                        replaceEmDash           = s.p['replaceEmDash'],
                        removeComments          = s.p['removeComments'],
                        removeLineComments      = s.p['removeLineComments'],
                        #definitionsOnly         = s.p['definitionsOnly'],
        )
        s.read_settings(s.p['settings']);


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


    def _processMetaMarkdown(s, md):
        """
        processes one markdown file
        """
        return s._parse(md)

    def _process_template(s, template_name, specific_params=None):
        """
        processes template strings eg for the page template or style

        :template_name:     key of the template in `s.p`
        :specific_params:   parameters specific to the file rendered (eg
                            the body html for rendering a page template)
        :returns:           the template with parameters filled in
        """
        if specific_params is None: specific_params = {}
        result = mm.parsetext(s.p[template_name], fieldParsers={"parameters": mm.parse_dict})
        template = result.body
        params = result.meta.get("parameters", {})
        params = {
            k: s.p[k] if k in s.p else v
            for k,v in params.items()
        }
        specific_params.update(params)
        if specific_params:
            try:
                template = template.format(**specific_params)
            except KeyError as e:
                print ("\nTEMPLATE ERROR\n=================")
                print ("defined items: ", tuple(specific_params.keys()))
                print ("missing item:  ", e)
                print ()
                template = "KEY ERROR: {} ".format(e)
        return template

    def read_settings(s, settings):
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
        return s._process_template("style")

    def _template(s, **params):
        """
        processes the internal page template, returning propert HTML

        :params:    keyword arguments corresponding to the fields the
                    template expect to be filled from the file data,
                    such as body text and style
        :returns:   the final page HTML
        """
        return s._process_template("template", params)


    def createHtmlPageFromHtml(s, bodyHtml, meta=None):
        """
        creates an entire HtmlPage based on the bodyHtml and meta data
        """
        if meta is None: meta = {}
        #print(meta)

        title = meta.get("title", "")
        metaTags = (
                s.p['meta'].format(field=field, value=value)
                for field, value in meta.get("meta", {}).items()
        )

        return s._template(
            body=bodyHtml,
            metatags = "\n".join(metaTags), # that's html meta tags
            style=s._style,
            **meta                          # that's meta data that might be rendered
        )

    def createHtmlPageFromMetaMarkdown(s, metaMarkdown):
        """
        creates an entire HtmlPage based on the meta markdown

        :returns:   Namedtuple(html, innerHtml, metaData, metaDataRaw)
        """
        processed = s._processMetaMarkdown(metaMarkdown+s._settings_body)
        metaData = contract([s._settings_meta, processed.meta])
        html = s.createHtmlPageFromHtml(
                    bodyHtml    = processed.html,
                    meta        = metaData,
        )
        MMD = namedtuple("mmdData", "pageHtml innerHtml metaData metaDataRaw")
        return MMD(html, processed.html, metaData, processed.meta)

    def __call__(s, *args, **kwargs):
        """
        alias for `createHtmlPageFromMetaMarkdown`
        """
        return s.createHtmlPageFromMetaMarkdown(*args, **kwargs)


pagebuilder = PageBuilder()

#######################################################################
## MAIN

def main(**kwargs):
    """
    actual execution when the module is called from the command line

    all parameters are passed in `kwargs`:

    :mdfiles:           iterable of metamarkdown file names
    :join:              if true, also generate joint output for html
    :no_style:          ignore style information
    :serve:             launch a server (see `port`)
    :port:              if server is given, that's the port, otherwise ignored
    :save_templates:    save template files in current directory, then exit
    """

    if kwargs.get("serve", False):
        import http.server as hs
        port = kwargs.get("port", 8000)
        def run_server(port, bind=None, handler_class=None, server_class=None, protocol=None):
            """
            serve the local directory (code from http.server)
            """
            if handler_class is None: handler_class = hs.SimpleHTTPRequestHandler
            if server_class  is None: server_class  = hs.HTTPServer
            if protocol      is None: protocol      = "HTTP/1.0"
            if bind          is None: bind          = "127.0.0.1"

            server_address = (bind, port)
            handler_class.protocol_version = protocol
            #with server_class(server_address, handler_class) as httpd: # does not work in 3.4
            httpd = server_class(server_address, handler_class)
            sa = httpd.socket.getsockname()
            serve_message = "Serving HTTP on {host} port {port} (http://{host}:{port}/) ..."
            print(serve_message.format(host=sa[0], port=sa[1]))
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nKeyboard interrupt received, exiting.")
                sys.exit(0)
            #end with
        run_server(port)

    if kwargs.get("save_templates", False):
        print ("saving css to _STYLE.css, page template to _TEMPLATE.html, " +
                    "settings file to _SETTINGS, example file to EXAMPLE.md")
        with open("_STYLE.css", "w") as f: f.write(_STYLE)
        with open("_TEMPLATE.html", "w") as f: f.write(_TEMPLATE)
        with open("_SETTINGS", "w") as f: f.write(_SETTINGS)
        with open("EXAMPLE.md", "w") as f: f.write(_EXAMPLE)
        sys.exit(0)

    mdfiles     = kwargs.get("mdfiles", [])
    no_style    = kwargs.get("no_style", False)
    join        = kwargs.get("join", False)

    style, template, settings = readStyleTemplateSettings()
    if no_style: style = ""
    builder = PageBuilder(style=style, template=template, settings=settings)
    files = []
    full_html = ""
    full_meta = {}
    meta_data_list = []
    meta_data_raw_list = []

    for fn in mdfiles:
        fnbase, _ = os.path.splitext(fn)
        fnhtml = fnbase+".html"
        files.append( (fn, fnbase, fnhtml) )
        with open(fn, "r") as f: mmd = f.read()
        html, inner_html, meta_data, meta_data_raw = builder(mmd)
        meta_data['_filename'] = fn
        meta_data['_filenamebase'] = fnbase
        meta_data_raw['_filename'] = fn
        meta_data_raw['_filenamebase'] = fnbase
        meta_data_list.append(meta_data)
        meta_data_raw_list.append(meta_data_raw)
        full_html = full_html + inner_html
        full_meta = contract([meta_data, full_meta])
            # this applies the meta data from the right, so oldest entry wins!
            # (in particular, settings always win!)
        if "filename" in meta_data: fnhtml = meta_data['filename'].strip()
        print("converting {0} to html (output: {1})".format(fn, fnhtml))
        with open(fnhtml, "w") as f: f.write(html)

    # creating page.html
    if join or 'join' in full_meta or 'jointfilename' in full_meta:
        html = builder.createHtmlPageFromHtml(full_html, full_meta)
        if "jointfilename" in full_meta: fnhtml = full_meta['jointfilename'].strip()
        else: fnhtml = "document.html"
        print("saving joined html file (output: {0})".format(fnhtml))
        with open(fnhtml, "w") as f: f.write(html)

    # creating index.html
    print ("saving index (output: index.html)")
    md = "\n".join(_INDEX_LINE.format(f) for f in files)
        # TODO: this is wrong if the file contains the `filename` directive
        # TODO: this does not link to the joined file
    md = _INDEX.format(md)
    with open("index.html", "w") as f:
        f.write(_TEMPLATE.format(body=mdwn.markdown(md), title="INDEX", style="", metatags=""))

    # saving the meta data
    FNBASE = "index"
    print ("saving meta data (output: {0}.yaml, {0}.json, {0}_raw.yaml, {0}_raw.json)".format(FNBASE))
    with open("{}.yaml".format(FNBASE), "w") as f:
        f.write(yaml.dump(meta_data_list, default_flow_style=False))
    with open("{}r.yaml".format(FNBASE), "w") as f:
        f.write(yaml.dump(meta_data_raw_list, default_flow_style=False))
    with open("{}.json".format(FNBASE), "w") as f:  f.write(json.dumps(meta_data_list))
    with open("{}r.json".format(FNBASE), "w") as f: f.write(json.dumps(meta_data_raw_list))



if __name__ == "__main__":

    description = """
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

- _TEMPLATE.html    -- the base template used
- _STYLE.css        -- style information
- _SETTINGS         -- a settings file (meta markdown format)

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

    import sys
    import os
    import argparse

    def readStyleTemplateSettings():
        """
        look for style, template and settings files on a number of locations
        """
        try:
            with open("_STYLE.css", "r") as f: style = f.read()
            print ("reading local _STYLE.css")
        except FileNotFoundError:
            style = _STYLE

        try:
            with open("_TEMPLATE.html", "r") as f: template = f.read()
            print ("reading local _TEMPLATE.html")
        except FileNotFoundError:
            template = _TEMPLATE

        try:
            with open("_SETTINGS", "r") as f: settings = f.read()
            print ("reading local _SETTINGS")
        except FileNotFoundError:
            settings = ""

        return (style, template, settings)


    ap = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
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
    args = ap.parse_args()
    #print (args)

    if args.serve:
        main(serve=True, port=8000)
        sys.exit(0)


    if args.version:
        print(__version__)
        sys.exit(0)

    if args.save_templates:
        main(save_templates=True, port=8000)
        sys.exit(0)

    main(
        mdfiles     = args.mdfiles,
        join        = args.join,
        no_style    = args.no_style,
    )
