#!/usr/bin/env python3

from base import *
from board import *

class App(MyObject):

  def __init__(self):
    self._board = None
    self._max_gen = None


  def help(self):
    return "[boardsize <n>] [gen <n>] -- plays a game of life"


  def run(self):
    ca_builder(self)
    board_size = None
    while handling_args():
      board_size = next_arg_if("boardsize", 20)
      self._max_gen = next_arg_if("gen",5)

    check_arg(board_size >= 4 and board_size <= 40, "boardsize")
    self._board = Board(board_size)
    pr("Board size:",self._board.size())
    self._board.display()




if __name__ == "__main__":
  try:
    App().run()
  except Exception as e:
    report_exception(e)
