from abc import ABC, abstractmethod

from app.types import GuardrailValidationResult


class BaseGuardrail(ABC):
    @abstractmethod
    async def validate_input(self, input_text: str) -> GuardrailValidationResult:
        pass
    
    @abstractmethod
    async def validate_output(self, output_text: str) -> GuardrailValidationResult:
        pass
