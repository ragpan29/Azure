#!/usr/bin/env python
import sys
import string


def check_negative(query, negative, matchtype):
    negative_found = 0
    negative_tokens = negative.split()

    if matchtype=="broad":
        presence = 0
        for broad in negative_tokens:
            if broad in query:
                presence = presence + 1
        if presence == len(negative_tokens):
            negative_found = 1
    elif matchtype == "phrase":
        if negative in query:
            negative_found = 1
    else:
        if negative == query:
            negative_found = 1

    return negative_found


while True:
    line = sys.stdin.readline()
    if not line:
        break

    line = string.strip(line, "\n ")
    query, negative, matchtype = string.split(line, "\t")
    
    print( check_negative(query, negative, matchtype) )

