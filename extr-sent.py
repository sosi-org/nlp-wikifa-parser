# -*- coding: utf-8 -*-
from lxml import etree
import sys
import bz2
import unicodedata
import re

RE_EXTRACT=[
    #ur".*\[\[.+\|(.*?)\]\]",  #no colon
    #ur".*\[\[(.*?)\]\]",  #no colon
    ur".*\[\[([^\|^\:]*?)\]\]", #no "|" or ":"
    ur".*\[\[.*\|([^\:]*?)\]\]", #with | without :
    ur".*\[\[en:([^\|\:]*?)\]\]", #with | without :
    r"<sub>(.*)</sub>", 
    r"<sup>(.*)</sup>",
    ur"{{ب\|(.*)}}",
    #r"{{[^\|]*?\|(.*)}}",

]


RE_CUT=[
#    r"\[\[.*\]\]", #"[[:]]",
    r"{{.*}}",
    r"\[http:.*\]",  # // --> forbidden
    r"\[https:.*\]",
    r"\[//.*?\]",
    #        #r"\*(.*)\n",
    r"<ref .*</ref>", #one-liner ref
    r"<ref>.*</ref>", #one-liner ref
    r"<ref [^>]*/>",
    #r"<ref/>", #not tested
    #r"\'\'\'.*\'\'\'", #works
    #r"\A\*\ ",
    #r"\A\*\n",
    #r"\A\*\*\n",  #put a dot in end.
    #r"\A\#\#\n",        
    #r"\A\#\n",
    r"\A\*",
    r"\A\*\*",  #put a dot in end.
    r"\A\#\#",        
    r"\A\#",
    r"==.*==",       
    r"===.*===",       

    r"<p .*</p>", 
    r"<a .*</a>", 
    r"{{.*}}",
    #r"{{[^\|]*\|.*}}",

    r"{{{.*}}}",       
    r"{{{{.*}}}}",       
    r"{.*}",       

    r"\'\'\'.*\'\'\'",
    r"\'\'.*\'\'", 
    r"\'\'\'\'\'.*\'\'\'\'\'",
    r"\A\:",
    r"\A\:\:",  #emove whole line

    #r"\<\!\-\-.*\-\-\>",
    r"<!--.*-->",
    #r"http:.*? ", #space
    #r"https:.*? ", #space
    r"http:.*?[ \n\Z]",
    r"https:.*?[ \n\Z]",

    r"(--.*\(UTC\))", ## not work
    r"\#REDIRECT",
    r"\#redirect",
    ur"#تغییرمسیر",

    r"<references/>",
    r"<noinclude>",
    r"<nowiki>.*</nowiki>",
    r"<[gG]allery>.*</[gG]allery>",

    r"<div.*?</div>",
    r"<b>",
    r"</b>",
    r"<code>.*?</code>",
    r"<small>",
    r"</small>",
    r"<strong>",
    r"</strong>",
    r"<br/>",
    r"<br />",
    r"<li.*?</li>",
    r"<ul.*?</ul>",
    #span
    #strong
    ur"\[\[رده:.*?\]\]",
    ur"\[\[ویکی‌پدیا:.*\]\]",
    ur"\[\[[Ii]mage:.*\]\]",
    ur"\[\[[Cc]ategory:.*\]\]",

    #r"<ref .*/>", #not tested

    ur"\[\[تصویر:.*\]\]",
    ur"\[\[کاربر:.*\]\]",
    ur"\[\[بحث:.*\]\]",
    ur"\[\[پرونده:.*\]\]",
    ur"\[\[:تصویر.*\]\]", #????
    ur"\[\[:کاربر.*\]\]",
    ur"\[\[:بحث.*\]\]",
    ur"\[\[:پرونده.*\]\]",
]


