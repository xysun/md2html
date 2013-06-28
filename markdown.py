from settings import * 
from renderers import Render, Mkd_renderer, Mkd_html
import pdb

# META:
#    Author: Xiayun Sun
#    Email:  xiayun.sun@gmail.com
#
# PROGRESS:
#    blockquote                      DONE
#    code (block & inline)           DONE
#    header                          DONE
#    link (only []())                DONE
#    list (ordered and unordered)
#         ordered                    DONE
#         unordered                  DONE 
#    emphasis(single/double/triple)  DONE
#    linebreak                       DONE 
#
# TODO:
#    header line like '=' and '-'    DONE
#    HTML entities                   NO
#    horizontal rules (?)            PRIORITY3
#    images                          PRIORITY4
#    reference-style links (?)       PRIORITY2
#    original html tags              NO
#
# NOTE:
#    Tabs are expanded to 4 spaces
#    I've modified some of Gruber's test cases, but ONLY for non-significant spaces/newlines
#
#
################################
# UTILITY FUNCTIONS            #
################################

def is_empty(data): # return line length when it is empty, 0 otherwise
    size = len(data)
    i = 0
    while i < size and data[i] != '\n':
        if data[i] != ' ' and data[i] != '\t':
            return 0
        i += 1
    return i + 1

def new_work_buffer(rndr):
    tmp = []
    rndr.work.append(tmp)
    return tmp

def release_work_buffer(rndr, buf): 
    assert len(rndr.work) > 0 and rndr.work[-1] == buf
    rndr.work.pop()


################################
# SPAN-LEVEL PARSING FUNCTIONS #
# They return #char consumed   #
################################

# These are "char_triggers"

def char_escape(ob, rndr, data, offset):
    size = len(data)
    if size > 1:
        if 'normal_text' in dir(rndr.make):
            rndr.make.normal_text(ob, data[1:2])
        else:
            ob.append(data[1])
    return 2

def char_linebreak(ob, rndr, data, offset):
    size = len(data)
    if len(offset) < 2 or offset[-1] != ' ' or offset[-2] != ' ':
        return 0
    # remove all trailing spaces
    while len(ob) > 0 and ob[-1] == ' ':
        ob.pop()

    return rndr.make.linebreak(ob)

def get_link_inline(link, title, data):

    size = len(data)

    if size <= 0:
        return 0

    i = 0
    link_b = link_e = title_e = title_b = 0

    while i < size and (data[i] == ' ' or data[i] == '\t' or data[i] == '\n'):
        i += 1
    link_b = i
    while i < size and data[i] != '"' and data[i] != "'":
        i += 1
    link_e = i

    if i < size and (data[i] == "'" or data[i] == '"'):
        i += 1
        title_b = i

        title_e = size - 1
        while  title_e > title_b and (data[title_e] == ' ' or data[title_e] == '\t' or data[title_e] == '\n'):
            title_e -= 1

        if data[title_e] != "'" and data[title_e] != '"':
            title_b = title_e = 0
            link_e = i

    while link_e < size and link_e > link_b and (data[link_e - 1] == ' ' or data[link_e - 1] == '\t' or data[link_e - 1] == '\n'):
        link_e -= 1
    
    if data[link_b] == '<':
        link_b += 1
    if data[link_e - 1] == '>':
        link_e -= 1

    i = link_b
    while i < link_e:
        mark = i
        while i < link_e and data[i] != '\\':
            i += 1

        link.extend(data[mark:i])
        while i < link_e and data[i] == '\\':
            i += 1

    if title_e > title_b:
        title.extend(data[title_b:title_e])

    return 0


def char_link(ob, rndr, data, offset):
    size = len(data)

    if 'link' not in dir(rndr.make):
        return 0

    level = i = 1
    while i < size:
        if data[i-1] == '\\':
            continue
        elif data[i] == '[':
            level += 1
        elif data[i] == ']':
            level -= 1
            if level <= 0:
                break
        i += 1
    if i >= size:
        return 0
    txt_e = i
    i += 1
    
    content = new_work_buffer(rndr)
    link = new_work_buffer(rndr)
    title = new_work_buffer(rndr)
    ret = 0

    if i < size and data[i] == '(':
        span_end = i
        while span_end < size and not (data[span_end] == ')' and (span_end == i or data[span_end - 1] != '\\')):
            span_end += 1
        
        if span_end >= size or get_link_inline(link, title, data[i+1:span_end]) < 0:
            release_work_buffer(rndr, title)
            release_work_buffer(rndr, link)
            release_work_buffer(rndr, content)

            return i if not ret else 0

        i = span_end + 1
    
    elif data[i] != '(': # not a link
        release_work_buffer(rndr, title)
        release_work_buffer(rndr, link)
        release_work_buffer(rndr, content)
       
        return 0

    if txt_e > 1:
        parse_inline(content, rndr, data[1:txt_e])
    
    ret = rndr.make.link(ob, link, title, content)

    release_work_buffer(rndr, title)
    release_work_buffer(rndr, link)
    release_work_buffer(rndr, content)

    return i if ret else 0

