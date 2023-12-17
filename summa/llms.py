import openai
import logging
import time
from abc import ABC, abstractmethod
from decouple import config
from enum import Enum


class ModelVersion(Enum):
    OPENAI_GPT_3_5_TURBO = "gpt-3.5-turbo"
    OPENAI_GPT_4 = "gpt-4"
    META_LLAMA_2_70B_CHAT_HF = "meta-llama/Llama-2-70b-chat-hf"
    META_LLAMA_2_7B_CHAT_HF = "meta-llama/Llama-2-7b-chat-hf"
    DEEPINFRA_AIROPOROS_70B = "deepinfra/airoboros-70b"
    MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1 = "mistralai/Mixtral-8x7B-Instruct-v0.1"


class ModelOutput:
    def __init__(self, model, model_version: ModelVersion, prompt):
        self.model = model
        self.model_version = model_version
        self.prompt_template = prompt.prompt_template
        self.prompt_template_path = prompt.prompt_template_path
        self.prompt = prompt
        self.output = None
        self.generation_time = None
        self._generation_time_start = time.time()

    def __str__(self):
        return f"{self.model} - {self.model_version} - {self.prompt_template_path}: {self.output} ({self.generation_time} seconds)"

    def measure_generation_time(self):
        self.generation_time = time.time() - self._generation_time_start


class TextGeneration(ABC):
    def __init__(self, model, model_version: ModelVersion):
        self.model = model
        self.model_version = model_version.value

    @abstractmethod
    def generate(self, text: str) -> ModelOutput:
        pass


class OpenAIClient(TextGeneration):
    def __init__(self, model, model_version, api_key, base_url=None):
        if base_url is None:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        super().__init__(model, model_version)

    def generate(self, prompt):
        try:
            output = ModelOutput(
                model=self.model, model_version=self.model_version, prompt=prompt
            )
            # Generate text using the OpenAI chat completions API
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": str(prompt)}],
                model=self.model_version,
                temperature=0,
            )
            # Return the first choice (the best one), stripped of whitespace
            output.output = completion.choices[0].message.content.strip()
            # Store the output and the time it took to generate it
            output.measure_generation_time()
            return output
        except Exception as e:
            logging.error(f"Error occurred during text generation: {str(e)}")
            return None


class DeepInfraClient(OpenAIClient):
    def __init__(self, model, model_version):
        api_key = config("DEEPINFRA_API_KEY")
        super().__init__(
            model,
            model_version,
            api_key,
            base_url="https://api.deepinfra.com/v1/openai",
        )


class OpenAI(OpenAIClient):
    def __init__(self, model_version=ModelVersion.OPENAI_GPT_3_5_TURBO):
        api_key = config("OPENAI_API_KEY")
        super().__init__("OpenAI", model_version, api_key)


class Meta(DeepInfraClient):
    def __init__(self, model_version=ModelVersion.META_LLAMA_2_70B_CHAT_HF):
        super().__init__("Meta", model_version)


class DeepInfra(DeepInfraClient):
    def __init__(self, model_version=ModelVersion.DEEPINFRA_AIROPOROS_70B):
        super().__init__("DeepInfra", model_version)


class MistralAI(DeepInfraClient):
    def __init__(self, model_version=ModelVersion.MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1):
        super().__init__("MistralAI", model_version)
