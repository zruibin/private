#! /usr/bin/env python
# -*- coding: utf-8 -*- 
#
# book.py
#
# Created by Ruibin.Chow on 2024/02/05.
# Copyright (c) 2024年 Ruibin.Chow All rights reserved.
# 

"""

"""

import os, re, json, sys, platform, fnmatch, stat
import subprocess, shutil, json
import datetime
import tarfile, gzip, zipfile, bz2
import urllib.request
from pathlib import Path
import multiprocessing
import inspect
from enum import Enum
import collections

print(sys.path)
sys.path.append(r'../app') 
print(sys.path)
import Util


SLASH = "/"
DOCS = "docs"
DEST_NAME = "dest"
DEST_DIR = ""
CSS_STYLE = ""

CONTENT_TMP = """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<style>
%s
</style>
</head><body>
<div class="container">
%s
</div>
</body></html>
"""

INDEX_TMP = """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<style>
%s
</style>
</head><body>
<div class="container">
<ul>
%s
</ul>
</div>
</body></html>
"""


class Color(Enum):
    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Fuchsia = 35 # 紫红色
    Cyan = 36 # 青蓝色
    White = 37

def operator(cmdString, newline=True):
    print(cmdString)
    res = subprocess.Popen(cmdString, 
                            shell=True, 
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    sout, serr = res.communicate() # res.stdout, res.stderr
    if serr:
        hasError = False
        datas = str(serr, "utf-8").split("\n")
        for data in datas: 
            print(data)
            if "error:" in data: hasError = True
        if hasError:
            errStr = "\033[" + str(31) + "m" + "stdout->Error." + "\033[0m"
            print(errStr, color=Color.Red)
            raise Exception(errStr)
    if sout:
        hasError = False
        datas = str(sout, "utf-8").split("\n")
        for data in datas: 
            print(data)
            if "error:" in data: hasError = True
        if hasError:
            errStr = "\033[" + str(31) + "m" + "stdout->Error." + "\033[0m"
            print(errStr, color=Color.Red)
            raise Exception(errStr)
    pass

def operatorCMD(parameterList, newline=True):
    cmdString = " ".join(parameterList)
    operator(cmdString, newline)
    pass

def json_minify(string, strip_space=True):
    """
    A port of the `JSON-minify` utility to the Python language.
    Based on JSON.minify.js: https://github.com/getify/JSON.minify
    """
    tokenizer = re.compile('"|(/\*)|(\*/)|(//)|\n|\r')
    end_slashes_re = re.compile(r'(\\)*$')

    in_string = False
    in_multi = False
    in_single = False

    new_str = []
    index = 0
    for match in re.finditer(tokenizer, string):
        if not (in_multi or in_single):
            tmp = string[index:match.start()]
            if not in_string and strip_space:
                # replace white space as defined in standard
                tmp = re.sub('[ \t\n\r]+', '', tmp)
            new_str.append(tmp)
        elif not strip_space:
            # Replace comments with white space so that the JSON parser reports
            # the correct column numbers on parsing errors.
            new_str.append(' ' * (match.start() - index))

        index = match.end()
        val = match.group()

        if val == '"' and not (in_multi or in_single):
            escaped = end_slashes_re.search(string, 0, match.start())

            # start of string or unescaped quote character to end string
            if not in_string or (escaped is None or len(escaped.group()) % 2 == 0):  # noqa
                in_string = not in_string
            index -= 1  # include " character in next catch
        elif not (in_string or in_multi or in_single):
            if val == '/*':
                in_multi = True
            elif val == '//':
                in_single = True
        elif val == '*/' and in_multi and not (in_string or in_single):
            in_multi = False
            if not strip_space:
                new_str.append(' ' * len(val))
        elif val in '\r\n' and not (in_multi or in_string) and in_single:
            in_single = False
        elif not ((in_multi or in_single) or (val in ' \r\n\t' and strip_space)):  # noqa
            new_str.append(val)

        if not strip_space:
            if val in '\r\n':
                new_str.append(val)
            elif in_multi or in_single:
                new_str.append(' ' * len(val))

    new_str.append(string[index:])
    return ''.join(new_str)

#-------------------------------------------------------------------------------

def readCss():
    path = "../vender/css"
    cssList = ["default.css", "article.default.css"]
    global CSS_STYLE
    for css in cssList:
        cssFile = os.path.join(path, css)
        print(cssFile)
        content = Util.getTheFileContent(cssFile)
        CSS_STYLE = CSS_STYLE + content
    # print(CSS_STYLE)
    pass

def readBooks():
    booksJson = None
    with open("./book.json", 'r', encoding='utf-8') as fw:
        jsonString = json_minify(fw.read())
        booksJson = json.loads(jsonString)
    return booksJson

def clone(name, git, tag):
    if os.path.exists(name):
        return
    destCmd = "git clone --depth=1 "
    if len(tag) > 0: destCmd = destCmd + " -b " + tag + " "
    destCmd = destCmd + git  + " "
    if len(name) > 0: destCmd = destCmd + name + " "

    try:
        runCMD = destCmd
        gitHttps = "https://github.com/"
        ssh = "git@github.com:"
        if gitHttps in runCMD:
            runCMD = runCMD.replace(gitHttps, ssh)
        operator(runCMD)
    except Exception as e:
        print(str(e), color=Color.Red)
        operator(destCmd)
    pass

def processChapters(ymls):
    # print(ymls)
    orderDict = collections.OrderedDict()
    def setOrderDict(key, value):
        if key in orderDict:
            values = orderDict[key]
            values.append(value)
        else:
            orderDict[key] = [value]

    category = ""
    for data in ymls:
        if data.count(SLASH) == 1:
            value = data.replace(SLASH, "")
            setOrderDict(SLASH, value)
        else:
            if ".md:" not in data:
                category = data.split("/:")[0]
                continue
            else:
                value = data.replace(category+SLASH, "")
                setOrderDict(category, value)
    return orderDict

def generateChaters(orderChapters, name):

    destPath = os.path.join(DEST_DIR, name)
    print(destPath)
    if not os.path.exists(destPath):
        os.makedirs(destPath)

    chapters = []
    index = 0
    print(os.getcwd())
    for key, values in orderChapters.items():
        key = key.strip(SLASH)
        subIndex = 1
        for value in values:
            data = value.split(":")
            fileName = str(data[0]).strip()
            desc = str(data[1]).strip()
            filePath = os.path.join(DOCS, key, fileName)
            
            outputDir = os.path.join(destPath, key)
            outputFile = os.path.join(destPath, key, fileName.replace(".md", ".html"))
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)

            indexName = str(index)+"."+str(subIndex)
            content = Util.getTheFileContent(filePath)
            # 将markdown文本转换html的样式
            content  = Util.transformTheMarkdownToHtml(content)
            content = CONTENT_TMP % (CSS_STYLE, content)
            Util.writeContentToFile(outputFile, content)
            # print(indexName, "---->", filePath, desc, outputDir, outputFile)
            subIndex = subIndex + 1
            chapters.append([indexName, key, fileName.replace(".md", ".html")])

        index = index + 1
    print(" ")
    indexPath = os.path.join(destPath, "index.html")
    print(chapters)
    html = ""
    for chapter in chapters:
        category = chapter[0]
        dirPath = chapter[1]
        file = chapter[2]
        name = file.replace(".html", "")
        filePath = os.path.join(dirPath, file)
        content = '<li><a href="%s">%s %s</a></li>' % (filePath, category, name)
        html = html + content

    content = CONTENT_TMP % (CSS_STYLE, html)
    Util.writeContentToFile(indexPath, content)