#{{ب|هفت کشور نمی‌کنند امروز|بی مقالات سعدی انجمنی}}
#http://fa.wikipedia.org/wiki/%D8%B3%D8%B9%D8%AF%DB%8C#.D8.AF.D8.B1_.D8.B3.D8.AA.D8.A7.DB.8C.D8.B4_.D8.B3.D8.B9.D8.AF.DB.8C

#RE_CUT=[RE_CUT[len(RE_CUT)-1]]

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

REPL_A=[
("  "," ")
]


UNWANTED_TITLES=[
    ur"\Aبحث کاربر:",
    ur"\Aکاربر:",
    ur"بحث:.*",
    ur"\Aبحث:.*",
    ur"\Aبحث:",
    ur"بحث:",
    ur"\Aمدیاویکی:",
    ur"\Aبحث ویکی‌پدیا:",  #بحث ویکی‌پدیا:فرهنگ شهروندی
    ur"الگو:",
    ur"ویکی‌پدیا:", #ویکی‌پدیا:Protection log
]
#based on:
# http://baraujo.net/blog/?p=81

#https://docs.python.org/2/library/re.html
def myprocess(x, trace=False):
    x0=x
    def replall(x):
        for f,t in REPL_A:
            x = x.replace(f, t)
        return x

    #x=x.replace("\n"," ")
    nx=x
    while True:
        for r in RE_CUT:
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
        nx=replall(nx)

        for r in RE_EXTRACT:
            #
            res=re.match(r, nx)
            if not res is None:
                nx00=nx
                #nx=str(res.groups()[0]) #one group only
                nx="".join(list(res.groups())) #keep all groups
                nx=" "+nx+" "
                if nx00 !=nx:
                    #print ">>>>"+nx.encode('UTF-8')
                    #print "<<<<"+nx00.encode('UTF-8')
                    pass


        
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

#from: https://github.com/larsmans/wiki-dump-tools/blob/master/textonly.py
# Media and categories; the codes for these differ per language.
# We have the most popular ones (>900.000 articles as of July 2012) here,
# as well as Latin, which is useful for testing.
# Add other languages as required.
_MEDIA_CAT = """
[Ii]mage|[Cc]ategory # English
|[Aa]rchivo # Spanish
|[Ff]ile # English, Italian
|[CcKk]at[ée]gor[íi][ea] # Dutch, German, French, Italian, Spanish, Polish, Latin
|[Bb]estand # Dutch
|[Bb]ild # German
|[Ff]icher # French
|[Pp]lik # Polish
|[Ff]asciculus # Latin
"""
_UNWANTED = re.compile(r"""
(:?
\{\{ .*? \}\} # templates
| \| .*? \n # left behind from templates
| \}\} # left behind from templates
| <math> .*? </math>
| <nowiki> .*? </nowiki>
| <ref .*?> .*? </ref>
| <ref .*?/>
| <span .*?> .*? </span>
| \[lll\[ (:?%s): (\[\[.*?\]\]|.)*? \]\]
| \[lll\[ [a-z]{2,}:.*? \]\] # interwiki links
| \{\| .*? \|\}
| \[lll\[ (:? [^]]+ \|)?
| \]\]
| '{2,}
)
""" % _MEDIA_CAT,
re.DOTALL | re.MULTILINE | re.VERBOSE)

#   | =+ # headers
#| <!--.*?-->
#| <div .*?> .*? </div>

def text_only(text):
    return text # _UNWANTED.sub("", text)





#TAG_TEXT = '{http://www.mediawiki.org/xml/export-0.8/}text'
TAG_TEXT = '{http://www.mediawiki.org/xml/export-0.10/}text'
TAG_TITLE = '{http://www.mediawiki.org/xml/export-0.10/}title'

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
         self.unwantedTitle = False


