class CategoryNotFound(Exception):
  def __init__(self, categoryName):
    self.categoryName = categoryName

  def __str__(self):
    return f"Category ({self.categoryName}) does not exist."


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