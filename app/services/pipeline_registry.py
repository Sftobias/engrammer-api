from typing import Dict, Callable, List
from dataclasses import dataclass

@dataclass
class RegisteredPipeline:
    id: str
    name: str
    description: str
    factory: Callable[[], object]

class PipelineRegistry:
    def __init__(self):
        self._registry: Dict[str, RegisteredPipeline] = {}

    def register(self, pipe: RegisteredPipeline):
        if pipe.id in self._registry:
            raise ValueError(f"Pipeline id already registered: {pipe.id}")
        self._registry[pipe.id] = pipe

    def get(self, pipeline_id: str) -> RegisteredPipeline:
        if pipeline_id not in self._registry:
            raise KeyError(f"Unknown pipeline: {pipeline_id}")
        return self._registry[pipeline_id]

    def list(self) -> List[RegisteredPipeline]:
        return list(self._registry.values())

PIPELINES = PipelineRegistry()
