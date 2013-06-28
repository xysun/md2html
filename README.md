md2html
=====

A lightweight markdown to html parser in Python

#### Release Notes

* 28-Jun-2013    v0.2

     * Adding support for header lines using '=' and '-', reference style likes; horizontal rules
     * Fixed bug: last paragraph in list now wrapped in `<p>` properly by using a nasty global variable
     * Known bug when use horizontal rule after unordered list, both using asterisk, horizontal rule won't get properly rendered.

* 27-Jun-2013    v0.1
     
     Working, but you have my warnings. Specifically:

     * No support for reference style links
     * No support for header lines using '=' and '-'
     * No support for horizontal rules
     * Known bug: last paragraph in list won't be wrapped in `<p>`

#### How to Use:

First download all source files. Run `python3 testing.py` to ensure all tests are passed.

Quick way to translate input markdown to output html:

    python3 md2html.py [input_file] [output_file]

To use within your own code:

    from markdown import markdown
    from renderers import Mkd_html

    out = markdown(source, Mkd_html())

    # both source and out are strings

#### Notes

Below are the features that I don't intend to add in the near future, more a choice of style:

* image support
* native HTML tags support

#### Credits

I used the same design structure as [libsoldout](http://fossil.instinctive.eu/libsoldout/home)