def char_codespan(ob, rndr, data, offset):
    size = len(data)
    nb = f_begin = f_end = i = 0

    while nb < size and data[nb] == '`':
        nb += 1
    end = nb
    while end < size and i < nb:
        if data[end] == '`':
            i += 1
        else:
            i = 0
        end += 1
    if i < nb and end >= size:
        return 0

    f_begin = nb
    while f_begin < end and (data[f_begin] == ' ' or data[f_begin] == '\t'):
        f_begin += 1
    f_end = end - nb
    while f_end > nb and (data[f_end - 1] == ' ' or data[f_end-1] == '\t'):
        f_end -= 1

    if f_begin < f_end:
        if not rndr.make.codespan(ob, data[f_begin:f_end]):
            end = 0
    else:
        if not rndr.make.codespan(ob, 0):
            end = 0

    return end

def char_emphasis(ob, rndr, data, offset):
    size = len(data)
    c = data[0]
    ret = 0
    
    
    if size > 2 and data[1] != c:
        # whitespace cannot follow an opening emphasis
        ret = parse_emph1(ob, rndr, data[1:],  c)
        if data[1] == ' ' or data[1] == '\t' or data[1] == '\n' or ret == 0:
            return 0
        return ret + 1

    if size > 3 and data[1] == c and data[2] != c:
        ret = parse_emph2(ob, rndr, data[2:], c)
        if data[2] == ' ' or data[2] == '\t' or data[2] == '\n' or ret == 0:
            return 0
        return ret + 2
    if size > 4 and data[1] == c and data[2] == c and data[3] != c:
        ret = parse_emph3(ob, rndr, data[3:], c)
        if data[3] == ' ' or data[3] == '\t' or data[3] == '\n' or ret == 0:
            return 0
        return ret + 3

def parse_emph1(ob, rndr, data, c):
    size = len(data)
    i = 0

    if 'emphasis' not in dir(rndr.make):
        return 0
    
    if size > 1 and data[0] == c and data[1] == c:
        i = 1
    
    while i < size:
        length = find_emph_char(data[i:], c)
        if not length:
            return 0
        
        i += length
        if i >= size:
            return 0

        if i + 1 < size and data[i + 1] == c:
            i += 1
            continue

        # no space after emphasis
        if data[i] == c and data[i-1] != ' ' and data[i-1] != '\t' and data[i-1] != '\n':
            work = new_work_buffer(rndr)
            parse_inline(work, rndr, data[:i])
            r = rndr.make.emphasis(ob, work, c)
            release_work_buffer(rndr, work)
            if r is None:
                return 0
            else:
                return i + 1
    return 0

def parse_emph2(ob, rndr, data, c):
    size = len(data)
    i = 0

    if 'double_emphasis' not in dir(rndr.make):
        return 0
    
    while i < size:
        length = find_emph_char(data[i:], c)
        if not length:
            return 0
        i += length
        if i+1 < size and data[i] == c and data[i+1] == c and i and data[i-1] != ' ' and data[i-1] != '\t' and data[i-1] != '\n':
            work = new_work_buffer(rndr)
            parse_inline(work, rndr, data[:i])
            r = rndr.make.double_emphasis(ob, work, c)
            release_work_buffer(rndr, work)

            return 0 if r is None else i + 2
    return 0

def parse_emph3(ob, rndr, data, c):
    size = len(data)
    i = length = 0
    
    while i < size:
        length = find_emph_char(data[i:], c)
        if not length:
            return 0
        i += length
        if data[i] != c or data[i-1] == ' ' or data[i-1] == '\t' or data[i-1] == '\n':
            continue
        if i+2 < size and data[i+1] == c and data[i+2] == c and 'triple_emphasis' in dir(rndr.make):
            work = new_work_buffer(rndr)
            parse_inline(work, rndr, data[:i])
            r = rndr.make.triple_emphasis(ob, work, c)
            release_work_buffer(rndr, work)

            return 0 if r is None else i + 3
    return 0

