import os
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.converter import TextConverter
import io
import re

def parse():
    #projectDir = 'D:/Projects/Extraction-of-Skills-master'
    projectDir = os.getcwd()+'../'
    resumeDir = projectDir + '/uploads/resume'
    print("dir= ",resumeDir)

    def convert_pdf_to_txt(path):
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
        page_interpreter = PDFPageInterpreter(resource_manager, converter)

        with open(path, 'rb') as fh:

            for page in PDFPage.get_pages(fh,
                                        caching=True,
                                        check_extractable=True):
                page_interpreter.process_page(page)

            text = fake_file_handle.getvalue()

        # close open handles
        converter.close()
        fake_file_handle.close()

        return text

    resumeTxt = []
    for filename in os.listdir(resumeDir):
        if(filename.endswith(".pdf")):
            try:
                resumeTxt.append(convert_pdf_to_txt(resumeDir+filename))
            except Exception:
                print('Error reading .pdf file' + filename)

    len(resumeTxt)
    print(resumeTxt[0])  

    resumeTxtNoStopword = []

    for resume in resumeTxt:
        text = resume
        text = text.split()
        useful_words = [w for w in text ]#if w not in sw]
        resumeTxtNoStopword.append(" ".join(useful_words))

    def tokenize(text):
        # obtains tokens with a least 1 alphabet
        pattern = re.compile(r'[A-Za-z]+[\w^\']*|[\w^\']*[A-Za-z]+[\w^\']*')
        return pattern.findall(text.lower())

    i = 0
    tokenized_resumes = []
    for resume in resumeTxtNoStopword:
        r = tokenize(resume)
        tokenized_resumes.append(r)
        i += 1

    print(tokenized_resumes[0])