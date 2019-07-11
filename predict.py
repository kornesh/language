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
        clean = token.replace('<', '').replace('>', '').split(' ')[0].lower()
        if html_token:
            token = '<'+clean.title()+'>'
            #print(token.title())
        if token.startswith('<') and clean.replace('/', '') not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'dl', 'ol', 'li', 'tr', 'td', 'table', 'th', 'dd', 'dt']:
            continue
        t = NQToken(start_byte=0, end_byte=0, token=token, html_token=html_token)
        output.append(t._asdict())
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

def generate_nq_jsonl(page, question):
    doctokens = nq_tokenizer(page)
    candidates = []
    stack = []

    for i, t in enumerate(doctokens):
        if t['token'].startswith('<'):
            token = t['token'].replace('/', '')
            if token.replace('<', '').replace('>', '').lower() not in ['p', 'ul', 'dl', 'ol', 'li', 'tr', 'td', 'table', 'th', 'dd', 'dt']:
                continue
            if len(stack) != 0 and token == stack[-1][0]:
                s  = stack.pop()
                # if i - s[1] == 1:
                #     print("skipping", s[0], t['token'], "start_token", s[1], "end_token", i, "top_level", not bool(stack), "stack", stack)
                #     continue
                candidates.append(collections.OrderedDict([
                    ("start_token", s[1]),
                    ("top_level", not bool(stack)),
                    ("start_byte", -1),
                    ("end_token", i + 1),
                    ("end_byte", -1)]))
                #print(s[0], t['token'], "start_token", s[1], "end_token", i, "top_level", not bool(stack), "stack", stack)
            else:
                stack.append((t['token'], i))

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
    return e._asdict()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--page',
        type=str,
        help='Page filename')
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
        page = f.read()

    data = generate_nq_jsonl(page, args.question)
    #print(data)
    with open(args.output, 'w') as f:
        json.dump(dict(data), f)