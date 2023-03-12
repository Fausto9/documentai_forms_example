import os
from typing import Iterator, Optional, Sequence, Tuple

import google.cloud.documentai_v1 as docai
from tabulate import tabulate

PROJECT_ID = 'cybernetic-zoo-252604'
API_LOCATION = "us"  # Choose "us" or "eu"

assert PROJECT_ID, "PROJECT_ID is undefined"
assert API_LOCATION in ("us", "eu"), "API_LOCATION is incorrect"

# Test processors
document_ocr_display_name = "document-ocr"
form_parser_display_name = "form-parser"

test_processor_display_names_and_types = (
    (document_ocr_display_name, "OCR_PROCESSOR"),
    (form_parser_display_name, "FORM_PARSER_PROCESSOR"),
)


def get_client() -> docai.DocumentProcessorServiceClient:
    client_options = {"api_endpoint": f"{API_LOCATION}-documentai.googleapis.com"}
    return docai.DocumentProcessorServiceClient(client_options=client_options)


def get_parent(client: docai.DocumentProcessorServiceClient) -> str:
    return client.common_location_path(PROJECT_ID, API_LOCATION)


def get_client_and_parent() -> Tuple[docai.DocumentProcessorServiceClient, str]:
    client = get_client()
    parent = get_parent(client)
    return client, parent

def print_processor_types(processor_types: Sequence[docai.ProcessorType]):
    def sort_key(pt):
        return (not pt.allow_creation, pt.category, pt.type_)

    sorted_processor_types = sorted(processor_types, key=sort_key)
    data = processor_type_tabular_data(sorted_processor_types)
    headers = next(data)
    colalign = next(data)

    print(tabulate(data, headers, tablefmt="pretty", colalign=colalign))
    print(f"→ Processor types: {len(sorted_processor_types)}")


def processor_type_tabular_data(
    processor_types: Sequence[docai.ProcessorType],
) -> Iterator[Tuple[str, str, str, str]]:
    def locations(pt):
        return ", ".join(sorted(loc.location_id for loc in pt.available_locations))

    yield ("type", "category", "allow_creation", "locations")
    yield ("left", "left", "left", "left")
    if not processor_types:
        yield ("-", "-", "-", "-")
        return
    for pt in processor_types:
        yield (pt.type_, pt.category, f"{pt.allow_creation}", locations(pt))

def fetch_processor_types() -> Sequence[docai.ProcessorType]:
    client, parent = get_client_and_parent()
    response = client.fetch_processor_types(parent=parent)

    return response.processor_types


def print_processor_types(processor_types: Sequence[docai.ProcessorType]):
    def sort_key(pt):
        return (not pt.allow_creation, pt.category, pt.type_)

    sorted_processor_types = sorted(processor_types, key=sort_key)
    data = processor_type_tabular_data(sorted_processor_types)
    headers = next(data)
    colalign = next(data)

    print(tabulate(data, headers, tablefmt="pretty", colalign=colalign))
    print(f"→ Processor types: {len(sorted_processor_types)}")


def processor_type_tabular_data(
    processor_types: Sequence[docai.ProcessorType],
) -> Iterator[Tuple[str, str, str, str]]:
    def locations(pt):
        return ", ".join(sorted(loc.location_id for loc in pt.available_locations))

    yield ("type", "category", "allow_creation", "locations")
    yield ("left", "left", "left", "left")
    if not processor_types:
        yield ("-", "-", "-", "-")
        return
    for pt in processor_types:
        yield (pt.type_, pt.category, f"{pt.allow_creation}", locations(pt))

processor_types = fetch_processor_types()
print_processor_types(processor_types)


def create_processor(display_name: str, type: str) -> docai.Processor:
    client, parent = get_client_and_parent()
    processor = docai.Processor(display_name=display_name, type_=type)

    return client.create_processor(parent=parent, processor=processor)

