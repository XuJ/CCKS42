import argparse
import json
import os
import random

import tensorflow.compat.v1 as tf

from data_cleaning import argument_cleaning
from reannotate_training_data import ReAnnotate


def run_data_prepare(data_dir, split, result_dir, model_name):
  input_dir = os.path.join(data_dir, 'ccks 4_2 Data')
  train_input_file = 'event_element_train_data_label.txt'
  test_input_file = 'event_element_dev_data.txt'
  output_dir = os.path.join(data_dir, 'ccks42ee')
  if not tf.io.gfile.exists(output_dir):
    tf.io.gfile.makedirs(output_dir)
  train_file = 'train.json'
  dev_file = 'dev.json'
  test_file = 'eval.json'
  dev_ratio = 1 / 11
  random.seed(42)
  role_event_type_dict = {
    '高层死亡': ['公司名称', '高层人员', '高层职务', '死亡/失联时间', '死亡年龄'], '破产清算': ['公告时间', '公司名称', '公司行业', '受理法院', '裁定时间'],
    '重大资产损失': ['公告时间', '公司名称', '损失金额', '其他损失'], '重大对外赔付': ['公告时间', '公司名称', '赔付金额', '赔付对象'],
    '重大安全事故': ['公告时间', '公司名称', '伤亡人数', '损失金额', '其他影响'], '股权冻结': ['冻结金额', '被冻结股东', '冻结开始日期', '冻结结束日期'],
    '股权质押': ['质押金额', '质押方', '接收方', '质押开始日期', '质押结束日期'], '股东增持': ['增持金额', '增持的股东', '增持开始日期'],
    '股东减持': ['减持金额', '减持的股东', '减持开始日期'],
  }
  role_entity_type_dict = {
    '公司名称': '公司', '高层人员': '人名', '高层职务': '职称', '死亡/失联时间': '时间', '死亡年龄': '数字', '公司行业': '行业', '公告时间': '时间', '受理法院': '机构',
    '裁定时间': '时间', '损失金额': '数字', '其他损失': '文本短语', '赔付金额': '数字', '赔付对象': '公司/人名', '伤亡人数': '数字', '其他影响': '文本短语',
    '冻结金额': '数字', '被冻结股东': '公司/人名', '冻结开始日期': '时间', '冻结结束日期': '时间', '质押金额': '数字', '质押方': '公司/人名', '接收方': '公司/人名',
    '质押开始日期': '时间', '质押结束日期': '时间', '增持金额': '数字&单位', '增持的股东': '公司/人名', '增持开始日期': '时间', '减持金额': '数字&单位',
    '减持的股东': '公司/人名', '减持开始日期': '时间',
  }

  if split == 'train':
    train_json = {
      'version': 'v2.0', 'data': []
    }
    dev_json = {
      'version': 'v2.0', 'data': []
    }
    with tf.io.gfile.GFile(os.path.join(input_dir, train_input_file), 'r') as input_fh, tf.io.gfile.GFile(
        os.path.join(output_dir, train_file), 'w') as train_fh, tf.io.gfile.GFile(os.path.join(output_dir, dev_file),
      'w') as dev_fh:
      for i, org_line in enumerate(input_fh):
        org_json = json.loads(org_line)
        org_text = org_json['content']
        text = argument_cleaning(org_text)
        re_annotate = ReAnnotate(text)

        if random.random() < dev_ratio:
          task = 'dev'
        else:
          task = 'train'

        data = {
          'paragraphs': [{
            'id': '{}_{}'.format(task.upper(), i), 'context': text, 'qas': [],
          }], 'id': '{}_{}'.format(task.upper(), i), 'title': org_json['doc_id'],
        }

        for question_main_idx, event in enumerate(org_json['events']):
          event_type = event['event_type']
          role_list = role_event_type_dict[event_type]
          arguments = []
          roles = []
          for role in event.keys():
            if role not in ['event_type', 'event_id']:
              argument = event[role].strip()
              if len(argument) > 0:
                loc = text.find(argument)
                if re_annotate.digit_check(argument, loc):
                  arguments.append(argument)
                  roles.append(role)

          if len(roles) == 0:
            continue
          argument_locs = re_annotate.generate_locs(arguments)
          argument_loc_dict = {}
          for l, a in zip(argument_locs, arguments):
            argument_loc_dict[a] = l

          for question_minor_idx, role in enumerate(role_list):
            # question = '{}|{}|{}：{}'.format(question_main_idx, event_type, role_entity_type_dict[role], role)
            question = '{}事件中第{}个{}是什么{}'.format(event_type, question_main_idx + 1, role, role_entity_type_dict[role])
            if role in roles:
              argument = event[role].strip()
              argument_start = argument_loc_dict[argument]
              answers = [{
                'text': argument, 'answer_start': argument_start
              }]
              is_impossible = False
            else:
              answers = []
              is_impossible = True

            qas = {
              'question': question,
              'id': '{}_{}_QUERY_{}_{}'.format(task.upper(), i, question_main_idx, question_minor_idx),
              'answers': answers, 'is_impossible': is_impossible,
            }

            data['paragraphs'][0]['qas'].append(qas)

        if task == 'train':
          train_json['data'].append(data)
        elif task == 'dev':
          dev_json['data'].append(data)

      json.dump(train_json, train_fh, ensure_ascii=False)
      json.dump(dev_json, dev_fh, ensure_ascii=False)

  elif split == 'test':
    cl_pred_result_file = os.path.join(result_dir, 'models', model_name, 'results', 'ccks42ec,ccks42num,ccks42ee_cl',
      'ccks42ec_eval_preds.json')
    num_pred_result_file = os.path.join(result_dir, 'models', model_name, 'results', 'ccks42ec,ccks42num,ccks42ee_cl',
      'ccks42num_eval_preds.json')
    test_json = {
      'version': 'v2.0', 'data': []
    }
    task = 'eval'
    text_label_dict = {}
    with tf.io.gfile.GFile(cl_pred_result_file, 'r') as cl_pred_fh:
      for text, label in json.load(cl_pred_fh).items():
        text_label_dict[text] = label
    text_num_dict = {}
    with tf.io.gfile.GFile(num_pred_result_file, 'r') as num_pred_fh:
      for text, num in json.load(num_pred_fh).items():
        text_num_dict[text] = num

    with tf.io.gfile.GFile(os.path.join(input_dir, test_input_file), 'r') as input_fh, tf.io.gfile.GFile(
        os.path.join(output_dir, test_file), 'w') as test_fh:
      for i, org_line in enumerate(input_fh):
        org_json = json.loads(org_line)
        org_text = org_json['content']
        text = argument_cleaning(org_text)

        data = {
          'paragraphs': [{
            'id': '{}_{}'.format(task.upper(), i), 'context': text, 'qas': [],
          }], 'id': '{}_{}'.format(task.upper(), i), 'title': org_json['doc_id'],
        }

        if text in text_label_dict.keys():
          label = text_label_dict[text]
        else:
          print('label', text)
          continue
        # event_type, r = label.split('_')
        event_type = label
        if text in text_num_dict.keys():
          num = text_num_dict[text]
        else:
          print('num', text)
          continue
        r = num
        for question_main_idx in range(int(r)):
          role_list = role_event_type_dict[event_type]
          for question_minor_idx, role in enumerate(role_list):
            # question = '{}|{}|{}：{}'.format(question_main_idx, event_type, role_entity_type_dict[role], role)
            question = '{}事件中第{}个{}是什么{}'.format(event_type, question_main_idx + 1, role, role_entity_type_dict[role])
            qas = {
              'question': question,
              'id': '{}_{}_QUERY_{}_{}'.format(task.upper(), i, question_main_idx, question_minor_idx),
            }
            data['paragraphs'][0]['qas'].append(qas)

        test_json['data'].append(data)
      json.dump(test_json, test_fh, ensure_ascii=False)
  else:
    print('split is either train or test, other input is invalid')


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--dir", required=True, help="location of all data")
  parser.add_argument("--split", required=True, help="generate train data or test data")
  parser.add_argument("--result", default=None, help="location of result")
  parser.add_argument("--model", default=None, help="pretrained model name")
  args = parser.parse_args()
  run_data_prepare(args.dir, args.split, args.result, args.model)


if __name__ == '__main__':
  main()
