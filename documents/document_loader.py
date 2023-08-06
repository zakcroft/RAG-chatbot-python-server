import os
import pathlib
import shutil

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader, \
    UnstructuredExcelLoader
from langchain.document_loaders.csv_loader import CSVLoader

recursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
    chunk_size=int(os.getenv("TEXT_SPLIT_CHUNK_SIZE")),
    chunk_overlap=int(os.getenv("TEXT_SPLIT_OVERLAP")),
)


def get_file_folder_location(folder="default"):
    root_folder = "./files/"
    folder_location = f"{root_folder}{folder}/"
    pathlib.Path(folder_location).mkdir(parents=True, exist_ok=True)
    return folder_location


def store_file(file):
    folder_location = get_file_folder_location()
    file_location = f"{folder_location}{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    return file_location, file.filename


def split_pdf_to_chunks(file):
    pdf_path, file_name = store_file(file)
    loader = PyPDFLoader(pdf_path)

    if os.getenv("TEXT_SPLIT_BY_PAGE") == "True":
        docs = loader.load()  # Pages are made for pdfs with .load()
    else:
        docs = loader.load_and_split(text_splitter=recursiveCharacterTextSplitter)

    docs = add_extra_metadata(docs, file_name)
    return docs


def split_docx_to_chunks(file):
    docx_path, file_name = store_file(file)
    loader = Docx2txtLoader(docx_path)
    docs = loader.load_and_split(text_splitter=recursiveCharacterTextSplitter)
    docs = add_extra_metadata(docs, file_name)
    return docs


def split_excel_to_chunks(file):
    csv_path, file_name = store_file(file)
    loader = UnstructuredExcelLoader(file_path=csv_path)
    docs = loader.load_and_split(text_splitter=recursiveCharacterTextSplitter)
    docs = add_extra_metadata(docs, file_name)
    return docs


def split_csv_to_chunks(file):
    csv_path, file_name = store_file(file)
    loader = CSVLoader(file_path=csv_path)
    docs = loader.load_and_split(text_splitter=recursiveCharacterTextSplitter)
    docs = add_extra_metadata(docs, file_name)
    return docs


def split_pptx_to_chunks(file):
    pptx_path, file_name = store_file(file)
    loader = UnstructuredPowerPointLoader(
        pptx_path
    )
    docs = loader.load_and_split(text_splitter=recursiveCharacterTextSplitter)
    docs = add_extra_metadata(docs, file_name)
    return docs


def add_extra_metadata(docs, file_name):
    for i, doc in enumerate(docs, start=1):
        #  only pdfs have true page numbers so for the other file types page number === chunk_number
        if 'page' not in doc.metadata:
            doc.metadata['page'] = i
        doc.metadata['chunk_number'] = i
        doc.metadata['file_name'] = file_name

    print(len(docs))
    print(docs)

    return docs


def store_and_split_file(file):
    content_type = file.content_type
    print('Uploading doc type', content_type)
    if content_type == "application/pdf":
        return split_pdf_to_chunks(file)
    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return split_docx_to_chunks(file)
    if content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        return split_pptx_to_chunks(file)
    if content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return split_excel_to_chunks(file)


# def convert_docx_to_pdf(file):
#     store_file(file)
#     name = file.filename.split(".")[0]
#     folder_location = get_file_folder_location()
#     print(folder_location + name + '.docx')
#     print(folder_location + name + '.pdf')
#     convert(folder_location + name + '.docx', folder_location + name + '.pdf')
# print(pdf)
# store_file(pdf)
# return split_pdf_to_chunks(pdf)
# return split_pdf_to_chunks(pdf)
