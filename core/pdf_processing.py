# Title extraction
# Abstract and keywords extraction
# refrences extraction
# Authors and their info (instituitons) extraction
# cleaning (equations, images, figures)
# release date extraction
import re
import string

import spacy
from spacy.matcher import Matcher
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords


class PDFProcessing():
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Model not found. Download and install it.
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")


    def spacyNER(self, text):
        doc = self.nlp(text)

        persons = []
        organizations = []
        locations = []
        geopolitical_entities = []
        dates = []

        for ent in doc.ents:
            if ent.label_ == "PERSON" and ent.text not in persons:
                persons.append(ent.text)
            elif ent.label_ == "ORG" and ent.text not in organizations:
                organizations.append(ent.text)
            elif ent.label_ == "LOC" and ent.text not in locations:
                locations.append(ent.text)
            elif ent.label_ == "GPE" and ent.text not in geopolitical_entities:
                geopolitical_entities.append(ent.text)
            elif ent.label_ == "DATE" and ent.text not in dates:
                dates.append(ent.text)

        return {
            "persons": persons,
            "organizations": organizations,
            "locations": locations,
            "geopolitical_entities": geopolitical_entities,
            "dates": dates
        }

    def is_title(self, token):
        # Customize this function based on your specific data and title characteristics
        return token.is_title or (token.is_upper and len(token.text) > 1)

    def should_stop_extraction(self, token):
        # Customize this function to specify conditions to stop extraction
        stop_conditions = ["keywords", "index", "terms", "figure", "table"]
        return self.is_title(token) and token.text.lower() in stop_conditions

    def contains_date(self, text):
        # Check if the text contains a date-like entity using SpaCy's Named Entity Recognition (NER)
        doc = self.nlp(text)
        return any(ent.label_ == "DATE" for ent in doc.ents)

    def extract_abstract(self, text):
        doc = self.nlp(text)
        abstract_start = None
        abstract_end = len(doc)

        # Define alternative terms for the abstract
        abstract_synonyms = ["abstract", "summary", "summary of findings", "executive summary", "highlights"]

        for i, token in enumerate(doc):
            if token.text.lower() in abstract_synonyms:
                abstract_start = i   # Start extraction after the word "abstract"
            elif abstract_start is not None and (self.should_stop_extraction(token) or self.contains_date(token.text)):
                # Stop extraction when a title-like token or date-like entity is encountered
                abstract_end = i
                break

        # Extract the abstract
        abstract = doc[abstract_start:abstract_end].text.strip()
        text_without_abstract = text[:doc[abstract_start].idx] + text[doc[abstract_end].idx:].strip()

        return abstract, text_without_abstract

    def extract_references(self, text):
        # Split the text into lines
        lines = text.split('\n')

        # Flag to indicate when to start extracting references
        start_extraction = False

        # Define patterns for references
        reference_patterns = [
            r'^\d+\.',  # Numerical labeling like '1.'
            r'^\[\d+\]',  # Numerical labeling like '[1]'
            r'^[A-Z][A-Za-z\s]*,\s[A-Z][\w\s]*\d{4}',  # Author and year pattern, e.g., 'Author, J. 2000'
            # Add more patterns as needed based on your specific data
        ]

        # Extract lines matching reference patterns
        references = []
        ref_synonyms = ["references", "bibliography"]
        for line in lines:
            # Check if the line contains a reference title
            if line.strip().lower() in ref_synonyms:
                start_extraction = True
                continue

            # Start extracting references when the title is found
            if start_extraction and any(re.match(pattern, line) for pattern in reference_patterns):
                references.append(line.strip())

        if len(references) < 7:
            # Find the index of the line containing "references" or "bibliography"
            ref_title_index = next((i for i, line in enumerate(lines) if line.strip().lower() in ref_synonyms), None)

            if ref_title_index is not None:
                # Extract references from the line containing "references" or "bibliography" to the end of the article
                references += [line.strip() for line in lines[ref_title_index + 1:]]

        # Find the index of the first line after references
        first_line_after_references = len(text)
        for reference in references:
            reference_index = text.find(reference)
            if reference_index != -1:
                first_line_after_references = min(first_line_after_references, reference_index)

        # Extract text without references
        text_without_references = text[:first_line_after_references].strip()

        return references, text_without_references

    def extract_keywords(self, article_text):
        # Define common indicators for keywords
        keyword_indicators = ['Keywords', 'Key Terms', 'Key Words', 'Index Terms',
                              'Phrases', 'Subjects', 'Topics']
        # Convert the text to lowercase for case-insensitive matching
        lower_text = article_text.lower()

        # Process the text with spaCy
        doc = self.nlp(lower_text)

        # Variable to store the extracted keywords
        extracted_keywords = ""

        # Variable to indicate whether we are currently extracting keywords
        extracting_keywords = False

        # Set of special characters
        special_chars = set(string.punctuation)

        # Iterate through spaCy tokens
        for i, token in enumerate(doc):
            # Check if the current token or the combination of the current and next token
            # contains any of the keyword indicators
            current_token_text = token.text.lower()
            next_token_text = doc[i + 1].text.lower() if i + 1 < len(doc) else ''
            combined_text = f"{current_token_text} {next_token_text}".strip()

            # Check for both single-word and multi-word keyword indicators
            if any(indicator.lower() in current_token_text or indicator.lower() in combined_text for indicator in keyword_indicators):
                # Set the flag to start extracting keywords
                extracting_keywords = True
                print(f"Found indicator: {combined_text}")
                # If the indicator is attached to special characters, start extracting from the next token
                if combined_text[-1] in special_chars:
                    continue
                else:
                    extracted_keywords += combined_text + ' '
                # Exit the loop after extracting the first set of keywords
                break

        # If we found a keyword indicator, continue extracting until a period is encountered
        if extracting_keywords:
            for token in doc[i + 1:]:
                # If the token is a period, stop extracting keywords
                if token.text == '.':
                    break
                # Concatenate the token's text to the extracted_keywords variable
                extracted_keywords += token.text + ' '

        # Remove extra spaces and return the extracted keywords
        return extracted_keywords.strip()

    '''
    def ie_stanford(txt):
        """
            Name entity recognition (StanfordCoreNlP)
        """
        nlp = StanfordCoreNLP('http://localhost:9000')
        ann = nlp.annotate(txt, properties={
            'annotators': 'tokenize, ssplit, pos, lemma, ner',
            'outputFormat': 'json'})
        ent = [(w['word'], w['ner']) for sent in ann["sentences"] for w in sent['tokens']]
        for item in ent:
            print(item[0], item[1])
    '''



