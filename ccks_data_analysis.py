import json
import os
import re

import pandas as pd

data_dir = 'D:\\项目\\11 CCKS\\CCKS\\data'

argument_event_type_dict = {
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


def entity_analysis():
  file_name = 'ccks 4_1 Data\\event_entity_train_data_label.csv'

  uid_list = []
  text_list = []
  event_type_list = []
  entity_list = []
  with open(os.path.join(data_dir, file_name), 'r', encoding='utf-8-sig') as input_fh:
    for line in input_fh:
      try:
        assert len(line.strip().split('\t')) == 4
      except AssertionError:
        print(line, line.strip().split('\t'))
        break
      uid, text, event_type, entity = line.strip().split('\t')
      uid_list.append(uid)
      text_list.append(text)
      event_type_list.append(event_type)
      entity_list.append(entity)
  df = pd.DataFrame({
    'uid': uid_list,
    'text': text_list,
    'event_type': event_type_list,
    'entity': entity_list
  })
  df['text_len'] = df['text'].apply(lambda x: len(x))
  print(df['event_type'].value_counts())
  print(df['text_len'].describe())
  print(len(df['uid'].unique()))


def argument_analysis():
  file_name = 'ccks 4_2 Data\\event_element_train_data_label.txt'
  uid_list = []
  text_list = []
  event_num_list = []
  event_type_dict = {}
  argument_num_dict = {}
  for event_type in argument_event_type_dict.keys():
    argument_num_dict[event_type] = {}
    for argument in argument_event_type_dict[event_type]:
      argument_num_dict[event_type][argument] = 0
  with open(os.path.join(data_dir, file_name), 'r', encoding='utf8') as input_fh:
    for line in input_fh:
      data = json.loads(line)
      uid = data['doc_id']
      text = data['content']
      event_num = len(data['events'])
      uid_list.append(uid)
      text_list.append(text)
      event_num_list.append(event_num)
      for event in data['events']:
        event_type = event['event_type']
        event_type_dict[event_type] = event_type_dict.get(event_type, 0) + 1

        argument_list = argument_event_type_dict[event_type]
        for argument in argument_list:
          if argument in event.keys():
            argument_num_dict[event_type][argument] += 1
      if event_num > 1:
        event_set = set()
        for event in data['events']:
          event_set.add(event['event_type'])
        print(event_set)

  df = pd.DataFrame({
    'uid': uid_list,
    'text': text_list,
    'event_num': event_num_list,
  })
  df['text_len'] = df['text'].apply(lambda x: len(x))
  print(df['event_num'].value_counts())
  print(df['text_len'].describe())
  print(event_type_dict)
  print(argument_num_dict)
  print(len(df['uid'].unique()))


def min_partition_analysis():
  splitter = '。|！|？|……'
  file_name = 'ccks 4_2 Data\\event_element_train_data_label.txt'
  with open(os.path.join(data_dir, file_name), 'r', encoding='utf8') as input_fh:
    for line in input_fh:
      data = json.loads(line)
      uid = data['doc_id']
      text = data['content']
      if len(data['events']) == 0:
        continue
      arguments_dict = {}
      for event in data['events']:
        event_type = event['event_type']
        arguments_dict[event_type] = []
        argument_list = argument_event_type_dict[event_type]
        for role in argument_list:
          if role in event.keys():
            arguments_dict[event_type].append(event[role])
      if len(data['events']) > 1:
        print(len(data['events']), arguments_dict)
      for sentence in re.split(splitter, text):
        has_event = False
        has_all_events = False
        for event_type, arguments in arguments_dict.items():
          all_in = 0
          for argument in arguments:
            if argument in sentence:
              has_event = True
              all_in += 1
          if all_in == len(arguments):
            has_all_events = 1
            break
        if has_event:
          if has_all_events:
            print(sentence, event_type)
          else:
            print(sentence, event_type)


if __name__ == '__main__':
  # entity_analysis()
  argument_analysis()
  # min_partition_analysis()