def outp3(p):
    global gstate
    #    p=text_only(p)
    p=myprocess(p,True)
    p=text_only(p)
    #p = p.replace('.', '.\n')
    p = p.replace('. ', '.\n')
    #print "a"
    #print unicode(u'\xd8').encode('UTF-8')
    #print "b"
    #p = p.replace(u'\xd8'.encode('UTF-8'), '?\n')
    p = p.replace(u'\xd8', u'\xd8\n')

    if not gstate.unwantedTitle:
        sys.stdout.write(p.encode('UTF-8'))

    unwantedTitle=False
    for r in UNWANTED_TITLES:
        t=gstate.nextTitle
        res=re.match(r, t)
        if not res is None:
            unwantedTitle=True
    if unwantedTitle:
        uwt="حذف شد:"
    else:
        uwt=""
    gstate.unwantedTitle=unwantedTitle

    sys.stdout.write("\n-------------------------%s---%s\n"%(uwt,gstate.nextTitle.encode('UTF-8'),))

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
        if event == 'end' and elem.tag == TAG_TEXT:
            func(elem, *args, **kwargs)
        if event == 'end' and elem.tag == TAG_TITLE:
            ttl = unicodedata.normalize('NFKD', unicode(elem.text))
            gstate.nextTitle = ttl 
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
#---- 3 hours
#17:16 -- 22:23
#---- +5 hours!


