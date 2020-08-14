import os
import re
import json

data_dir = 'data\\output\\electra_large'
result_file = 'electra_finetuning_data_output_electra_large_result_20200811_120519.txt'
output_file = '{}_single.txt'.format(result_file.split('.')[0])

event_num_dict = {}
unique_event_num_dict = {}
with open(os.path.join(data_dir, result_file), 'r', encoding='utf8') as input_fh, open(os.path.join(data_dir, output_file), 'w', encoding='utf8') as output_fh:
  for _i, line in enumerate(input_fh):
    data = json.loads(line)
    event_num = len(data['events'])
    event_num_dict[event_num] = event_num_dict.get(event_num, 0) + 1
    events_set = set()
    for event in data['events']:
      event_str = ''
      for k, v in event.items():
        event_str += '{}_{}/'.format(k,v)
      events_set.add(event_str)
    unique_event_num = len(events_set)
    if unique_event_num> 1:
      print(_i, data['doc_id'], events_set)
    unique_event_num_dict[unique_event_num] = unique_event_num_dict.get(unique_event_num, 0) + 1
    data['events'] = [data['events'][0]]
    result = json.dumps(data, ensure_ascii=False)
    output_fh.write(result)
    output_fh.write('\n')

print(event_num_dict)
print(unique_event_num_dict)
