import json
import os
import re

data_dir = 'data\\output\\electra_large'
result_file = 'electra_annot_finetuning_data_output_electra_large_result_20200826_092123.txt'
output_file = '{}_single.txt'.format(result_file.split('.')[0])
output_file2 = '{}_full.txt'.format(result_file.split('.')[0])
abbr_file = 'data\\abbr_map.json'

with open(abbr_file, 'r', encoding='utf8') as abbr_fh:
  abbr_maps = json.load(abbr_fh)

event_num_dict = {}
unique_event_num_dict = {}
with open(os.path.join(data_dir, result_file), 'r', encoding='utf8') as input_fh, open(
    os.path.join(data_dir, output_file), 'w', encoding='utf8') as output_fh, open(
  os.path.join(data_dir, output_file2), 'w', encoding='utf8') as output_fh2:
  for _i, line in enumerate(input_fh):
    data = json.loads(line)
    doc_id = data['doc_id']
    abbr_map = abbr_maps[doc_id]
    event_num = len(data['events'])
    event_num_dict[event_num] = event_num_dict.get(event_num, 0) + 1
    events_set = set()
    valid_idx = []
    tmp_data_events = []
    for _j, event in enumerate(data['events']):
      updated_event = {}
      event_str = ''
      for k, v in event.items():
        v = v.strip()
        v = re.sub(r'[<br>|&nbsp;|\s]+', '', v)
        if v in abbr_map.keys():
          v = abbr_map[v]
        # if v != event[k]:
        #   print(v, event[k])
        event[k] = v
        event_str += '{}_{}/'.format(k, v)
      if event_str not in events_set:
        events_set.add(event_str)
        valid_idx.append(_j)
        tmp_data_events.append(event)
    unique_event_num = len(events_set)
    if unique_event_num > 1:
      print(_i, data['doc_id'], events_set)
    unique_event_num_dict[unique_event_num] = unique_event_num_dict.get(unique_event_num, 0) + 1
    data['events'] = tmp_data_events
    result2 = json.dumps(data, ensure_ascii=False)
    output_fh2.write(result2)
    output_fh2.write('\n')
    data['events'] = [data['events'][0]]
    result = json.dumps(data, ensure_ascii=False)
    output_fh.write(result)
    output_fh.write('\n')

print(event_num_dict)
print(unique_event_num_dict)
