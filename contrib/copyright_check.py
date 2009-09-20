# Copyright (C) 2009, Luke Kenneth Casson Leighton <lkcl@lkcl.net>
""" This is a debian copyright file checker.  Put debian/copyright
    file conforming to http://dep.debian.net/deps/dep5/ and
    this program tells you which copyright holders you missed.

    Limitations:
    
    * for each section, you must put the full set of copyright holders.
      whilst the file lists are "carried over" i.e. later sections
      override earlier ones (see "remove_files()"), the same trick is
      NOT applied to copyright holders.

    * the qgram algorithm is applied to do some fuzzy string matching.
      it's pretty good, but don't rely on it to be perfect.

    * copyright year matching goes against "199" and "200" not
      "198?", "199?", "200?" and certainly not "201?".  if a name
      happens to have "199" or "200" in it, on a line that happens
      to have the word "copyright" in it, it gets assumed to be
      a copyright holder

    * random sentences tacked onto the end of copyrights in files
      are assumed to be part of the copyright holders' name

    * copyrights are assumed to be in the first 80 lines of the file

    * if the file doesn't _have_ a copyright notice, this program can't
      bloody well find it, can it??
"""

import glob
import sys
import os
from string import strip

# qgram: a way to "roughly" match words.  you're supposed to set splitlen
# to half the length of the average word, but 3 is good enough.
def qgram_set(word, splitlen):
    s = set()
    pad = '\0'*(splitlen-1)
    word = pad + word + pad
    for idx in range(len(word)-splitlen):
        s.add(word[idx:idx+splitlen])
    return s

def qgram(word1, word2, splitlen=3):
    s1 = qgram_set(word1, splitlen)
    s2 = qgram_set(word2, splitlen)
    un = len(s1.union(s2))
    ic = len(s1.intersection(s2))
    return float(ic) / float(un)

def truncate_qgram(word1, word2):
    if word1 == word2:
        return 1.0
    qg = 0
    if len(word1) > len(word2):
        tmp = word1
        word1 = word2
        word2 = tmp
    for i in range(len(word1), len(word2)+1):
        qg = max(qgram(word1, word2[:i]), qg)
    return qg

# testing, testing... ok, it works.
#print qgram("Copyright (C) 2009, Luke Kenneth Casson Leighton <lkcl@lkcl.net>",
#             "Copyright (C) 2006, Google, Inc.")
#print qgram("Copyright (C) 2009, Luke Kenneth Casson Leighton <lkcl@lkcl.net>",
#            "Copyright (C) 2009, Luke Kenneth Casson Leighton <lkcl@lkcl.net>")
#print qgram("Copyright (C) 2009, Luke Kenneth Casson Leighton <lkcl@lkcl.net>",
#             "Copyright (c) 2008, Luke Kenneth Casson Leighton")
#print qgram("Copyright (C) 2009, Luke Kenneth Casson Leighton <lkcl@lkcl.net>",
#             "Copyright (c) 2008, 2009, Luke Kenneth Casson Leighton ")
#print qgram("Copyright (C) 2009, Luke Kenneth Casson Leighton",
#             "Copyright (c) 2008, 2009, Luke Kenneth Casson Leighton ")

def check_match(word, word_list):
    matches = set()
    not_matches = set()
    for word2 in word_list:
        match = truncate_qgram(word, word2)
        if match > 0.6:
            matches.add((word, word2))
        else:
            not_matches.add((word, word2))
    return matches, not_matches

def sanitise(copyright):
    if copyright[0] == ':':
        copyright = copyright[1:].strip()
    co = "(c)"
    fco = copyright.lower().find(co)
    if fco >= 0:
        copyright = copyright[:fco] + copyright[fco+len(co):]
    srrs = "some rights reserved"
    srr = copyright.lower().find(srrs)
    if srr >= 0:
        copyright = copyright[:srr] + copyright[srr+len(srrs):]
    arrs = "all rights reserved"
    arr = copyright.lower().find(arrs)
    if arr >= 0:
        copyright = copyright[:arr] + copyright[arr+len(arrs):]
    return copyright
    # hmmm... something not quite right here...
    res = ''
    for c in copyright:
        if c.isalnum():
            res += c
        else:
            res += ' '
    res = res.split(' ')
    res = filter(lambda x:x, res)
    return ' '.join(res)

def find_file_copyright_notices(fname):
    ret = set()
    f = open(fname)
    lines = f.readlines()
    for l in lines[:80]: # hmmm, assume copyright to be in first 80 lines
        idx = l.lower().find("copyright")
        if idx < 0:
            continue
        copyright = l[idx+9:].strip()
        copyright = sanitise(copyright)
        # hmm, do a quick check to see if there's a year,
        # if not, skip it
        if not copyright.find("200") >= 0 and \
           not copyright.find("199") >= 0 :
           continue
        ret.add(copyright)
    return ret

