from settings import * 
from renderers import Render, Mkd_renderer, Mkd_html
import pdb

# META:
#    Author: Xiayun Sun
#    Email:  xiayun.sun@gmail.com
#

# TODO:
#    header line like '=' and '-'    DONE
#    HTML entities                   NO
#    horizontal rules                DONE
#    images                          NO
#    reference-style links           DONE
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
        if data[i] not in ' \t':
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

def tag_length(data):
    # only deal with auto link
    size = len(data)
    i = 0
    if size < 3:
        return 0

    while i < size and data[i] != '>':
        i += 1
    if i >= size:
        return 0
    if 'http' not in ''.join(data[:i]):
        return 0
    return i+1

# These are "char_triggers"

def char_langle_tag(ob, rndr, data, offset):
    size = len(data)
    ret = 0
    end = tag_length(data)

    if end:
        if 'autolink' in dir(rndr.make):
            ret = rndr.make.autolink(ob, data[1:end-1])
    if not ret:
        return 0
    else:
        return end

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

def get_link_ref(rndr, link, title, data): # data is id
    size = len(data)
    lr = {}
    for l in rndr.refs:
        if build_ref_id(data) == l['id']:
            lr = l
            break
    if not lr:
        return -1

    link.extend(list(l['link']))
    title.extend(list(l['title']))

    return 0

def get_link_inline(link, title, data):

    size = len(data)

    if size <= 0:
        return 0

    i = 0
    link_b = link_e = title_e = title_b = 0

    while i < size and data[i] in ' \t\n':
        i += 1
    link_b = i
    while i < size and data[i] != '"' and data[i] != "'":
        i += 1
    link_e = i

    if i < size and (data[i] == "'" or data[i] == '"'):
        i += 1
        title_b = i

        title_e = size - 1
        while  title_e > title_b and data[title_e] in ' \t\n':
            title_e -= 1

        if data[title_e] != "'" and data[title_e] != '"':
            title_b = title_e = 0
            link_e = i

    while link_e < size and link_e > link_b and data[link_e - 1] in ' \t\n':
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
    global normal_text
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

    while i < size and data[i] in ' \t\n':
        i += 1
    
    content = new_work_buffer(rndr)
    link = new_work_buffer(rndr)
    title = new_work_buffer(rndr)
    ret = 0
    
    if i < size and data[i] == '(':
        span_end = i
        while span_end < size and not (data[span_end] == ')' and (span_end == i or data[span_end - 1] != '\\')):
            span_end += 1
        
        if span_end >= size or get_link_inline(link, title, data[i+1:span_end]) < 0:#TODO: duplicate ending statements

            release_work_buffer(rndr, title)
            release_work_buffer(rndr, link)
            release_work_buffer(rndr, content)
            return 0

        i = span_end + 1
    
    elif i < size and data[i] == '[': # reference style
        id_data = ''
        id_size = 0
        id_end = i
        while id_end < size and data[id_end] != ']':
            id_end += 1
        if id_end >= size:
            release_work_buffer(rndr, title)
            release_work_buffer(rndr, link)
            release_work_buffer(rndr, content)
            return 0

        if i + 1 == id_end:
            id_data = data[1:txt_e]
        else:
            id_data = data[i+1:id_end]
        
        j = get_link_ref(rndr, link, title, id_data)

        if j < 0:
            release_work_buffer(rndr, title)
            release_work_buffer(rndr, link)
            release_work_buffer(rndr, content)
            return 0
        i = id_end + 1          
    
    else: # not a link
        j = get_link_ref(rndr, link, title, data[1:txt_e])
        if j < 0:
            release_work_buffer(rndr, title)
            release_work_buffer(rndr, link)
            release_work_buffer(rndr, content)
            return 0

        i = txt_e + 1       

    if txt_e > 1:
        normal_text = 1
        parse_inline(content, rndr, data[1:txt_e])
    
    ret = rndr.make.link(ob, link, title, content)

    release_work_buffer(rndr, title)
    release_work_buffer(rndr, link)
    release_work_buffer(rndr, content)
    
    normal_text = 0
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
    while f_begin < end and data[f_begin] in ' \t':
        f_begin += 1
    f_end = end - nb
    while f_end > nb and data[f_end - 1] in ' \t':
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
        if data[1] in ' \t\n' or ret == 0:
            return 0
        return ret + 1

    if size > 3 and data[1] == c and data[2] != c:
        ret = parse_emph2(ob, rndr, data[2:], c)
        if data[2] in ' \t\n' or ret == 0:
            return 0
        return ret + 2
    if size > 4 and data[1] == c and data[2] == c and data[3] != c:
        ret = parse_emph3(ob, rndr, data[3:], c)
        if data[3] in ' \t\n' or ret == 0:
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
        if data[i] == c and data[i-1] not in ' \t\n':
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
        if i+1 < size and data[i] == c and data[i+1] == c and i and data[i-1] not in ' \t\n':
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
        if data[i] != c or data[i-1] in ' \t\n':
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
        while i < size and data[i] != c and data[i] not in '`[':
            i += 1
        if i >= size:
            return 0
        if data[i] == c:
            return i

        if i and data[i-1] == '\\':
            i += 1
            continue
        
