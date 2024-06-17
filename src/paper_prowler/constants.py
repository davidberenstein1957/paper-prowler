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

import os
from pathlib import Path

DATABASE_DIRECTORY = os.getenv("DATABASE_DIRECTORY", Path(__file__).parent.parent / "data")
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(DATABASE_DIRECTORY, "database.json"))

QUERIES_ARXIV = [
    "synthetic data generation llms",
    "LLMs as judges",
    "data quality for LLMs",
    "human feedback LLMs",
    "LLM benchmarking and evaluation",
]

QUERIES_RSS = [
    "https://hnrss.org/frontpage?q=python+OR+llm+OR+synthetic+OR+ai+OR+openai+OR+mistral+OR+hugging+face",
    #    "LLMs as judges",
    #    "data quality for LLMs",
    #    "human feedback LLMs",
]
