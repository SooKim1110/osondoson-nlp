'''
    Tokenize korean using open-korean-text
       - https://github.com/open-korean-text/open-korean-text
       - http://konlpy.org/ko/latest/api/konlpy.tag/#okt-class
'''

import re

# from konlpy.tag import Okt
from konlpy.tag import Mecab
from rasa.shared.nlu.training_data.message import Message
from typing import Any, List, Text, Dict

from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer

from rasa.nlu.constants import TOKENS_NAMES, MESSAGE_ATTRIBUTES

class KoreanTokenizer(Tokenizer):

  def __init__(self, component_config = None):
    super(KoreanTokenizer, self).__init__(component_config)
    self.mecab = Mecab()

  def tokenize(self, message: Message, attribute: Text) -> List[Token]:
    # type: (Text) -> List[Token]
    text = message.get(attribute)
    token_list=self.mecab.morphs(text)

    running_offset = 0
    result = []
    for token in token_list:
        token_offset = text.index(token, running_offset)
        token_len = len(token)
        running_offset = token_offset + token_len
        result.append(Token(token, token_offset))

    return result
# provides = [TOKENS_NAMES[attribute] for attribute in MESSAGE_ATTRIBUTES]
# #defaults = { # Flag to check whether to split intents "intent_tokenization_flag": False, # Symbol on which intent should be split "intent_split_symbol": "_", } 
# def __init__(self, component_config: Dict[Text, Any] = None) -> None:
#   super().__init__(component_config)
#   from sudachipy import dictionary
#   from sudachipy import tokenizer
#   self.tokenizer_obj = dictionary.Dictionary().create()
#   self.mode = tokenizer.Tokenizer.SplitMode.A 
#   mt = MeCab.Tagger()
  
# @classmethod 
# def required_packages(cls) -> List[Text]:
#    return ["sudachipy"]

# #def tokenize(self, text: Text) -> List[Token]:
# def tokenize(self, message: Message, attribute: Text) -> List[Token]:
#   text = message.get(attribute)
#   words = [m.surface() for m in self.tokenizer_obj.tokenize(text, self.mode)]

#  return self._convert_words_to_tokens(words, text)
#     name = "component.KoreanTokenizer"

#     provides = ["tokens"]

#     '''
#     okt implementation
#     '''
#     # defaults = {
#     #     # If True, token normalization
#     #     "norm":False,
#     #     # If Ture, token stemming
#     #     "stem":False
#     # }


# def tokenize(text: Text) -> List[Token]:
#   mt = MeCab.Tagger()
#   parsed = mt.parse(text)
#   # parsed returns token => POS separated by tab in multiple lines
#   x = (parsed.replace('\n', '\t').split('\t'))
#   words = []
#   for i in range(0, len(x) - 2, 2):
#       w = x[i]
#       words.append(w)

#   running_offset=0
#   tokens = []
#   for word in words:
#       word_offset = text.index(word, running_offset)
#       word_len = len(word)
#       running_offset = word_offset + word_len
#       tokens.append(Token(word, word_offset))
#   return tokens
  
# def process(self, message: Message, **kwargs: Any) -> None:
#   message.set("tokens", self.tokenize(message.text))