normal_text = 0
def parse_inline(ob, rndr, data):
    global normal_text
    size = len(data)
    i = end = 0

    if len(rndr.work) > rndr.make.max_work_stack:
        if size:
            ob.append(''.join(data))
        return None

    while i < size:
        while end < size:
            action = rndr.active_char.get(data[end], None)
            if action is not None and not normal_text:
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

def is_hrule(data):
    i = n = 0
    size = len(data)
    if size < 3:
        return 0
    while i <= 2 and data[i] == ' ': #remove at most 3 spaces
        i += 1 

    if i + 2 >= size or (data[i] not in '*-_'):
        return 0
    c = data[i]

    while i < size and data[i] != '\n':
        if data[i] == c:
            n += 1
        elif data[i] not in ' \t':
            return 0
        i += 1

    return n >= 3

def build_ref_id(data):
    return ''.join([c for c in data if not c in ' \n\t'])

def is_ref(data, peg, end, last, refs):
    i = id_offset = id_end = link_offset = link_end = title_offset = title_end = line_end = 0
    lr = {} # {link_ref object}

    if peg + 3 >= end:
        return 0
    while i <= 2 and data[peg+i] == ' ':
        i += 1
    if i == 3 and data[peg+3] == ' ':
        return 0
    
    i += peg
    if data[i] != '[':
        return 0
    i += 1
    id_offset = i
    while i < end and data[i] not in '\n]':
        i += 1
    if i >= end or data[i] != ']':
        return 0
    id_end = i

    i += 1
    if i >= end or data[i] != ':':
        return 0
    i += 1
    while i < end and data[i] in ' \t':
        i += 1
    if i < end and data[i] == '\n':
        i += 1
    while i < end and data[i] in ' \t':
        i += 1
    if i >= end:
        return 0

    if data[i] == '<':
        i += 1
    link_offset = i
    while i < end and data[i] not in ' \t\n':
        i += 1
    if data[i-1] == '>':
        link_end = i - 1
    else:
        link_end = i

    while i < end and data[i] in ' \t':
        i += 1
    if i < end and data[i] not in '\n(' and data[i] != "'" and data[i] != '"':
        return 0
    line_end = 0
    
    if i >= end or data[i] == '\n':
        line_end = i
    if i + 1 < end and data[i] == '\n':
        line_end = i + 1

    if line_end:
        i = line_end + 1
        while i < end and data[i] in ' \t':
            i += 1
    
    if i + 1 < end and (data[i] == "'" or data[i] == '"' or data[i] == '('):
        i += 1
        title_offset = i
        while i < end and data[i] != '\n':
            i += 1
        title_end = i + (i + 1 < end and data[i] == '\n')
        i -= 1
        while i > title_offset and data[i] in ' \t':
            i -= 1
        if i > title_offset and (data[i] == '"' or data[i] == ')' or data[i] == "'"):
            line_end = title_end
            title_end = i
    
    if not line_end:
        return 0
    lr['id'] = build_ref_id(data[id_offset:id_end])
    lr['link'] = data[link_offset:link_end]
    lr['title'] = data[title_offset:title_end]
    refs.append(lr)
    return line_end

