# -*- coding: utf-8 -*-
import json
import os
import re

def openJSON(filename):
    """Returns a json file as a python dictionary
    ----------
    filename : string
        Filename of a human readable (multiline) json.
    Returns
    -------
    data : dictionary
        Python dictionary representing exactly the data from the input file.
    Notes
    -----
    It uses the program 'jq' which might need to be installed in advance.
    """
    tempFile = filename[:filename.find('.')] + "Python.json"
    print('jq -c . ' + filename + ' > ' + tempFile)
    os.system('jq -c . ' + filename + ' > ' + tempFile)
    with open(tempFile, 'r') as f:
        data = json.load(f)
    print('rm ' + tempFile)
    os.system('rm ' + tempFile)
    return data

def replaceHref(data, linkGen):
    """Replaces links in the json data into the correct format
    ----------
    data : string
        A string given from the json file.
    linkGen : function
        It takes three arguments: 1. href which is the url wo which should be
        linked. 2. target which describes for html in which window the link
        should be opened. 3. text which is the text on which the link is
        applied. It returns a string.
    Returns
    -------
    data : string
        The input string but the hrefs are replaced with the help of linkGen.
    """
    hrefRegex = r"\[href='[^']*\' *text='[^']*'\]"
    while re.search(hrefRegex,data):
        match2 = re.search(hrefRegex,data)
        s2 = match2.start(0)
        e2 = match2.end(0)
        match2 = data[s2:e2]
        href = match2[match2.find('href')+6:]
        href = href[:href.find('\'')]
        if 'http' in href:
            target = "target=\"_blank\" "
        else:
            target = ""
        text = match2[match2.find('text')+6:]
        text = text[:text.find('\'')]
        data = data[:s2] + linkGen(href, target, text) + data[e2:]
        #data = data[:s2] + '<a href="' + href + '" ' + target +'>' + text + '</a>' + data[e2:]
    return data

def replaceCite(data, citeGen):
    """Replaces links in the json data into the correct format
    ----------
    data : string
        A string given from the json file.
    citeGen : function
        It takes one argument: cite: Which is the identificator for the
        citation. It returns a string which replaced the cites with theh help of
        citeGen.
    Returns
    -------
    data : string
        The input string but the hrefs are replaced with the help of linkGen.
    """
    citeRegex = r"\[cite='[^']*\'\]"
    while re.search(citeRegex,data):
        match2 = re.search(citeRegex,data)
        s2 = match2.start(0)
        e2 = match2.end(0)
        match2 = data[s2:e2]
        cite = match2[match2.find('cite')+6:]
        cite = cite[:cite.find('\'')]
        data = data[:s2] + citeGen(cite) + data[e2:]
    return data

def insertData(text, data, templateNonLoopRegex, newline, linkGen, citeGen, escape, characters):
    """Inserts data from the json into the template
    ----------
    text : string
        template
    data : dictionary
        dictionary representing the data from the json file
    templateNonLoopRegex : regex
        regex which finds all template tags that are not loop template tags.
    newline : string
        representation of newline in output ("</br>" in html, "}\par{" in latex)
    linkGen : function
        It takes three arguments: 1. href which is the url wo which should be
        linked. 2. target which describes for html in which window the link
        should be opened. 3. text which is the text on which the link is
        applied. It returns a string.
    citeGen : function
        It takes one argument: cite: Which is the identificator for the
        citation. It returns a string which replaced the cites with theh help of
        citeGen.
    escape : string
        string that escapes characters ("\\" in latex)
    characters : list[char]
        list of characters to escape.
    Returns
    -------
    data : string
        The input string where all template tags are replaced with the
        appropriate data from the json file.
    """
    #regex = r'<!\-\- *!TEMPLATE *(\[\"?[a-z,A-Z,0-9]+\"?\])+ *\-\->'
    while re.search(templateNonLoopRegex,text):
        match = re.search(templateNonLoopRegex,text)
        s = match.start(0)
        e = match.end(0)
        match = text[s:e]
        match = match[match.find('[')+1:match.rfind(']')].split('][')
        replacement = data
        for ele in match:
            if('"' in ele):
                accessor = ele[1:-1]
            else:
                accessor = int(ele)
            if((accessor in replacement) or (type(accessor) == int and type(replacement) == list)):
                replacement = replacement[accessor]
            else:
                replacement = ""
        if(type(replacement) != str):
            replacement = str(replacement)
        if(replacement != ""):
            replacement = replaceHref(replacement, linkGen)
            replacement = replaceCite(replacement, citeGen)
            for char in characters:
                replacement = replacement.replace(char, escape + char)
            replacement = replacement.replace('\n',newline)
        text = text[:s] + replacement + text[e:]
    return text

