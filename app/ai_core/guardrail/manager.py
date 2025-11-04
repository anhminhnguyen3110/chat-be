from app.ai_core.guardrail.content_guardrail import ContentGuardrail
from app.config.settings import settings
from app.types import GuardrailValidationResult


class GuardrailManager:
    def __init__(self):
        self.enabled = settings.ENABLE_GUARDRAIL
        self.guardrails = [
            ContentGuardrail()
        ]
    
    async def validate_input(self, input_text: str) -> GuardrailValidationResult:
        if not self.enabled:
            return {
                "is_safe": True,
                "blocked": False,
                "reason": None
            }
        
        for guardrail in self.guardrails:
            result = await guardrail.validate_input(input_text)
            if not result.get("is_safe", True):
                return result
        
        return {
            "is_safe": True,
            "blocked": False,
            "reason": None
        }
    
    async def validate_output(self, output_text: str) -> GuardrailValidationResult:
        if not self.enabled:
            return {
                "is_safe": True,
                "blocked": False,
                "reason": None
            }
        
        for guardrail in self.guardrails:
            result = await guardrail.validate_output(output_text)
            if not result["valid"]:
                return result
        
        return {
            "valid": True,
            "reason": None,
            "blocked": False
        }


guardrail_manager = GuardrailManager()
