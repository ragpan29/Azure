#/usr/bin/python

def contiguous_ngram(tokens, imp, click):
    ngrams = []
    for idx, focus_token in enumerate(tokens):
        if idx+1 >= len(tokens):
            continue
        else:
            next_token = tokens[idx+1]
            ngrams.append((focus_token+' '+next_token,imp,click))
    return ngrams

def skip_ngram(tokens, imp, click,skip=2):
    ngrams = []
    for idx, focus_token in enumerate(tokens):
        for next_token in tokens[(idx+skip):len(tokens)]:
            ngrams.append((focus_token+' '+next_token,imp,click))
            
    return ngrams

def ngram(query, imp, click,skip=None):
    tokens = query.strip().split()
    if len(tokens)==1:
        return [(query, imp, click)]
    
    if (skip):
        ngrams = skip_ngram(tokens, imp, click, skip)
    else:
        ngrams = contiguous_ngram(tokens, imp, click)
    
    return ngrams

@outputSchema("tokens: {(token:chararray, impressions:int, clicks:int)}")
def forward_ngram(query, imp, click, skip=None):
    return ngram(query, imp, click, skip)

@outputSchema("tokens: {(token:chararray, impressions:int, clicks:int)}")
def reverse_ngram(query, imp, click, skip=None):
    tokens = query.split(' ')
    tokens_rev = reversed(tokens)
    query_rev = ' '.join(tokens_rev)
    return ngram(query_rev, imp, click, skip)