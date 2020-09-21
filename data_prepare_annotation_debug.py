import argparse
import json
import os
import re

import tensorflow.compat.v1 as tf

from data_cleaning import is_chinese_char


def argument_cleaning_v3_debug(content):
  pattern = r'\d{4}[-|年|./]\d{1,2}[-|月|./]\d{1,2}[日]?(\d{1,2}[时](\d{1,2}[分])?)?(-((\d{4}[-|年|./])?\d{1,2}[-|月|./])?\d{1,2}[日]?)?'
  matched_dates = re.finditer(pattern, content)
  offsets = []
  for d in reversed(list(matched_dates)):
    offset = 0
    end = d.end()
    post_chinese_char = True
    bug_post_chinese_char = True
    if end < len(content):
      post_chinese_char = is_chinese_char(content[end])
    if end < len(content) - 1:
      bug_post_chinese_char = is_chinese_char(content[end + 1])

    if (bug_post_chinese_char == False) and (post_chinese_char == True):
      offset = -1
    elif (bug_post_chinese_char == True) and (post_chinese_char == False) and (content[end] != ' '):
      offset = 1

    if offset != 0:
      offsets.append((end, offset))
  return offsets


def run_data_prepare(data_dir):
  train_dir = os.path.join(data_dir, 'ccks 4_2 Data')
  annotated_dir = os.path.join(data_dir, 'annotated')
  train_input_file = 'event_element_train_data_label.txt'
  multi_event_types = ['股东减持', '股权质押', '股权冻结', '股东增持']

  offsets_dict = {}
  with tf.io.gfile.GFile(os.path.join(train_dir, train_input_file), 'r') as train_fh:
    for i, org_line in enumerate(train_fh):
      org_json = json.loads(org_line)
      org_text = org_json['content']
      doc_id = org_json['doc_id']
      offsets = argument_cleaning_v3_debug(org_text)
      offsets_dict[doc_id] = offsets

  for event_type in multi_event_types:
    tf.io.gfile.rename(os.path.join(annotated_dir, '{}.json'.format(event_type)),
      os.path.join(annotated_dir, '{}_backup.json'.format(event_type)), True)
    with tf.io.gfile.GFile(os.path.join(annotated_dir, '{}_backup.json'.format(event_type)),
        'r') as input_fh, tf.io.gfile.GFile(os.path.join(annotated_dir, '{}.json'.format(event_type)),
        'w') as output_fh:
      for line in input_fh:
        data = json.loads(line)
        doc_id = data['key']
        offsets = offsets_dict[doc_id]
        if len(offsets) > 0:
          for qas in data['qas']:
            for qas_sub in qas:
              if len(qas_sub['answers']) > 0:
                ans = qas_sub['answers'][0]
                start = int(ans['start'])
                end = int(ans['end'])
                for (time_end, offset) in offsets:
                  if start > time_end:
                    start += offset
                    end += offset
                ans['start'] = start
                ans['end'] = end
        output_line = json.dumps(data, ensure_ascii=False)
        output_fh.write(output_line)
        output_fh.write('\n')


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--dir", required=True, help="location of all data")
  args = parser.parse_args()
  run_data_prepare(args.dir)


if __name__ == '__main__':
  main()
