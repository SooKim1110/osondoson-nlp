from typing import Any, Dict, List, Text

from pythainlp import word_tokenize

from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.shared.nlu.training_data.message import Message


class ThaiTokenizer(Tokenizer):

    defaults = {
        # Flag to check whether to split intents
        "intent_tokenization_flag": False,
        # Symbol on which intent should be split
        "intent_split_symbol": "_",
        # Text will be tokenized with case sensitive as default
        "case_sensitive": True,
    }

    supported_language_list = ["th"]

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super().__init__(component_config)

        self.case_sensitive = self.component_config["case_sensitive"]

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        if not self.case_sensitive:
            text = text.lower()
        words = word_tokenize(text)

        if not words:
            words = [text]

        return self._convert_words_to_tokens(words, text)
