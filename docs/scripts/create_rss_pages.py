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

import mkdocs_gen_files
import pandas as pd
from paper_prowler.database import Database

database = Database.from_disk()

DATA_PATH = "sections/rss"


def load_data() -> None:
    index_dict = {"id": [], "titles": [], "abstracts": [], "contents": [], "queries": [], "datetimes": []}
    for paper in database.storage.values():
        if paper.meta["type"] == "rss":
            index_dict["id"].append(paper.id)
            index_dict["titles"].append(f"{paper.meta['title']}")
            index_dict["abstracts"].append(paper.content.replace("\n", " "))
            index_dict["contents"].append(paper.meta["content"])
            index_dict["queries"].append(paper.meta["query"])
            index_dict["datetimes"].append(paper.meta["datetime"])
            paper_path = f"{DATA_PATH}/{hash(paper.meta['query'])}/{paper.id}.md"
            with mkdocs_gen_files.open(paper_path, "w") as f:
                f.write("---\n" "hide:\n" "- toc\n" "- navigation\n" "---\n")
                f.write(f"# {paper.meta['title']} \n")
                f.write(f"[Arxiv Link]({paper.meta['url']}) - {paper.meta['datetime']} \n")
                f.write("## Abstract \n")
                f.write(f"{paper.content} \n")
                f.write("## Socials \n")
                f.write("| LinkedIn | X |\n")
                f.write("|------|-------|\n")
                f.write(f"|{paper.meta.get('linkedin')}|{paper.meta.get('x')}|\n\n")
                f.write("## HTML\n")
                f.write(f"{paper.meta['content']}")

    df = pd.DataFrame(index_dict)
    with mkdocs_gen_files.open(f"{DATA_PATH}/index.md", "w") as f:
        f.write("---\n" "hide:\n" "- toc\n" "- navigation\n" "---\n")
        for _, query in enumerate(df["queries"].unique()):
            f.write(f'=== "{query}"\n\n')
            f.write("    | title | abstract |\n")
            f.write("    |------|-------|\n")
            filtered_df = df[df["queries"] == query]
            for _, row in filtered_df.iterrows():
                f.write(f"    | [{row['titles']}](./{hash(query)}/{row['id']}.md) | {row['abstracts']} |\n")

    with mkdocs_gen_files.open("SUMMARY.md", "a") as f:
        for query in df["queries"].unique():
            f.write("* RSS\n")
            f.write(f"    * [Overview]({DATA_PATH}/index.md)\n")
            f.write(f"    * {query}\n")
            filtered_df = df[df["queries"] == query]
            for _, row in filtered_df.iterrows():
                f.write(f"        * [{row['titles']}]({DATA_PATH}/{hash(query)}/{row['id']}.md)\n")


load_data()
