import re
import spacy
from dateutil import parser

from core import pdf_title
from core.pdf_cleaning import TextCleaner
from core.pdf_manipulation import PDFManipulation

# Title extraction
# Abstract and keywords extraction
# refrences extraction
# Authors and their info (instituitons) extraction
# cleaning (equations, images, figures)
# release date extraction

class PDFProcessing():
    """
       Class for processing PDF documents to extract various information.

       This class provides methods for extracting title, abstract, keywords, references,
       authors and institutions, release date, and cleaning the text of a PDF document.

       Attributes:
           nlp (spacy.Language): SpaCy language model for natural language processing.
    """
    def __init__(self):
        """
                Initialize PDFProcessing object.

                Downloads and loads the SpaCy language model if not already installed.
        """
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            # Model not found. Download and install it.
            spacy.cli.download("en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")


    def analyze_extract_data(self,text, first_page, pdf_url, pdf_file):
        """
                Analyze and extract various data from a PDF document.

                Args:
                    text (str): Text content of the PDF document.
                    first_page (str): Content of the first page of the PDF document.
                    pdf_url (str): URL of the PDF document.
                    pdf_file: File object of the PDF document.

                Returns:
                    dict: Extracted data from the PDF document.
        """
        pdf_manipulator = PDFManipulation()
        text_cleaner = TextCleaner()
        abstract, text_without_abstract = self.extract_abstract(text)
        references, text_without_references = self.extract_references(text_without_abstract)
        keywords = self.extract_keywords(first_page)
        authors = self.extract_persons(first_page)
        institutions = self.extract_institutions(first_page)
        dates = self.extract_dates(text)
        title = pdf_manipulator.pdf_title_from_content(pdf_file)
        title = title if title else ""
        title = pdf_title.sanitize(' '.join(title.split()))
        cleaned_text = text_cleaner.cleaning_text(text_without_references)
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
            'text': cleaned_text,
            'date': dates[0],
        }
        return article_data
    # this is independent than the text cleaning, this is for attributes cleaning
    def clean_text(self, text):
        """
            Clean text by removing non-printable characters and special symbols, returning the first line.

            Args:
                text (str): The text to be cleaned.

            Returns:
                str: The cleaned first line of the text.
        """
        cleaned_text = ''.join(char for char in text if char.isprintable())
        cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
        return cleaned_text.split('\n')[0]

    def extract_persons(self, text):
        """
            Extract persons (authors) from the given text using named entity recognition.

            Args:
                text (str): The text from which to extract persons.

            Returns:
                list: A list of extracted persons.
        """
        doc = self.nlp(text)
        authors = [self.clean_text(ent.text) for ent in doc.ents if ent.label_ == "PERSON"]
        return authors

    def extract_institutions(self, text):
        """
           Extract institutions (organizations) from the given text using named entity recognition.

           Args:
               text (str): The text from which to extract institutions.

           Returns:
               list: A list of extracted institutions.
        """
        doc = self.nlp(text)
        institutions = [self.clean_text(ent.text) for ent in doc.ents if ent.label_ == "ORG"]
        # just a small filtering to improve results of the NLP model :)
        filter_keywords = ["univ", "departement", "college", "school","cole","departement","tech","institut"]
        filtered_institutions = [inst for inst in institutions if
                                 any(keyword in inst.lower() for keyword in filter_keywords)]
        return filtered_institutions if filtered_institutions else institutions

    def extract_dates(self, text):
        """
            Extract dates from the given text using named entity recognition.

            Args:
                text (str): The text from which to extract dates.

            Returns:
                list: A list of extracted dates.
        """
        doc = self.nlp(text)
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        valid_dates = [date for date in dates if self.is_valid_date(date)]
        unique_dates = set(valid_dates)  # Remove duplicates
        filtered_dates = [date for date in unique_dates if parser.parse(date).year <= 2023]
        formatted_dates = sorted([parser.parse(date).strftime("%Y-%m-%d") for date in filtered_dates], reverse=True)
        return formatted_dates

    def is_valid_date(self, date_str):
        """
            Check if a given string represents a valid date.

            Args:
                date_str (str): The string to be checked.

            Returns:
                bool: True if the string represents a valid date, False otherwise.
        """
        try:
            parser.parse(date_str)
            return True
        except ValueError:
            return False



    def should_stop_extraction(self, token):
        """
            Check if extraction should stop based on a given token.

            Args:
                token: A token from SpaCy.

            Returns:
                bool: True if extraction should stop, False otherwise.
        """
        stop_conditions = ["keywords", "index", "key", "figure", "table","introduction","ccs"]
        return token.text.lower() in stop_conditions

    def contains_date(self, text):
        """
           Check if the given text contains any dates.

           Args:
               text (str): The text to be checked.

           Returns:
               bool: True if the text contains any dates, False otherwise.
        """
        doc = self.nlp(text)
        return any(ent.label_ == "DATE" for ent in doc.ents)


    def extract_abstract(self, text):
        """
           Extract the abstract from the given text.

           Args:
               text (str): The text from which to extract the abstract.

           Returns:
               tuple: A tuple containing the extracted abstract and the text without the abstract.
        """
        doc = self.nlp(text)
        abstract_start = 0
        abstract_end = len(doc)-1
        #Defining alt terms for the abstract (it might be one of them and they all mean the same)
        abstract_synonyms = ["abstract", "summary", "summary of findings", "executive summary", "highlights"]
        consecutive_uppercase_text = ""
        for i, token in enumerate(doc):
            if token.text.lower() in abstract_synonyms or consecutive_uppercase_text.lower() in abstract_synonyms or  any(re.match(fr'^\d+\.\s*{re.escape(synonym.lower())}', token.text, re.IGNORECASE) for synonym in abstract_synonyms):
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
        """
           Extract references from the given text.

           Args:
               text (str): The text from which to extract references.

           Returns:
               tuple: A tuple containing the extracted references and the text without the references.
        """
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
            if line.lower() in ref_synonyms or any(re.match(fr'^\d+\.\s*{re.escape(synonym.lower())}', line, re.IGNORECASE) for synonym in ref_synonyms):
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
        if not references or not text_without_references:
            text_without_references = text
        return references, text_without_references


    def extract_keywords(self,text):
        """
            Extract keywords from the given text.

            Args:
                text (str): The text from which to extract keywords.

            Returns:
                str: The extracted keywords.
        """
        #the synonyms for keywords
        keyword_indicators = ['Keywords', 'Key Terms', 'Key Words', 'Index Terms',
                              'Phrases', 'Subjects', 'Topics']
        #combine them to form a regex pattern to test on and check the article_text
        keyword_pattern = '|'.join(re.escape(keyword) for keyword in keyword_indicators)
        start_pattern = re.compile(fr'\b({keyword_pattern})\s*[:\-\—\n]\s*', re.IGNORECASE)
        match_start = start_pattern.search(text)
        if match_start:
            start_index = match_start.end()
            end_pattern = re.compile(r'(\.|^\d+\.\s|[IVXLCDM]+\.\s*[A-Z]|The|Reference|Introduction)',re.IGNORECASE)
            match_end = end_pattern.search(text, start_index)
            # If the end pattern is found, extract the content
            if match_end:
                end_index = match_end.start()
                return text[start_index:end_index].strip()
            else:
                return text[start_index:].strip()
        return None







