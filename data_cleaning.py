import re


def argument_cleaning_v1(content):
  text = re.sub(r'\s', ' ', content)
  text = re.sub(r'<br>', ' ', text)
  text = re.sub(r'&nbsp', ' ', text)
  pattern = r'\d{4}[-|年|./]+\d{1,2}[-|月|./]+\d{1,2}[日]?'
  matched_dates = re.findall(pattern, text)
  for d in matched_dates:
    words_blank = " " + d + " "
    text = text.replace(d, words_blank)
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
      text = text[:(i*2)+s] + words_blank + text[(i*2)+e:]
  return text