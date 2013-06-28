import unittest, pdb
from markdown import markdown
from renderers import Mkd_renderer, Mkd_html

class TestMd2HTML:

    def general(self, fname):
        with open(self.directory + fname + self.input_postfix, 'r') as f:
            src = f.read()
        with open(self.directory + fname + self.output_postfix, 'r') as f:
            out = f.read()
        
        # take out trailing '\n' in out
        while len(out) > 0 and out[-1] == '\n':
            out = out[:-1]
        
        ob = markdown(src, Mkd_html())
        self.assertEqual(out, ob)

class TestMd2HTML_gruber(TestMd2HTML, unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.directory = 'testsuite/gruber/'
        self.input_postfix = '.text'
        self.output_postfix = '.html'

    def test_all(self):
        self.general('Backslash escapes')
        self.general('Blockquotes with code blocks') 
        self.general('Code Blocks')
#        self.general('Code Spans')
        self.general('Links, inline style')
#        self.general('Links, reference style')
#        self.general('Links, shortcut references')
#        self.general('Literal quotes in titles') auto link
#        self.general('Markdown Documentation - Basics')
#        self.general('Markdown Documentation - Syntax')
#        self.general('Ordered and unordered lists')    horizontal rule
        self.general('Nested blockquotes') 
        self.general('Strong and em together')
        self.general('Tabs')
        self.general('Tidyness')


class TestMd2HTML_carlcow(TestMd2HTML, unittest.TestCase):
    def setUp(self):
        self.directory = 'testsuite/karlcow/'
        self.input_postfix = '.md'
        self.output_postfix = '.out'
    
    def test_2_paragraphs(self):
        self.general('2-paragraphs-line')
        self.general('2-paragraphs-line-tab')
        self.general('2-paragraphs-line-spaces')
        self.general('2-paragraphs-line-returns')
        self.general('2-paragraphs-hard-return')
        self.general('2-paragraphs-hard-return-spaces')
    
    def test_paragraph(self):
        self.general('paragraph-hard-return')
        self.general('paragraph-line')
        self.general('paragraph-trailing-leading-spaces')
        self.general('paragraphs-2-leading-spaces')
        self.general('paragraphs-3-leading-spaces')
        self.general('paragraphs-leading-space')
        self.general('paragraphs-trailing-spaces')

    def test_em(self):
        self.general('em-middle-word')
        self.general('em-star')
        self.general('em-underscore')
        self.general('strong-middle-word')
        self.general('strong-star')
        self.general('strong-underscore')

    def test_EOL(self):
        self.general('EOL-CR+LF')
        self.general('EOL-CR')
        self.general('EOL-LF')

    def test_ampersand(self):
        self.general('ampersand-text-flow')
        self.general('ampersand-uri') 

    def test_escape(self):
        self.general('asterisk-near-text')
        self.general('asterisk')
        self.general('backslash-escape')

    def test_header(self):
        self.general('header-level1-hash-sign-closed')
        self.general('header-level1-hash-sign-trailing-1-space')
        self.general('header-level1-hash-sign-trailing-2-spaces')
        self.general('header-level1-hash-sign')
        self.general('header-level2-hash-sign-closed')
        self.general('header-level2-hash-sign')
        self.general('header-level3-hash-sign-closed')
        self.general('header-level3-hash-sign')
        self.general('header-level4-hash-sign-closed')
        self.general('header-level4-hash-sign')
        self.general('header-level5-hash-sign-closed')
        self.general('header-level5-hash-sign')
        self.general('header-level6-hash-sign-closed')
        self.general('header-level6-hash-sign')

    def test_line_break(self):
        self.general('line-break-2-spaces')
        self.general('line-break-5-spaces')
    
    def test_link(self):
        self.general('link-bracket-paranthesis-title')
        self.general('link-bracket-paranthesis')
    
    def test_blockquote(self):
        self.general('blockquote-added-markup')
        self.general('blockquote-line-2-paragraphs')
        self.general('blockquote-line')
        self.general('blockquote-multiline-1-space-begin')
        self.general('blockquote-multiline-1-space-end') 
        self.general('blockquote-multiline')
        self.general('blockquote-multiline-2-paragraphs')
        self.general('blockquote-nested-multiplereturn-level1')
        self.general('blockquote-nested-multiplereturn')
        self.general('blockquote-nested-return-level1') 
        self.general('blockquote-nested') 

    def test_code(self):
        self.general('code-1-tab')
        self.general('code-4-spaces-escaping')
        self.general('code-4-spaces')
#        self.general('list-code') list
        self.general('inline-code-escaping-entities')
        self.general('inline-code-with-visible-backtick')
        self.general('inline-code')
    
    def test_list(self):
        self.general('unordered-list-items-dashsign')
        self.general('unordered-list-items-leading-1space')
        self.general('unordered-list-items-leading-2spaces')
        self.general('unordered-list-items-leading-3spaces')
        self.general('unordered-list-items-plussign')
        self.general('unordered-list-items')
        self.general('unordered-list-paragraphs') 
        self.general('unordered-list-unindented-content')
        self.general('unordered-list-with-indented-content')
        self.general('list-blockquote')
        self.general('list-code')
        self.general('list-multiparagraphs-tab')
        self.general('list-multiparagraphs')
        self.general('ordered-list-escaped')
        self.general('ordered-list-items-random-number')
        self.general('ordered-list-items')

if __name__ == '__main__':
    unittest.main()
