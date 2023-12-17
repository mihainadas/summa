import summa.processors as processors
from summa.llms import OpenAI, Meta, DeepInfra, MistralAI
from summa.llms import ModelVersion
from summa.evals import f1_score_chars, f1_score_words

import concurrent.futures


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
    for o in sorted_outputs:
        f1_chars = f1_score_chars(original_text, o.output)
        f1_words = f1_score_words(original_text, o.output)
        print(
            f"{o.model_version:<50} {o.prompt_template:<50} f1_chars={f1_chars:.6f}, f1_words={f1_words:.6f}"
        )


# Modify the restore_diacritics function to accept model and prompt_template as arguments
def restore_diacritics(input, model, prompt_template):
    output = processors.restore_diacritics(input, model, prompt_template)
    return output


def run_restore_diacritics(input):
    restored_outputs = []
    models = [
        OpenAI(model_version=ModelVersion.OPENAI_GPT_3_5_TURBO),
        OpenAI(model_version=ModelVersion.OPENAI_GPT_4),
        Meta(model_version=ModelVersion.META_LLAMA_2_70B_CHAT_HF),
        Meta(model_version=ModelVersion.META_LLAMA_2_7B_CHAT_HF),
        DeepInfra(model_version=ModelVersion.DEEPINFRA_AIROPOROS_70B),
        MistralAI(model_version=ModelVersion.MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1),
    ]

    prompt_templates = [
        "restore_diacritics.md",
        "restore_diacritics_verbose.md",
        "restore_diacritics_verbose_1s.md",
        "restore_diacritics_verbose_2s.md",
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit restore_diacritics tasks to the executor
        futures = [
            executor.submit(restore_diacritics, input, model, prompt_template)
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
