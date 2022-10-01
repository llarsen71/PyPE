from PyPE.Tokenizer import Tokenizer
from PyPE import P, S, C, Cg, whitespace1 as ws, alpha, digit

# Define named patterns (i.e., tokens) that will be used in our patterns
word   = 'word'   | alpha**1       # One or more characters
number = 'number' | digit**1       # One or more digits
open   = 'open'   | P('(')         # Open paren starts the Numbers grammar
close  = 'close'  | P(')')         # Close paren closes the Numbers grammar

# Define a Words grammar to Number grammer switch
W2N = (open, 'Numbers', close)

# Define our two grammars which are words or numbers separated by spaces
words   = [word, ws, W2N]   # Note the grammar swith that is included
numbers = [number, ws]

# Add the two grammars, and start with 'Words' as the root grammar
T = Tokenizer('Words', Words=words, Numbers=numbers)

# Here is the text to parse
text = "cat rat (11 12 13) bat"

# Print the tokens that are parsed
for token, match in T.getTokens(text):
  print("%s: %s" % (token, match))