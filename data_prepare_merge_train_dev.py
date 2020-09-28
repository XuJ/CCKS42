import argparse
import json
import os

import tensorflow.compat.v1 as tf


def run_data_prepare(data_dir, part):
  input_dir = os.path.join(data_dir, 'finetuning_data', part)

  tf.io.gfile.rename(os.path.join(input_dir, 'train.tsv'), os.path.join(input_dir, 'train_backup.tsv'), True)
  tf.io.gfile.rename(os.path.join(input_dir, 'dev.tsv'), os.path.join(input_dir, 'dev_backup.tsv'), True)
  with tf.io.gfile.GFile(os.path.join(input_dir, 'train_backup.tsv'), 'r') as input_fh1, tf.io.gfile.GFile(
      os.path.join(input_dir, 'dev_backup.tsv'), 'r') as input_fh2, tf.io.gfile.GFile(
      os.path.join(input_dir, 'train.tsv'), 'w') as output_fh:
    for input_line in input_fh1:
      output_fh.write(input_line)
    for input_line in input_fh2:
      output_fh.write(input_line)
  tf.io.gfile.remove(os.path.join(input_dir, 'train_backup.tsv'))
  tf.io.gfile.remove(os.path.join(input_dir, 'dev_backup.tsv'))
  print('Done')


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--dir", required=True, help="location of all data")
  parser.add_argument("--part", default='full', help="build full/single/multi event model")
  args = parser.parse_args()
  run_data_prepare(args.dir, args.part)


if __name__ == '__main__':
  main()
