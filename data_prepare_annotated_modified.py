import argparse
import json
import os

import tensorflow.compat.v1 as tf


def run_data_prepare(data_dir, part):
  if part == 'full':
    input_dir = os.path.join(data_dir, 'ccks42ee')
  else:
    input_dir = os.path.join(data_dir, 'ccks42{}'.format(part))
  annotated_dir = os.path.join(data_dir, 'annotated')
  # multi_event_types = ['股东减持', '股东增持', '股权质押', '股权冻结']
  multi_event_types = ['股东减持']
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
  annotated_dict = {}
  for event_type in multi_event_types:
    with tf.io.gfile.GFile(os.path.join(annotated_dir, '{}.json'.format(event_type)), 'r') as fh:
      for line in fh:
        data = json.loads(line)
        doc_id = data['key']
        sorted_answers = []
        answers = []
        rank_no = 0
        backup_dict = {}
        for qas in data['qas']:
          answer = {}
          for qas_sub in qas:
            role = qas_sub['question'].strip()
            if len(qas_sub['answers']) == 0:
              ans = {
                'text': '无答案', 'start': backup_dict.get(role, 0)
              }
            else:
              ans = qas_sub['answers'][0]
            answer[role] = ans
            rank_no += ans['start']
            backup_dict[role] = ans['start']
          answers.append((rank_no, answer))
        for rank_no, answer in sorted(answers, key=lambda x: x[0]):
          sorted_answers.append(answer)
        if doc_id in annotated_dict.keys():
          print('duplicate doc_id:', doc_id)
          continue
        annotated_dict[doc_id] = sorted_answers

  tasks = ['train', 'dev']
  for task in tasks:
    print(task)
    input_file = '{}_backup.json'.format(task)
    output_file = '{}.json'.format(task)
    tf.io.gfile.copy(os.path.join(input_dir, output_file), os.path.join(input_dir, input_file), True)
    with tf.io.gfile.GFile(os.path.join(input_dir, input_file), 'r') as input_fh, tf.io.gfile.GFile(
        os.path.join(input_dir, output_file), 'w') as output_fh:
      orig_json = json.load(input_fh)
      for data in orig_json['data']:
        doc_id = data['title']
        if doc_id not in annotated_dict.keys():
          continue
        uid = data['id']
        paragraph = data['paragraphs'][0]
        event_type = paragraph['qas'][0]['question'].strip().split('事件中')[0]
        role_list = role_event_type_dict[event_type]
        annotated_ans = annotated_dict[doc_id]

        paragraph['qas'] = []
        for question_main_idx, answer in enumerate(annotated_ans):
          for question_minor_idx, role in enumerate(role_list):
            question = '{}事件中第{}个{}是什么{}'.format(event_type, question_main_idx + 1, role, role_entity_type_dict[role])
            if (role in answer.keys()) and (answer[role]['text'] != '无答案'):
              answers = [{
                'text': answer[role]['text'].strip(), 'answer_start': int(answer[role]['start'])
              }]
              is_impossible = False
            else:
              answers = []
              is_impossible = True

            qas = {
              'question': question, 'id': '{}_QUERY_{}_{}'.format(uid, question_main_idx, question_minor_idx),
              'answers': answers, 'is_impossible': is_impossible,
            }
            data['paragraphs'][0]['qas'].append(qas)
      json.dump(orig_json, output_fh, ensure_ascii=False)
    tf.io.gfile.remove(os.path.join(input_dir, input_file))
    print('Done')


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--dir", required=True, help="location of all data")
  parser.add_argument("--part", default='full', help="build full/single/multi event model")
  args = parser.parse_args()
  run_data_prepare(args.dir, args.part)


if __name__ == '__main__':
  main()
