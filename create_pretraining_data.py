import os
import json
import re

data_dir = 'data\\ccks 4_2 Data'
input_file = 'event_element_train_data_label.txt'
pred_file = 'event_element_dev_data.txt'
output_dir = 'data\\pretrain'
output_file = 'pretrain_corpus.txt'
with open(os.path.join(data_dir, input_file), 'r', encoding='utf8') as train_fh, open(os.path.join(data_dir, pred_file),
    'r', encoding='utf8') as test_fh, open(os.path.join(output_dir, output_file), 'w', encoding='utf8') as output_fh:
  for i, org_line in enumerate(train_fh):
    org_json = json.loads(org_line)
    org_text = org_json['content']
    text = re.sub(r'\s', ' ', org_text)
    text = re.sub(r'<br>', ' ', text)
    text = re.sub(r'&nbsp', ' ', text)
    output_fh.write(text)
    output_fh.write('\n')
    output_fh.write('\n')
  for i, org_line in enumerate(test_fh):
    org_json = json.loads(org_line)
    org_text = org_json['content']
    text = re.sub(r'\s', ' ', org_text)
    text = re.sub(r'<br>', ' ', text)
    text = re.sub(r'&nbsp', ' ', text)
    output_fh.write(text)
    output_fh.write('\n')
    output_fh.write('\n')