def sanatizeHtml(html, templateRegex):
    """Returns a sanatized html file after things are inserted
    ----------
    html : string
        output after loop unroling and insert data
    templateRegex : regex
        regex to find the template tags
    Returns
    -------
    html : string
        Sanatizes many things.
    Notes
    -----
    If the output is not as expected this might be the function which caused it.
    """
    #remove empty links
    linkRegex = r'<a[^>]*href=""[^>]*>'
    while re.search(linkRegex,html):
        match = re.search(linkRegex,html)
        s = match.start(0)
        e = match.end(0)
        s2 = e + html[e:].find('</a>')
        html = html[:s] + html[e:s2] + html[s2+4:]

    #remove template comments
    while re.search(templateRegex,html):
        match = re.search(templateRegex,html)
        s = match.start(0)
        e = match.end(0)
        html = html[:s] + html[e:]
    #remove wrong commas
    html = re.sub(",\s+<", "<", html)
    wrongPunctuationRegex = r'[\,][^\s]'
    while re.search(wrongPunctuationRegex, html):
        match = re.search(wrongPunctuationRegex, html)
        s = match.start(0)
        e = match.end(0)
        html = html[:s+1] + ' ' + html[s+1:e] + html[e:]
    #first letter is capitalized
    tagStartRegex = r'<[td,p,b][^>]*>[ ,\n]*[a-z]'
    while re.search(tagStartRegex, html):
        match = re.search(tagStartRegex,html)
        s = match.start(0)
        e = match.end(0)
        html = html[:e-1] + html[e-1:e].upper() + html[e:]
    #capitalize all words in title
    headerTag = r'<h[0-9][^>]*>[^<]+</h[0-9]>'
    for match in re.finditer(headerTag,html):
        s = match.start(0)
        e = match.end(0)
        match = html[s:e]
        s = s + match.find('>')+1
        match = html[s:e]
        e = s + match.find('<')
        html = html[:s] + html[s:e].title() + html[e:]
    #undo some capitalization
    html = html.replace("'S", "'s")
    html = html.replace("Http", "http")
    return html

def sanatizeLatex(latex, templateRegex):
    """Returns a sanatized latex file after things are inserted
    ----------
    latex : string
        output after loop unroling and insert data
    templateRegex : regex
        regex to find the template tags
    Returns
    -------
    latex : string
        Sanatizes many things.
    Notes
    -----
    If the output is not as expected this might be the function which caused it.
    """
    #remove empty links
    linkRegex = r'\\href\{\}\{[^\}]+\}'
    while re.search(linkRegex,latex):
        match = re.search(linkRegex,latex)
        s = match.start(0)
        e = match.end(0)
        match = latex[s:e]
        match = match[8:-1]
        latex = latex[:s] + match + latex[e:]
    #remove some spaces
    latex = re.sub(',\s+\\template\{ *ENDLOOP', '\\template{ENDLOOP', latex)
    #remove wrong commas
    wrongPunctuationRegex = r'[\,][^\s]'
    while re.search(wrongPunctuationRegex, latex):
        match = re.search(wrongPunctuationRegex, latex)
        s = match.start(0)
        e = match.end(0)
        latex = latex[:s+1] + ' ' + latex[s+1:e] + latex[e:]
    #remove template comments
    while re.search(templateRegex,latex):
        match = re.search(templateRegex,latex)
        s = match.start(0)
        e = match.end(0)
        latex = latex[:s] + latex[e:]
    #add newlines
    wrongLineBreakRegex = r'\\\\[^\n]'
    while re.search(wrongLineBreakRegex,latex):
        match = re.search(wrongLineBreakRegex,latex)
        s = match.start(0)
        e = match.end(0)
        latex = latex[:s+2] + '\n' + latex[e-1:]
    #remove some commas
    commaRegex = r',[\s,}]+[&,\\]'
    while re.search(commaRegex, latex):
        match = re.search(commaRegex,latex)
        s = match.start(0)
        e = match.end(0)-1
        match = latex[s:e]
        latex = latex[:s] + latex[s+1:]
    #first letter is capitalized
    textbfRegex = r'\\textbf\{[a-z][^\}]+\}'
    while re.search(textbfRegex, latex):
        match = re.search(textbfRegex,latex)
        s = match.start(0)
        e = match.end(0)-1
        match = latex[s:e]
        s2 = match.find('{')+1+s
        match = latex[s2:e]
        s3 = re.search(r'\S+', match).start(0)+s2
        latex = latex[:s3] + latex[s3:e].capitalize() + latex[e:]
    textbfRegex = r'&\s*[a-z]'
    while re.search(textbfRegex, latex):
        match = re.search(textbfRegex,latex)
        s = match.start(0)
        e = match.end(0)
        match = latex[s:e]
        latex = latex[:e-1] + latex[e-1:e].capitalize() + latex[e:]
    #capitalize all words in title
    sectionTitleRegex = r'\\Large(\\[a-z]+)+ [a-z,\s]+[}]?[\s]*&'
    while re.search(sectionTitleRegex, latex):
        match = re.search(sectionTitleRegex,latex)
        s = match.start(0)
        e = match.end(0)-1
        match = latex[s:e]
        s2 = re.search(r' [a-z, ]+', match).start(0)+s
        match = latex[s2:e]
        latex = latex[:s2] + latex[s2:e].title() + latex[e:]
    #undo some capitalization
    """
    html = html.replace("'S", "'s")
    html = html.replace("Http", "http")"""
    return latex

