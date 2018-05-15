#!/usr/bin/env python3 
"""
creates a self-contained HTML page from a metamarkdown file

(c) Copyright Stefan LOESCH 2018. All rights reserved.
Licensed under the MIT License
<https://opensource.org/licenses/MIT>
"""
__version__ = "1.1beta"

import metamarkdown as mm
from transformer import transform


_TEMPLATE = """
<html>

    <head>
        
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
            template = template.format(**specific_params)
        return template

    def read_settings(s, settings):
        """
        process the settings file (overwrites current settings)

        :settings:          the (text from) the settings file
        """
        s._settings_body = ""
        s._settings_meta = {}
        processed = s._processMetaMarkdown(settings)
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
        
        metaTags = (
                s.p['meta'].format(field=field, value=value) 
                for field, value in meta.get("meta", {}).items()
        )
        
        return s._template(
            body=bodyHtml, 
            metatags = "\n".join(metaTags),
            style=s._style,
        )
    
    def createHtmlPageFromMetaMarkdown(s, metaMarkdown):
        """
        creates an entire HtmlPage based on the meta markdown
        """
        processed = s._processMetaMarkdown(metaMarkdown+s._settings_body)
        return s.createHtmlPageFromHtml(processed.html, transform([s._settings_meta, processed.meta]))

    def __call__(s, *args, **kwargs):
        """
        alias for `createHtmlPageFromMetaMarkdown`
        """
        return s.createHtmlPageFromMetaMarkdown(*args, **kwargs)


pagebuilder = PageBuilder()


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
- _SETTINGS.md      -- a settings file

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
            with open("_SETTINGS.md", "r") as f: settings = f.read()
            print ("reading local _SETTINGS.md")
        except FileNotFoundError:
            settings = ""

        return (style, template, settings)


    ap = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("mdfiles", nargs="*", help="metamarkdown file(s)")
    ap.add_argument("--save-templates", action="store_true", default=False, 
            help="save the style and template files locally and exit")
    args = ap.parse_args()
    #print (args)

    if args.save_templates:
        print ("saving css to _STYLE.css, page template to _TEMPLATE.html, " +
                    "settings file to _SETTINGS.md, example file to EXAMPLE.md")
        with open("_STYLE.css", "w") as f: f.write(_STYLE)
        with open("_TEMPLATE.html", "w") as f: f.write(_TEMPLATE)
        with open("_SETTINGS.md", "w") as f: f.write(_SETTINGS)
        with open("EXAMPLE.md", "w") as f: f.write(_EXAMPLE)
        sys.exit(0)

    style, template, settings = readStyleTemplateSettings()
    builder = PageBuilder(style=style, template=template, settings=settings)
    for fn in args.mdfiles:
        fnbase, _ = os.path.splitext(fn)
        print("converting {0} to html (output: {1}.html)".format(fn, fnbase))
        with open(fn, "r") as f: mmd = f.read()
        html = builder(mmd)
        with open(fnbase+".html", "w") as f: f.write(html)



