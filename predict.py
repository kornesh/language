import re
import random
import argparse
import collections
import json

regex = r"<[^>^]*>|[a-zA-Z0-9]+|[\S]"

def tokenizer(text):
    return re.findall(regex, text)

#Test
text = "<html><body><h1>Google Inc.</h1><p>Google was founded in 1998 By:<ul><li>Larry</li><li>Sergey</li></ul></p></body></html>"
question = "When Google was founded"
assert tokenizer(text) == ['<html>', '<body>', '<h1>', 'Google', 'Inc', '.', '</h1>', '<p>', 'Google', 'was', 'founded', 'in', '1998', 'By', ':', '<ul>', '<li>', 'Larry', '</li>', '<li>', 'Sergey', '</li>', '</ul>', '</p>', '</body>', '</html>']

#print(tokenizer(text))

def nq_tokenizer(text):
    output = []
    tokens = tokenizer(text)
    for token in tokens:
        html_token = token.startswith('<')
        t = NQToken(start_byte=0, end_byte=0, token=token, html_token=html_token)
        output.append(dict(t._asdict()))
    return output

NQExample = collections.namedtuple(
    'NQExample',
    [
        'example_id',
        'question_text',
        'question_tokens',
        'document_url',
        'document_title',
        'document_html',
        'document_tokens',
        'long_answer_candidates',
        'annotations'
    ])
NQToken = collections.namedtuple(
    'NQToken',
    [
        'start_byte',
        'token',
        'html_token',
        'end_byte'
    ])

def convert_question_to_nqexample(question, page):
    doctokens = nq_tokenizer(page)
    candidates = []

    for i in range(10):
        rand = random.randint(10, len(doctokens)-10)    
        candidates.append({"start_token": rand , "top_level": True, "start_byte": -1, "end_token": rand + 10, "end_byte": -1})

    e = NQExample(
        example_id=0,
        question_text=question,
        question_tokens=nq_tokenizer(question),
        document_url='http://sr.exoot.co/question',
        document_title='Predict Answer',
        document_html=page,
        document_tokens=doctokens,
        long_answer_candidates=candidates,
        annotations=[]
    )
    return dict(e._asdict())



parser = argparse.ArgumentParser()
parser.add_argument(
    '--page',
    type=str,
    help='Ppge filename')
parser.add_argument(
    '--question',
    type=str,
    help='Question text')
parser.add_argument(
    '--output',
    type=str,
    help='output')

args = parser.parse_args()

with open(args.page, 'r') as f:
    text = f.read()

data = convert_question_to_nqexample(args.question, text)
with open(args.output, 'w') as f:
    json.dump(data, f)