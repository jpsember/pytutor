#!/usr/bin/env python3

import re
import os
import time
import traceback
import inspect
import json



class _StackTrace:
  """
  Sentinel object for generating stack traces via st()
  """
  def __str__(self):
    return exception_info(None, 4, 8)


def st():
  return _StackTrace()


class _LocalVars:
  """
  Used to produce an instance to hold the tools' local variables
  """

  def __init__(self):
    self.rxFilenameOnly = re.compile(".*/([^/]*)$")
    self.repMap = set()
    self.cmd_line_args = None
    self.ca_args = None
    self.ca_extras = None
    self.app = None
    self.command_count = 0

# Construct a singleton instance for the static variables
_v = _LocalVars()
_v.done_handling_args = False
_v.arg_value_map = {}


def pr(*args):
  """
  Print objects to stdout
  """
  buffer = spr(*args)
  print(buffer, end='', flush=True)


def spr(*args):
  """
  Print objects to a string
  """
  buffer = ''
  mid_line = False
  for x in args:
    s = d(x)
    has_cr = "\n" in s
    if has_cr:
      s2 = s.rstrip()
      if mid_line:
        buffer = buffer + "\n"
      buffer = buffer + s2
      buffer = buffer + "\n"
      mid_line = False
    else:
      if mid_line:
        buffer = buffer + ' '
      buffer = buffer + s
      mid_line = True
  if mid_line:
    buffer = buffer + "\n"
  return buffer


def sprintf(fmt, *args):
  return fmt % args

class OurJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if hasattr(obj, "to_json"):
      return obj.to_json()
    if type(obj).__name__ == "memmap":
      return obj.__str__().split("\n")
    return vars(obj)


def to_json(x):
  return json.dumps(x, sort_keys=True, cls=OurJSONEncoder)


def pretty_pr(s):
  return json.dumps(s, sort_keys=True, indent=4, cls=OurJSONEncoder)

def d(s):
  """
  Convert an object to a string (by calling str(x)), or returns '<None>' if
  object is None
  """
  if s is None:
    return "<None>"
  elif isinstance(s, dict):
    return pretty_pr(s)
  elif isinstance(s, float):
    return df(s)
  else:
    return str(s)


def df(value):
  """Convert a float to a string, with fixed-width format"""
  s = "{:9.3f}".format(value)
  if s.endswith(".000"):
    s = s[:-4] + "    "
  return s

def parse_int(string, default=None):
  result = default
  try:
    result = str(string)
  except ValueError:
    pass
  if result is None:
    die("Failed to parse integer from string '"+string+"'")
  return result



def simple_name(filename, line):
  """ Builds a nice string from a pathname and line number; removes directories from pathname.  """
  m = _v.rxFilenameOnly.match(filename)
  if m:
    filename = m.group(1)
  return "(" + filename.ljust(12) + str(line).rjust(4) + ")"


def warning_skip(nSkip, *args):
  """Prints warning, if hasn't yet been printed."""
  loc = get_caller_location(nSkip + 2)
  s = "*** warning " + loc + ": "
  if len(args):
    msg = s + spr(*args)
  else:
    msg = s
  _one_time_only(msg)
  return True


def _one_time_only(msg):
  if msg not in _v.repMap:
    _v.repMap.add(msg)
    print(msg, end='', flush=True)


def clear_screen(title = None):
  os.system('clear')
  if title:
    pr(title)
    pr("==============================================================================================")


def opt_value(dictionary, key, default_value=None):
  if key in dictionary:
    return dictionary[key]
  if default_value is None:
    die("Missing key:",key)
  return default_value


def warning(*args):
  warning_skip(1, *args)
  return True


def unimp(*args):
  """Prints unimplemented msg, if hasn't yet been printed."""
  loc = get_caller_location()
  s = "*** unimplemented " + loc + ": "
  if len(args):
    msg = s + spr(*args)
  else:
    msg = s
  _one_time_only(msg)
  return True


def get_caller_location(nSkip=2):
  h = inspect.stack()
  if 0 <= nSkip < len(h):
    fi = h[nSkip]  # inspect.getframeinfo(h[1])
    loc = simple_name(fi[1], fi[2])  # fi.__file__,fi.f_lineno)
  else:
    loc = "(UNKNOWN LOCATION)"
  return loc


def my_assert(cond):
  warning_skip(1, "checking assertion")
  error_if(not cond)


def not_none(arg):
  """
  Raise exception if argument is 'None';
  otherwise, return the argument
  """
  if arg is None:
    error("Argument is 'None'")
  return arg


