import openai
import google.generativeai as genai
import logging
import time
import os
from abc import ABC, abstractmethod
from decouple import config
from enum import Enum

logger = logging.getLogger(__name__)


class PromptTemplate:
    """
    A class for storing a prompt template and its keyword arguments.
    """

    def __init__(self, template=None, template_filename=None, prompts_dir="prompts"):
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
            self._set_template_from_file(template_filename, prompts_dir=prompts_dir)
        else:
            raise ValueError("Prompt template or template filename must be specified")

    def _set_template_from_file(self, template_filename, prompts_dir):
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


class TextGenerationLLM(ABC):
    def __init__(self, model, model_version):
        self.model = model
        self.model_version = model_version.value

    def __str__(self):
        return f"{self.model_version} ({self.model})"

    @abstractmethod
    def generate(self, prompt: Prompt) -> "TextGenerationOutput":
        pass


class TextGenerationOutput:
    def __init__(self, model: TextGenerationLLM, model_version, prompt: Prompt):
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
        self.evals = None

    def __str__(self):
        return f"{self.model} - {self.model_version} - {self.prompt_template_filename}: {self.output} ({self.generation_time} seconds)"

    def measure_generation_time(self):
        self.generation_time = time.time() - self._generation_time_start


class Summa(TextGenerationLLM):
    class ModelVersions(Enum):
        SUMMA_ECHO = "summa-echo"

    def __init__(self, model_version=ModelVersions.SUMMA_ECHO):
        super().__init__("Summa", model_version)

    def generate(self, prompt):
        if self.model_version != Summa.ModelVersions.SUMMA_ECHO.value:
            raise ValueError(
                f"Invalid model version for Summa: {self.model_version}. Expected: {self.ModelVersions.SUMMA_ECHO.value}"
            )
        output = TextGenerationOutput(
            model=self.model, model_version=self.model_version, prompt=prompt
        )
        # Return the prompt input as the output, effectively echoing it (used for baseline comparison)
        output.output = "\n".join(prompt.kwargs.values())
        output.measure_generation_time()
        return output