def skip_file(fname):
    if fname.startswith(".svn"):
        return True
    if fname.startswith(".git"):
        return True
    if fname.startswith(".sw"):
        return True
    if fname == "output": # no thanks
        return True
    if fname.find("PureMVC_Python_1_0") >= 0: # no thanks
        return True
    if fname.endswith(".pyc"): # ehmm.. no.
        return True
    if fname.endswith(".java"): # no again
        return True
    return False

def get_files(d):
    res = []
    for p in glob.glob(os.path.join(d, "*")):
        if not p:
            continue
        (pth, fname) = os.path.split(p)
        if skip_file(fname):
            continue
        if os.path.islink(p):
            continue
        if os.path.isdir(p):
            res += get_dir(p)
        else:
            res.append(p)
    return res

def get_dir(match):
    data_files = []
    for d in glob.glob(match):
        if skip_file(d):
            continue
        if os.path.islink(d):
            continue
        if os.path.isdir(d):
            (pth, fname) = os.path.split(d)
            expath = get_files(d)
            data_files += expath
        else:
            data_files.append(d)
    return data_files

class DebSect:
    def __init__(self, pattern, files):
        self.file_pattern = pattern
        self.files = files
        self.copyrights = set()
        self.listed_copyrights = set()
        self.files_by_author = {}

    def read_files_for_copyrights(self):
        for fname in self.files:
            if fname.endswith("copyright_check.py"): # skip this program!
                continue
            if fname == 'debian/copyright': # skip this one duh
                continue
            cops = find_file_copyright_notices(fname)
            self.listed_copyrights.update(cops)
            for c in cops:
                if not self.files_by_author.has_key(c):
                    self.files_by_author[c] = set()
                if fname not in self.files_by_author[c]:
                    self.files_by_author[c].add(fname)
        print "Pattern", self.file_pattern
        for author in self.copyrights:
            print "Copyright:", author
        for author in self.listed_copyrights:
            print "Listed Copyright:", author

    def remove_files(self, to_remove):
        for fname in to_remove:
            if fname in self.files:
                self.files.remove(fname)

    def check_copyright_matches(self):
        self.matches = set()
        self.not_matches = set()

        for author in self.listed_copyrights:
            matches, not_matches = check_match(author, self.listed_copyrights)
            self.matches.update(matches)
            for (word1, word2) in not_matches:
                matches1, not_matches1 = check_match(word2, self.copyrights)
                #print "matches1, not_matches1", word1, word2, matches1, not_matches1
                if len(matches1) > 0:
                    continue
                #print "not matches", repr(word2), self.copyrights
                #print self.files_by_author[word2]
                self.not_matches.add(word2)

        if self.not_matches:
            print
            print"   ** ** ** ** **"
            for m in self.not_matches:
                print "   ** not matches:", m
                for fname in self.files_by_author[m]:
                    print"   ** ** ** ** **:", fname
        print

all_files = get_dir("*")
copyright_sects = []
all_listed_files = []

#print "all files", all_files

# read debian/copyright file and collect all matched files,
# copyrights and licenses
current_debsect = None
current_copyrights = set()
current_licenses = set()

dc = open("debian/copyright")
for l in dc.readlines():
    if l.startswith("License:"):
        current_licenses.add(strip(l[8:]))
        continue
    if l.startswith("Copyright:"):
        current_copyrights.add(sanitise(strip(l[10:])))
        continue
    if not l.startswith("Files:"):
        continue
    if current_debsect:
        current_debsect.licenses = current_licenses
        current_debsect.copyrights = current_copyrights
        current_copyrights = set()
        current_licenses = set()
    l = l.split(" ")
    l = map(strip, l)
    listed_files = []
    for pattern in l[1:]:
        if pattern[-1] == ',':
            pattern = pattern[:-1]
        files = get_dir(pattern)
        listed_files += files
        all_listed_files += files
    current_debsect = DebSect(l[1:], listed_files)
    copyright_sects.append(current_debsect)

if current_debsect:
    current_debsect.copyrights = current_copyrights
    current_debsect.licenses = current_licenses

dc.close()

# remove already-matching: further down takes precedence
for i in range(1, len(copyright_sects)):
    for j in range(i):
        #print i, j, copyright_sects[i].file_pattern, copyright_sects[j].file_pattern
        copyright_sects[j].remove_files(copyright_sects[i].files)
    
for dc in copyright_sects:
    dc.read_files_for_copyrights()
    dc.check_copyright_matches()
    print

#def check_in(l1, l2):
#    res = []
#    for fname in l1:
#        if fname not in l2:
#            res.append(fname)
#    return res
#
#not_in = check_in(all_files, listed_files)
#for fname in not_in:
#    print fname
#print listed_files
#print check_in(listed_files, all_files)