def find_emph_char(data, c): # find the next emph char
    size = len(data)
    i = 0
    while i < size:
        while i < size and data[i] != c and data[i] != '`' and data[i] != '[':
            i += 1
        if i >= size:
            return 0
        if data[i] == c:
            return i

        if i and data[i-1] == '\\':
            i += 1
            continue
        

def parse_inline(ob, rndr, data):
    size = len(data)
    i = 0
    end = 0

    if len(rndr.work) > rndr.make.max_work_stack:
        if size:
            ob.append(''.join(data))
        return None

    while i < size:
        while end < size:
            action = rndr.active_char.get(data[end], None)
            if action is not None:
                break
            end += 1

        if 'normal_text' in dir(rndr.make):
            rndr.make.normal_text(ob, data[i:end])
        else:
            ob.append(''.join(data[i:end]))

        if end >= size:
            break
        i = end

        # calling the trigger
        end = action(ob, rndr, data[i:], data[:i])
        if not end:
            end = i + 1
        else:
            i += end
            end = i
    

#################################
# BLOCK-LEVEL PARSING FUNCTIONS #
################################

def is_headerline(data):
    size = len(data)
    i = 0

    if data[i] == '=':
        i = 1
        while i < size and data[i] == '=':
            i += 1
        while i < size and (data[i] == ' ' or data[i] == '\t'):
            i += 1
        if i >= size or data[i] == '\n':
            return 1
        else:
            return 0
    if data[i] == '-':
        i = 1
        while i < size and data[i] == '-':
            i += 1
        while i < size and (data[i] == ' ' or data[i] == '\t'):
            i += 1
        if i >= size or data[i] == '\n':
            return 2
        else:
            return 0

    return 0

# prefix code. returns prefix length for block code; they all eat the FIRST special char only to allow nesting

def prefix_code(data): 
    size = len(data)

    if size > 0 and data[0] == '\t':
        return 1
    if size > 3 and ''.join(data[0:4]) == '    ':
        return 4
    
    return 0
   
def prefix_quote(data):
    size = len(data)
    i = 0

    if i < size and data[i] == ' ':
        i += 1
    if i < size and data[i] == ' ':
        i += 1
    if i < size and data[i] == ' ':
        i += 1
    if i < size and data[i] == '>':
        if i+1 < size and (data[i+1] == ' ' or data[i+1] == '\t'):
            return i + 2
        else:
            return i + 1
    else:
        return 0

def prefix_oli(data):
    size = len(data)
    i = 0
    if i < size and data[i] == ' ':
        i += 1
    if i < size and data[i] == ' ':
        i += 1
    if i < size and data[i] == ' ':
        i += 1
    
    if i >= size or data[i] < '0' or data[i] > '9':
        return 0
    while i < size and data[i] >= '0' and data[i] <= '9':
        i += 1
    if i + 1 >= size or data[i] != '.' or (data[i+1] != ' ' and data[i+1] != '\t'):
        return 0
    i += 2

    while i < size and (data[i] == ' ' or data[i] == '\t'):
        i += 1
    return i

def prefix_uli(data):
    size = len(data)
    i = 0
    if i < size and data[i] == ' ':
        i += 1
    if i < size and data[i] == ' ':
        i += 1
    if i < size and data[i] == ' ':
        i += 1
    if i + 1 >= size or (data[i] != '*' and data[i] != '+' and data[i] != '-') or (data[i+1] != ' ' and data[i+1] != '\t'):
        return 0
    i += 2
    while i < size and (data[i] == ' ' or data[i] == '\t'):
        i += 1
    return i

# All parse_* functions return #chars consumed

pre_empty = 0

