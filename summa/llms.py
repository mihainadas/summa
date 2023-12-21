import openai
import logging
import time
import os
from abc import ABC, abstractmethod
from decouple import config
from enum import Enum


class PromptTemplate:
    """
    A class for storing a prompt template and its keyword arguments.
    """

    def __init__(self, template=None, template_filename=None):
        """
        Initializes a PromptTemplate object.

        Args:
            template (str, optional): The prompt template string. Defaults to None.
            template_filename (str, optional): The filename of the prompt template file. Defaults to None.

        Raises:
            ValueError: If neither template nor template_filename is specified.
        """
        if template is not None:
            self.template = template
            self.template_filename = None
        elif template_filename is not None:
            self.template_filename = template_filename
            self._set_template_from_file(template_filename)
        else:
            raise ValueError("Prompt template or template filename must be specified")

    def _set_template_from_file(self, template_filename, prompts_dir="prompts"):
        """
        Sets the prompt template from a file.

        Args:
            prompt_template_filename (str): The filename of the prompt template file.
            prompts_dir (str, optional): The directory where the prompt template file is located. Defaults to "prompts".
        """
        # Get the directory of the current file
        module_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the prompt template file
        template_path = os.path.join(module_dir, prompts_dir, template_filename)

        with open(template_path, "r") as file:
            self.template = file.read()

        self.template_path = template_path

    def render(self, *args, **kwargs):
        """
        Renders the prompt by substituting keyword arguments in the template.

        Args:
            **kwargs: Keyword arguments to be substituted in the template.

        Returns:
            str: The rendered prompt string.
        """
        if self.template is None:
            return None

        # Check if only a single positional argument is provided and no keyword arguments
        if len(args) == 1 and not kwargs:
            kwargs = {"input": args[0]}

        return self.template.format(**kwargs)

    def __str__(self):
        """
        Returns the string representation of the PromptTemplate object.

        Returns:
            str: The string representation of the PromptTemplate object.
        """
        return self.template


class Prompt:
    def __init__(self, prompt_template: PromptTemplate, *args, **kwargs):
        self.prompt_template = prompt_template
        if len(args) == 1 and not kwargs:
            self.kwargs = {"input": args[0]}

    @property
    def prompt(self):
        return self.prompt_template.render(**self.kwargs)

    def __str__(self):
        return self.prompt


class ModelVersions(Enum):
    """
    Enum class representing different model versions.
    """

    OPENAI_GPT_3_5_TURBO = "gpt-3.5-turbo"
    OPENAI_GPT_4 = "gpt-4"
    META_LLAMA_2_70B_CHAT_HF = "meta-llama/Llama-2-70b-chat-hf"
    META_LLAMA_2_7B_CHAT_HF = "meta-llama/Llama-2-7b-chat-hf"
    DEEPINFRA_AIROBOROS_70B = "deepinfra/airoboros-70b"
    MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1 = "mistralai/Mixtral-8x7B-Instruct-v0.1"


class TextGenerationModel(ABC):
    def __init__(self, model, model_version: ModelVersions):
        self.model = model
        self.model_version = model_version.value

    @abstractmethod
    def generate(self, prompt: Prompt) -> "ModelOutput":
        pass


class ModelOutput:
    def __init__(
        self, model: TextGenerationModel, model_version: ModelVersions, prompt: Prompt
    ):
        self.model = model
        self.model_version = model_version
        self.prompt_template = prompt.prompt_template.template
        self.prompt_template_filename = prompt.prompt_template.template_filename
        self.prompt_template_path = prompt.prompt_template.template_path
        self.prompt = prompt.prompt
        self.prompt_kwargs = prompt.kwargs
        self.output = None
        self.generation_time = None
        self._generation_time_start = time.time()

    def __str__(self):
        return f"{self.model} - {self.model_version} - {self.prompt_template_path}: {self.output} ({self.generation_time} seconds)"

    def measure_generation_time(self):
        self.generation_time = time.time() - self._generation_time_start


class OpenAIClient(TextGenerationModel):
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
                messages=[{"role": "user", "content": prompt.prompt}],
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
    def __init__(self, model_version=ModelVersions.OPENAI_GPT_3_5_TURBO):
        api_key = config("OPENAI_API_KEY")
        super().__init__("OpenAI", model_version, api_key)


class Meta(DeepInfraClient):
    def __init__(self, model_version=ModelVersions.META_LLAMA_2_70B_CHAT_HF):
        super().__init__("Meta", model_version)


class DeepInfra(DeepInfraClient):
    def __init__(self, model_version=ModelVersions.DEEPINFRA_AIROBOROS_70B):
        super().__init__("DeepInfra", model_version)


class MistralAI(DeepInfraClient):
    def __init__(
        self, model_version=ModelVersions.MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1
    ):
        super().__init__("MistralAI", model_version)


class Models(Enum):
    OPENAI_GPT_3_5_TURBO = OpenAI(model_version=ModelVersions.OPENAI_GPT_3_5_TURBO)
    OPENAI_GPT_4 = OpenAI(model_version=ModelVersions.OPENAI_GPT_4)
    META_LLAMA_2_70B_CHAT_HF = Meta(
        model_version=ModelVersions.META_LLAMA_2_70B_CHAT_HF
    )
    META_LLAMA_2_7B_CHAT_HF = Meta(model_version=ModelVersions.META_LLAMA_2_7B_CHAT_HF)
    DEEPINFRA_AIROBOROS_70B = DeepInfra(
        model_version=ModelVersions.DEEPINFRA_AIROBOROS_70B
    )
    MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1 = MistralAI(
        model_version=ModelVersions.MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1
    )
