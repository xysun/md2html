import pdb
from settings import * 

class Mkd_renderer: # standard renderer
    def __init__(self):
        self.emph_chars = ['*','_']

    def lus_body_escape(self, ob, src):
        size = len(src)
        i = 0
        org = 0
        while i < size:
            org = i
            while i < size and src[i] != '<' and src[i] != '>' and src[i] != '&' and src[i] != '\t':
                i += 1
            
            if i > org:
                ob.append(''.join(src[org:i]))

            if i >= size:
                break
            elif src[i] == '<':
                ob.append('&lt;')
            elif src[i] == '\t':
                ob.append('    ')
            elif src[i] == '>':
                ob.append('&gt;')
            elif src[i] == '&':
                if i + 5 < size and src[i:i+5] == ['&', 'a', 'm', 'p', ';']:
                    ob.append(src[i])
                else:
                    ob.append('&amp;')
            i += 1
    
    def lus_attr_escape(self, ob, src):
        size = len(src)
        i = 0
        while i < size:
            org = i
            while i < size and src[i] != '<' and src[i] != '>' and src[i] != '&' and src[i] != '"':
                i += 1
            if i > org:
                ob.append(''.join(src[org:i]))
            
            if i >= size:
                break
            elif src[i] == '<':
                ob.append('&lt;')
            elif src[i] == '>':
                ob.append('&gt;')
            elif src[i] == '&':
                ob.append('&amp;')
            elif src[i] == '"':
                ob.append('&quot;')
            i += 1
        
    # rendering functions return 1 if succeed

    def autolink(self, ob, link):
        ob.append('<a href="')
        self.lus_attr_escape(ob, link)
        ob.append('">')
        self.lus_body_escape(ob, link)
        ob.append('</a>')
        return 1
    
    def blockcode(self, ob, text):
        ob.append('\n')
        ob.append('<pre><code>')
        if text:
            self.lus_body_escape(ob, text)
        ob.append('</code></pre>')
        ob.append('\n')
    
    def codespan(self, ob, text):
        ob.append('<code>')
        if text:
            self.lus_body_escape(ob, text)
        ob.append('</code>')
        return 1
    
    def list(self, ob, text, flag):
        ob.append('\n')
        if flag & MKD_LIST_ORDERED:
            ob.append('<ol>')
        else:
            ob.append('<ul>')
        ob.append('\n')
        
        if text:
            ob.append(text)
        
        if flag & MKD_LIST_ORDERED:
            ob.append('</ol>')
        else:
            ob.append('</ul>')

        ob.append('\n')


    def listitem(self, ob, text, flag):
        ob.append('<li>')
        if text:
            while text[-1] == '\n':
                text.pop()
            ob.append(''.join(text))
        ob.append('</li>')
        ob.append('\n')

    def header(self, ob, text, level):
        ob.append('\n')
        ob.append('<h' + repr(level) + '>')
        if text:
            ob.append(''.join(text))
        ob.append('</h' + repr(level) + '>')
        ob.append('\n')

    def emphasis(self, ob, text, c):
        if len(text) <= 0:
            return 0
        ob.append('<em>')
        if text:
            ob.append(''.join(text))
        ob.append('</em>')
        return 1

    def double_emphasis(self, ob, text, c):
        if not text:
            return 0
        ob.append('<strong>')
        ob.append(''.join(text))
        ob.append('</strong>')
        return 1
    
    def triple_emphasis(self, ob, text, c):
        if not text:
            return 0
        ob.append('<strong><em>')
        ob.append(''.join(text))
        ob.append('</em></strong>')
        return 1
    
    def blockquote(self, ob, text):
        ob.append('\n')
        ob.append('<blockquote>')
        if text:
            ob.append(''.join(text))
        ob.append('</blockquote>')
        ob.append('\n')
    
    def link(self, ob, link, title, content):

        ob.append('<a href="')
        if link:
            self.lus_attr_escape(ob, link)
        if title:
            ob.append('" title="')
            self.lus_attr_escape(ob, title)
        ob.append('">')
        if content:
            ob.append(''.join(content))

        ob.append('</a>')
        return 1

    def paragraph(self, ob, text):
        ob.append('\n')
        ob.append('<p>')
        if text:
            ob.append(''.join(text))
        ob.append('</p>')
        ob.append('\n')

    def normal_text(self, ob, text):
        self.lus_body_escape(ob, text) 

    def epilog(self, ob): # remove head and trailing '\n'
        i = 0
        size = len(ob)
        while i < size and ob[i][0] == '\n':
            i += 1
        del ob[:i]
        size = len(ob)
        i = size - 1
        while i >= 0 and ob[i][-1] == '\n':
            i -= 1
        del ob[i+1:]

class Mkd_html(Mkd_renderer): # html renderer
    def __init__(self):
        Mkd_renderer.__init__(self)
        self.max_work_stack = 64
    
    def linebreak(self, ob):
        # remove trailing spaces
        ob.append('<br />')
        ob.append('\n')
        return 1
    def hrule(self, ob):
        ob.append('\n')
        ob.append('<hr />')
        ob.append('\n')

class Render:
    def __init__(self, make=None, active_char={}):
        self.make = make # Mkd_renderer
        self.active_char = active_char # dict of char_trigger functions
        self.work = [] # buffer
        self.refs = [] # list of ref objects: {"id":, "link", "title"}

def test():
    m = Mkd_html()
    print(dir(m))
    print(m.emph_chars)

if __name__ == '__main__':
    test()