def is_headerline(data):
    size = len(data)
    i = 0

    if data[i] == '=':
        i = 1
        while i < size and data[i] == '=':
            i += 1
        while i < size and data[i] in ' \t':
            i += 1
        if i >= size or data[i] == '\n':
            return 1
        else:
            return 0
    if data[i] == '-':
        i = 1
        while i < size and data[i] == '-':
            i += 1
        while i < size and data[i] in ' \t':
            i += 1
        if i >= size or data[i] == '\n':
            return 2
        else:
            return 0

    return 0

# prefix code. returns prefix length for block code; they all eat the FIRST special char only to allow nesting

def prefix_code(data): 
    size = len(data)
    
    # allow both \t and space
    if size > 0 and data[0] == '\t':
        return 1
    if size > 3 and ''.join(data[0:4]) == '    ':
        return 4
    return 0
   
def prefix_quote(data):
    size = len(data)
    i = 0

    while i < size and i <= 3 and data[i] == ' ': # allow 3 spaces
        i += 1
    
    if i < size and data[i] == '>':
        if i+1 < size and (data[i+1] in ' \t'): # allow space after >
            return i + 2
        else:
            return i + 1
    else:
        return 0

def prefix_oli(data):
    size = len(data)
    i = 0
    while i <= 2 and data[i] == ' ': 
        i += 1
    
    if i >= size or not data[i].isdigit():
        return 0
    while i < size and data[i].isdigit():
        i += 1
    if i + 1 >= size or data[i] != '.' or data[i+1] not in ' \t':
        return 0
    i += 2

    while i < size and data[i] in ' \t':
        i += 1
    return i

def prefix_uli(data):
    size = len(data)
    i = 0
    while i <= 2 and data[i] == ' ':
        i += 1
    if i + 1 >= size or (data[i] not in '*+-') or (data[i+1] not in ' \t'):
        return 0
    i += 2
    while i < size and (data[i] == ' ' or data[i] == '\t'):
        i += 1
    return i

# All parse_* functions return #chars consumed

pre_empty = MKD_LIST_FIRSTPARSE #

