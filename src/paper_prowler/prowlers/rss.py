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
import feedparser
from haystack import Document
from haystack.components.fetchers import LinkContentFetcher

from paper_prowler.prowlers.base import Prowler

fetcher = LinkContentFetcher()


class RssProwler(Prowler):
    type = "rss"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def search(self, query: str = None) -> list[arxiv.Result]:
        return feedparser.parse(query)

    def post_process(
        self, results: list[arxiv.Result], query: Optional[str] = "", synthesize: Optional[bool] = False
    ) -> None:
        # The `results` variable in the provided code snippet is being used to store the parsed
        # results obtained from an RSS feed based on the query provided. These results are then
        # processed further in the `post_process` method of the `RssProwler` class.
        results["entries"] = [
            result for result in results["entries"] if hash(result["title"]) not in self.database.storage
        ]
        if synthesize:
            instructions = [f"instruction:\n{result.summary} \n\nurl:\n{result.entry_id}" for result in results]
            linkedin_posts = self.synthesizer.synthesize(instructions, platform="LinkedIn", content="abstract")
            x_posts = self.synthesizer.synthesize(instructions, platform="Twitter", content="abstract")
        else:
            linkedin_posts = ["" for _ in results]
            x_posts = linkedin_posts

        docs = [
            Document(
                id=hash(result["title"]),
                content=result["summary"],
                meta={
                    "type": self.type,
                    "url": result["id"],
                    "title": result["title"],
                    "content": fetcher.run(urls=[result["link"]])["streams"][0]
                    .to_string()
                    .split("</main>")[0]
                    .split("<main>")[-1],
                    "datetime": results["updated_parsed"],
                    "query": query,
                    "linkedin:": li_post,
                    "x": x_post,
                },
            )
            for li_post, x_post, result in zip(linkedin_posts, x_posts, results["entries"])
        ]

        self.str_pipeline.run({"document_cleaner": {"documents": docs}})