def check_state(cond, *args):
  if cond:
    return
  error(_log_msg("Illegal state", *args))


def check_arg(cond, *args):
  if cond:
    return
  error(_log_msg("Bad argument:", *args))


def error(msg=None):
  """
  Raise an exception, optionally with a message
  """
  if msg is None:
    msg = "error occurred"
  raise Exception(msg)


def error_if(cond, msg=None):
  """
  Raise an exception, optionally with a message, if a condition is true
  """
  print("...refactor to use 'check_state' instead of 'error_if'...")
  if cond:
    error(msg)


def error_unless(cond, msg=None):
  error_if(not cond, msg)


def die(*args):
  error(_log_msg("...exiting program!", *args))


def halt(*args):
  loc = get_caller_location(2)
  s = "...at " + loc + ":" + _log_msg("   halting program early (development only)", *args)
  print(s)
  quit()


def _log_msg(default_msg, *args):
  if len(args) == 0:
    args = [default_msg]
  return spr(*args)



_last_timer_mark = None


def time_ms():
  return int(round(time.time() * 1000))


def timer_start(message=None):
  global _last_timer_mark
  _last_timer_mark = time_ms()
  output = ""
  if message:
    output = "(Starting timer: " + message + ")"
  return output


def timer_mark(message=None):
  global _last_timer_mark
  if not _last_timer_mark:
    return timer_start(message)

  current = time_ms()
  diff = current - _last_timer_mark
  _last_timer_mark = current
  message_expr = ""
  if message:
    message_expr = " : " + message
  return "({:6.3f}s {})".format(diff / 1000.0, message_expr)


def report_exception(e, skip=1, limit=20):
  message = exception_info(e, skip + 1, limit)
  pr(message)


def exception_info(e, skip=1, limit=20):
  """
  Get subset of stack trace from exception
  """
  if e is None:
    info = traceback.extract_stack(None, limit + skip)
  else:
    info = traceback.extract_tb(e.__traceback__)
  info = info[skip:skip + limit]

  # Build list of prefixes we'll omit, including lines within system libraries
  # that we'll omit altogether
  #
  prefix_map = {}
  prefix_map["/usr"] = "!"

  # Filter stack trace entries
  #
  # Construct list of lists [location, text]
  #                      or [skip count, None]
  #
  filtered = []
  omit_count = 0

  for x in info:
    f2 = x.filename

    for key, val in prefix_map.items():
      if x.filename.startswith(key):
        if val == "!":
          f2 = None
        else:
          if x.filename.startswith(val):
            f2 = x.filename[len(val):]
    if f2 is None:
      omit_count += 1
      continue

    if omit_count > 0:
      filtered.append([omit_count, None])
      omit_count = 0

    line_info = x.line
    loc_str = '{:s} ({:d})'.format(f2, x.lineno)
    filtered.append([loc_str, line_info])

  if omit_count > 0:
    filtered.append([omit_count, None])

  # Determine maximum length of line info,
  # and replace skip counts with appropriate text
  #
  max_len = 20
  for x in filtered:
    if x[1] is None:
      x[0] = '...{:d} omitted...'.format(x[0])
    max_len = max(max_len, len(x[0]))

  result = ""
  if e:
    result += "=" * 125 + "\n"
  fmt = '{:' + str(max_len) + 's} : {:s}'
  for elem in filtered:
    loc_str, line = elem
    if line is None:
      s = loc_str
    else:
      s = fmt.format(loc_str, line)
    result = result + s + "\n"

  if e:
    result += "***\n"
    as_str = str(e)
    # Deal with exception chaining; remove excess comments
    clip = as_str.find("Caused by")
    if clip > 0:
      as_str = as_str[0:clip]
    result += "*** " + as_str.strip()
  return result


def ca_builder(app=None):
  c = _v.cmd_line_args
  if c is None:
    _v.app = app
    import argparse
    from argparse import RawDescriptionHelpFormatter
    epilog = None
    c = argparse.ArgumentParser(epilog=epilog, formatter_class=RawDescriptionHelpFormatter)
    _v.cmd_line_args = c
  return c


def ca_args():
  if _v.ca_args is None:
    _v.ca_args, _v.ca_extras = ca_builder().parse_known_args()
    for s in _v.ca_extras:
      if s.startswith("-"):
        die("Unknown argument:", s)
  return _v.ca_args


def assert_args_done():
  ca_args()
  extras = _v.ca_extras
  if len(extras) != 0:
    die("extraneous arguments:", *extras)


def has_next_arg():
  """
  Return true iff more arguments exist
  """
  ca_args()
  return len(_v.ca_extras) != 0


