import argparse
import json
import os
from collections import deque

import tensorflow.compat.v1 as tf


def run_data_prepare(data_dir, part):
  input_dir = os.path.join(data_dir, 'electra_ensemble2', 'finetuning_data', part)

  tf.io.gfile.rename(os.path.join(input_dir, 'train.json'), os.path.join(input_dir, 'train_backup.json'), True)
  tf.io.gfile.rename(os.path.join(input_dir, 'dev.json'), os.path.join(input_dir, 'dev_backup.json'), True)
  with tf.io.gfile.GFile(os.path.join(input_dir, 'train_backup.json'), 'r') as input_fh1, tf.io.gfile.GFile(
      os.path.join(input_dir, 'dev_backup.json'), 'r') as input_fh2, tf.io.gfile.GFile(
      os.path.join(input_dir, 'train.json'), 'w') as output_fh:
    orig_json1 = json.load(input_fh1)
    orig_json2 = json.load(input_fh2)
    train_json = {
      'version': 'v2.0', 'data': []
    }
    for data in orig_json1['data']:
      train_json['data'].append(data)
    for data in orig_json2['data']:
      train_json['data'].append(data)
    json.dump(train_json, output_fh, ensure_ascii=False)
  tf.io.gfile.remove(os.path.join(input_dir, 'train_backup.json'))
  tf.io.gfile.remove(os.path.join(input_dir, 'dev_backup.json'))
  print('Done')


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--dir", required=True, help="location of all data")
  parser.add_argument("--part", default='full', help="build full/single/multi event model")
  args = parser.parse_args()
  run_data_prepare(args.dir, args.part)


if __name__ == '__main__':
  main()
