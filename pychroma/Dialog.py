from distutils.util import strtobool

# https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input/50216611#50216611
def prompt(question: str, default: bool) -> bool:
  """ Prompt the yes/no-*question* to the user. """
  question += f' [Y/n]: ' if default else f' [y/N]: '
  while True:
    user_input = input(question).lower()
    try:
      result = strtobool(user_input)
      return result
    except ValueError:
      if not user_input or user_input.isspace():
        return default
      print("Please use y/n or yes/no.\n")

def ask(question: str, default: str) -> str:
  """ Prompt with default answer """
  user_input = input(question + f' [default "{default}"] ')
  return user_input if user_input and not user_input.isspace() else default
