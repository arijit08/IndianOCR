import platform
from tempfile import TemporaryDirectory
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
import PyPDF2
from PIL import Image
import os
import io
import cv2 as cv

#This programme uses Tesseract (OCR lib) to convert pdfs
if platform.system() == "Windows":
    #If Windows, you must install Tesseract first, and set the path below to its exe
    pytesseract.pytesseract.tesseract_cmd = (
        "C:/Program Files/Tesseract-OCR/tesseract.exe"
    )

    global poppler_path
    # Windows also needs poppler_exe. Install and set the path below
    poppler_path = Path("C:/Users/08arijit/Documents/Libraries/Release-22.12.0-0/poppler-22.12.0/Library/bin")

#Function to check if directory exists, if not create it
def makedirs(path):
    if not os.path.isdir(path):
            os.makedirs(path)

#Function that takes in pdf, converts pages into images, reads text by OCR, saves pdf with text data
#"out" argument can be "txt" or "pdf", which denotes output file type
def read_pdf_ocr(pdf_path, output_path, out):

    image_file_list = []

    pdf_file = Path(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    text_file = os.path.join(output_path, pdf_name + ".txt")
    pdf_output = os.path.join(output_path, pdf_name + "_ocr.pdf")

    print("Reading OCR from " + pdf_name + ", saving as " + out + "type")

    #Create temp directory to save images (from pdf pages)
    with TemporaryDirectory() as tempdir:

        print("Creating temporary directory at " + tempdir)

        #Use poppler to convert the pdf into images of its pages
        if platform.system() == "Windows":
            pdf_pages = convert_from_path(
                pdf_file, 500, poppler_path=poppler_path
            )
        else:
            pdf_pages = convert_from_path(pdf_file, 500)

        #Save the images obtained above to the temp directory
        for page_enumeration, page in enumerate(pdf_pages, start=1):
            #Process the image stored in "page" variable here, to maximise possibility of recognition
            page = preprocess(page)

            filename = f"{tempdir}/page_{page_enumeration:03}.jpg"
            page.save(filename, "JPEG")
            image_file_list.append(filename)
        
        print("Extracted images from pdf file " + pdf_name)
        
        #Make output path if it does not exist
        makedirs(output_path)

        image_len = len(image_file_list)
        i = 0

        if out == "txt":
            for image_file in image_file_list:
                #Below function actually reads the text from the images. Set lang arg for language/script to read
                text = str(((pytesseract.image_to_string(Image.open(image_file), lang="mar"))))
                with open(text_file, "ab+") as output_file:
                    text = text.replace("-\n", "")
                    output_file.write(text.encode('utf8'))
                i = i + 1
                print(str((100*i)/image_len) + "% done")
        elif out == "pdf":
            with open(pdf_output, "w+b") as output_pdf:
                pdf_writer = PyPDF2.PdfFileWriter()
                for image_file in image_file_list:
                    #Below function actually reads the text from the images. Set lang arg for language/script to read
                    page = pytesseract.image_to_pdf_or_hocr(image_file,lang="mar")
                    pdf = PyPDF2.PdfFileReader(io.BytesIO(page))
                    #Append/add the pdf page obtained above to our output pdf file
                    pdf_writer.add_page(pdf.getPage(0))
                    pdf_writer.write(output_pdf)
                    i = i + 1
                    #Show progress
                    print(str((100*i)/image_len) + "% done")

#Function to preprocess image of page to maximise possibility of recognition
def preprocess(image):
    #Use parameter optimisation to see which combination of brightness, contrast, binary threshold, etc. maximise recognition
    #Use cv
    
    return image

#Later modify code to allow non pdf file types as well
pdf_path = Path(input("Enter pdf path: "))
#pdf_path = Path("C:/Users/08arijit/Documents/Data Science and Machine Learning/Data projects/IndiaOCR/test/5.pdf")
output_path = os.path.join(os.path.dirname(pdf_path), os.path.splitext(os.path.basename(pdf_path))[0] + "_ocr")
#output_path = Path("C:\\Users\\08arijit\\Documents\\Data Science and Machine Learning\\Data projects\\Marathi OCR\\test")
read_pdf_ocr(pdf_path,output_path, "pdf")