def main():
    currentDir = os.getcwd()
    readCss()
    global DEST_DIR
    DEST_DIR = os.path.join(currentDir, DEST_NAME)
    # print(DEST_DIR)
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    
    # return
    html = ""
    books = readBooks()
    for book in books:
        # print(book)
        name = book["name"]
        git = book["git"]
        tag = book["tag"]
        if len(git) == 0: continue
        clone(name, git, tag)
        os.chdir(name)
        ymls = []
        with open("./chapters.yml", 'r', encoding='utf-8') as f:
            lines = f.read().split("- ")
            for line in lines:
                if len(line) == 0: continue
                ymls.append(SLASH+line.strip())
        orderChapters = processChapters(ymls)
        generateChaters(orderChapters, name)
        html = html + '<li><a href="%s/%s/index.html">%s</a></li>' % (DEST_NAME, name, name)
    
    os.chdir(currentDir)
    indexPath = os.path.join(currentDir, "index.html")
    content = CONTENT_TMP % (CSS_STYLE, html)
    Util.writeContentToFile(indexPath, content)
    pass

if __name__ == '__main__':
    main()
    pass

"""
<link rel="stylesheet" href="../../../../vender/js/highlight/zruibin_code.css" />
<!-- <script type="text/javascript" charset="UTF-8" src="../../../../vender/js/highlight/highlight.min.js" />  -->
<script>
hljs.configure({
    // 忽略未经转义的 HTML 字符
    ignoreUnescapedHTML: true,
});
hljs.highlightAll();
</script>
"""


