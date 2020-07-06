import os
import json

import re
import random

model_name = 'electra_small'
data_dir = 'data\\ccks 4_2 Data'
input_file = 'event_element_train_data_label.txt'
pred_file = 'event_element_dev_data.txt'
cl_pred_result_file = 'data\\output\\{}\\ccks42ec_eval_preds.json'.format(model_name)
output_dir = 'data\\ccks42ee'
train_file = 'train.json'
dev_file = 'dev.json'
test_file = 'eval.json'
dev_ratio = 1 / 11
random.seed(42)
role_event_type_dict = {
  '高层死亡': ['公司名称', '高层人员', '高层职务', '死亡/失联时间', '死亡年龄'],
  '破产清算': ['公告时间', '公司名称', '公司行业', '受理法院', '裁定时间'],
  '重大资产损失': ['公告时间', '公司名称', '损失金额', '其他损失'],
  '重大对外赔付': ['公告时间', '公司名称', '赔付金额', '赔付对象'],
  '重大安全事故': ['公告时间', '公司名称', '伤亡人数', '损失金额', '其他影响'],
  '股权冻结': ['冻结金额', '被冻结股东', '冻结开始日期', '冻结结束日期'],
  '股权质押': ['质押金额', '质押方', '接收方', '质押开始日期', '质押结束日期'],
  '股东增持': ['增持金额', '增持的股东', '增持开始日期'],
  '股东减持': ['减持金额', '减持的股东', '减持开始日期'],
}

train_json = {
  'version': 'v2.0',
  'data': []
}
dev_json = {
  'version': 'v2.0',
  'data': []
}
with open(os.path.join(data_dir, input_file), 'r', encoding='utf8') as input_fh, open(
    os.path.join(output_dir, train_file), 'w', encoding='utf8') as train_fh, open(os.path.join(output_dir, dev_file),
                                                                                  'w',
                                                                                  encoding='utf8') as dev_fh:
  for i, org_line in enumerate(input_fh):
    org_json = json.loads(org_line)
    org_text = org_json['content']
    text = re.sub(r'\s', ' ', org_text)

    if random.random() < dev_ratio:
      task = 'dev'
    else:
      task = 'train'

    data = {
      'paragraphs': [
        {
          'id': '{}_{}'.format(task.upper(), i),
          'context': text,
          'qas': [],
        }
      ],
      'id': '{}_{}'.format(task.upper(), i),
      'title': org_json['doc_id'],
    }

    for question_main_idx, event in enumerate(org_json['events']):
      event_type = event['event_type']
      role_list = role_event_type_dict[event_type]
      annotated_role_set = set(event.keys()) - set(['event_type', 'event_id'])
      assert annotated_role_set.issubset(set(role_list))

      for question_minor_idx, role in enumerate(role_list):
        question = '第{}_{}个问题：{}是什么？'.format(question_main_idx, question_minor_idx, role)
        if role in event.keys():
          argument = event[role]
          argument_start = text.find(argument)
          if argument_start == -1:
            print(argument, role, text)
          answers = [
            {
              'text': argument,
              'answer_start': argument_start
            }
          ]
          is_impossible = False
        else:
          answers = []
          is_impossible = True

        qas = {
          'question': question,
          'id': '{}_{}_QUERY_{}_{}'.format(task.upper(), i, question_main_idx, question_minor_idx),
          'answers': answers,
          'is_impossible': is_impossible,
        }

        data['paragraphs'][0]['qas'].append(qas)

    if task == 'train':
      train_json['data'].append(data)
    elif task == 'dev':
      dev_json['data'].append(data)

  json.dump(train_json, train_fh, ensure_ascii=False)
  json.dump(dev_json, dev_fh, ensure_ascii=False)


test_json = {
  'version': 'v2.0',
  'data': []
}
task = 'eval'
text_label_dict = {}
with open(cl_pred_result_file, 'r', encoding='utf8') as cl_pred_fh:
  for text, label in json.load(cl_pred_fh).items():
    text_label_dict[text]=label

with open(os.path.join(data_dir, pred_file), 'r', encoding='utf8') as input_fh, open(
    os.path.join(output_dir, test_file), 'w', encoding='utf8') as test_fh:
  for i, org_line in enumerate(input_fh):
    org_json = json.loads(org_line)
    org_text = org_json['content']
    text = re.sub(r'\s', ' ', org_text)

    data = {
      'paragraphs': [
        {
          'id': '{}_{}'.format(task.upper(), i),
          'context': text,
          'qas': [],
        }
      ],
      'id': '{}_{}'.format(task.upper(), i),
      'title': org_json['doc_id'],
    }

    if text in text_label_dict.keys():
      label = text_label_dict[text]
    else:
      print(text)
    event_type, r = label.split('_')
    for question_main_idx in range(1, int(r) + 1):
      role_list = role_event_type_dict[event_type]
      for question_minor_idx, role in enumerate(role_list):
        question = '第{}_{}个问题：{}是什么？'.format(question_main_idx, question_minor_idx, role)
        qas = {
          'question': question,
          'id': '{}_{}_QUERY_{}_{}'.format(task.upper(), i, question_main_idx, question_minor_idx),
        }
        data['paragraphs'][0]['qas'].append(qas)

    test_json['data'].append(data)
  json.dump(test_json, test_fh, ensure_ascii=False)

