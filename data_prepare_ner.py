import os
import json

model_name = 'electra_large'
input_dir = 'data\\ccks42ee'
output_dir = 'data\\ner'
train_file = 'train.json'
dev_file = 'dev.json'
test_file = 'eval.json'
role_event_type_dict = {'股权冻结': '冻结金额', '股权质押': '质押金额', '股东增持': '增持金额', '股东减持': '减持金额'}
# role_event_type_dict = {'股权冻结': '被冻结股东', '股权质押': '接收方', '股东增持': '增持的股东', '股东减持': '减持的股东'}

for split_file in [train_file, dev_file, test_file]:
  print(split_file)
  with open(os.path.join(input_dir, split_file), 'r', encoding='utf8') as input_fh, open(
      os.path.join(output_dir, split_file), 'w', encoding='utf8') as output_fh:
    org_json = json.load(input_fh)
    org_data = org_json['data']
    output_data = []
    for data in org_data:
      output_paragraphs = []
      for paragraph in data['paragraphs']:
        output_qas = []
        answers = set()
        for qas in paragraph['qas']:
          event_type = qas['question'].split('事件')[0]
          role = qas['question'].split('是什么')[0].split('个')[-1]
          if event_type in role_event_type_dict.keys():
            if role == role_event_type_dict[event_type]:
              if 'answers' in qas:
                if len(qas['answers'])>0:
                  if (qas['answers'][0]['text'], qas['answers'][0]['answer_start']) in answers:
                    continue
                  else:
                    answers.add((qas['answers'][0]['text'], qas['answers'][0]['answer_start']))
              output_qas.append(qas)
        if len(output_qas) > 0:
          paragraph['qas'] = output_qas
          output_paragraphs.append(paragraph)
      if len(output_paragraphs) > 0:
        data['paragraphs'] = output_paragraphs
        output_data.append(data)
    split_json = {'version': 'v2.0', 'data': output_data}
    json.dump(split_json, output_fh, ensure_ascii=False)