def loopUnroling(text,
        data,
        templateLoopRegex,
        templateEndLoopHeadRegex,
        templateRegexHead,
        templateRegexTail,
        endTag,
        templateId):
    """replaces the loop tags with the appropriate amount of single template
    tags.
    ----------
    text : string
        template
    data : dictionary
        dictionary representing the data from the json file
    templateLoopRegex : regex
        regex which finds all loop template tags.
    templateEndLoopHeadRegex : regexEndLoop
        regex which finds all endLoop template tags.
    templateRegexHead : regex
        regex to find start of a template tag
    templateRegexTail : regex
        regex to find end of a template tag
    endTag : regex
        regex to find end of tag ("}" for latex, ">" for html)
    templateId : regex
        regex to differentiate template from other tags
    Returns
    -------
    text : string
        Input text with all loop tags replaced with the appropriate amount of
        single template tags.
    """
    while re.search(templateLoopRegex,text):
        match1 = re.search(templateLoopRegex,text)
        s1 = match1.start(0)
        e1 = match1.end(0)
        match1 = text[s1:e1]
        var = match1[match1.find('"')+1:]
        var = var[:var.find('"')]
        match1 = match1[match1.find('[')+1:match1.rfind(']')].split('][')
        regexEndLoop = templateEndLoopHeadRegex + '"' + var + '"' + templateRegexTail
        match2 = re.search(regexEndLoop,text[e1:])
        s2 = match2.start(0)+e1
        e2 = match2.end(0)+e1
        match2 = text[s2:e2]
        loopBody = text[e1:s2]
        loopBody = re.sub("^\s+|\s+$", "", loopBody)

        loopEle = data
        for ele in match1:
            if('"' in ele):
                loopEle = loopEle[ele[1:-1]]
            else:
                loopEle = loopEle[int(ele)]
        nItr = len(loopEle)
        stitchedText = ""
        for i in range(nItr):
            templateVariableRegex = templateRegexHead + r'[^' + endTag +']*\[' + var + r'\][^' + endTag +']*' + templateRegexTail
            ithLoopBody = loopBody
            while re.search(templateVariableRegex,ithLoopBody):
                match = re.search(templateVariableRegex,ithLoopBody)
                s = match.start(0)
                e = match.end(0)
                match = ithLoopBody[s:e]
                match = match.replace('[' + var + ']', '[' + str(i) + ']')
                ithLoopBody = ithLoopBody[:s] + match + ithLoopBody[e:]
            stitchedText += ithLoopBody

        textHead = text[:s1]
        openTag = text[s1:e1].replace(templateId + 'LOOP ', templateId + 'LOOPUNROLED ')
        textTail = text[s2:]
        text = textHead + openTag + stitchedText + textTail

    return text

def parseHtml(html, data):
    """Processes the html template and inserts the data.
    ----------
    html : string
        output after loop unroling and insert data
    data : dictionary
        all the data from the json to insert into the template
    Returns
    -------
    html : string
        html string which has all the inserted data
    Notes
    -----
    To adapt the program for a new data format it should be sufficient to write
    your own parseXXX(XXX, data) function.
    """
    templateSelector = r'\["?[a-z,A-Z,0-9,_]+"?\]'
    templateId=r'!TEMPLATE '
    templateRegexHead = r'<!-- *!TEMPLATE +'
    templateRegexTail = r' *-->'
    templateRegex = templateRegexHead + r'[^>]+' + templateRegexTail
    templateNonLoopRegex = templateRegexHead + r'(' + templateSelector + r')+' + templateRegexTail
    templateLoopRegex = templateRegexHead + r'LOOP \"[a-z,A-Z]+\" +' + r'(' + templateSelector + r')+' + templateRegexTail
    templateEndLoopHeadRegex = templateRegexHead + r'ENDLOOP '
    html = loopUnroling(html,
        data=data,
        templateLoopRegex=templateLoopRegex,
        templateEndLoopHeadRegex=templateEndLoopHeadRegex,
        templateRegexHead=templateRegexHead,
        templateRegexTail=templateRegexTail,
        endTag='>',
        templateId=templateId)
    html = insertData(
        text=html,
        data=data,
        templateNonLoopRegex=templateNonLoopRegex,
        newline='</p><p>',
        linkGen=lambda href, target,text: '<a href="' + href + '" ' + target +'>' + text + '</a>',
        citeGen=lambda cite: '<b>[' + cite + ']</b>',
        escape='',
        characters=[]
        )
    html = sanatizeHtml(html, templateRegex=templateRegex)
    return html

