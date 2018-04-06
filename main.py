import re
import urllib.request
import urllib.error
import json
import io
import hashlib
try:
    to_unicode = unicode
except NameError:\
    to_unicode = str

# funkcja do otwierania stron i dekodowania
def openPage(link):
    req = urllib.request.Request(link)
    try:
        responsePage = urllib.request.urlopen(req)
        result = responsePage.read().decode("utf-8")
        return result
    except urllib.error.HTTPError as e:
        print(e.code)
        return openPage(link)

# funkcja do wyciagania wszystkich działów
def extractSection(page):
    extractedPage = openPage(page)
    Section = []
    Section += re.findall(r'<section class="category-extended has-separator" data-id="[\S\s]*?">[\S\s]*?<header>[\S\s]*?<a href="([\S\s]*?)" >[\S\s]*?<h3>[\S\s]*?<\/h3>[\S\s]*?<\/a>', extractedPage)
    return Section

# funckja do wyciagania 2 działów - Z archiwum kulturystyki i SKLEP SFD
def extractOnlyTwoSection(page):
    extractedPage = openPage(page)
    OnlyTwoSection = []
    OnlyTwoSection += re.findall(r'<section class="category-extended has-separator" data-id="121">[\S\s]*?<header>[\S\s]*?<a href="([\S\s]*?)" >[\S\s]*?<h3>[\S\s]*?<\/h3>[\S\s]*?<\/a>', extractedPage)
    OnlyTwoSection += re.findall(r'<section class="category-extended has-separator" data-id="138">[\S\s]*?<header>[\S\s]*?<a href="([\S\s]*?)" >[\S\s]*?<h3>[\S\s]*?<\/h3>[\S\s]*?<\/a>', extractedPage)
    return OnlyTwoSection

# funkcja do wyciagania tematow
def extractTopic(page, table):
    print('Strona: ' + page)

    extractedPage = openPage(page)

    # wyciągniecię tematów z wyświetlonego działu + sub fora (o ile takowy istnieje)
    table += re.findall(r'<div class="topic-title" title="[\S\s]*?">[\S\s]*?<a href="([\S\s]*?)" title="[\S\s]*?" class="">', extractedPage)

    # print(table)

    # funkcja sprawdzająca czy w danym dziale znajduje się sub for
    if ((re.findall(r'<div class="stronnicowanie">[\S\s]*?<li class=(current)>[\S\s]*?<a href="[\S\s]*?">(1)<\/a>', extractedPage))):
        subFor = []
        subFor += re.findall(r'<div class="topic">[\S\s]*?<h3>[\S\s]*?<a href="([\S\s]*?)" title="[\S\s]*?">', extractedPage)
        for i in subFor:
            print('subFor: ' + i)
            extractTopic(i, table)

    # funkcja sprawdzająca, czy istnieje kolejna strona w dziale + sub forze
    if (re.search(r'<div class="stronnicowanie">[\S\s]*?<\/ul>[\S\s]*?<a href="([\S\s]*?)" title="Następna strona">', extractedPage)):
        nextSite = re.search(r'<div class="stronnicowanie">[\S\s]*?<\/ul>[\S\s]*?<a href="([\S\s]*?)" title="Następna strona">', extractedPage)
        nextSite = nextSite.group(1)
        print('następna strona: ' + nextSite)
        extractTopic(nextSite, table)
    return table

# funkcja do znajdowania autorów
def findAuthors(page):
    extractedPage = openPage(page)
    authors = []
    authors += re.findall(r'<div class="author">[\S\s]*?<div data-online="[\S\s]*?<strong>([\S\s]*?)<\/strong>', extractedPage)
    # for i in authors:
    #     print('authors: ' + i)
    return authors

