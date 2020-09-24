import os
import json
import argparse
import time
import tensorflow.compat.v1 as tf


def run_prediction(data_dir, part, result_dir, model_name):
  today = time.strftime('%Y%m%d_%H%M%S', time.gmtime())
  output_dir = os.path.join(data_dir, 'finetuning_data', 'output', model_name)
  if not tf.io.gfile.exists(output_dir):
    tf.io.gfile.makedirs(output_dir)
  if part == 'full':
    ec_pred_file = os.path.join(result_dir, 'models', model_name, 'results', 'ccks42ec,ccks42reg_cl',
      'ccks42ec_eval_preds.json')
    num_pred_file = os.path.join(result_dir, 'models', model_name, 'results', 'ccks42ec,ccks42reg_cl',
      'ccks42reg_eval_preds.json')
    ee_pred_file = os.path.join(data_dir, 'models', model_name, 'results', 'ccks42bagging', 'vote1',
      'ccks42bagging_eval_1_preds.json')
    ee_input_file = os.path.join(result_dir, 'finetuning_data', 'ccks42ee', 'eval.json')
  else:
    ec_pred_file = os.path.join(result_dir, 'models', model_name, 'results', 'ccks42ec,ccks42reg_cl',
      'ccks42ec_eval_preds.json')
    num_pred_file = os.path.join(result_dir, 'models', model_name, 'results', 'ccks42ec,ccks42reg_cl',
      'ccks42reg_eval_preds.json')
    ee_pred_file = os.path.join(result_dir, 'models', model_name, 'results', 'ccks42{}_qa'.format(part),
      'ccks42{}_eval_1_preds.json'.format(part))
    ee_input_file = os.path.join(data_dir, 'ccks42{}'.format(part), 'eval.json')
  output_file = os.path.join(output_dir, 'result_{}_{}.txt'.format(part, today))

  with tf.io.gfile.GFile(ec_pred_file, 'r') as ec_pred_fh:
    text_event_type_dict = json.load(ec_pred_fh)
  with tf.io.gfile.GFile(num_pred_file, 'r') as num_pred_fh:
    text_event_num_dict = json.load(num_pred_fh)
  with tf.io.gfile.GFile(ee_pred_file, 'r') as ee_pred_fh:
    question_id_answer_dict = json.load(ee_pred_fh)
  event_types_count_dict = {}
  for k, v in text_event_type_dict.items():
    event_types_count_dict[v] = event_types_count_dict.get(v, 0) + 1
  print(event_types_count_dict)

  multi = 0
  single = 0
  with tf.io.gfile.GFile(ee_input_file, 'r') as ee_input_fh, tf.io.gfile.GFile(output_file, 'w') as output_fh:
    data = json.load(ee_input_fh)["data"]
    for _i, i in enumerate(data):
      # print(_i)
      text = i['paragraphs'][0]['context']
      event_type = text_event_type_dict[text]
      event_num = text_event_num_dict[text]
      event_num = int(event_num)
      doc_id = i['title']
      qas_dict = {}
      if event_num > 1:
        multi += 1
      else:
        single += 1
      for n in range(event_num):
        qas_dict[n] = []
      for j in i['paragraphs'][0]['qas']:
        question_id = j['id']
        event_index = int(question_id.split('_')[3])
        question = j['question']
        event_element = question.split('是什么')[0].split('个')[-1]
        answer = question_id_answer_dict[question_id]
        qas_dict[event_index].append((event_element, answer))
      events = []
      for n in range(event_num):
        event = {
          'event_type': event_type
        }
        for (q, a) in qas_dict[n]:
          if len(a) > 0:
            event[q] = a
        events.append(event)
      result = {
        'doc_id': doc_id, 'events': events
      }
      output_fh.write(json.dumps(result, ensure_ascii=False))
      output_fh.write('\n')
  print('#' * 30)
  print('multi class:', multi)
  print('single class:', single)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--dir", required=True, help="location of all data")
  parser.add_argument("--part", default='full', help="build full/single/multi event model")
  parser.add_argument("--result", required=True, help="location of result")
  parser.add_argument("--model", required=True, help="pretrained model name")
  args = parser.parse_args()
  run_prediction(args.dir, args.part, args.result, args.model)


if __name__ == '__main__':
  main()