def parse_listitem(ob, rndr, data, flag):
    global pre_empty
    size = len(data)
    pre_space = has_inside_empty = in_empty = sublist = 0

    while pre_space < size and pre_space <= 2 and data[pre_space] == ' ':
        pre_space += 1
    
    peg = prefix_uli(data) or prefix_oli(data) # get rid of *
    if not peg:
        return 0

    end = peg
    while end < size and data[end-1] != '\n': # only stop at first \n!
        end += 1
         
    listitem_buf = new_work_buffer(rndr)
    inter = new_work_buffer(rndr)

    listitem_buf.extend(data[peg:end]) # put item till first \n on to buffer
    peg = end
    
    while peg < size: # parse rest
        end += 1
        while end < size and data[end-1] != '\n':
            end += 1
        if is_empty(data[peg:end]):
            in_empty = 1
            peg = end
            continue
        
        i = 0

        while i < end - peg and i <= 3 and data[peg + i] == ' ':
            i += 1
        pre = i
        if data[peg] == '\t': # 1 tab = 4 spaces
            i = 1
            pre = 8
        
        if pre_empty == MKD_LIST_FIRSTPARSE: # parse first list, update pre_empty
            pre_empty = in_empty
        
        if (prefix_uli(data[peg+i:end]) and not is_hrule(data[peg+i:end])) or prefix_oli(data[peg+i:end]): # a list symbol appears again
            if in_empty:
                has_inside_empty = 1
            if pre == pre_space:
                break # same level
            if not sublist: # diff level, has sublist
                sublist = len(listitem_buf) # sublist is the starting pos of sublist

        elif in_empty and i < 4 and data[peg] != '\t':
            flag = MKD_LIST_END
            break
        elif in_empty:
            listitem_buf.append('\n') # ensure <p>
            has_inside_empty = 1
        
        in_empty = 0
        listitem_buf.extend(data[peg+i:end])
        peg = end
    
    if has_inside_empty: # it's a block
        flag = MKD_LIST_BLOCK
    
    if flag == MKD_LIST_BLOCK:
        if sublist and sublist < len(listitem_buf):
            parse_block(inter, rndr, listitem_buf[:sublist])
            parse_block(inter, rndr, listitem_buf[sublist:])
        else:
            parse_block(inter, rndr, listitem_buf)
    else:
        if sublist and sublist < len(listitem_buf):
            if pre_empty:
                parse_block(inter, rndr, listitem_buf[:sublist])
            else:
                parse_inline(inter, rndr, listitem_buf[:sublist])
                parse_block(inter, rndr, listitem_buf[sublist:])
        else:
            if pre_empty:
                parse_block(inter, rndr, listitem_buf)
            else:
                parse_inline(inter, rndr, listitem_buf)

    if 'listitem' in dir(rndr.make):
        rndr.make.listitem(ob, inter, flag)
    release_work_buffer(rndr, inter)
    release_work_buffer(rndr, listitem_buf)
    pre_empty = has_inside_empty #update global pre_empty
    return peg

def parse_list(ob, rndr, data, flag): #TODO: UGLY..better than flags? 
    size = len(data)
    list_buf = new_work_buffer(rndr)
    i = j = 0

    while i < size:
        j = parse_listitem(list_buf, rndr, data[i:size], flag)
        i += j
        if not j or flag == MKD_LIST_END:
            break
    
    if 'list' in dir(rndr.make):
        rndr.make.list(ob, ''.join(list_buf), flag)
    release_work_buffer(rndr, list_buf)
    
    return i

def parse_blockcode(ob, rndr, data):
    size = len(data)

    blockcode_buf = new_work_buffer(rndr)

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
                blockcode_buf.append('\n')
            else:
                blockcode_buf.extend(data[peg:end])

        peg = end

    while len(blockcode_buf) > 0 and blockcode_buf[-1] == '\n':
        blockcode_buf.pop()
    blockcode_buf.append('\n') #ensure only 1 \n

    if 'blockcode' in dir(rndr.make):
        rndr.make.blockcode(ob, blockcode_buf)
    release_work_buffer(rndr, blockcode_buf)

    return peg


