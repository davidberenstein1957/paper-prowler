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

from typing import List

from distilabel.llms import LLM, OpenAILLM
from distilabel.steps.tasks import TextGeneration


class Synthesizer:
    def __init__(self, llm: LLM = None, system_prompt: str = None):
        if system_prompt is None:
            system_prompt = (
                "You are an expert social media expert for a tech company in the field of AI, NLP and LLMs. "
                "Write a post for PLATFORM based on the following CONTENT. "
                "Make sure to include the exact URL and make it concise and catchy without hashtags."
            )
        if llm is None:
            llm = OpenAILLM(model="gpt-3.5-turbo")
        self.system_prompt = system_prompt
        self.task = TextGeneration(llm=llm)
        self.task.load()

    def synthesize(self, instructions: List[str], platform: str, content: str) -> List[str]:
        results = next(
            self.task.process(
                [
                    {
                        "instruction": instruction,
                        "system_prompt": self.system_prompt.replace("PLATFORM", platform).replace("CONTENT", content),
                    }
                    for instruction in instructions
                ]
            )
        )
        return [result["generation"] for result in results]