# funkcja do wyciagania linków z konkretnych postów
def idPost(page):
    extractedPage = openPage(page)
    idPostTableOld = []
    idPostTableNew = []
    idPostTableOld += re.findall(r'<div id="[\S\s]*?" class="hentry" >[\S\s]*?<a href="([\S\s]*?)" title="Udostępnij post"', extractedPage)
    # usuwanie śmieci z tablicy
    for i in idPostTableOld:
        tmp = re.sub(r'[\S\s]*<\/span>[\S\s]*<a href="', "", i)
        idPostTableNew.append(tmp)
    return idPostTableNew

# funkcja generująca id
def idCreator(postList):
    table = []
    for i in postList:
        tmp = "407333" + i
        md5 = hashlib.md5(tmp.encode('utf-8')).hexdigest()
        m = str(int(md5, 16))
        table.append(m[:len(m) // 2])
    return table

# funkcja parsująca tytuł tematu
def parseSubject(string):
    returnSubject = re.sub(r'&#243;', 'ó', string)
    returnSubject = re.sub(r'&#211;', 'Ó', returnSubject)
    returnSubject = re.sub(r'&quot;', '', returnSubject)
    returnSubject = re.sub(r',,', '', returnSubject)
    returnSubject = re.sub(r'&amp;', '&', returnSubject)
    returnSubject = re.sub(r'&#233;', 'ę', returnSubject)
    return returnSubject

# funkcja parsująca datę początkową
def startDateParse(date):
    tmp = re.search(r'(\d*)-(\d*)-(\d*) (\d*):(\d*):(\d*)', date)
    if(tmp):
        returnDate = tmp.group(1) + "-" + tmp.group(2) + "-" + tmp.group(3) + "T" + tmp.group(4) + ":" + tmp.group(5) + ":" + tmp.group(6) + "Z"
    return returnDate

# funkcja parsująca datę końcową
def endDateParse(date):
    tmp = re.search(r'([\S\s]*?T[\S\s]*:)', date)
    returnDate = tmp.group(1) + "59Z"
    return returnDate

# funkcja wyciągająca wszystkie dane i zapisująca do pliku
def extractData(page):
    print('Post: ' + page)
    extractedPage = openPage(page)
    beforeParseDate = []
    startDate = []
    endDate = []
    beforeContent = []
    content = []

    # wyciąganie linków do konkretnych postów
    postID = idPost(page)
    # print(postID)

    # generowanie id (MD5)
    tableID = idCreator(postID)
    # print(tableID)

    # wyciąganie tematu i parsowanie na poprawny
    beforeParseSubject = re.search(r'<meta property="og:title" content="([\S\s]*?)"', extractedPage).group(1)
    newSubject = parseSubject(beforeParseSubject)

    # wyciąganie wszystkich autorów na stronie
    authors = findAuthors(page)
    # print(authors)

    # wyciąganie wszystkich dat na stronie
    beforeParseDate += re.findall(r'<time itemprop="commentTime" title="([\S\s]*?)">', extractedPage)
    # print(beforeParseDate)
    for index in beforeParseDate:
        startDate.append(startDateParse(index))
        endDate.append(endDateParse(startDateParse(index)))

    # wyciąganie wszystkich postów (contentu)
    beforeContent += re.findall(r'<div class="author">[\S\s]*?<div class="content-post">([\S\s]*?)<div class="bottom-box">', extractedPage)
    # print(beforeContent)

    for cont in beforeContent:
        # zmienianie wielokrotnosci znaku <br /> na znak nowej lini
        tmp = re.sub(r'(<br \/>)+|(<br\/>)+', ' \n ', cont)
        # zamiana &#243; na ó
        tmp = re.sub(r'&#243;', 'ó', tmp)
        # zamiana &#211; na Ó
        tmp = re.sub(r'&#211;', 'Ó', tmp)
        # zamiana &#163; na £
        tmp = re.sub(r'&#163;', '£', tmp)
        # zamiana &#233; na literę ę
        tmp = re.sub(r'&#233;', 'ę', tmp)
        # zamiana &#167; na paragraf
        tmp = re.sub(r'&#167;', '§', tmp)
        # zamiana &#160; na spację
        tmp = re.sub(r'&#160;', ' ', tmp)
        # zamiana &#39; na '
        tmp = re.sub(r'&#39;', '\'', tmp)
        # zamiana &amp; na &
        tmp = re.sub(r'&amp;', '&', tmp)
        # zamiana &gt; na >
        tmp = re.sub(r'&gt;', '>', tmp)
        # usuwanie cytowań
        tmp = re.sub(r'<blockquote>[\S\s]*?<\/blockquote>', '', tmp)
        # usuwanie div i pustych końcowych miejsc
        tmp = re.sub(r'<\/div>[\S\s]*?$', '', tmp)
        # usuwanie znacznika span edited wraz zawartością
        tmp = re.sub(r'<span class="edited">[\S\s]*?<\/span>', '', tmp)
        # usuwanie tylko znacznika span
        tmp = re.sub(r'<span [\S\s]*?>|<\/span>', '', tmp)
        # zostawianie samych linkow bez otoczki <a href='' /a>
        tmp = re.sub(r'<a href="([\S\s]*?)"[\S\s]*?<\/a>', r'\1', tmp)
        # usuwanie śmieci z a href
        tmp = re.sub(r'&nbsp;', " ", tmp)
        # usuwanie znaku cudzysłowia
        tmp = re.sub(r'&quot;', '', tmp)
        # usuwanie cudzysłowia
        tmp = re.sub(r',,', '', tmp)
        # usuwanie img
        tmp = re.sub(r'<img[\S\s]*?>', '', tmp)
        # usuwanie znacznikow
        tmp = re.sub(r'<i>|<b>|<u>|<\/i>|<\/b>|<\/u>|<br>|>|<', '', tmp)
        # usuwanie końcowych spacji
        tmp = re.sub(r'\n[\s]*', '', tmp)
        content.append(tmp)

    test = 0
    while test < len(content):
        if content[test] == '':
            content.pop(test)
            startDate.pop(test)
            endDate.pop(test)
            authors.pop(test)
        else:
            test += 1

    # zapisywanie wynikow do pliku
    if (len(tableID) == len(content) == len(startDate) == len(postID) == len(authors)):
        for i in range(0, len(authors)):
            with io.open('data.json', 'a', encoding='utf8') as outfile:
                str_ = json.dumps({
                    'iid': tableID[i],
                    'id': tableID[i] + "-1",
                    'url': postID[i],
                    'title': newSubject,
                    'creator': authors[i],
                    'duration_start': startDate[i],
                    'duration_end': endDate[i],
                    'content': content[i],
                    'lang': 'pl',
                    'lname': "sfd",
                },
                    indent=4, sort_keys=False,
                    separators=(',', ': '), ensure_ascii=False)
                outfile.write(to_unicode(str_))

    # zabezpieczenie przed niewylapaniem niektorych elementow, jezeli liczba autorow, dat i textu nie jest taka sama
    else:
        print("SKIP: TABLICE NIE SA ROWNEJ DLUGOSCI")

    if (re.search(r'<div class="stronnicowanie">[\S\s]*?<\/ul>[\S\s]*?<a href="([\S\s]*?)" title="Następna strona">', extractedPage)):
        nextSite = re.search(r'<div class="stronnicowanie">[\S\s]*?<\/ul>[\S\s]*?<a href="([\S\s]*?)" title="Następna strona">', extractedPage)
        nextSite = nextSite.group(1)
        print('następna strona: ' + nextSite)
        extractData(nextSite)
    return

# url strony
url = 'http://www.sfd.pl/Forum'

# tablica z głównymi działami
MainSection = extractSection(url)

# tablica z 2 głównymi działami
MainSection2 = extractOnlyTwoSection(url)

# tablica z topicami
Topic = []

# wyciągnięcie topiców. Aby wyciągnąć ze wszystkich działów, trzeba zmienić zmienną MainSection2 na MainSection
for page in MainSection2:
    extractTopic(page, Topic)

print(len(Topic))

# wyciągnięcie wszystkich potrzebnych informacji
for topics in set(Topic):
    extractData(topics)