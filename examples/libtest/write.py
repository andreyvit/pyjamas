import sys


def write(text):
    pass

def writebr(text):
    pass


data = ""

def write_web(text):
    global data
    data += text
    JS(" write.element.innerHTML = write.data; ")

def writebr_web(text):
    write(text + "<br />\n")

def init_web():
    JS(""" write.element = $doc.createElement("div");
           $doc.body.appendChild(write. element); """)

def write_std(text):
    print text,

def writebr_std(text):
    print text

if sys.platform in ['mozilla', 'ie6', 'opera', 'oldmoz', 'safari']:
    init_web()
    write = write_web
    writebr = writebr_web
else:
    write = write_std
    writebr = writebr_std

