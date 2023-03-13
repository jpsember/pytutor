from base import *

class Board(MyObject):

  # This is the object's constructor (i.e. called by "x = Board(12)")
  #
  #  size: the size of the (square) board
  #
  def __init__(self, size):
    # Specify the attributes for the object
    #
    self._size = size    # the '_' prefix is a convention to indicate that we're talking about an object attribute
    #
    # The board 'looks' like a grid, but to represent or store this internally, we need to figure out how.
    # Let's use a list.
    #
    self._cells = [0] * size * size   # Construct a list (or array) of (size*size) zeros


  # This method gets the size of the board
  #
  def size(self):
    return self._size


  # Get the contents of cell at x,y
  #
  # We want to map x,y coordinates on the board to array indexes i in the array.
  #
  #                                   "view space"              "internal space"
  #
  #
  #  The answer is f(x,y) =>  (x + (y * width))    (where width = height = size, because it's a square board)
  #
  def cell(self, x, y):
    return self._cells[y * self._size + x]

  # Get the index of the cell at x,y
  #
  def cell_index(self, i):
    warning("not finished yet")
    # it should return a list of two elements, [x,y]
    return [3,4]

  # Print the board
  #
  def display(self):
    # A nested loop:
    # outer loop is for each row
    # inner loop is for each column in that row
    #
    # We'll construct a string, and later, print the string out
    s = ""
    for row_num in range(self._size):
      for col_num in range(self._size):
        c = self.cell(col_num, row_num)
        if c == 1:
          s = s + "▓▓"
        else:
          s = s + "░░"

      # After the columns, print a linefeed
      s = s + "\n"

    pr(s)

    pr("cell_index(14):")
    pr(self.cell_index(14))