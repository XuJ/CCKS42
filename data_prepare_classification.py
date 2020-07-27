import os
import json

import re
import random

data_dir = 'data\\ccks 4_2 Data'
input_file = 'event_element_train_data_label.txt'
pred_file = 'event_element_dev_data.txt'
output_dir = 'data\\ccks42ec'
output_dir2 = 'data\\ccks42num'
train_file = 'train.tsv'
dev_file = 'dev.tsv'
test_file = 'eval.tsv'
dev_ratio = 1 / 11
random.seed(42)
with open(os.path.join(data_dir, input_file), 'r', encoding='utf8') as input_fh, open(
    os.path.join(output_dir, train_file), 'w', encoding='utf8') as train_fh, open(os.path.join(output_dir, dev_file),
                                                                                  'w',
                                                                                  encoding='utf8') as dev_fh, open(os.path.join(output_dir2, train_file), 'w', encoding='utf8') as train_fh2, open(os.path.join(output_dir2, dev_file),  'w', encoding='utf8') as dev_fh2:
  for org_line in input_fh:
    data = json.loads(org_line)
    org_text = data['content']
    text = re.sub(r'\s', ' ', org_text)
    text = re.sub(r'<br>', ' ', text)
    text = re.sub(r'&nbsp', ' ', text)
    event_type_orig = data['events'][0]['event_type']
    event_num = str(int(len(data['events'])))
    # event_type = '{}_{}'.format(event_type_orig, event_num)
    event_type = event_type_orig
    output_line = '\t'.join([text, event_type])
    output_line2 = '\t'.join([text, event_num])
    if random.random() < dev_ratio:
      dev_fh.write(output_line)
      dev_fh.write('\n')
      dev_fh2.write(output_line2)
      dev_fh2.write('\n')
    else:
      train_fh.write(output_line)
      train_fh.write('\n')
      train_fh2.write(output_line2)
      train_fh2.write('\n')

single_event_types_orig = ['重大资产损失', '高层死亡', '重大对外赔付', '重大安全事故', '破产清算']
multi_event_types_orig = ['股东减持', '股权质押', '股权冻结', '股东增持']
print(single_event_types_orig+multi_event_types_orig)
# event_types = []
# for event_type in multi_event_types_orig:
#   for i in [1, 2, 3, 4, 5]:
#     event_types.append('{}_{}'.format(event_type, i))
# for event_type in single_event_types_orig:
#   event_types.append('{}_1'.format(event_type))
# print(event_types)
#
# for file in [train_file, dev_file]:
#   event_type_count_dict = {}
#   with open(os.path.join(output_dir, file), 'r', encoding='utf8') as train_fh:
#     for org_line in train_fh:
#       if len(org_line.split('\t')) != 2:
#         print(len(org_line.split('\t')), org_line)
#       if org_line.split('\t')[-1].strip() not in event_types:
#         print(org_line.split('\t')[-1].strip(), org_line)
#       else:
#         event_type = org_line.split('\t')[-1].strip()
#         event_type_count_dict[event_type] = event_type_count_dict.get(event_type, 0) + 1
#   print(file, event_type_count_dict)

with open(os.path.join(data_dir, pred_file), 'r', encoding='utf8') as input_fh, open(
    os.path.join(output_dir, test_file), 'w', encoding='utf8') as test_fh, open(
  os.path.join(output_dir2, test_file), 'w', encoding='utf8') as test_fh2:
  for org_line in input_fh:
    data = json.loads(org_line)
    org_text = data['content']
    text = re.sub(r'\s', ' ', org_text)
    text = re.sub(r'<br>', ' ', text)
    text = re.sub(r'&nbsp', ' ', text)
    output_line = '\t'.join([text, '没有标签自己预测'])
    test_fh.write(output_line)
    test_fh.write('\n')
    test_fh2.write(output_line)
    test_fh2.write('\n')
