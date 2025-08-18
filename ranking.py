class Ranking:
  def __init__(self, name, tournaments = None):
    self.name = name
    self.tournaments = tournaments
    if tournaments is None:
      self.tournaments = []