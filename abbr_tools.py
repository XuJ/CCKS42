# encoding:utf-8
"""
    name:huyebowen
    mail:huyebowen@hexin.com
    用法： 直接调用abbr_extract，输入位json 数据， 返回为(全称，简称)列表
"""

import re

import fool

from data_cleaning import argument_cleaning_v1


def get_abbr_sentence(text):
  pattern = re.compile('[^，。]*简称[^，。]*[，。]')
  abbr_text = pattern.findall(text)
  return abbr_text


def get_abbr_list(text_list):
  # 返回简称和句中的起始位置 (start, end, abbr_name)
  result = list()
  text = "".join(text_list)
  for ele in re.finditer(r"[简称|或]“([^”“]*)”", text):
    name = ele.group().strip("简称|或").strip('“|”')
    if name not in ["本公司", "公司"]:
      result.append((ele.start(), ele.end(), name))
  return result, text


def get_ans_name(content):
  ans_type = ["公司名称", "高层人员", "被冻结股东", "质押方", "接收方", "增持的股东", "减持的股东"]
  ans_name = []
  for ans in content['events']:
    ans_name.extend([ans[at] for at in ans_type if at in ans.keys()])
  return ans_name


def abbr_extract(content, task='train'):
  result = []
  if task == 'test':
    abbr_text_list = get_abbr_sentence(argument_cleaning_v1(content['content']))
    abbr_list, abbr_text = get_abbr_list(abbr_text_list)
    full_name = [ele for ele in fool.ner(abbr_text)[0] if ele[2] in ['company', 'org']]
    abbr_set = set([n[2] for n in abbr_list])
    for abbr in abbr_list:
      ab_s, ab_e, ab_text = abbr
      candidate = None
      for f in full_name:
        if (int(f[1]) < ab_s) & (f[3] not in abbr_set):
          candidate = (f[3].strip(), ab_text)
        elif int(f[1]) > ab_s:
          break
      if candidate is not None:
        result.append(candidate)
      else:
        print(abbr, full_name)
    return result

  elif task == 'train':
    abbr_text_list = get_abbr_sentence(argument_cleaning_v1(content['content']))
    abbr_list, abbr_text = get_abbr_list(abbr_text_list)
    ans_name = get_ans_name(content)
    for name in ans_name:
      temp = 10000
      candidate_abbr = None
      if name not in abbr_text:
        continue
      end = abbr_text.index(name) + len(name)
      for abbr in abbr_list:
        start = abbr[0]
        if start - end < 0:
          continue
        elif start - end < temp:
          temp = start - end
          candidate_abbr = abbr[2]
      if candidate_abbr is not None:
        result.append((name, candidate_abbr))
    return result


if __name__ == "__main__":
  import json

  d = {}
  with open('data/ccks 4_2 Data/event_element_dev_data.txt', 'r', encoding='utf8') as input_fh:
    for i, line in enumerate(input_fh):
      e = {}
      data = json.loads(line)
      content = data['content']
      doc_id = data['doc_id']
      for n, a in abbr_extract(data, task='test'):
        n = n.strip()
        a = a.strip()
        n = re.sub(r'[<br>|&nbsp;|\s]+', '', n)
        a = re.sub(r'[<br>|&nbsp;|\s]+', '', a)
        if a in e.keys():
          if n == e[a]:
            continue
          else:
            print(a, n, e[a], content, doc_id)
        else:
          e[a] = n
      d[doc_id] = e
  with open('data/abbr_map.json', 'w', encoding='utf8') as output_fh:
    json.dump(d, output_fh)
  print(d)
