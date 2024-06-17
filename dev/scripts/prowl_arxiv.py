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
from paper_prowler.constants import QUERIES_ARXIV
from paper_prowler.prowlers import ArxivProwler


def load_data():
    results = []
    print("Loading ArxivProwler")
    arxiv_prowler = ArxivProwler()
    print("Running search and indexing results")
    for query in QUERIES_ARXIV:
        results = arxiv_prowler.search(query, max_results=10)
        arxiv_prowler.post_process(results, query, synthesize=True)
    print("Data updated successfully!")


load_data()