def parseLatex(latex, data):
    """Processes the latex template and inserts the data.
    ----------
    latex : string
        output after loop unroling and insert data
    data : dictionary
        all the data from the json to insert into the template
    Returns
    -------
    latex : string
        latex string which has all the inserted data
    Notes
    -----
    To adapt the program for a new data format it should be sufficient to write
    your own parseXXX(XXX, data) function.
    """
    templateSelector = r'\[\"?[a-z,A-Z,0-9,_]+\"?\]'
    templateId=r'template{'
    templateRegexHead = r'\\template\{ *'
    templateRegexTail = r' *\}'
    templateRegex = templateRegexHead + r'[^\}]+' + templateRegexTail
    templateNonLoopRegex = templateRegexHead + r'(' + templateSelector + r')+' + templateRegexTail
    templateLoopRegex = templateRegexHead + r'LOOP \"[a-z,A-Z]+\" +' + r'(' + templateSelector + r')+' + templateRegexTail
    templateEndLoopHeadRegex = templateRegexHead + r'ENDLOOP '
    latex = loopUnroling(latex,
        data=data,
        templateLoopRegex=templateLoopRegex,
        templateEndLoopHeadRegex=templateEndLoopHeadRegex,
        templateRegexHead=templateRegexHead,
        templateRegexTail=templateRegexTail,
        endTag='\}',
        templateId=templateId)
    latex = insertData(
        text=latex,
        data=data,
        templateNonLoopRegex=templateNonLoopRegex,
        newline='}\\par{',
        linkGen=lambda href, target,text: '\\href{' + (href if href.startswith('http') else 'http://retoweber.info/'+href) + '}{' + text + '}',
        citeGen=lambda cite: '\\textbf{[' + cite + ']}',
        escape='\\',
        characters=['&'])
    latex = sanatizeLatex(latex, templateRegex=templateRegex)
    return latex

def generateHtml(template):
    """Takes the template and outputs a valid html in German and English.
    ----------
    template : string
        The string from the template file.
    Returns
    -------
        None
    Notes
    -----
    It produces as a side effect three files a German and English version of the
    cv and an index file identical with the English cv.
    """
    data = openJSON('cv.json')
    #grades = openJSON('grades.json')
    with open(template, 'r') as f:
        html = f.readlines()
    htmlEn = ''.join(html)
    htmlDe = htmlEn.replace('"en"', '"de"')
    htmlEn = parseHtml(htmlEn, data)
    htmlDe = parseHtml(htmlDe, data)
    with open('cv_en.html', 'w+', encoding='utf-8') as f:
        f.write(htmlEn)
    with open('cv_de.html', 'w+', encoding='utf-8') as f:
        f.write(htmlDe)
    with open('index.html', 'w+', encoding='utf-8') as f:
        f.write(htmlEn)

def generateLatex(template):
    """Takes the template and outputs a valid latex in German and English.
    And produces afterwards automatically a pdf and removes all log and intermediate files from it.
    ----------
    template : string
        The string from the template file.
    Returns
    -------
        None
    Notes
    -----
    It produces as a side effect two files a German and English version of the
    cv.
    """
    data = openJSON('cv.json')
    with open(template, 'r') as f:
        latex = f.readlines()
    latexEn = ''.join(latex)
    latexDe = latexEn.replace('"en"', '"de"')
    latexEn = parseLatex(latexEn, data)
    latexDe = parseLatex(latexDe, data)
    with open('cv_en.tex', 'w') as f:
        f.write(latexEn)
    print('xelatex cv_en.tex')
    os.system('xelatex cv_en.tex')
    print('rm cv_en.aux cv_en.log cv_en.out')
    os.system('rm cv_en.aux cv_en.log cv_en.out')
    with open('cv_de.tex', 'w') as f:
        f.write(latexDe)
    print('xelatex cv_de.tex')
    os.system('xelatex cv_de.tex')
    print('rm cv_de.aux cv_de.log cv_de.out')
    os.system('rm cv_de.aux cv_de.log cv_de.out')

generateHtml('htmlTemplate.html')
generateLatex('latexTemplate.tex')