"""

=== در ستایش سعدی ===
* [[مجد همگر]]:
{{شعر|نستعلیق}}{{ب|از سعدی مشهور سخن شعر روان جوی|کاو کعبه فضل است و دلش چشمه زمزم}}{{پایان شعر}}
* [[محمد تقی بهار]]:<ref>[http://siminsagh.com/bahar/divan-mt/mosammatha-mt/40355 سیمین ساق - دیوان بهار، مسمط‌ها، شماره۱ ]</ref>

{{شعر|نستعلیق}}
{{ب|سعدیا! چون تو کجا نادره گفتاری هست؟|یا چو شیرین سخنت نخل شکرباری هست؟}}
{{ب|یا چو بستان و گلستان تو گلزاری هست؟ |هیچم ار نیست، تمنای توام باری هست}}
{{ب|«مشنو ای دوست! که غیر از تو مرا یاری هست|یا شب و روز بجز فکر توام کاری هست»}}
{{ب|لطف گفتار تو شد دام ره مرغ هوس|به هوس بال زد و گشت گرفتار قفس}}
{{ب|پایبند تو ندارد سر دمسازی کس|موسی اینجا بنهد رخت به امید قبس}}
{{ب|«به کمند سر زلفت نه من افتادم و بس|که به هر حلقهٔ زلف تو گرفتاری هست»}}
{{پایان شعر}}
* [[همام تبریزی]] در ستایش سعدی:
{{شعر|نستعلیق}}{{ب|همام را سخن دل‌فریب و شیرین است|ولی چه سود که بیچاره نیست شیرازی}}{{پایان شعر}}
* [[سیف‌الدین فرغانی]] معاصر سعدی، خطاب به وی:<ref>جعفر شعار، حسن انوری، گزیده قصاید سعدی|زبان=فارسی</ref>
{{شعر|نستعلیق}}{{ب|نمی‌دانم که چون باشد به معدن زر فرستادن|به دریا قطره آوردن به کان گوهر فرستادن}}
{{ب|چو بلبل در فراق گل از این اندیشه خاموشم|که بانگ زاغ چون شاید به خنیاگر فرستادن}}
{{ب|حدیث شعر من گفتن کنار طبع چون آبت|به آتشگاه زرتشت است خاکستر فرستادن}}
{{ب|ضمیرت جام جمشید است و در وی نوش جان‌پرور|برٍاو جرعه‌ای نتوان از این ساغر فرستادن}}
{{ب|تو کشورگیر آفاقی و شعر تو تو را لشکر|چه خوش باشد چنین لشکر به هر کشور فرستادن}}{{پایان شعر}}
* [[عبدالحسین زرین‌کوب]]:سعدی معانی لطیف تازه را در عبارات آسان بیان می‌کند و از تعقید و تکلف برکنار می‌ماند. بعید نیست اگر بگوییم این بیت را در وصف خود سروده‌است:<ref>با کاروان حله، عبدالحسین زرین‌کوب، ص۲۴۴</ref>
{{شعر|نستعلیق}}
{{ب|صبر بسیار بباید پدر پیر فلک را|که دگر مادر گیتی چو تو فرزند بزاید}}
{{پایان شعر}}
* [[محمدعلی فروغی]] دربارهٔ سعدی می‌نویسد «اهل ذوق اِعجاب می‌کنند که سعدی هفتصد سال پیش به زبان امروزی ما سخن گفته‌است ولی حق این است که [...] ما پس از هفتصد سال به زبانی که از سعدی آموخته‌ایم سخن می‌گوییم».
* [[ضیاء موحد]] دربارهٔ وی می‌نویسد «زبان فارسی پس از [[فردوسی]] به هیچ شاعری به‌اندازهٔ سعدی مدیون نیست».
زبان سعدی به «سهل ممتنع» معروف شده‌است، از آنجا که به نظر می‌رسد نوشته‌هایش از طرفی بسیار آسان‌اند و از طرفی دیگر گفتن یا ساختن شعرهای مشابه آنها ناممکن.
* [[روح‌الله خمینی]]: او نیز در بیت «شاعر اگر سعدی شیرازی است / بافته‌های من و تو بازی است» به مقام والای سعدی اشاره می‌کند.
* [[گارسن دوتاسی]]: سعدی تنها نویسنده ایرانی است که نزد توده مردم اروپا شهرت دارد
* [[باربیه دومنار]]: در آثار سعدی لطف طبع [[هوراس]]، سهولت بیان [[اوید]]، قریحهٔ بذله‌گوی [[رابله]] و سادگی [[لافونتن]] را می‌توان یافت
* [[سر ادوین آرنولد]]: باری دگر همراه من آی، از آن آسمان گرفته،

تا گوش بر نغمهٔ خوش‌آهنگ و سحرآسای سعدی گذاریم،

بلبلی هزاردستان، که، از دل گلستان خویش، به پارسی هر دم نوایی دیگر ساز خواهد کرد...<ref>شیراز، مهد شعر و عرفان به نقل از کتاب Light of Asia</ref>



- راهنمای ویرایش، شروع مقالهٔ جدید و چیزهای بسیار دیگر [[ویکی‌پدیا:پرسش‌های رایج|پرسش‌های رایج]] - پرسش‌های رایج در مورد پایگاه [[ویکی‌پدیا:واژه‌نامه|واژه‌نامه]] - واژه‌نامهٔ اصطلاحات متداول در ویکی‌پدیا [[ویکی‌پدیا:سیاست‌ها و رهنمودها|سیاست‌ها و توصیه‌ها برای مشارکت‌کنندگان]] [[ویکی‌پدیا:شیوه‌نامه|شیوه‌نامه]] [[ویکی‌پدیا:فرهنگ شهروندی|شهروند خوب ویکی‌پدیا باشید]] [[ویکی‌پدیا:راه و رسم ویکی‌پدیا|روش کار ویکی‌پدیا]] [[ویکی‌پدیا:خودآموز دیدگاه بی‌طرف|بی‌طرفی]] [[ویکی‌پدیا:شیوه‌نامه|شیوه‌نامه]] [[ویکی‌پدیا:پرهیز از اشتباهات متداول|پرهیز از اشتباهات متداول]] [[ویکی‌پدیا:شهروندی|شهروندی]] [[ویکی‌پدیا:دیدگاه بی‌طرف|دیدگاه بی‌طرف]] [[ویکی‌پدیا:تماس با ما|تماس با ما]] [[ویکی‌پدیا:ویکی‌پدیانویسان|ویکی‌پدیانویسان]] - فهرست‌های مختلف از مشارکت‌کنندگان.
 اگر دوست دارید می‌توانید نامتان را اضافه کنید.
[[رده:انجمن‌های راهنمایی ویکی‌پدیا]][[رده:راهنمای ویکی‌پدیا]][[رده:اطلاعات پایه‌ای ویکی‌پدیا]]
----------------------------بحث کاربر:روزبه/بایگانی ۵

"""