def next_arg(default_value=None):
  """
  Read next argument; if none exist, return default value; fail if none provided
  """
  if has_next_arg():
    arg = _v.ca_extras.pop(0)
  else:
    if default_value is None:
      die("missing argument")
    arg = default_value
  return arg


def _parse_value_to_match_type(value, value_of_type):
  if isinstance(value_of_type, float):
    return float(value)
  if isinstance(value_of_type, int):
    return int(value)
  return value


def next_arg_if(name, default_value=False):
  """
  If next argument doesn't exist, or doesn't match the provided name, return the default value.
  Otherwise, read the next argument, and:
   If default value is false, return true (i.e. it's a boolean flag argument);
   Otherwise:
     read the next argument (failing if there isn't one)
     parse its argument based on the type of the default value
     return the parsed value
  """
  effective_default = _v.arg_value_map.get(name) or default_value
  if has_next_arg() and _v.ca_extras[0] == name:
    _v.done_handling_args = False
    next_arg()
    if type(effective_default) != bool:
      value = _parse_value_to_match_type(next_arg(), effective_default)
      _v.arg_value_map[name] = value
    else:
      value = True
      _v.arg_value_map[name] = value
  else:
    value = effective_default
  return value


def handling_args():
  """
  Conditional for 'while handling_args()' to repeat
  a loop that handles a sequence of arguments.
  If no explicit arguments were provided, this will return false
  """
  _v.done_handling_args = not _v.done_handling_args
  return _v.done_handling_args



def execute_commands():
  _v.done_handling_args = False
  _v.arg_value_map = {}
  try:
    _v.app.perform()
  except KeyboardInterrupt as exc:
    raise Exception("KeyboardInterrupt") from exc




def chomp(string, suffix):
  if string.endswith(suffix):
    return string[:-len(suffix)]
  return string


def txt_read(path, defcontents=None):
  if defcontents and not os.path.isfile(path):
    return defcontents
  with open(path) as f:
    contents = f.read()
  return contents


def txt_write(path, contents):
  with open(path, "w") as text_file:
    text_file.write(contents)

def mkdir(path, name = None):
  if not os.path.exists(path):
    if name:
      pr("Creating",name,":",path)
    os.makedirs(path)




def clamp(value, min_val, max_val):
  if value < min_val:
    return min_val
  if value > max_val:
    return max_val
  return value

def where(depth=1):
  """
  Construct a string describing the current location in the program
  """
  info = inspect.stack()[depth]
  filename = info[1]
  line_no = info[2]
  line_text = info[3]
  s = "%s (%d)" % (filename, line_no)
  return "%-22s: %s" % (s,line_text)

def pw(depth = 1):
  """
  Display the current location in the program
  """
  print(where(1+depth))




def name_of(var, back_count=1, default_value=None):
  # Get name of variable
  frame = inspect.currentframe()
  for i in range(back_count):
    frame = frame.f_back
  callers_local_vars = frame.f_locals.items()
  names = [var_name for var_name, var_val in callers_local_vars if var_val is var]
  if len(names) != 1:
    if default_value is not None:
      return default_value
    return str(type(var))
  return names[0]


#-------------------------------------------------------------------------------------
# A convenient base class that supports selective logging, naming
#-------------------------------------------------------------------------------------

class MyObject:

  def __init__(self, **kwargs):
    self._verbose = kwargs.get("verbose", False)
    self._name = kwargs.get("name", None)

  def set_verbose(self, verbose=True):
    self._verbose = verbose
    return self

  def set_name(self, name):
    check_state(name)
    self._name = name
    return self

  def name(self):
    if self._name is None:
      n = self.provide_name()
      check_state(n, "failed to get name for "+str(self))
      self._name = n
    return self._name

  def provide_name(self):
    n = self.__class__.__name__
    k = n.rfind(".")
    n = n[k + 1:]
    return n

  def log(self, *args):
    if self._verbose:
      pr("("+self.name()+")", *args)


def quick_tests():
  clear_screen("just called clear_screen")
  pr("\n\n\n========== base.py: basic python tools =========")

  pr("Here's a stack trace:", st())
  warning("This is a warning;", 5, 12, 42.123456, "alpha", "bravo")
  unimp("this code is unimplemented")
  if True:
    print(timer_start("Beginning a time consuming operation"))
    time.sleep(0.5)
    print(timer_mark("Slept for 1/2 sec"))
    time.sleep(0.2)
    print(timer_mark("Slept for a bit more"))

  x = "this is a string"
  pr("name_of:",name_of(x))




if __name__ == "__main__":
  quick_tests()

