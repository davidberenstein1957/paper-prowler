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

import json
from pathlib import Path
from typing import Any, Dict

from haystack import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore

from paper_prowler.constants import DATABASE_PATH


class Database(InMemoryDocumentStore):
    def to_disk(self, path: str = DATABASE_PATH):
        data: Dict[str, Any] = self.to_dict()
        data["documents"] = [doc.to_dict(flatten=False) for doc in self.storage.values()]
        with open(path, "w") as f:
            json.dump(data, f)

    @classmethod
    def from_disk(cls, path: str = DATABASE_PATH) -> "Database":
        if Path(path).exists():
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                cls_object = cls.from_dict(data)
                cls_object.write_documents([Document(**doc) for doc in data["documents"]])
                return cls_object
            except Exception as e:
                print(e)
                return cls()
        else:
            return cls()