class OpenAIClient(TextGenerationLLM):
    def __init__(self, model, model_version, api_key, base_url=None):
        if base_url is None:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        super().__init__(model, model_version)

    def generate(self, prompt):
        try:
            output = TextGenerationOutput(
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
            logger.error(
                f"Error occurred during text generation: {str(e)} (Model: {self.model}, Model Version: {self.model_version})"
            )
            raise e


class DeepInfraClient(OpenAIClient):
    def __init__(self, model, model_version):
        api_key = config("DEEPINFRA_API_KEY", default="None")
        super().__init__(
            model,
            model_version,
            api_key,
            base_url="https://api.deepinfra.com/v1/openai",
        )


class GoogleAIClient(TextGenerationLLM):
    def __init__(self, model, model_version, api_key):
        genai.configure(api_key=api_key)
        super().__init__(model, model_version)

    def generate(self, prompt):
        try:
            output = TextGenerationOutput(
                model=self.model, model_version=self.model_version, prompt=prompt
            )

            # Setting up the model
            generation_config = {
                "temperature": 0.0,
            }
            safety_settings = {}
            for harm_category in genai.types.HarmCategory:
                if not harm_category in [
                    genai.types.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
                    genai.types.HarmCategory.HARM_CATEGORY_DEROGATORY,
                    genai.types.HarmCategory.HARM_CATEGORY_TOXICITY,
                    genai.types.HarmCategory.HARM_CATEGORY_VIOLENCE,
                    genai.types.HarmCategory.HARM_CATEGORY_SEXUAL,
                    genai.types.HarmCategory.HARM_CATEGORY_MEDICAL,
                    genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS,
                ]:
                    safety_settings[harm_category] = (
                        genai.types.HarmBlockThreshold.BLOCK_NONE
                    )
            # Generate text using the Google chat completions API, stripping whitespace
            response = genai.GenerativeModel(self.model_version).generate_content(
                prompt.prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )
            output.output = response.text.strip()
            # Calculate the time it took to generate it
            output.measure_generation_time()
            return output
        except Exception as e:
            logger.error(
                f"Unexpected error during text generation: {str(e)} (Model: {self.model}, Model Version: {self.model_version}, Prompt Feedback: {response.prompt_feedback if response.prompt_feedback else 'N/A'}, Prompt: {prompt.prompt})"
            )
            raise e


class OpenAI(OpenAIClient):
    class ModelVersions(Enum):
        GPT_3_5_TURBO = "gpt-3.5-turbo"
        GPT_4 = "gpt-4"
        GPT_4_TURBO = "gpt-4-turbo"
        GPT_4o = "gpt-4o"

    def __init__(self, model_version=ModelVersions.GPT_4o):
        api_key = config("OPENAI_API_KEY", default="None")
        super().__init__("OpenAI", model_version, api_key)


class Meta(DeepInfraClient):
    class ModelVersions(Enum):
        META_LLAMA_2_7B_CHAT_HF = "meta-llama/Llama-2-7b-chat-hf"
        META_LLAMA_2_70B_CHAT_HF = "meta-llama/Llama-2-70b-chat-hf"
        META_LLAMA_3_8B_INSTRUCT = "meta-llama/Meta-Llama-3-8B-Instruct"
        META_LLAMA_3_70B_INSTRUCT = "meta-llama/Meta-Llama-3-70B-Instruct"

    def __init__(self, model_version=ModelVersions.META_LLAMA_3_70B_INSTRUCT):
        super().__init__("Meta", model_version)


class DeepInfra(DeepInfraClient):
    class ModelVersions(Enum):
        DEEPINFRA_AIROBOROS_70B = "deepinfra/airoboros-70b"

    def __init__(self, model_version=ModelVersions.DEEPINFRA_AIROBOROS_70B):
        super().__init__("DeepInfra", model_version)


class MistralAI(DeepInfraClient):
    class ModelVersions(Enum):
        MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1 = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    def __init__(
        self, model_version=ModelVersions.MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1
    ):
        super().__init__("MistralAI", model_version)


class OpenLLMRO(DeepInfraClient):
    class ModelVersions(Enum):
        OPENLLMRO_ROLLAMA_2_7B_CHAT_V1 = "mihainadas/RoLlama2-7b-Chat-v1"

    def __init__(self, model_version=ModelVersions.OPENLLMRO_ROLLAMA_2_7B_CHAT_V1):
        super().__init__("OpenLLM-Ro", model_version)


class Google(GoogleAIClient):
    class ModelVersions(Enum):
        GEMINI_1_0_PRO = "gemini-1.0-pro-latest"
        GEMINI_1_5_PRO = "gemini-1.5-pro-latest"
        GEMINI_1_5_FLASH = "gemini-1.5-flash-latest"

    def __init__(self, model_version):
        api_key = config("GCP_API_KEY", default="None")
        super().__init__("Google", model_version, api_key)


class TextGenerationLLMs(Enum):
    SUMMA_ECHO = Summa()

    OPENAI_GPT_3_5_TURBO = OpenAI(model_version=OpenAI.ModelVersions.GPT_3_5_TURBO)
    OPENAI_GPT_4 = OpenAI(model_version=OpenAI.ModelVersions.GPT_4)
    OPENAI_GPT_4_TURBO = OpenAI(model_version=OpenAI.ModelVersions.GPT_4_TURBO)
    OPENAI_GPT_4o = OpenAI(model_version=OpenAI.ModelVersions.GPT_4o)

    GOOGLE_GEMINI_1_0_PRO = Google(model_version=Google.ModelVersions.GEMINI_1_0_PRO)
    GOOGLE_GEMINI_1_5_PRO = Google(model_version=Google.ModelVersions.GEMINI_1_5_PRO)
    GOOGLE_GEMINI_1_5_FLASH = Google(
        model_version=Google.ModelVersions.GEMINI_1_5_FLASH
    )

    META_LLAMA_2_7B_CHAT_HF = Meta(
        model_version=Meta.ModelVersions.META_LLAMA_2_7B_CHAT_HF
    )
    META_LLAMA_2_70B_CHAT_HF = Meta(
        model_version=Meta.ModelVersions.META_LLAMA_2_70B_CHAT_HF
    )
    META_LLAMA_3_8B_INSTRUCT = Meta(
        model_version=Meta.ModelVersions.META_LLAMA_3_8B_INSTRUCT
    )
    META_LLAMA_3_70B_INSTRUCT = Meta(
        model_version=Meta.ModelVersions.META_LLAMA_3_70B_INSTRUCT
    )

    DEEPINFRA_AIROBOROS_70B = DeepInfra()

    MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V0_1 = MistralAI()

    OPENLLMRO_ROLLAMA_2_7B_CHAT_V1 = OpenLLMRO()
