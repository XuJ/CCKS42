import os
import json

import re
import random

model_name = 'electra_large'
data_dir = 'data\\ccks 4_2 Data'
input_file = 'event_element_train_data_label.txt'
output_dir = 'data\\analysis'
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
event_type_questions_dict = {}
for k, v in role_event_type_dict.items():
  event_type_questions_dict[k] = []
  for i, r in enumerate(v):
    event_type_questions_dict[k].append({
      'question': r,
      'question_type': 'single',
      'group': '1',
      'enum_values': [],
      'key': i
    })

random.seed(42)
idx = random.randint(1, 100)
with open(os.path.join(data_dir, input_file), 'r', encoding='utf8') as input_fh:
  for i, org_line in enumerate(input_fh):
    org_json = json.loads(org_line)
    org_text = org_json['content']
    text = re.sub(r'\s', ' ', org_text)

    qas = []
    for question_main_idx, event in enumerate(org_json['events']):
      qas_sub = []
      event_type = event['event_type']
      role_list = role_event_type_dict[event_type]
      annotated_role_set = set(event.keys()) - set(['event_type', 'event_id'])
      assert annotated_role_set.issubset(set(role_list))

      questions = event_type_questions_dict[event_type]
      for question_minor_idx, role in enumerate(role_list):
        if role in event.keys():
          argument = event[role]
          argument_start = text.find(argument)
          if argument_start == -1:
            print(argument, role, text)
            qas_sub.append({
              'question': role,
              'answers': []
            })
          else:
            qas_sub.append({
              'question': role,
              'answers': [{
                'start_block': '0',
                'start': argument_start,
                'end_block': '0',
                'end': argument_start + len(argument) - 1,
                'text': argument,
                'sub_answer': None
              }]
            })
        else:
          qas_sub.append({
            'question': role,
            'answers': []
          })

      qas.append(qas_sub)
    data = {
      'document': [
        {
          'block_id': '0',
          'text': text,
        }
      ],
      'key': '{}'.format(i),
      'qas': qas,
      'questions': questions,
      'status': 1,
    }
    output_file = '{}_{}.json'.format(event_type, idx)
    if os.path.exists(os.path.join(output_dir, output_file)):
      if os.stat(os.path.join(output_dir, output_file)).st_size >= 900000:
        idx = random.randint(1, 100)
        output_file = '{}_{}.json'.format(event_type, idx)
    with open(os.path.join(output_dir, output_file), 'a', encoding='utf8') as output_fh:
      output_line = json.dumps(data, ensure_ascii=False)
      output_fh.write(output_line)
      output_fh.write('\n')
