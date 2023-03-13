from base import *

#######################################################################
# This is the Dog class
#

class Dog(MyObject):

  def __init__(self, name):
    self._name = name
    self._hunger = 0   # not hungry


  def eat(self):
    if self._hunger == 0:
      pr(self._name, "is ignoring the food")
    else:
      pr(self._name,"is chomping away")
      self._hunger -= 1


  def bark(self):
    if self._hunger > 2:
      pr(self._name, "is whining")
    else:
      pr(self._name,"says woof woof")
      self._hunger += 1


  def do_stuff(self):
    self.bark()
    self.bark()
    self.bark()
    self.bark()
    self.bark()
    self.bark()
    self.bark()
    self.bark()
    self.eat()
    self.eat()
    self.bark()
    self.bark()




#######################################################################
# These are functions that use the Doc class, but are not part
# of the class!
#


def prog1():
  m = Dog("Fido")

  # Generate psuedorandom numbers.
  #

  # Using Python's time library to get a seed for our random number generator.
  import time
  seed = int(time.time())  # this sets seed => number of seconds since 1970

  pr("seed:", seed)
  j = seed
  for x in range(20):
    j = (j * 937) % 271
    if (j % 2) == 0:
      m.bark()
    else:
      m.eat()


# This is a statement that is NOT a class or function definition, so it will run when the script gets to it
#
pr("hello")

# This is a function; when the script gets to this point, it defines the function but doesn't execute it
#

def prog2():
  warning("no prog2 yet")


# This is a statement that is NOT a class or function definition, so it will run when the script is loaded
#
pr("booyah")


def main():
  prog = 2

  if prog == 1:
    prog1()
  elif prog == 2:
    prog2()
  else:
    die("no such program:", prog)


#######################################################################
# These are instructions that are not within a class or a function,
# so they will run when the script is run
#

if __name__ == "__main__":
  main()
