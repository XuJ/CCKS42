import re

role_event_type_dict = {
  '高层死亡': ['公司名称', '高层人员', '高层职务', '死亡/失联时间', '死亡年龄'], '破产清算': ['公告时间', '公司名称', '公司行业', '受理法院', '裁定时间'],
  '重大资产损失': ['公告时间', '公司名称', '损失金额', '其他损失'], '重大对外赔付': ['公告时间', '公司名称', '赔付金额', '赔付对象'],
  '重大安全事故': ['公告时间', '公司名称', '伤亡人数', '损失金额', '其他影响'], '股权冻结': ['冻结金额', '被冻结股东', '冻结开始日期', '冻结结束日期'],
  '股权质押': ['质押金额', '质押方', '接收方', '质押开始日期', '质押结束日期'], '股东增持': ['增持金额', '增持的股东', '增持开始日期'],
  '股东减持': ['减持金额', '减持的股东', '减持开始日期'],
}
role_entity_type_dict = {
  '公司名称': '公司', '高层人员': '人名', '高层职务': '职称', '死亡/失联时间': '时间', '死亡年龄': '数字', '公司行业': '行业', '公告时间': '时间', '受理法院': '机构',
  '裁定时间': '时间', '损失金额': '数字', '其他损失': '文本短语', '赔付金额': '数字', '赔付对象': '公司/人名', '伤亡人数': '数字', '其他影响': '文本短语', '冻结金额': '数字',
  '被冻结股东': '公司/人名', '冻结开始日期': '时间', '冻结结束日期': '时间', '质押金额': '数字', '质押方': '公司/人名', '接收方': '公司/人名', '质押开始日期': '时间',
  '质押结束日期': '时间', '增持金额': '数字&单位', '增持的股东': '公司/人名', '增持开始日期': '时间', '减持金额': '数字&单位', '减持的股东': '公司/人名', '减持开始日期': '时间',
}
ner_entity_type_dict = {
  'company': '公司', 'person': '人名', 'time': '时间'
}
doc_span_length = 512
doc_stride = 128


def is_chinese_char(cp):
  """Checks whether CP is the codepoint of a CJK character."""
  # This defines a "chinese character" as anything in the CJK Unicode block:
  #   https://en.wikipedia.org/wiki/CJK_Unified_Ideographs_(Unicode_block)
  #
  # Note that the CJK Unicode block is NOT all Japanese and Korean characters,
  # despite its name. The modern Korean Hangul alphabet is a different block,
  # as is Japanese Hiragana and Katakana. Those alphabets are used to write
  # space-separated words, so they are not treated specially and handled
  # like the all of the other languages.
  cp = ord(cp)
  if ((cp >= 0x4E00 and cp <= 0x9FFF) or  #
    (cp >= 0x3400 and cp <= 0x4DBF) or  #
    (cp >= 0x20000 and cp <= 0x2A6DF) or  #
    (cp >= 0x2A700 and cp <= 0x2B73F) or  #
    (cp >= 0x2B740 and cp <= 0x2B81F) or  #
    (cp >= 0x2B820 and cp <= 0x2CEAF) or (cp >= 0xF900 and cp <= 0xFAFF) or  #
    (cp >= 0x2F800 and cp <= 0x2FA1F)):  #
    return True
  return False


def argument_cleaning_v3(content):
  pattern = r'\d{4}[-|年|./]\d{1,2}[-|月|./]\d{1,2}[日]?(\d{1,2}[时](\d{1,2}[分])?)?(-((\d{4}[-|年|./])?\d{1,2}[-|月|./])?\d{1,2}[日]?)?'
  matched_dates = re.finditer(pattern, content)
  for d in reversed(list(matched_dates)):
    start = d.start()
    end = d.end()
    pre_chinese_char = True
    post_chinese_char = True
    if start > 0:
      pre_chinese_char = is_chinese_char(content[start - 1])
    if end < len(content) - 1:
      post_chinese_char = is_chinese_char(content[end + 1])
    if pre_chinese_char:
      if post_chinese_char:
        pass
      else:
        content = content[:end] + ' ' + content[end:]
    else:
      if post_chinese_char:
        content = content[:start] + ' ' + content[start:]
      else:
        content = content[:end] + ' ' + content[end:]
        content = content[:start] + ' ' + content[start:]
  text = re.sub(r'\s+', ' ', content)
  return text


def argument_cleaning_v2(content):
  text = re.sub(r'\s', ' ', content)
  pattern = r'\d{4}[-|年|./]+\d{1,2}[-|月|./]+\d{1,2}[日]?'
  matched_dates = re.findall(pattern, text)
  for d in matched_dates:
    words_blank = " " + d + " "
    text = text.replace(d, words_blank)
  text = re.sub(r'\s', ' ', text)
  return text


def argument_cleaning_v1(content):
  text = re.sub(r'\s', ' ', content)
  pattern = r'\d{4}[-|年|./]+\d{1,2}[-|月|./]+\d{1,2}[日]?'
  matched_dates = re.findall(pattern, text)
  for d in matched_dates:
    words_blank = " " + d + " "
    text = text.replace(d, words_blank)
  text = re.sub(r'\s', ' ', text)
  return text


def argument_cleaning(content):
  text = re.sub(r'\s', ' ', content)
  text = re.sub(r'<br>', ' ', text)
  text = re.sub(r'&nbsp', ' ', text)
  pattern = r'[\d|〇|一|二|三|四|五|六|七|八|九|十]{4}[-|年|./]+[\d|一|二|三|四|五|六|七|八|九|十]{1,3}[-|月|./]+[\d|一|二|三|四|五|六|七|八|九|十]{1,3}[日]?'
  matched_dates = re.finditer(pattern, text)
  for i, d in enumerate(matched_dates):
    s, e = d.span()
    words_blank = " " + d.group() + " "
    text = text[:(i * 2) + s] + words_blank + text[(i * 2) + e:]
  return text
