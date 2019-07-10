import json

with open('custom.jsonl', 'r') as f:
    data = json.load(f)

def get_answer(pred):
    output = []
    for i in range(pred['start_token'], pred['end_token']):
        output.append(data['document_tokens'][i]['token'])
    return " ".join(output)

with open('predictions.json', 'r') as f:
    predictions = json.load(f)['predictions'][0]

print("Q:", data['question_text'])
print("A_S:", get_answer(predictions['short_answers'][0]))
print("A_L:", get_answer(predictions['long_answer']))