def parse_listitem(ob, rndr, data, flag):
    global pre_empty
    size = len(data)
    orgpre = has_inside_empty = in_empty = sublist = 0

    if size > 1 and data[0] == ' ':
        orgpre = 1
        if size > 2 and data[1] == ' ':
            orgpre = 2
            if size > 3 and data[2] == ' ':
                orgpre = 3
    
    peg = prefix_uli(data) or prefix_oli(data)
    if not peg:
        return 0

    end = peg
    while end < size and data[end-1] != '\n':
        end += 1
    
    work = new_work_buffer(rndr)
    inter = new_work_buffer(rndr)

    work.extend(data[peg:end])
    peg = end
    
    
    while peg < size:
        end += 1
        while end < size and data[end-1] != '\n':
            end += 1
        if is_empty(data[peg:end]):
            in_empty = 1
            peg = end
            continue
        
        i = 0

        if end - peg > 1 and data[peg] == ' ':
            i = 1
            if end - peg > 2 and data[peg + 1] == ' ':
                i = 2
                if end - peg > 3 and data[peg + 2] == ' ':
                    i = 3
                    if end - peg > 4 and data[peg + 3] == ' ':
                        i = 4
        pre = i
        if data[peg] == '\t':
            i = 1
            pre = 8
        
        pre_empty = in_empty
        
        if prefix_uli(data[peg+i:end]) or prefix_oli(data[peg+i:end]):
            if in_empty:
                has_inside_empty = 1
            if pre == orgpre:
                break
            if not sublist:
                sublist = len(work)

        elif in_empty and i < 4 and data[peg] != '\t':
            flag = flag | MKD_LI_END
            break
        elif in_empty:
            work.append('\n')
            has_inside_empty = 1
        
        in_empty = 0

        work.extend(data[peg+i:end])
        peg = end
    
    if has_inside_empty:
        flag |= MKD_LI_BLOCK
    
    if (flag & MKD_LI_BLOCK):
        if sublist and sublist < len(work):
            parse_block(inter, rndr, work[:sublist])
            parse_block(inter, rndr, work[sublist:])
        else:
            parse_block(inter, rndr, work)
    else:
        if sublist and sublist < len(work):
            if pre_empty:
                parse_block(inter, rndr, work[:sublist])
            else:
                parse_inline(inter, rndr, work[:sublist])
            parse_block(inter, rndr, work[sublist:])
        else:
            if pre_empty:
                parse_block(inter, rndr, work)
            else:
                parse_inline(inter, rndr, work)

    if 'listitem' in dir(rndr.make):
        rndr.make.listitem(ob, inter, flag)
    release_work_buffer(rndr, inter)
    release_work_buffer(rndr, work)
    return peg

def parse_list(ob, rndr, data, flag):
    size = len(data)
    work = new_work_buffer(rndr)
    i = j = 0

    while i < size:
        j = parse_listitem(work, rndr, data[i:size], flag)
        i += j
        if not j or (flag & MKD_LI_END):
            break
    
    if 'list' in dir(rndr.make):
        rndr.make.list(ob, ''.join(work), flag)
    release_work_buffer(rndr, work)
    
    return i
    

def parse_blockcode(ob, rndr, data):
    size = len(data)

    work = new_work_buffer(rndr)

    peg = 0
    while peg < size:
        end = peg + 1
        while end < size and data[end-1] != '\n':
            end += 1
        pre = prefix_code(data[peg:end])
        if pre:
            peg += pre
        elif not is_empty(data[peg:end]): # non-empty non-prefixed line breaks pre
            break

        if peg < end:
            if is_empty(data[peg:end]):
                work.append('\n')
            else:
                work.extend(data[peg:end])

        peg = end

    while len(work) > 0 and work[-1] == '\n':
        work.pop()
    work.append('\n')

    if 'blockcode' in dir(rndr.make):
        rndr.make.blockcode(ob, work)
    release_work_buffer(rndr, work)

    return peg


def parse_atxheader(ob, rndr, data):
    size = len(data)
    level = end = skip = span_peg = span_size = 0

    if not size or data[0] != '#':
        return 0

    while level < size and level < 6 and data[level] == '#':
        level += 1
    
    i = level
    while i < size and (data[i] == ' ' or data[i] == '\t'):
        i += 1

    span_peg = i # start

    end = i
    while end < size and data[end] != '\n':
        end += 1
    skip = end # end

    if end <= i: # blank ### TODO: do we insert <h>?
        return parse_paragraph(ob, rndr, data)

    while end and data[end-1] == '#':
        end -= 1

    while end and (data[end - 1] == ' ' or data[end - 1] == '\t'):
        end -= 1

    if end <= i:
        parse_paragraph(ob, rndr, data)

    span_size = end - span_peg

    if 'header' in dir(rndr.make):
        span = new_work_buffer(rndr)
        parse_inline(span, rndr, data[span_peg:end])
        rndr.make.header(ob, span, level)
        release_work_buffer(rndr, span)

    return skip


