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

from typing import Optional

import arxiv
from haystack import Document

from paper_prowler.prowlers.base import Prowler


class ArxivProwler(Prowler):
    type = "arxiv"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = arxiv.Client()

    def search(
        self, query: str = None, max_results: int = 10, sort_by=arxiv.SortCriterion.Relevance
    ) -> list[arxiv.Result]:
        search = arxiv.Search(query=query, max_results=max_results, sort_by=sort_by)
        results = self.client.results(search)
        return list(results)

    def post_process(
        self, results: list[arxiv.Result], query: Optional[str] = "", synthesize: Optional[bool] = False
    ) -> None:
        results = [result for result in results if hash(result.title) not in self.database.storage]
        if synthesize:
            instructions = [f"instruction:\n{result.summary} \n\nurl:\n{result.entry_id}" for result in results]
            linkedin_posts = self.synthesizer.synthesize(instructions, platform="LinkedIn", content="abstract")
            x_posts = self.synthesizer.synthesize(instructions, platform="Twitter", content="abstract")
        else:
            linkedin_posts = ["" for _ in results]
            x_posts = linkedin_posts

        docs = [
            Document(
                id=hash(result.title),
                content=result.summary,
                meta={
                    "type": self.type,
                    "url": result.entry_id,
                    "title": result.title,
                    "content": result.pdf_url.replace("http://", "https://"),
                    "datetime": result.updated.strftime("%Y-%m-%d %H:%M:%S"),
                    "query": query,
                    "linkedin": li_post,
                    "x": x_post,
                },
            )
            for li_post, x_post, result in zip(linkedin_posts, x_posts, results)
        ]
        self.str_pipeline.run({"document_cleaner": {"documents": docs}})
