import json
import os
import re

data_dir = 'data\\output\\electra_large'
result_file = 'electra_best_finetuning_data_output_electra_large_result_full_20200927_060953.txt'
output_file = '{}_single.txt'.format(result_file.split('.')[0])
output_file2 = '{}_full.txt'.format(result_file.split('.')[0])
# abbr_file = 'data\\abbr_map.json'
pred_file = 'data\\ccks 4_2 Data\\event_element_dev_data.txt'

doc_id_text_dict = {}
with open(pred_file, 'r', encoding='utf8') as pred_fh:
  for org_line in pred_fh:
    data = json.loads(org_line)
    doc_id_text_dict[data['doc_id']] = data['content']


def reformat_date(d, doc_id):
  text = doc_id_text_dict[doc_id]
  year_flag = int('年' in d)
  month_flag = int('月' in d)
  day_flag = int('日' in d)
  if 3 > year_flag + month_flag + day_flag > 0:
    if year_flag and month_flag:
      new_d = d + '日'
      if text.find(new_d) >= 0:
        print('add 日:', doc_id, d, new_d)
        return new_d
    elif month_flag and day_flag:
      if d.startswith('-'):
        d = d[1:]
      if text.find('2019年' + d) >= 0:
        new_d = '2019年' + d
        print('add 2019年:', doc_id, d, new_d)
        return new_d
      elif text.find('2020年' + d) >= 0:
        new_d = '2020年' + d
        print('add 2020年:', doc_id, d, new_d)
        return new_d
  return d


role_entity_type_dict = {
  '公司名称': '公司', '高层人员': '人名', '高层职务': '职称', '死亡/失联时间': '时间', '死亡年龄': '数字', '公司行业': '行业', '公告时间': '时间', '受理法院': '机构',
  '裁定时间': '时间', '损失金额': '数字', '其他损失': '文本短语', '赔付金额': '数字', '赔付对象': '公司/人名', '伤亡人数': '数字', '其他影响': '文本短语', '冻结金额': '数字',
  '被冻结股东': '公司/人名', '冻结开始日期': '时间', '冻结结束日期': '时间', '质押金额': '数字', '质押方': '公司/人名', '接收方': '公司/人名', '质押开始日期': '时间',
  '质押结束日期': '时间', '增持金额': '数字&单位', '增持的股东': '公司/人名', '增持开始日期': '时间', '减持金额': '数字&单位', '减持的股东': '公司/人名', '减持开始日期': '时间',
}
single_event_types = ['高层死亡', '重大安全事故', '重大资产损失', '破产清算', '重大对外赔付']

# with open(abbr_file, 'r', encoding='utf8') as abbr_fh:
#   abbr_maps = json.load(abbr_fh)

event_num_dict = {}
unique_event_num_dict = {}
with open(os.path.join(data_dir, result_file), 'r', encoding='utf8') as input_fh, open(
    os.path.join(data_dir, output_file), 'w', encoding='utf8') as output_fh, open(os.path.join(data_dir, output_file2),
  'w', encoding='utf8') as output_fh2:
  for _i, line in enumerate(input_fh):
    data = json.loads(line)
    doc_id = data['doc_id']
    # abbr_map = abbr_maps[doc_id]
    event_num = len(data['events'])
    if event_num == 0:
      print('event_num zero error:', _i, data['doc_id'])
      continue
    event_type = data['events'][0]['event_type']
    if event_type not in event_num_dict:
      event_num_dict[event_type] = {}
    event_num_dict[event_type][event_num] = event_num_dict[event_type].get(event_num, 0) + 1
    events_set = set()
    tmp_data_events = []
    for _j, event in enumerate(data['events']):
      updated_event = {}
      event_str = ''
      for k, v in event.items():
        v = v.strip()
        v = re.sub(r'(?<![a-zA-Z])(<br>|&nbsp;|\s)+', '', v)
        v = re.sub(r'(<br>|&nbsp;|\s)+(?![a-zA-Z])', '', v)
        v = re.sub(r'(?<=[a-zA-Z])(<br>|\s)+(?=[a-zA-Z])', ' ', v)
        # if v in abbr_map.keys():
        #   v = abbr_map[v]
        if k != 'event_type' and role_entity_type_dict[k] == '时间':
          v = reformat_date(v, doc_id)
        event[k] = v
        event_str += '{}_{}/'.format(k, v)
      if event_str not in events_set:
        events_set.add(event_str)
        tmp_data_events.append(event)
    unique_event_num = len(events_set)
    if unique_event_num > 1 and event_type in single_event_types:
      print('event type single error:', _i, data['doc_id'], events_set)
    if event_type not in unique_event_num_dict:
      unique_event_num_dict[event_type] = {}
    unique_event_num_dict[event_type][event_num] = unique_event_num_dict[event_type].get(event_num, 0) + 1
    data['events'] = tmp_data_events
    if event_type in single_event_types:
      data['events'] = [data['events'][0]]
    result2 = json.dumps(data, ensure_ascii=False)
    output_fh2.write(result2)
    output_fh2.write('\n')
    if len(data['events']) > 0:
      data['events'] = [data['events'][0]]
    result = json.dumps(data, ensure_ascii=False)
    output_fh.write(result)
    output_fh.write('\n')

print(event_num_dict)
print(unique_event_num_dict)
