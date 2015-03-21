from lxml import etree
import sys
import bz2
import unicodedata
import re

#based on:
# http://baraujo.net/blog/?p=81


#https://docs.python.org/2/library/re.html
def myprocess(x):
    x0=x
    rea=[
        r"\[\[.*\]\]", #"[[:]]",
        r"{{.*}}",
        r"\[http:.*\]",  # // --> forbidden
        r"\[https:.*\]",
        #        #r"\*(.*)\n",
        r"<ref.*</ref>", #one-liner ref
        r"\'\'\'.*\'\'\'", #works
        r"\A\*\ ",
        r"==.*==",        
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
    #  \A  only start of the line
    #   \Z  end of string



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
        pass
    return x
#TAG = '{http://www.mediawiki.org/xml/export-0.8/}text'
TAG = '{http://www.mediawiki.org/xml/export-0.10/}text'

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
        global counter
        normalized = unicodedata.normalize('NFKD', \
                unicode(elem.text)).encode('ASCII','ignore').lower()

        normalized = unicodedata.normalize('NFKD', unicode(elem.text))

        #normalized=myprocess(normalized)
        st=normalized.split("\n")
        for l in st:
            #print l
            q = myprocess(l)
            if len(q)>0:
                print q
                pass    


        #print elem.text
        #print normalized.replace('\n', ' ')
        #print normalized
        #print >>fout, normalized.replace('\n', ' ')
        if counter % 10000 == 0: print "Doc " + str(counter)
        counter += 1
 
def main():
    #fin = bz2.BZ2File(sys.argv[1], 'r')
    fin = open('fawiki-20150228-pages-meta-current.xml','r')
    fout = open('2013_wikipedia_en_pages_articles.txt', 'w')
    context = etree.iterparse(fin)
    global counter
    counter = 0
    fast_iter(context, process_element, fout)
 
if __name__ == "__main__":
    main()


"""
todo:  
use yield
connect lines again
and split again using .
empty lines are paragraph breaks?

"""
