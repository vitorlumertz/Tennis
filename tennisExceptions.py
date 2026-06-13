class CategoryNotFound(Exception):
  def __init__(self, categoryName):
    self.categoryName = categoryName

  def __str__(self):
    return f"Category ({self.categoryName}) does not exist."


class PlayerNotFound(Exception):
  def __init__(self, playerName, categoryName):
    self.playerName = playerName
    self.categoryName = categoryName

  def __str__(self):
    return f"Player ({self.playerName}) not found in category ({self.categoryName})."


class AddingDoubleInSingleCategory(Exception):
  def __init__(self, doubleName, categoryName):
    self.doubleName = doubleName
    self.categoryName = categoryName

  def __str__(self):
    return f"Trying to add double ({self.doubleName}) in single category ({self.categoryName})."


class DuplicatedCategory(Exception):
  def __init__(self, categoryName):
    self.categoryName = categoryName

  def __str__(self):
    return f"Trying to add category ({self.categoryName}), but it already exists."


class DuplicatedTeam(Exception):
  def __init__(self, teamName, categoryName):
    self.teamName = teamName
    self.categoryName = categoryName

  def __str__(self):
    return f"Trying to add team ({self.teamName}) in category ({self.categoryName}), but it already exists."


class DrawingDoublesError(Exception):
  def __init__(self, categoryName):
    self.categoryName = categoryName

  def __str__(self):
    return f"Error drawing doubles in category ({self.categoryName})."


class ForfeitWithNoResultError(Exception):
  def __str__(self):
    return "Forfeit given with no result. Forfeit must define the score when the match ended. If the match did not start, the result must be WO."