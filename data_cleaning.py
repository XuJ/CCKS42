import re


def argument_cleaning(content):
  text = re.sub(r'\s', ' ', content)
  text = re.sub(r'<br>', ' ', text)
  text = re.sub(r'&nbsp', ' ', text)
  pattern = r'\d{4}[-|年|./]+\d{1,2}[-|月|./]+\d{1,2}[日]?'
  matched_dates = re.findall(pattern, text)
  for d in matched_dates:
    words_blank = " " + d + " "
    text = text.replace(d, words_blank)
  return text
