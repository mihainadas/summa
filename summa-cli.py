from summa.processors import RestoreDiacritics
from summa.llms import (
    PromptTemplate,
    Prompt,
    ModelVersions,
    OpenAI,
    Meta,
    DeepInfra,
    MistralAI,
)
from summa.evals import f1_score_chars, f1_score_words, ca_score_chars, ca_score_words

import concurrent.futures
import logging

log = logging.getLogger(__name__)


def eval(original_text, restored_outputs):
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
    rd = RestoreDiacritics(model)
    output = rd.process(Prompt(prompt_template, input))
    return output


def run_restore_diacritics(input):
    restored_outputs = []
    models = [
        OpenAI(model_version=ModelVersions.OPENAI_GPT_3_5_TURBO),
        OpenAI(model_version=ModelVersions.OPENAI_GPT_4),
        Meta(model_version=ModelVersions.META_LLAMA_2_70B_CHAT_HF),
        Meta(model_version=ModelVersions.META_LLAMA_2_7B_CHAT_HF),
        DeepInfra(model_version=ModelVersions.DEEPINFRA_AIROBOROS_70B),
        MistralAI(model_version=ModelVersions.MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1),
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


original_text = (
    "Mâine, când răsare soarele, voi mânca un măr și voi înghiți apă sifonată."
)
input_text = "Maine, cand rasare soarele, voi manca un mar si voi inghiti apa sifonata."

eval(original_text, run_restore_diacritics(input_text))
