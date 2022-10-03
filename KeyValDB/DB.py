# ==============================================================================

class DB(object):
  """
  The DB class is a database that stores dictionary like objects as rows and has
  methods to select, delete, and sort rows.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, rows=None): # type: (Union[None, List[Dict[str, Any]]]) -> None
    """
    :param rows: Initial rows to add to the database (default None).
    """
    rows = rows or []
    self.rows = rows

  # ----------------------------------------------------------------------------

  def __len__(self):
    return len(self.rows)

  # ----------------------------------------------------------------------------

  def __getitem__(self, index):
    from six import string_types
    if isinstance(index, string_types):
      for row in self.rows:
        if index in row:
          return row[index]
      raise Exception("No rows in DB contain the field '{0}'".format(index))
    return self.rows[index]

  # ----------------------------------------------------------------------------

  def __contains__(self, field):
    from six import string_types
    if isinstance(field, string_types):
      for row in self.rows:
        if field in row: return True
    return field in self.rows

  # ----------------------------------------------------------------------------

  def addRow(self, row):  # type: (Dict[str, Any]) -> DB
    """
    Add a row to the database.

    :param row: A database row (dictionary like object).
    :return: The current DB.
    """
    self.rows.append(row)
    return self

  # ----------------------------------------------------------------------------

  def __isInSet__(self, *is_present, **fields):
    # type: (*List[Union[str, Callable[[Dict[str,Any]], bool]], **Dict[str, Any]) -> Callable[[Dict[str,Any]], bool]
    """
    Return a function that checks whether a row matches the given specification.

    :param is_present: List of fields that must be present, or function that
           takes a row and return a boolean indicating if row is acceptable.
    :param fields: Field name and value to match. The value may be a function
           that takes the field values and returns a boolean indicating whether
           the field value is acceptable.
    :return: True if a row is part of the selected set or False otherwise.
    """
    def isInSet(row):
      for col_name in is_present:
        if callable(col_name):
          if col_name(row) != True: return False
        elif col_name not in row: return False
      for col_name, value in fields.items():
        if col_name not in row: return False
        if callable(value) and value(row[col_name]) != True: return False
        elif value != row[col_name]: return False
      return True
    return isInSet

  # ----------------------------------------------------------------------------

  def select(self, *is_present, **fields):
    # type: (*List[Union[str, Callable[[Dict[str,Any]], bool]], **Dict[str, Any]) -> DB
    """
    Select rows from the DB.

    :param is_present: List of fields that must be present, or function that
           takes a row and return a boolean indicating if row is acceptable.
    :param fields: Field name and value to match. The value may be a function
           that takes the field values and returns a boolean indicating whether
           the field value is acceptable.
    :return: A new DB with the selected rows.
    """
    isInSet = self.__isInSet__(*is_present, **fields)
    results = [row for row in self.rows if isInSet(row)]
    return DB(results)

  # ----------------------------------------------------------------------------

  def delete(self, *is_present, **fields):
    # type: (*List[Union[str, Callable[[Dict[str,Any]], bool]], **Dict[str, Any]) -> DB
    """
    Delete rows from the database that match the query.

    :param is_present: List of fields that must be present, or function that
           takes a row and return a boolean indicating if row is acceptable.
    :param fields: Field name and value to match. The value may be a function
           that takes the field values and returns a boolean indicating whether
           the field value is acceptable.
    :return: A new DB with the given rows deleted.
    """
    isInSet = self.__isInSet__(*is_present, **fields)
    rows = [row for row in self.rows if not isInSet(row)]
    return DB(rows)

  # ----------------------------------------------------------------------------

  def deleteRows(self, rows, newDB=True):
    # type: (Union[DB, List[Dict[str, Any]]], bool) -> DB
    """
    Delete the given rows from the DB.

    :param rows: The rows to delete from the database (as a DB, list, or tuple).
    :param newDB: Creates a new DB if True (default), or updates the current DB
           and returns it.

    :return: The DB with deleted rows. This is a new DB if newDB is True.
    """
    if not isinstance(rows, (list,DB,tuple)): rows = [rows]
    filtered_rows = [row for row in self.rows if row not in rows]
    if newDB: return DB(filtered_rows)
    self.rows = filtered_rows
    return self

  # ----------------------------------------------------------------------------

  def orderby(self, field):
    #type: (Union[str, Callable[[Dict[str, Any], Dict[str, Any]], int]) -> DB
    """
    Return a database with the fields sorted according to the given fields.
    :param field: The field to use for sorting rows or a key extraction function that
           takes a DB row and returns the value to use for sorting purposes.
    :return: A new database ordered by the given field.
    """
    from six import string_types
    if isinstance(field, string_types):
      fieldname = field
      key = lambda row1: row1[fieldname]
      rows = [row for row in self.rows if field in row]
    else:
      import copy
      key = field
      rows = copy.copy(self.rows)

    rows = sorted(rows, key=key)
    return DB(rows)

  # ----------------------------------------------------------------------------

  def groupby(self, field, dropIfNoField=True):
    #type: (str) -> DB
    """
    Group the DB rows by the given field. Each row in the grouped DB is a DB with
    containing the grouped rows.

    :param field: The field to use when grouping rows
    :param dropIfNoField: Indicates whether to remove rows that don't contain the field.
    :return: DB with grouped rows.
    """

    groupedDB = DB()
    groups = {}
    for row in self.rows:
      if field not in row:
        if not dropIfNoField:
          groupedDB.addRow(DB().addRow(row))
        continue


      field_val = row[field]
      if field_val not in groups:
        db = DB()
        groups[field_val] = db
        groupedDB.addRow(db)

      groups[field_val].addRow(row)
    return groupedDB

  # ----------------------------------------------------------------------------

  def merge(self, other_db):
    # type: (Union[DB, List[Dict[str,Any]]) -> DB
    """
    Merge the rows from another database into this database
    :param other_db: The other database to add rows from.
    :return: The updated database.
    """
    if isinstance(other_db, (list, tuple)):
      self.rows.extend(other_db)
      return self

    if not isinstance(other_db, DB): return
    self.rows.extend(other_db.rows)
    return self

# ==============================================================================

