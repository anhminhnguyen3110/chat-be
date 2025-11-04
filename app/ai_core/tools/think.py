"""Think tool for analytical reasoning."""

from langchain_core.messages import HumanMessage

from app.ai_core.tools.base import BaseTool
from app.ai_core.llm import LLMFactory, LLMProviderType
from app.ai_core.prompts.tool_prompts import get_think_prompt
from app.config.settings import settings
from app.types import ToolParams, ToolResult


class ThinkTool(BaseTool):
    """Think tool for step-by-step analytical reasoning."""
    
    @property
    def name(self) -> str:
        return "think"
    
    @property
    def description(self) -> str:
        return "Think through a problem step by step before taking action"
    
    async def execute(self, params: ToolParams) -> ToolResult:
        """Execute thinking process."""
        prompt = params.get("prompt", "")
        
        if not prompt:
            return {
                "result": "No prompt provided",
                "tool": self.name,
                "error": "Missing prompt parameter"
            }
        
        llm = LLMFactory.create(
            provider_type=LLMProviderType(settings.LLM_PROVIDER),
            model=settings.LLM_MODEL,
            temperature=0.3,
            max_tokens=settings.LLM_MAX_TOKENS,
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            enable_guardrail=False
        )
        
        think_prompt = get_think_prompt(prompt)
        
        response = await llm.ainvoke([HumanMessage(content=think_prompt)])
        
        return {
            "result": response.content,
            "tool": self.name,
            "prompt_length": len(prompt),
            "response_length": len(response.content)
        }
