import os
import json
import re

model_name = 'electra_small'
ec_pred_file = 'data\\output\\{}\\ccks42ec_eval_preds.json'.format(model_name)
ee_pred_file = 'data\\output\\{}\\ccks42ee_eval_1_preds.json'.format(model_name)
ee_input_file = 'data\\ccks42ee\\eval.json'
output_file = 'data\\output\\{}\\result.txt'.format(model_name)

with open(ec_pred_file, 'r', encoding='utf8') as ec_pred_fh:
  text_event_type_dict = json.load(ec_pred_fh)
with open(ee_pred_file, 'r', encoding='utf8') as ee_pred_fh:
  question_id_answer_dict = json.load(ee_pred_fh)
event_types_count_dict = {}
for k, v in text_event_type_dict.items():
  event_types_count_dict[v] = event_types_count_dict.get(v, 0) + 1
print(event_types_count_dict)

multi = 0
single = 0
with open(ee_input_file, 'r', encoding='utf8') as ee_input_fh, open(output_file, 'w', encoding='utf8') as output_fh:
  data = json.load(ee_input_fh)["data"]
  for _i, i in enumerate(data):
    print(_i)
    events = []
    text = i['paragraphs'][0]['context']
    event_type = text_event_type_dict[text]
    event_type, event_num = event_type.split('_')
    event_num = int(event_num)
    doc_id = i['title']
    qas_dict = {}
    if event_num > 1:
      multi += 1
    else:
      single += 1
    for n in range(1, event_num + 1):
      qas_dict[n] = []
    for j in i['paragraphs'][0]['qas']:
      question_id = j['id']
      event_index = int(question_id.split('_')[3])
      question = j['question']
      event_element = question.split('：')[-1]
      answer = question_id_answer_dict[question_id]
      qas_dict[event_index].append((event_element, answer))
    events = []
    for n in range(1, event_num + 1):
      event = {
        'event_type': event_type
      }
      for (q, a) in qas_dict[n]:
        if len(a) > 0:
          event[q] = a
      events.append(event)
    result = {
      'doc_id': doc_id,
      'events': events
    }
    output_fh.write(json.dumps(result, ensure_ascii=False))
    output_fh.write('\n')
print('#' * 30)
print(multi)
print(single)