"""
<Element {http://www.mediawiki.org/xml/export-0.10/}sha1 at 0x7f46600e5830>
<Element {http://www.mediawiki.org/xml/export-0.10/}revision at 0x7f46600e5560>
<Element {http://www.mediawiki.org/xml/export-0.10/}page at 0x7f46600e5440>
<Element {http://www.mediawiki.org/xml/export-0.10/}title at 0x7f46600e58c0>
<Element {http://www.mediawiki.org/xml/export-0.10/}ns at 0x7f46600e5908>
<Element {http://www.mediawiki.org/xml/export-0.10/}id at 0x7f46600e5950>
<Element {http://www.mediawiki.org/xml/export-0.10/}id at 0x7f46600e59e0>
<Element {http://www.mediawiki.org/xml/export-0.10/}parentid at 0x7f46600e5a28>
<Element {http://www.mediawiki.org/xml/export-0.10/}timestamp at 0x7f46600e5a70>
<Element {http://www.mediawiki.org/xml/export-0.10/}username at 0x7f46600e5b00>
<Element {http://www.mediawiki.org/xml/export-0.10/}id at 0x7f46600e5b48>
<Element {http://www.mediawiki.org/xml/export-0.10/}contributor at 0x7f46600e5ab8>
<Element {http://www.mediawiki.org/xml/export-0.10/}minor at 0x7f46600e5b90>
<Element {http://www.mediawiki.org/xml/export-0.10/}comment at 0x7f46600e5bd8>
<Element {http://www.mediawiki.org/xml/export-0.10/}model at 0x7f46600e5c20>
<Element {http://www.mediawiki.org/xml/export-0.10/}format at 0x7f46600e5c68>
<Element {http://www.mediawiki.org/xml/export-0.10/}text at 0x7f46600e5cb0>


  <page>
    <title>مدیاویکی:Bugreports</title>
    <ns>8</ns>
    <id>22</id>
    <revision>
      <id>20077</id>
      <parentid>260</parentid>
      <timestamp>2004-02-06T00:28:54Z</timestamp>
      <contributor>
        <username>روزبه</username>
        <id>4</id>
      </contributor>
      <model>wikitext</model>
      <format>text/x-wiki</format>
      <text xml:space="preserve">گزارش اشکالات</text>
      <sha1>mmyx9wvd106q8jk53ib73bx6xzjykp2</sha1>
    </revision>
  </page>


"""


""" Issue:
 پ.
ک.

«مظلوم دوغان» [زندانی کُرد] در اعترا

REMOVE THESE PAGES:
بحث کاربر:

REMOVE CERTAIN SECTIONS:
کاربر:صالحی
مدیاویکی:
english titles
بحث ویکی‌پدیا:فرهنگ شهروندی


----------------------------گردشگری
 گفته می‌شود.
 واژه گردشگر از زمانی پدید آمد که افراد طبقه متوسط اقدام به مسافرت کردن نمودند.


 ن امر ممکن شد.
 صنعت |پیوند = |عنوان = Tourism|زبان = انگلیسی|بازیابی = ۱۴ می‌۲۰۰۸}}</ref>
 ???
 جامعه ملل |پیوند = |عنوان = Tourism|زبان = انگلیسی|بازیابی = ۱۴ می‌۲۰۰۸}}</ref>با د


-----------------گاه‌شماری میلادی
 نیز مشهور شد.
 ???

--زبان

.[[پرونده:Brain Surface Gyri.SVG|thumb|بخش‌هایی از مغز که در پردازش زبان نقش دارند: کورتکس شنوایی اولیه انسان موجودی اجتماعی است و یکی

"""
