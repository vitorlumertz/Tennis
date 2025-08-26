class Team:
  def __init__(self, name:str, seedNumber=0, isSeed=None):
    self.name = name
    self.seedNumber = seedNumber
    if isSeed is None:
      if self.seedNumber > 0:
        isSeed = True
      else:
        isSeed = False
    self.isSeed = isSeed


class Player(Team):
  def __init__(self, name:str, seedNumber=0, isSeed=None):
    super().__init__(name, seedNumber, isSeed)


class Double(Team):
  def __init__(self, player1:Player, player2:Player, seedNumber=0, isSeed=None):
    name = f'{player1.name}/{player2.name}'
    super().__init__(name, seedNumber, isSeed)
    self.player1 = player1
    self.player2 = player2
