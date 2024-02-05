#! /usr/bin/python3
# coding=utf-8
# 
# server.py
# zruibin.cc
#
# Created by Ruibin.Chow on 15/12/31.
# Copyright (c) 2015年 www.zruibin.cc. All rights reserved.
#

import os, zipfile, random, shutil
import hashlib
import getpass

zipDir = './app'
zipName = 'app.zip'
encryptName = 'srv.d'
outputName = 'private.zip'


def getAllFileInDir(DIR):
    """返回指定目录下所有文件的集合"""
    array = []
    for root, dirs, files in os.walk(DIR):
        for name in files:
            path = root + '/' + name
            array.append(path)
            # print(os.path.basename(name))
    return array

def show(DIR):
    """列出指定目录下所有文件"""
    array = getAllFileInDir(DIR)
    for path in array:
        print(path)
    pass


def getTheFileContent(fileName):
    """获得文件的内容"""
    fp = open(fileName, 'r', encoding='utf8', errors='ignore') 
    allText = fp.read()
    fp.close()
    return allText


def writeContentToFile(fileName, content, mode='w'):
    """以特定的方式向文件写内容"""
    fp = open(fileName, mode)
    print(type(content))
    fp.write(str(content))
    fp.close()
    pass


def convert_character(string, origin_string, replace_string):
    """用指定的字符替换文本中指定的字符"""
    string = string.replace(origin_string, replace_string)
    return string



def zip(dirName, fileName):
    array = getAllFileInDir(dirName)
    z = zipfile.ZipFile(fileName, 'w')
    for name in array:
        z.write(name)
    z.close() 
    pass

def encodeFile():
    obj = keyAndPassword()
    content = getTheFileContent(zipName)
    content = encryptContent(str(content), obj)
    writeContentToFile(encryptName, content)
    os.remove(zipName)
    shutil.rmtree(zipDir)
    pass

def decodeFile():
    obj = keyAndPassword()
    content = getTheFileContent(encryptName)
    content = decryptContent(content, obj)
    writeContentToFile(zipName, content)
    os.remove(encryptName)
    pass


def keyAndPassword():
    key = input("key:")
    password = getpass.getpass("password:")
    print('key: ' + str(key) + '---' + 'password length: ' + str(len(password)))
    obj = dict()
    obj['key'] = hashlib.sha256(key.encode()).hexdigest()
    obj['password'] = hashlib.sha256(password.encode()).hexdigest()
    return obj

def encryptContent(content, obj):
    data = '<--' + str(obj['key']) + str(obj['password']) + '-->'
    length = len(content)
    insertIndex = random.randint(1, length)
    content = content[:insertIndex] + data + content[insertIndex:]
    return content

def decryptContent(content, obj):
    data = '<--' + str(obj['key']) + str(obj['password']) + '-->'
    content = convert_character(content, data, '')
    return content

def output():
    articleArray = getAllFileInDir("./article")
    venderArray = getAllFileInDir("./vender")
    imageArray = getAllFileInDir("./file/image")
    array = articleArray + venderArray + imageArray
    array.append("./about.html")
    array.append("./index.html")
    z = zipfile.ZipFile(outputName, 'w')
    for name in array:
        print(name)
        z.write(name)
    z.close()
    print("output done.")
    pass


def Main():
    option = input("encode(1)、decode(2)、output(3):")
    if int(option) == 1:
        # zip(zipDir, zipName)
        # encodeFile()
        print("encode was deprecated in Pyhton3.")
    if int(option) == 2:
        # decodeFile()
        print("decode was deprecated in Pyhton3.")
    if int(option) == 3:
        output()
    pass





if __name__ == '__main__':
    Main()
    pass





