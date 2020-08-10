import itertools
import re


class ReAnnotate(object):
  def __init__(self, text):
    self.text = text
    self.sentences = self.text.split('。|！|？')

  def digit_check(self, argument, loc):
    '''
    有的论元是简单的单字数字，例如“2”或“1”，
    这类数字极可能被错误地匹配到其他地方去，例如匹配到“2019年”或“第1号法令”等
    所以对于论元是数字的情形，增加一层校验，必须左右的字节不是数字才能输出
    即不会抽取数字中的数字作为论元
    :return: True表示通过检验，False表示为通过校验
    '''
    if loc < 0:
      return False
    elif loc > 0 and re.match(r'\d', argument[0]) and re.match(r'\d', self.text[loc - 1]):
      return False
    elif loc + len(argument) < len(self.text) - 1 and re.match(r'\d', argument[-1]) and re.match(r'\d',
        self.text[loc + len(argument)]):
      return False
    else:
      return True

  def get_locs(self, argument):
    res = []
    for i in range(len(self.text)):
      if self.text.startswith(argument, i):
        if self.digit_check(argument, i):
          res.append(i)
    return res

  def get_sentence(self, argument):
    res = [i for i in range(len(self.sentences)) if self.sentences[i].find(argument) != -1]
    return res

  def get_distance(self, locs):
    sum = 0
    for i, j in itertools.combinations(locs, 2):
      sum += abs(i - j)
    return sum

  def generate_locs(self, arguments):
    res = []
    for argument in arguments:
      res.append(self.get_locs(argument))

    min_distance = 99999999
    min_locs = None
    for locs in itertools.product(*res):
      distance = self.get_distance(locs)
      if distance < min_distance:
        min_distance = distance
        min_locs = locs
    return min_locs
