
html_instructions = """
// Put the response here. 
Be strict in following the html instructions"
Always make the response in HTML.
Break up large the response into paragraphs.
Always separate paragraphs and with <p> tags
"""

file_info_objects = """
     list[{"page": 3, "name": "file1", "href": "https://example.com/file1"}]  
     // A list of file info objects. With page number, name of file and href for links of where the information was obtained.
"""


custom_format_instructions = f"""
     Respond in json format
    {{
        "response":string  {html_instructions}
        "file_info_objects":{file_info_objects}
    }}
"""


# from langchain.output_parsers import ResponseSchema
# from langchain.output_parsers import StructuredOutputParser
#
# response_text = ResponseSchema(name="r", description="The answer to the query in HTML. Always make the response in HTML and always separate paragraphs by 2 lines like \n\n")
#
# page_number = ResponseSchema(name="page_number", description="This page number")
#
# file_name = ResponseSchema(name="file_name", description="The name of the file the information is retrieved from")
#
# file_links = ResponseSchema(name="file_links", description="The links to the files")
#
# response_schemas = [response_text,
#                     page_number,
#                     file_name,
#                     file_links]
#
# output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
#
# format_instructions = output_parser.get_format_instructions()

