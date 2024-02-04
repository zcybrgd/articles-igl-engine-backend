import spacy
import re
import string


class TextCleaner:
    """
       Class for cleaning text data.

       This class provides methods for cleaning text by removing unnecessary lines, numbers, URLs, and verbal sentences,
       as well as extra whitespaces.

       Attributes:
           nlp (spacy.Language): SpaCy language model for natural language processing.
           removal_words (set): Set of words indicating lines to be removed.
    """
    removal_words = {'figure', 'table', 'formula', 'equation', 'image', 'citations', 'reads', 'fig', '::', '<<'}

    def __init__(self):
        """
                Initialize TextCleaner object.

                Downloads and loads the SpaCy language model if not already installed.
        """
        self.nlp = spacy.load("en_core_web_lg")

    def cleaning_text(self, text):
        """
               Clean text by creating a pipeline that include all cleaning functions

               Args:
                   text (str): Input text to be cleaned.

               Returns:
                   str: Cleaned text.
        """
        # delete lines where mention of figures or things alike appear because we re not gonna display them
        cleaned_removal_words_text = self.delete_lines_with_removal_words(text)
        cleaned_unecessary_lines = self.delete_successive_one_word_lines(cleaned_removal_words_text)
        cleaned_numerics = self.delete_successive_numbers_lines(cleaned_unecessary_lines)
        return cleaned_numerics

    def clean_more(self, text):
        """
               Perform additional cleaning on the text.

               This method removes URLs, verbal sentences, and extra whitespaces.

               Args:
                   text (str): Input text to be cleaned.

               Returns:
                   str: Cleaned text with additional cleaning steps applied.
        """
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)

        # Detect and remove verbal sentences
        verbal_sentences = self.detect_verbal_sentences(text)
        for sentence in verbal_sentences:
            text = text.replace(sentence, '')

        # Remove extra whitespaces
        text = ' '.join(text.split())

        return text

    def detect_verbal_sentences(self, text):
        """
                Detect verbal sentences in the text.

                Args:
                    text (str): Input text to be analyzed.

                Returns:
                    list: List of verbal sentences detected in the text.
        """
        doc = self.nlp(text)
        verbal_sentences = []

        for sent in doc.sents:
            # Check if the sentence starts with a verb
            if sent[0].pos_ == "VERB":
                verbal_sentences.append(sent.text)

        return verbal_sentences

    def detect_urls(self, text):
        """
                Detect URLs in the text.

                Args:
                    text (str): Input text to be analyzed.

                Returns:
                    list: List of URLs detected in the text.
        """
        # Use a regular expression to find URLs in the text
        url_pattern = re.compile(r'https?://\S+')
        urls = url_pattern.findall(text)
        return urls

    def delete_successive_numbers_lines(self, text):
        """
               Delete successive lines consisting only of numbers from the text.

               Args:
                   text (str): Input text to be analyzed.

               Returns:
                   str: Text with successive lines consisting only of numbers removed.
        """
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            if any(c for c in line if c.isalpha() or c in string.punctuation):
                cleaned_lines.append(line)

        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text

    def delete_successive_one_word_lines(self, text):
        """
               Delete successive one-word lines from the text.

               Args:
                   text (str): Input text to be analyzed.

               Returns:
                   str: Text with successive one-word lines removed.
        """
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            doc = self.nlp(line)
            if doc:
                is_one_word_line = len(doc) == 1 or doc[0].is_punct
                if not is_one_word_line:
                    cleaned_lines.append(line)
        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text

    def delete_lines_with_removal_words(self, text):
        """
                Delete lines containing words from the removal_words set from the text.

                Args:
                    text (str): Input text to be analyzed.

                Returns:
                    str: Text with lines containing removal_words removed.
        """
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if not any(word in line.lower() for word in self.removal_words):
                cleaned_lines.append(line)
        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text
