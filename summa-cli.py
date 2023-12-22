import json
import os
from summa.preprocessors import TextPreprocessors
from summa.processors import TextProcessors
from summa.llms import Models, Prompt, PromptTemplate
from summa.evals import Evaluators
from summa.pipelines import PipelineRunner, PipelineRunOutput

import concurrent.futures
import logging

log = logging.getLogger(__name__)


def eval(original_text, restored_outputs):
    f1_score_chars = Evaluators.F1_SCORE_CHARS.value.evaluate
    f1_score_words = Evaluators.F1_SCORE_WORDS.value.evaluate
    ca_score_chars = Evaluators.CHARACTER_ACCURACY.value.evaluate
    ca_score_words = Evaluators.WORD_ACCURACY.value.evaluate

    sorted_outputs = sorted(
        restored_outputs,
        key=lambda o: (
            f1_score_words(original_text, o.output),
            o.model_version,
            o.prompt_template,
        ),
        reverse=True,
    )
    for i, o in enumerate(sorted_outputs, start=1):
        f1_chars = f1_score_chars(original_text, o.output)
        f1_words = f1_score_words(original_text, o.output)
        ca_chars = ca_score_chars(original_text, o.output)
        ca_words = ca_score_words(original_text, o.output)
        gen_time = o.generation_time
        print(
            f"{i:>2}. {o.model_version:<50} {o.prompt_template_filename:<50} f1_chars={f1_chars:.2f}, f1_words={f1_words:.2f}, ca_score_chars={ca_chars:.2f}, ca_score_words={ca_words:.2f}, gen_time={gen_time:.2f}"
        )


# Modify the restore_diacritics function to accept model and prompt_template as arguments
def restore_diacritics(model, prompt_template, input):
    rd = TextProcessors.BASIC.value
    output = rd.process(model, Prompt(prompt_template, input))
    return output


def run_restore_diacritics(input):
    restored_outputs = []
    models = [
        Models.OPENAI_GPT_3_5_TURBO.value,
        Models.OPENAI_GPT_4.value,
        Models.META_LLAMA_2_70B_CHAT_HF.value,
        Models.META_LLAMA_2_7B_CHAT_HF.value,
        Models.DEEPINFRA_AIROBOROS_70B.value,
        Models.MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1.value,
    ]

    prompt_templates = [
        PromptTemplate(template_filename="restore_diacritics.md"),
        PromptTemplate(template_filename="restore_diacritics_verbose.md"),
        PromptTemplate(template_filename="restore_diacritics_verbose_1s.md"),
        PromptTemplate(template_filename="restore_diacritics_verbose_2s.md"),
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit restore_diacritics tasks to the executor
        futures = [
            executor.submit(restore_diacritics, model, prompt_template, input)
            for model in models
            for prompt_template in prompt_templates
        ]

        # Retrieve the results as they become available
        for future in concurrent.futures.as_completed(futures):
            output = future.result()
            restored_outputs.append(output)

    return restored_outputs


raw_text = "Mâine, când răsare soarele, voi mânca un măr și voi înghiți apă sifonată."
preprocessed_text = (
    "Maine, cand rasare soarele, voi manca un mar si voi inghiti apa sifonata."
)

# eval(raw_text, run_restore_diacritics(preprocessed_text))

preprocessor = TextPreprocessors.STRIP_DIACRITICS.value
processor = TextProcessors.BASIC.value
llms = [
    Models.OPENAI_GPT_3_5_TURBO.value,
    Models.OPENAI_GPT_4.value,
    # Models.META_LLAMA_2_70B_CHAT_HF.value,
    # Models.META_LLAMA_2_7B_CHAT_HF.value,
    Models.DEEPINFRA_AIROBOROS_70B.value,
    # Models.MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1.value,
]
prompt_templates = [
    # PromptTemplate(template_filename="restore_diacritics.md"),
    # PromptTemplate(template_filename="restore_diacritics_verbose.md"),
    # PromptTemplate(template_filename="restore_diacritics_verbose_1s.md"),
    PromptTemplate(template_filename="restore_diacritics_verbose_2s.md"),
]
evaluators = [
    # Evaluators.F1_SCORE_WORDS.value,
    Evaluators.F1_SCORE_WORDS_CASE_INSENSITIVE.value,
]

runner = PipelineRunner(preprocessor, processor, llms, prompt_templates, evaluators)
raw_texts = []

json_dlrlc = "data/dexonline/dlrlc/json/dexonline_dlrlc_10.json"
json_crawler = "data/dexonline/crawler/json/dexonline_crawler_10.json"
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
    print(f"{model_version}: {sum(scores) / len(scores):.2f}")
