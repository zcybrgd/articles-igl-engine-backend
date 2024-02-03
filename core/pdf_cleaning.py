import spacy
import re
import string


class TextCleaner:
    removal_words = {'figure', 'table', 'formula', 'equation', 'image', 'citations', 'reads', 'fig', '::', '<<'}

    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")

    def cleaning_text(self, text):
        # delete lines where mention of figures or things alike appear because we re not gonna display them
        cleaned_removal_words_text = self.delete_lines_with_removal_words(text)
        cleaned_unecessary_lines = self.delete_successive_one_word_lines(cleaned_removal_words_text)
        cleaned_numerics = self.delete_successive_numbers_lines(cleaned_unecessary_lines)
        return cleaned_numerics

    def clean_more(self, text):
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
        doc = self.nlp(text)
        verbal_sentences = []

        for sent in doc.sents:
            # Check if the sentence starts with a verb
            if sent[0].pos_ == "VERB":
                verbal_sentences.append(sent.text)

        return verbal_sentences

    def detect_urls(self, text):
        # Use a regular expression to find URLs in the text
        url_pattern = re.compile(r'https?://\S+')
        urls = url_pattern.findall(text)
        return urls

    def delete_successive_numbers_lines(self, text):
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            if any(c for c in line if c.isalpha() or c in string.punctuation):
                cleaned_lines.append(line)

        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text

    def delete_successive_one_word_lines(self, text):
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
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if not any(word in line.lower() for word in self.removal_words):
                cleaned_lines.append(line)
        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text
