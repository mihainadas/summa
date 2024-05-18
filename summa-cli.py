import json
import os
from summa.preprocessors import TextPreprocessors
from summa.processors import TextProcessors
from summa.llms import TextGenerationLLMs, Prompt, PromptTemplate
from summa.evals import Evaluators
from summa.pipelines import PipelineRunner, PipelineRunOutput

import concurrent.futures
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

preprocessor = TextPreprocessors.STRIP_DIACRITICS.value
processor = TextProcessors.EXPONENTIAL_BACKOFF.value
llms = [
    TextGenerationLLMs.META_LLAMA_3_70B_INSTRUCT.value,
    TextGenerationLLMs.GOOGLE_GEMINI_1_0_PRO.value,
    TextGenerationLLMs.GOOGLE_GEMINI_1_5_PRO.value,
]
prompt_templates = [
    # PromptTemplate(template_filename="restore_diacritics.md"),
    # PromptTemplate(template_filename="restore_diacritics_verbose.md"),
    # PromptTemplate(template_filename="restore_diacritics_verbose_1s.md"),
    PromptTemplate(template_filename="restore_diacritics_verbose_3s.md"),
]
evaluators = [
    # Evaluators.F1_SCORE_WORDS.value,
    Evaluators.RER_CI_CL.value
]

runner = PipelineRunner(preprocessor, processor, llms, prompt_templates, evaluators)
raw_texts = []

json_crawler = "../summa-data/dexonline/crawler/json/dexonline_crawler_10.json"
with open(json_crawler, "r") as f:
    json_data = json.load(f)
    raw_texts = [d["text"] for d in json_data]

run_outputs = []
for raw_text in raw_texts:
    print(f"Processing '{raw_text}'", end="... ")
    run_output = runner.run(raw_text)
    print("Done.")
    run_outputs.append(run_output)

# average evaluation scores by model
model_scores = {}
for run_output in run_outputs:
    for output in run_output.processed_outputs:
        model_scores.setdefault(output.model_version, []).append(output.evals[0].score)
for model_version, scores in model_scores.items():
    print(f"{model_version}: {sum(scores) / len(scores):.4f}")