for display_name, type in test_processor_display_names_and_types:
    print(f"Creating {display_name} ({type})...")
    create_processor(display_name, type)
print("Done")

def list_processors() -> Sequence[docai.Processor]:
    client, parent = get_client_and_parent()
    response = client.list_processors(parent=parent)

    return response.processors


def print_processors(processors: Optional[Sequence[docai.Processor]] = None):
    def sort_key(processor):
        return processor.display_name

    if processors is None:
        processors = list_processors()
    sorted_processors = sorted(processors, key=sort_key)
    data = processor_tabular_data(sorted_processors)
    headers = next(data)
    colalign = next(data)

    print(tabulate(data, headers, tablefmt="pretty", colalign=colalign))
    print(f"→ Processors: {len(sorted_processors)}")


def processor_tabular_data(
    processors: Sequence[docai.Processor],
) -> Iterator[Tuple[str, str, str]]:
    yield ("display_name", "type", "state")
    yield ("left", "left", "left")
    if not processors:
        yield ("-", "-", "-")
        return
    for processor in processors:
        yield (processor.display_name, processor.type_, processor.state.name)

processors = list_processors()
print_processors(processors)

def get_processor(
    display_name: str,
    processors: Optional[Sequence[docai.Processor]] = None,
) -> Optional[docai.Processor]:
    if processors is None:
        processors = list_processors()
    for processor in processors:
        if processor.display_name == display_name:
            return processor
    return None

processor = get_processor(document_ocr_display_name, processors)

assert processor is not None
print(processor)




def process_file(
    processor: docai.Processor,
    file_path: str,
    mime_type: str,
) -> docai.Document:
    client = get_client()
    with open(file_path, "rb") as document_file:
        document_content = document_file.read()
    document = docai.RawDocument(content=document_content, mime_type=mime_type)
    request = docai.ProcessRequest(raw_document=document, name=processor.name)

    response = client.process_document(request)

    return response.document

processor = get_processor(form_parser_display_name)
assert processor is not None

file_path = r'C:\Users\Favel\Downloads\form.pdf'
mime_type = "application/pdf"

document = process_file(processor, file_path, mime_type)

def print_form_fields(document: docai.Document):
    sorted_form_fields = form_fields_sorted_by_ocr_order(document)
    data = form_field_tabular_data(sorted_form_fields, document)
    headers = next(data)
    colalign = next(data)

    print(tabulate(data, headers, tablefmt="pretty", colalign=colalign))
    print(f"→ Form fields: {len(sorted_form_fields)}")


def form_field_tabular_data(
    form_fields: Sequence[docai.Document.Page.FormField],
    document: docai.Document,
) -> Iterator[Tuple[str, str, str]]:
    yield ("name", "value", "confidence")
    yield ("right", "left", "right")
    if not form_fields:
        yield ("-", "-", "-")
        return
    for form_field in form_fields:
        name_layout = form_field.field_name
        value_layout = form_field.field_value
        name = text_from_layout(name_layout, document)
        value = text_from_layout(value_layout, document)
        confidence = value_layout.confidence
        yield (name, value, f"{confidence:.1%}")

def form_fields_sorted_by_ocr_order(
    document: docai.Document,
) -> Sequence[docai.Document.Page.FormField]:
    def sort_key(form_field):
        # Sort according to the field name detected position
        text_anchor = form_field.field_name.text_anchor
        return text_anchor.text_segments[0].start_index if text_anchor else 0

    fields = (field for page in document.pages for field in page.form_fields)
    fields = sorted(fields, key=sort_key)

    return fields


def text_from_layout(
    layout: docai.Document.Page.Layout, document: docai.Document
) -> str:
    full_text = document.text
    segs = layout.text_anchor.text_segments
    text = "".join(full_text[seg.start_index : seg.end_index] for seg in segs)
    if text.endswith("\n"):
        text = text[:-1]

    return text

print_form_fields(document)