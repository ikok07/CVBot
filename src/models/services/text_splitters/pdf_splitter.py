import json
import os
import uuid
from io import BytesIO
from pathlib import Path

from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.io import DocumentStream
from langchain_core.documents import Document
from openai import AsyncOpenAI

from src.models.services.text_splitters.base_splitter import BaseSplitter
from src.models.services.text_splitters.markdown_splitter import MarkdownSplitter


class PDFSplitter(BaseSplitter):
    image_path = Path("./artifacts")
    image_placeholder = "<--- image --->"
    page_break_placeholder = "<--- page-break --->"

    async def _generate_image_descriptions(self, image_uris: list[str]):
        client = AsyncOpenAI()
        response = await client.responses.create(
            model=os.getenv("PDF_IMAGE_DESCRIPTION_GENERATOR_MODEL"),
            input=[
                {
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": "Describe this image in a few sentences. Do not enumerate the images. Respond in JSON array, containing the descriptions for each image"
                    }] + [{"type": "input_image", "image_url": image_uri} for image_uri in image_uris],
                }
            ],
        )
        return response.output_text.replace("```", '').replace("json", '')

    def _replace_occurances(self, text: str, target: str, replacements: list[str]):
        for replacement in replacements:
            occurrence_index = text.find(target)
            if occurrence_index != -1:
                text = text[:occurrence_index] + replacement + text[occurrence_index + len(target):]
            else:
                raise ValueError("Replacements count is not equal to the targets count in the provided text!")

        return text

    async def split(self, file_content: bytes):
        pipeline_options = PdfPipelineOptions(
            generate_picture_images=True,
            images_scale=1.0,
            do_ocr=True,
            ocr_options=EasyOcrOptions(
                lang=["en", "bg"],
            ),
            accelerator_options=AcceleratorOptions(
                device=AcceleratorDevice.MPS
            )
        )
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        result = converter.convert(DocumentStream(name=str(uuid.uuid4()), stream=BytesIO(file_content)))
        markdown = result.document.export_to_markdown(
            image_placeholder=self.image_placeholder,
            page_break_placeholder=self.page_break_placeholder
        )
        image_uris = [str(picture.image.uri) for picture in result.document.pictures]
        image_descriptions: list[str] = json.loads(await self._generate_image_descriptions(image_uris))
        markdown = self._replace_occurances(markdown, self.image_placeholder, image_descriptions)
        
        markdown_splitter = MarkdownSplitter()
        return await markdown_splitter.split(markdown.encode("utf-8"))