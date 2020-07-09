import itertools


class ReAnnotate(object):
  def __init__(self, text):
    self.text = text
    self.sentences = self.text.split('。|！|？')

  def get_locs(self, argument):
    res = [i for i in range(len(self.text)) if self.text.startswith(argument, i)]
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
