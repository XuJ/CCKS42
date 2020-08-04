import os
import json

import re
import random
import argparse
import tensorflow.compat.v1 as tf


def run_data_prepare(data_dir):
  input_dir = os.path.join(data_dir, 'ccks 4_2 Data')
  input_file = 'event_element_train_data_label.txt'
  pred_file = 'event_element_dev_data.txt'
  output_dir = os.path.join(data_dir, 'ccks42ec')
  output_dir2 = os.path.join(data_dir, 'ccks42num')
  if not tf.io.gfile.exists(output_dir):
    tf.io.gfile.makedirs(output_dir)
  if not tf.io.gfile.exists(output_dir2):
    tf.io.gfile.makedirs(output_dir2)
  train_file = 'train.tsv'
  dev_file = 'dev.tsv'
  test_file = 'eval.tsv'
  dev_ratio = 1 / 11
  random.seed(42)
  with open(os.path.join(input_dir, input_file), 'r', encoding='utf8') as input_fh, open(
      os.path.join(output_dir, train_file), 'w', encoding='utf8') as train_fh, open(os.path.join(output_dir, dev_file),
    'w', encoding='utf8') as dev_fh, open(os.path.join(output_dir2, train_file), 'w',
    encoding='utf8') as train_fh2, open(os.path.join(output_dir2, dev_file), 'w', encoding='utf8') as dev_fh2:
    for org_line in input_fh:
      data = json.loads(org_line)
      org_text = data['content']
      text = re.sub(r'\s', ' ', org_text)
      text = re.sub(r'<br>', ' ', text)
      text = re.sub(r'&nbsp', ' ', text)
      event_type_orig = data['events'][0]['event_type']
      event_num = str(int(len(data['events'])))
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
  print(single_event_types_orig + multi_event_types_orig)

  with open(os.path.join(input_dir, pred_file), 'r', encoding='utf8') as input_fh, open(
      os.path.join(output_dir, test_file), 'w', encoding='utf8') as test_fh, open(os.path.join(output_dir2, test_file),
    'w', encoding='utf8') as test_fh2:
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


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--dir", required=True, help="location of all data")
  args = parser.parse_args()
  run_data_prepare(args.dir)


if __name__ == '__main__':
  main()