def parse_paragraph(ob, rndr, data):
    size = len(data)
    i = 0
    
    while i < size:
        end = i + 1
        while end < size and data[end-1] != '\n':
            end += 1
        level = is_headerline(data[i:size])
        if is_empty(data[i:]) or level != 0: 
            break
        if i and data[i] == '#':
            end = i
            break
        if i and data[i] == '>':
            end = i
            break
        i = end
    
    wsize = i

    while wsize > 0 and data[wsize-1] == '\n':
        wsize -= 1 # peg pointing to '\n'
    
    if not level:
        tmp = new_work_buffer(rndr)
        
        parse_inline(tmp, rndr, data[: wsize])
        
        if 'paragraph' in dir(rndr.make):
            rndr.make.paragraph(ob, tmp)
        release_work_buffer(rndr, tmp)
    else:
        if wsize:
            peg = j = 0
            i = wsize
            wsize -= 1
            while wsize and data[wsize] != '\n':
                wsize -= 1
            peg = wsize + 1
            while wsize and data[wsize-1] == '\n':
                wsize -= 1
            if wsize:
                tmp = new_work_buffer(rndr)
                parse_inline(tmp, rndr, data[j:j+wsize])
                if 'paragraph' in dir(rndr.make):
                    rndr.make.paragraph(ob, tmp)
                release_work_buffer(rndr, tmp)
                j += peg
                wsize = i - peg
            else:
                wsize = i
        if 'header' in dir(rndr.make):
            span = new_work_buffer(rndr)
            parse_inline(span, rndr, data[:wsize])
            rndr.make.header(ob, span, level)
            release_work_buffer(rndr, span)

    return end

def parse_blockquote(ob, rndr, data):
    size = len(data)
    work_data = []
    
    peg = end = pre = 0
    out = new_work_buffer(rndr)

    while peg < size:
        end = peg + 1
        while end < size and data[end-1] != '\n':
            end += 1
        pre = prefix_quote(data[peg:end])
        if pre:
            peg += pre
        elif is_empty(data[peg:end]) and (end >= size or (prefix_quote(data[end:size]) == 0 and not is_empty(data[end:size]))):
            break


        if peg < end:
            work_data += data[peg:end].copy()
        peg = end
    
    
    parse_block(out, rndr, work_data)
    if 'blockquote' in dir(rndr.make):
        rndr.make.blockquote(ob, out)
    
    
    release_work_buffer(rndr, out)

    return end


def parse_block(ob, rndr, data): 
    size = len(data)
    
    if (len(rndr.work) > rndr.make.max_work_stack):
        if size:
            ob.append(''.join(data))
        return None

    peg = 0 # peg is the index pointer
    while (peg < size):
        txt_data = data[peg:]
        if data[peg] == '#':
            peg += parse_atxheader(ob, rndr, txt_data)
        elif is_empty(txt_data) != 0:
            peg += is_empty(txt_data)
        elif prefix_quote(txt_data):
            peg += parse_blockquote(ob, rndr, txt_data)
        elif prefix_code(txt_data):
            peg += parse_blockcode(ob, rndr, txt_data)
        elif prefix_oli(txt_data):
            peg += parse_list(ob, rndr, txt_data, MKD_LIST_ORDERED)
        elif prefix_uli(txt_data):
            peg += parse_list(ob, rndr, txt_data, 0)
        else:
            # take out leading spaces
            while peg < size and (data[peg] == ' ' or data[peg] == '\t'):
                peg += 1
            txt_data = data[peg:]
            peg += parse_paragraph(ob, rndr, txt_data)

#########################
# MAIN FUNCTION         #
#########################

def markdown(ib, rndrer): 
    rndr = Render(make = rndrer)
    text = []
    ob = []
    
    if rndr.make.max_work_stack < 1:
        rndr.make.max_work_stack = 1

    # fill active_char
    if 'emphasis' in dir(rndr.make):
        for c in rndr.make.emph_chars:
            rndr.active_char[c] = char_emphasis
    if 'codespan' in dir(rndr.make):
        rndr.active_char['`'] = char_codespan
    if 'link' in dir(rndr.make):
        rndr.active_char['['] = char_link
    if 'linebreak' in dir(rndr.make):
        rndr.active_char['\n'] = char_linebreak

    rndr.active_char['\\'] = char_escape

    # first pass, copy ib to text, add one \n per new line, add a final \n if not present
    for (i,c) in [(i, ib[i]) for i in range(len(ib))]:
        if c != '\n':
            text.append(c)
        else:
            if (i + 1 < len(ib)) and ib[i+1] != '\n':
                text.append('\n')
            elif (i + 2 < len(ib)) and ib[i+1] == '\n' and ib[i+2] != '\n':
                text.append('\n')

    if text[-1] != '\n':
        text.append('\n')
    

    # second pass: actual rendering
    
    parse_block(ob, rndr, text)
    if "epilog" in dir(rndr.make):
        rndr.make.epilog(ob)
    return ''.join(ob)

def test():
    with open('testsuite/gruber/Ordered and unordered lists.text', 'r') as f:
        text = f.read()
    text2 = '''
*   list2
    
    line2

*   list3
'''
    ob = markdown(text2, Mkd_html())
    print(ob)

if __name__ == '__main__':
    test()
