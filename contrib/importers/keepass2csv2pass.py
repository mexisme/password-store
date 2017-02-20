#!/usr/bin/env python3

# Copyright 2015 David Francoeur <dfrancoeur04@gmail.com>
# This file is licensed under the GPLv2+. Please see COPYING for more information.

# KeePassX 2+ on Mac allows export to CSV. The CSV contains the following headers :
# "Group","Title","Username","Password","URL","Notes"
# Group and Title are used to build the path, @see prepareForInsertion
# Password is the first line and the url and the notes are appended after
#
# Usage: ./csv_to_pass.py test.csv

import csv
import itertools
import sys
from subprocess import Popen, PIPE

def pass_import_entry(path, data):
        """ Import new password entry to password-store using pass insert command """
        proc = Popen(['pass', 'insert', '--multiline', path], stdin=PIPE, stdout=PIPE)
        proc.communicate(data.encode('utf8'))
        proc.wait()

def readFile(filename, baseDir):
        """ Read the file and proccess each entry """
        with open(filename, 'rU') as csvIN:
                next(csvIN)
                outCSV=(line for line in csv.reader(csvIN, dialect='excel'))
                #for row in itertools.islice(outCSV, 0, 1):
                for row in outCSV:
                        #print("Length: ", len(row), row)
                        prepareForInsertion(row, baseDir)


def prepareForInsertion(row, baseDir):
        """ prepare each CSV entry into an insertable string """
        data = []
        path = []

        keyFolder = escape(row[0][4:])
        keyName = escape(row[1])

        for pathItem in (keyFolder, keyName, baseDir):
                if pathItem:
                        path.insert(0, pathItem)
        path = "/".join(path)

        fields = {
                "login": row[2],
                "password": row[3],
                "url": row[4],
                "notes": row[5]
        }
        # username = row[2]
        password = row[3]
        # url = row[4]
        # notes = row[5]

        #path = keyFolder+"/"+keyName+"/"+username

        data.append(password if password else "")
        data.append("---")
        for field in ("login", "url"):
                if fields[field]:
                        data.append("%s: %s" % (field, fields[field]))
        for field in ("notes",):
                if fields[field]:
                        yaml_field = fields[field].split("\n")
                        yaml_field = "  %s" % ("\n  ".join(yaml_field),)
                        data.append("%s: |\n%s" % (field, yaml_field))

        data = "\n".join(data)
        # data = "%s%s: %s\n" % (data, "login", username)
        # data = "%s%s: %s\n" % (data, "url", url)
        # data = "%s%s:\n%s\n" % (data, "notes", notes)

        pass_import_entry(path, data)
        print(path + " imported!")

def escape(strToEscape):
        """ escape the list """
        return strToEscape.replace(" ", "-").replace("&","and").replace("[","").replace("]","")


def main(argv):
        baseDir = ""
        inputFile = sys.argv[1]
        if len(sys.argv) > 1:
                baseDir = sys.argv[2]
        print("File to read: " + inputFile)
        readFile(inputFile, baseDir)


main(sys.argv)
