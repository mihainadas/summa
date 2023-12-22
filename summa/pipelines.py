from typing import List
import concurrent.futures
from .preprocessors import TextPreprocessor
from .processors import TextProcessor
from .llms import TextGenerationModel, ModelOutput, PromptTemplate, Prompt
from .evals import Evaluator, EvaluatorOutput


class PipelineRunOutput:
    def __init__(
        self,
        raw_text: str,
        preprocessed_text: str,
        processed_outputs: List[ModelOutput],
        evaluated_outputs: List[EvaluatorOutput],
    ):
        self.raw_text = raw_text
        self.preprocessed_text = preprocessed_text
        self.processed_outputs = processed_outputs
        self.evaluated_outputs = evaluated_outputs


class PipelineRunner:
    def __init__(
        self,
        preprocessor: TextPreprocessor,
        processor: TextProcessor,
        llms: List[TextGenerationModel],
        prompt_templates: List[PromptTemplate],
        evaluators: List[Evaluator],
    ):
        self.preprocessor = preprocessor
        self.processor = processor
        self.llms = llms
        self.prompt_templates = prompt_templates
        self.evaluators = evaluators

    def _preprocess(self, raw_text: str) -> str:
        return self.preprocessor.preprocess(raw_text)

    def _process(self, preprocessed_text: str) -> List[ModelOutput]:
        processed_outputs = []
        for model in self.llms:
            for prompt_template in self.prompt_templates:
                prompt = Prompt(prompt_template, preprocessed_text)
                processed_outputs.append(self.processor.process(model, prompt))
        return processed_outputs

    def _process_parallel(self, preprocessed_text: str) -> List[ModelOutput]:
        processed_outputs = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit process tasks to the executor
            futures = [
                executor.submit(self.processor.process, model, prompt)
                for model in self.llms
                for prompt_template in self.prompt_templates
                for prompt in [Prompt(prompt_template, preprocessed_text)]
            ]

            # Retrieve the results as they become available
            for future in concurrent.futures.as_completed(futures):
                output = future.result()
                processed_outputs.append(output)
        return processed_outputs

    def _evaluate(
        self, raw_text: str, processed_outputs: List[ModelOutput]
    ) -> List[EvaluatorOutput]:
        for output in processed_outputs:
            evaluated_outputs = []
            for evaluator in self.evaluators:
                evaluator_output = EvaluatorOutput(
                    evaluator, evaluator.evaluate(raw_text, output.output)
                )
                evaluated_outputs.append(evaluator_output)
            output.evaluator_outputs = evaluated_outputs

    def run(self, raw_text: str, sequential=False) -> PipelineRunOutput:
        preprocessed_text = self._preprocess(raw_text)
        if sequential:
            processed_outputs = self._process(preprocessed_text)
        else:
            processed_outputs = self._process_parallel(preprocessed_text)
        evaluated_outputs = self._evaluate(raw_text, processed_outputs)
        return PipelineRunOutput(
            raw_text, preprocessed_text, processed_outputs, evaluated_outputs
        )
