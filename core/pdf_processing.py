# Title extraction
# Abstract and keywords extraction
# refrences extraction
# Authors and their info (instituitons) extraction
# cleaning (equations, images, figures)
# release date extraction
import re
from datetime import datetime
import spacy
from dateutil import parser

from core import pdf_title
from core.pdf_manipulation import PDFManipulation


class PDFProcessing():
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            # Model not found. Download and install it.
            spacy.cli.download("en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")


    def analyze_extract_data(self,text, first_page, pdf_url,title, pdf_file):
        pdf_manipulator = PDFManipulation()
        abstract, text_without_abstract = self.extract_abstract(text)
        references, text_without_references = self.extract_references(text_without_abstract)
        keywords = self.extract_keywords(first_page)
        authors = self.extract_persons(first_page)
        institutions = self.extract_institutions(first_page)
        dates = self.extract_dates(text)
        print("\n\nkeywords: ", keywords)
        print("\n\nAuthors: ", authors)
        print("\n\nInstitutions: ", institutions)
        print("\n\ndates: ", dates)
        title = pdf_manipulator.pdf_title_from_content(pdf_file)
        print("title wlinaaa ta3 wlinaaaa: ", title)
        title = title if title else ""
        title = pdf_title.sanitize(' '.join(title.split()))
        print("\n\ntitle: ", title)
        abstract = abstract if abstract else ""
        references = references if references else ""
        keywords = keywords if keywords else ""
        authors = authors if authors else []
        institutions = institutions if institutions else []
        article_data = {
            'title': title,
            'authors': authors,
            'institutions': institutions,
            'keywords': keywords,
            'pdf_url': pdf_url,
            'bibliographie': references,
            'abstract': abstract,
            'text': 'This is the text of the article.',
            'date': dates[0],
        }
        return article_data
    #extract abstract
    #extract references
    #extract keywords
    #extract institutions
    #extract title
    #extract date
    #extract texte
    #extract auteurs

    def clean_text(self, text):
        cleaned_text = ''.join(char for char in text if char.isprintable())
        cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
        return cleaned_text.split('\n')[0]
    def extract_persons(self, text):
        doc = self.nlp(text)
        authors = [self.clean_text(ent.text) for ent in doc.ents if ent.label_ == "PERSON"]
        return authors
    def extract_institutions(self, text):
        doc = self.nlp(text)
        institutions = [self.clean_text(ent.text) for ent in doc.ents if ent.label_ == "ORG"]
        # just a small filtering to improve results of the NLP model :)
        filter_keywords = ["univ", "departement", "college", "school","cole","departement","tech","institut"]
        filtered_institutions = [inst for inst in institutions if
                                 any(keyword in inst.lower() for keyword in filter_keywords)]
        return filtered_institutions if filtered_institutions else institutions

    def extract_dates(self, text):
        doc = self.nlp(text)
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        valid_dates = [date for date in dates if self.is_valid_date(date)]
        unique_dates = set(valid_dates)  # Remove duplicates
        filtered_dates = [date for date in unique_dates if parser.parse(date).year <= 2023]
        formatted_dates = sorted([parser.parse(date).strftime("%Y-%m-%d") for date in filtered_dates], reverse=True)
        return formatted_dates

    def is_valid_date(self, date_str):
        try:
            parser.parse(date_str)
            return True
        except ValueError:
            return False


    def is_title(self, token):
        # Customize this function based on your specific data and title characteristics
        return token.is_title or (token.is_upper and len(token.text) > 1)

    def should_stop_extraction(self, token):
        # Customize this function to specify conditions to stop extraction
        stop_conditions = ["keywords", "index", "key", "figure", "table","introduction","ccs"]
        return token.text.lower() in stop_conditions

    def contains_date(self, text):
        # Check if the text contains a date-like entity using SpaCy's Named Entity Recognition (NER)
        doc = self.nlp(text)
        return any(ent.label_ == "DATE" for ent in doc.ents)

    def is_mostly_capitalized(self, text, threshold=0.7):
        words = text.split()
        capitalized_words = [word.capitalize() if word[0].isupper() else word for word in words]
        capitalized_count = sum(1 for word in capitalized_words if word[0].isupper())
        ratio_capitalized = capitalized_count / len(words)
        return ratio_capitalized >= threshold

    def doc_collection_of_mostly_capitalized(self, doc):
        mostly_capitalized_lines = []
        for sentence in doc.sents:
            if self.is_mostly_capitalized(sentence.text):
                cleaned_line = sentence.text.strip()
                if ',' not in cleaned_line:
                    mostly_capitalized_lines.append(cleaned_line)
        return mostly_capitalized_lines

    def extract_abstract(self, text):
        doc = self.nlp(text)
        abstract_start = 0
        abstract_end = len(doc)-1
        #Defining alt terms for the abstract (it might be one of them and they all mean the same)
        abstract_synonyms = ["abstract", "summary", "summary of findings", "executive summary", "highlights"]
        consecutive_uppercase_text = ""
        for i, token in enumerate(doc):
            if token.text.lower() in abstract_synonyms or consecutive_uppercase_text.lower() in abstract_synonyms:
                abstract_start = i  # Start extraction after the word "abstract"
            if token.text.isupper() and len(token.text) == 1 and len(token.text)>0:
                consecutive_uppercase_text += token.text
            elif abstract_start is not None and abstract_start!=0 and (self.should_stop_extraction(token)):
                # Stop extraction
                abstract_end = i
                break
            else:
                consecutive_uppercase_text = ""
        # we defined where it begins and where it ends, now it's time to extract
        abstract = doc[abstract_start:abstract_end].text.strip()
        text_without_abstract = text[:doc[abstract_start].idx] + text[doc[abstract_end].idx:].strip()

        return abstract, text_without_abstract

    def extract_references(self, text):
        lines = text.split('\n')
        start_extraction = False
        reference_patterns = [
            r'^\d+\.',  # numbers like '1.'
            r'^\[\d+\]',  # numbers like '[1]'
            r'^[A-Z][A-Za-z\s]*,\s[A-Z][\w\s]*\d{4}',  # Author and year pattern, 'Author, J. 2000'
        ]
        #and any(re.match(pattern, line) for pattern in reference_patterns)
        references = []
        ref_synonyms = ["bibliography","references"]
        successive_non_matching_lines = 0
        start_index = 0
        for i, line in enumerate(lines):
            # Whenrever we meet a reference synonym
            if line.strip().lower() in ref_synonyms:
                start_extraction = True
                start_index = i
            # We start extracting them when one of the synonyms is found
            if start_extraction:
                successive_non_matching_lines += 1
                if any(re.match(pattern, line) for pattern in reference_patterns):
                    successive_non_matching_lines = 0
                if successive_non_matching_lines >= 15:
                    break
                references.append(line.strip())

        if len(references) < 7:
            ref_title_index = next((i for i, line in enumerate(lines) if line.strip().lower() in ref_synonyms), None)
            if ref_title_index is not None:
                references += [line.strip() for line in lines[ref_title_index + 1:]]
        first_line_after_references = len(text)-1
        text_without_references = "\n".join(lines[:start_index] + lines[first_line_after_references:])
        return references, text_without_references

    def detect_article_title(self,text):

        # Process the text with spaCy
        doc = self.nlp(text)

        # Initialize variables to track candidate titles and their corresponding lines
        current_title = ""
        potential_titles = []
        potential_title_lines = []

        # Iterate through tokens in the document
        for sent in doc.sents:
            # Check if the sentence starts with common words
            if sent[0].text.lower() in ["on", "a", "the"]:
                current_title = sent.text.strip()
                continue

            for token in sent:
                # Check if the token is a proper noun (capitalized word)
                if token.pos_ == "PROPN":
                    current_title += " " + token.text
                else:
                    # Check if the current sequence is a potential title
                    if current_title and (current_title.istitle() or current_title.isupper()):
                        potential_titles.append(current_title.strip())
                        potential_title_lines.append(sent.text.split('\n')[0].strip())
                    current_title = ""

        # Check for the last potential title
        if current_title and (current_title.istitle() or current_title.isupper()):
            potential_titles.append(current_title.strip())
            potential_title_lines.append(sent.text.split('\n')[0].strip())

        # Return the longest potential title and its entire line
        if potential_titles:
            longest_title = max(potential_titles, key=len)
            index_of_longest_title = potential_titles.index(longest_title)
            return "\nLongest Title: " + str(longest_title), "\nPotential Line: " + str(
                potential_title_lines[index_of_longest_title])
        else:
            return None, None

    def extract_keywords(self,text):
        #the synonyms for keywords
        keyword_indicators = ['Keywords', 'Key Terms', 'Key Words', 'Index Terms',
                              'Phrases', 'Subjects', 'Topics']
        #combine them to form a regex pattern to test on and check the article_text
        keyword_pattern = '|'.join(re.escape(keyword) for keyword in keyword_indicators)
        start_pattern = re.compile(fr'\b({keyword_pattern})\s*[:\-\—\n]\s*', re.IGNORECASE)
        match_start = start_pattern.search(text)
        if match_start:
            start_index = match_start.end()
            end_pattern = re.compile(r'(\.|^\d+\.\s|[IVXLCDM]+\.\s*[A-Z]|The|Reference)')
            match_end = end_pattern.search(text, start_index)
            # If the end pattern is found, extract the content
            if match_end:
                end_index = match_end.start()
                return text[start_index:end_index].strip()
            else:
                return text[start_index:].strip()
        return None







