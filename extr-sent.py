from lxml import etree
import sys
import bz2
import unicodedata
import re

#based on:
# http://baraujo.net/blog/?p=81


#https://docs.python.org/2/library/re.html
def myprocess(x, trace=False):
    x0=x
    rea=[
        r"\[\[.*\]\]", #"[[:]]",
        r"{{.*}}",
        r"\[http:.*\]",  # // --> forbidden
        r"\[https:.*\]",
        #        #r"\*(.*)\n",
        r"<ref.*</ref>", #one-liner ref
        #r"\'\'\'.*\'\'\'", #works
        #r"\A\*\ ",
        r"\A\*",
        r"\A\*\*",  #put a dot in end.
        r"\A\#\#",        
        r"\A\#",
        r"==.*==",       
        r"===.*===",       

        r"<p.*</p>", 
        r"<a.*</a>", 
        r"{{.*}}",       
        r"{{{.*}}}",       
        r"{{{{.*}}}}",       
        r"{.*}",       
    
        r"\'\'\'.*\'\'\'",
        r"\'\'.*\'\'", 
        r"\'\'\'\'\'.*\'\'\'\'\'",
        r"<sub>.*</sub>", #note: is deleted
        r"<sup>.*</sup>",
        r"\A\:",
        r"\A\:\:",  #emove whole line

        #r"\<\!\-\-.*\-\-\>",
        r"<!--.*-->",
        r"http:.* ", #space
        r"https:.* ", #space

        r"(--.*\(UTC\))", ## not work
        r"\#REDIRECT",
        r"\#redirect",

        r"<references/>",
        r"<noinclude>"
        r"<nowiki>.*</nowiki>"
        r"<gallery>.*</gallery>"

    ]
    
    #rea=[rea[len(rea)-1]]

    """
    todo:
    ref (multiline)
    *
    |
    #REDIRECT 
    #redirect
    (english line)
    ''
    :
    ;
    ;:
    """

    """What to do?
    vowels
    numbers 1/3
    symbols like %
    english text
    full english lines
    multipline [[ | | ]]
    connected long words
    (...)
    """

    """
    done
    * xx
    '''xyz'''
    sentence not ending with .
    titles: should we eep them?
    non-senctences.
    """

    """bad signs:
    =
    |
    """
    """
    <ul><li><em>and html
    UTC
    |-style="background: #FFFFFF; color:#000000"
    #
    <ref>
    sentence not ending with .
    <!-- 
    """
    #R.E. codes:
    #  \A  only start of the line
    #  \Z  end of string

    #todo: More from:
    # https://github.com/larsmans/wiki-dump-tools/blob/master/textonly.py    



    #x=x.replace("\n"," ")
    nx=x
    while True:
        for r in rea:
            #
            #res=re.match(r, nx)
            #if not res is None:
            #    nx=str(res.groups()[1])
            #    print '*'
            #re.sub(pattern, repl, string)

            if trace:
                res=re.match(r, nx)
                if not res is None:
                    #c=str(res.groups()[0])
                    #sys.stderr.write((c+"\n").encode('UTF-8'))
                    pass

            nx=re.sub(r, "", nx)

        if nx==x:
            break #There wont be any more change.
        else:
            pass
            #print nx #updated
        x=nx
    #print "-------------"
    if x0 != x:
        #print x0
        #print "====="
        #print x
        #print "---------------"

        #print x
        if trace:
            #sys.stderr.write(".")
            sys.stderr.write((x0+"\n----\n"+x).encode('UTF-8'))
            pass
        pass
    return x
#TAG = '{http://www.mediawiki.org/xml/export-0.8/}text'
TAG = '{http://www.mediawiki.org/xml/export-0.10/}text'

#class MyBuffer:
#    def __init__(self):
#        self.buff = []
#        self.ctr=0
#    def push(self,s):
#        self.buff.append(s.encode('UTF-8'))
#        self.ctr+=1
#    def pull(self):
#        r=""
#        while True:
#            r += **

class State1:
    def __init__(self):
         self.counter = 0
         self.parctr = 0
         self.emptyline = True
         self.parag_accum = ""
         self.newArticle = True


def outp3(p):
    p=myprocess(p,True)
    p = p.replace('.', '.\n')
    #print "a"
    #print unicode(u'\xd8').encode('UTF-8')
    #print "b"
    #p = p.replace(u'\xd8'.encode('UTF-8'), '?\n')
    p = p.replace(u'\xd8', u'\xd8\n')

    sys.stdout.write(p.encode('UTF-8'))
    sys.stdout.write("\n-----------------------------\n")

def outp2(s, parcut=False, pagecut=False  ):
    global gstate
    #.translate(...)
    #sys.stdout.write(s.encode('UTF-8'))
    #for i in s:
    #    if i=='.':
    #s=map()
    #if parcut:
    #    outp3(gstate.parag_accum)
    #    gstate.parag_accum=""
    if pagecut:
        outp3(gstate.parag_accum)
        gstate.parag_accum=""

    #s = s.replace('..', '.')
    #s = s.replace('.', '.\n') #never here!
    #for versus map:
    gstate.parag_accum += s


def fast_iter(context, func, *args, **kwargs):
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # Author: Liza Daly
    # modified to call func() only in the event and elem needed
    for event, elem in context:
        #print elem
        #print elem.tag
        if event == 'end' and elem.tag == TAG:
            func(elem, *args, **kwargs)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context


def process_element(elem, fout):
        global gstate
        #normalized = unicodedata.normalize('NFKD', \
        #        unicode(elem.text)).encode('ASCII','ignore').lower()

        normalized = unicodedata.normalize('NFKD', unicode(elem.text))

        #normalized=myprocess(normalized)
        st=normalized.split("\n")
        for l in st:
            #print l
            q = myprocess(l)
            if len(q)>0:
                if gstate.newArticle:
                    gstate.newArticle=False
                    outp2("", pagecut=True)
                if gstate.emptyline:
                    gstate.parctr +=1
                    gstate.emptyline=False
                    parag_hdr = ("\n%d(%d): \n"%(gstate.parctr,gstate.counter) )
                    #fout.write( parag_hdr.encode('UTF-8') )
                    
                    #outp2(parag_hdr,parcut=True)
                    outp2("",parcut=True)
                    
                    #outp2("\n")
                #fout.write( q.encode('UTF-8') )
                outp2(q)
                pass 
                #invar: gstate.emptyline==False
            else:
                gstate.emptyline=True   


        #print elem.text
        #print normalized.replace('\n', ' ')
        #print normalized
        #print >>fout, normalized.replace('\n', ' ')
        if gstate.counter % 10000 == 0: print "Doc " + str(gstate.counter)
        gstate.counter += 1
        gstate.newArticle=True
 
def main():
    #fin = bz2.BZ2File(sys.argv[1], 'r')
    fin = open('fawiki-20150228-pages-meta-current.xml','r')
    fout = open('fa_sentences.txt', 'w')
    #fout = sys.stdout
    try:
        context = etree.iterparse(fin)
        global gstate
        gstate = State1()
        fast_iter(context, process_element, fout)
        outp2("",parcut=True)
    except Exception as e:
        print e
        fout.close()
 
if __name__ == "__main__":
    main()


"""
todo:  
use yield
connect the lines again and split again using "."
empty lines are paragraph breaks?

"""
#0:45
#1:45
#?
#17:16 -- ?
