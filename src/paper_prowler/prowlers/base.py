# Copyright 2024-present, David Berenstein, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import atexit
from abc import ABC, abstractmethod

from haystack import Pipeline
from haystack.components.converters import MarkdownToDocument, PyPDFToDocument, TextFileToDocument
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.joiners import DocumentJoiner
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.routers import FileTypeRouter
from haystack.components.writers import DocumentWriter

from paper_prowler.database import Database
from paper_prowler.synthesizer import Synthesizer


class Prowler(ABC):
    def __init__(
        self,
        synthesizer: Synthesizer = None,
        database: Database = None,
        cleaner: DocumentCleaner = None,
        splitter: DocumentSplitter = None,
        embedder: SentenceTransformersDocumentEmbedder = None,
        retriever: InMemoryEmbeddingRetriever = None,
        writer: DocumentWriter = None,
    ):
        self.pipeline = Pipeline()
        if synthesizer is None:
            synthesizer = Synthesizer()
        if database is None:
            database = Database.from_disk()
        if cleaner is None:
            cleaner = DocumentCleaner()
        if splitter is None:
            splitter = DocumentSplitter(split_by="passage", split_length=100)
        if embedder is None:
            embedder = SentenceTransformersDocumentEmbedder(model="TaylorAI/bge-micro-v2")
        if retriever is None:
            retriever = InMemoryEmbeddingRetriever(document_store=database)
        if writer is None:
            writer = DocumentWriter(document_store=database, policy="overwrite")
        self.synthesizer = synthesizer
        self.database = database
        self.cleaner = cleaner
        self.splitter = splitter
        self.embedder = embedder
        self.retriever: InMemoryEmbeddingRetriever = retriever
        self.writer = writer
        self.init_file_pipeline()
        self.init_str_pipeline()
        atexit.register(self.write_to_disk)

    def init_file_pipeline(self):
        self.file_pipeline = Pipeline()
        _file_type_router = FileTypeRouter(mime_types=["text/plain", "application/pdf", "text/markdown"])
        _text_file_converter = TextFileToDocument()
        _markdown_converter = MarkdownToDocument()
        _pdf_converter = PyPDFToDocument()
        _document_joiner = DocumentJoiner()
        _document_writer = DocumentWriter(self.database)
        self.file_pipeline.add_component(instance=_file_type_router, name="file_type_router")
        self.file_pipeline.add_component(instance=_text_file_converter, name="text_file_converter")
        self.file_pipeline.add_component(instance=_markdown_converter, name="markdown_converter")
        self.file_pipeline.add_component(instance=_pdf_converter, name="pypdf_converter")
        self.file_pipeline.add_component(instance=_document_joiner, name="document_joiner")
        self.file_pipeline.add_component(instance=_document_writer, name="document_writer")
        self.file_pipeline.connect("file_type_router.text/plain", "text_file_converter.sources")
        self.file_pipeline.connect("file_type_router.application/pdf", "pypdf_converter.sources")
        self.file_pipeline.connect("file_type_router.text/markdown", "markdown_converter.sources")
        self.file_pipeline.connect("text_file_converter", "document_joiner")
        self.file_pipeline.connect("pypdf_converter", "document_joiner")
        self.file_pipeline.connect("markdown_converter", "document_joiner")
        self.file_pipeline.connect("document_joiner", "document_writer")

    def init_str_pipeline(self):
        self.str_pipeline = Pipeline()
        self.str_pipeline.add_component(instance=self.cleaner, name="document_cleaner")
        self.str_pipeline.add_component(instance=self.splitter, name="document_splitter")
        self.str_pipeline.add_component(instance=self.embedder, name="document_embedder")
        self.str_pipeline.add_component(instance=self.writer, name="document_writer")
        self.str_pipeline.connect("document_cleaner", "document_splitter")
        self.str_pipeline.connect("document_splitter", "document_embedder")
        self.str_pipeline.connect("document_embedder", "document_writer")

    def init_url_pipeline(self):
        raise NotImplementedError

    def write_to_disk(self):
        self.database.to_disk()

    @abstractmethod
    def search(self):
        pass
