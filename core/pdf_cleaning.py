import spacy
import re
import string


class TextCleaner:
    removal_words = {'figure', 'table', 'formula', 'equation', 'image', 'citations', 'reads', 'fig'}

    def __init__(self):
        # Load the spaCy English model
        self.nlp = spacy.load("en_core_web_sm")

    def cleaning_text(self, text):
        # Step 1: Delete successive lines with only numbers
        cleaned_numbers_text = self.delete_successive_numbers_lines(text)
        # Step 2: Delete successive lines with one word only
        cleaned_one_word_text = self.delete_successive_one_word_lines(cleaned_numbers_text)

        # Step 3: Delete lines containing removal words
        cleaned_removal_words_text = self.delete_lines_with_removal_words(cleaned_one_word_text)

        # Step 4: Remove URLs and verbal sentences
        cleaned_text = self.clean_more(cleaned_removal_words_text)

        return cleaned_text

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
            # Check if the line contains non-numeric characters
            if any(c for c in line if c.isalpha() or c in string.punctuation):
                cleaned_lines.append(line)

        # Join the cleaned lines to form the final text
        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text

    def delete_successive_one_word_lines(self, text):
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Process the line with spaCy
            doc = self.nlp(line)

            # Check if the line has only one word (excluding punctuation)
            is_one_word_line = len(doc) == 1 and not doc[0].is_punct

            # Determine if the line should be added to the cleaned text
            if not is_one_word_line:
                # Add the line to cleaned text
                cleaned_lines.append(line)

        # Join the cleaned lines to form the final text
        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text

    def delete_lines_with_removal_words(self, text):
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Check if the line contains any removal words
            if not any(word in line.lower() for word in self.removal_words):
                cleaned_lines.append(line)

        # Join the cleaned lines to form the final text
        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text