def parse_atxheader(ob, rndr, data):
    size = len(data)
    level = end = skip = peg = span_size = i = 0 #TODO 4: is this good style?

    while level < size and level < 6 and data[level] == '#':
        level += 1
    
    i = level
    while i < size and (data[i] in ' \t'): # skip spaces after ###s
        i += 1

    peg = end = i # start
    
    while end < size and data[end] != '\n':
        end += 1
    skip = end # skip marks "far-end"

    while end and (data[end-1] in ' \t#'):
        end -= 1

    span_size = end - peg

    if 'header' in dir(rndr.make):
        header_buf = new_work_buffer(rndr)
        parse_inline(header_buf, rndr, data[peg:end])
        rndr.make.header(ob, header_buf, level)
        release_work_buffer(rndr, header_buf)

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
        if (i and data[i] == '#') or is_hrule(data[i:size]):
            end = i
            break
        if i and data[i] == '>':
            end = i
            break
        i = end
    
    wsize = i

    while wsize > 0 and data[wsize-1] == '\n':
        wsize -= 1 # peg pointing to '\n'
    
    if not level: # pure text
        tmp = new_work_buffer(rndr)
        
        parse_inline(tmp, rndr, data[: wsize])
        
        if 'paragraph' in dir(rndr.make):
            rndr.make.paragraph(ob, tmp)
        release_work_buffer(rndr, tmp)
    else: #headerline
        if wsize:
            peg = j = 0
            i = wsize
            wsize -= 1
            while wsize and data[wsize] != '\n': #get content after header
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
    blockquote_buf = new_work_buffer(rndr)

    while peg < size:
        end = peg + 1
        while end < size and data[end-1] != '\n':
            end += 1
        pre = prefix_quote(data[peg:end])
        if pre:
            peg += pre
        elif is_empty(data[peg:end]) and (end >= size or (prefix_quote(data[end:size]) == 0 and not is_empty(data[end:size]))):
            break

        work_data += data[peg:end].copy()
        peg = end
    
    parse_block(blockquote_buf, rndr, work_data)
    if 'blockquote' in dir(rndr.make):
        rndr.make.blockquote(ob, blockquote_buf)
    
    release_work_buffer(rndr, blockquote_buf)

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
        elif is_empty(txt_data) != 0: #TODO 3: can I avoid calling twice?
            peg += is_empty(txt_data)
        elif is_hrule(txt_data):
            if 'hrule' in dir(rndr.make): # TODO: better way than `in dir(object)` to detect a method?
                rndr.make.hrule(ob)
            while peg < size and data[peg] != '\n':
                peg += 1
            peg += 1
        elif prefix_quote(txt_data):
            peg += parse_blockquote(ob, rndr, txt_data)
        elif prefix_code(txt_data):
            peg += parse_blockcode(ob, rndr, txt_data)
        elif prefix_oli(txt_data):
            peg += parse_list(ob, rndr, txt_data, MKD_LIST_ORDERED)
        elif prefix_uli(txt_data):
            peg += parse_list(ob, rndr, txt_data, MKD_LIST_UNORDERED)
        else:
            # take out leading spaces
            while peg < size and (data[peg] in ' \t'):
                peg += 1
            txt_data = data[peg:]
            peg += parse_paragraph(ob, rndr, txt_data)

#########################
# MAIN FUNCTION         #
#########################

def markdown(ib, rndrer): 
    global pre_empty
    pre_empty = MKD_LIST_FIRSTPARSE 
    rndr = Render(make = rndrer)
    text = []
    ob = []
    start = end = 0
    
    size = len(ib)

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
    rndr.active_char['<'] = char_langle_tag

    # first pass, copy ib to text, add one \n per new line, add a final \n if not present
    #TODO 1: start-end style + while loops
    while start < size:
        ref_end = is_ref(ib, start, size, end, rndr.refs) # is_ref returns end position
        if ref_end:
            end = ref_end
            start = end
        else:
            end = start 
            while end < size and ib[end] != '\n':
                end += 1
            if end > start:
                text.extend(ib[start:end])
            while end < size and ib[end] == '\n':
                if end + 1 < len(ib) and ib[end+1] != '\n':
                    text.append('\n')
                if end + 2 < len(ib) and ib[end+1] == '\n' and ib[end+2] != '\n':
                    text.append('\n')
                end += 1
            start = end

    if rndr.refs: # sort
        rndr.refs.sort(key = lambda x: str.lower(x['id']))
    
#    print(rndr.refs)

    if text[-1] != '\n':
        text.append('\n')
    # second pass: actual rendering
    
    parse_block(ob, rndr, text)
    if "epilog" in dir(rndr.make):
        rndr.make.epilog(ob)

    assert len(rndr.work) == 0
    return ''.join(ob)

def test():
    with open('testsuite/gruber/Ordered and unordered lists.text', 'r') as f:
        text = f.read()
    text2 = '''
* list1
* list3
'''
    ob = markdown(text2, Mkd_html())
    print(ob)

if __name__ == '__main__':
    test()
