md2html
=====

A lightweight markdown to html parser in Python

#### Release Notes

* 27-Jun-2013    v0.1

     Working, but you have my warnings. Specifically:
     
     * No support for reference style links
     * No support for header lines using '=' and '-'
     * No support for horizontal rules
     * Known bug: last paragraph in list won't be wrapped in <p>

* 28-Jun-2013    v0.2

     * Adding support for header lines using '=' and '-'
     * Fixed bug: last paragraph in list now wrapped in <p> properly by using a nasty global variable

#### How to Use:

First download all source files. Run `python3 tests.py` to ensure all tests are passed.

Quick way to translate input markdown to output html:

    python3 md2html.py [input_file] [output_file]

To use within your own code:

    from markdown import markdown
    from renderers import Mkd_html

    out = markdown(source, Mkd_html())

    # both source and out are strings

#### Credits

I used the same design structure as [libsoldout](http://fossil.instinctive.eu/libsoldout/home)
