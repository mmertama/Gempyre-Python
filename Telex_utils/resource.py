import sys
import base64
import re
import os

def from_file_list(lst):
    """
    Generates a filemap for Telex
    :param lst: list of filenames.
    :return: two dictionaries, first is map second is to map it's keys to give arguments.
    """
    data = dict()
    names = dict()
    for inName in lst:
        encoded = ""
        with open(inName, 'rb') as infile:
            content = infile.read()
            encoded = base64.standard_b64encode(content).decode('utf-8')
        sname = '/' + re.sub('[^a-zA-Z_.]', '', os.path.basename(inName)) # why this was capitalize()?
        data[sname] = encoded
        names[inName] = sname
    return data, names
    
    
def from_file(*argv):
    """
    Generates a filemap for Telex
    :param argv: argument list of filenames.
    :return: two dictionaries, first is map second is to map it's keys to give arguments.
    """
    lst = list()
    for a in argv:
        lst.append(a);
    return from_file_list(lst)

