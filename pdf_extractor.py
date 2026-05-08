import fitz

def extract_text_from_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    full_text=""

    for page in doc:
        full_text+=page.get_text()

    doc.close()

    return full_text.strip()

if __name__ == "__main__":

    text= extract_text_from_pdf("sample_resume.pdf")
    print(text)