"""Chat agent for fast general conversation."""

from typing import Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.ai_core.agents.base import BaseAgent
from app.ai_core.llm.llm_factory import LLMFactory, LLMProviderType
from app.ai_core.agents.chat_agent.state import ChatAgentState
from app.config.settings import settings
from app.types import AgentConfig, NodeReturnType


class ChatAgent(BaseAgent):
    """
    Simple chat agent for fast responses.
    
    This agent is optimized for speed:
    - No Think/Plan tools (immediate response)
    - Single LLM node
    - Minimal processing overhead
    
    Use for:
    - General conversation
    - Simple Q&A
    - Quick responses
    """
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None
    ):
        """
        Initialize Chat Agent.
        
        Args:
            config: Optional configuration dict
        """
        config = config or {}
        
        self.llm = LLMFactory.create(
            provider_type=LLMProviderType(config.get("llm_provider", settings.LLM_PROVIDER)),
            model=config.get("model", settings.LLM_MODEL),
            temperature=config.get("temperature", settings.LLM_TEMPERATURE),
            max_tokens=config.get("max_tokens", settings.LLM_MAX_TOKENS),
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            enable_guardrail=config.get("enable_guardrail", False),  # Disable by default for chat
        )
        
        super().__init__(agent_type="chat", config=config)
    
    async def execute(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        history: Optional[list] = None,
        system_prompt: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> NodeReturnType:
        """
        Execute chat agent with system prompt support.
        
        Args:
            query: User query
            session_id: Session ID for checkpointer (NEW)
            user_id: User ID for tracking (NEW)
            history: Conversation history (legacy, will be deprecated)
            system_prompt: System prompt for the LLM
            metadata: Additional metadata
            
        Returns:
            Agent response
        """
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        if history:
            for msg in history:
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg.get("role") == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=query))
        
        state: ChatAgentState = {
            "messages": messages,
            "session_id": session_id,
            "system_prompt": system_prompt,
            "metadata": metadata or {},
        }
        
        config = self._build_graph_config(
            session_id=session_id,
            user_id=user_id,
            metadata=metadata
        )
        
        return await self._execute_internal(state, config)
    
    def _build_graph(self) -> StateGraph:
        """
        Build simple chat graph.
        
        Graph: chat_node → END
        
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(ChatAgentState)
        
        workflow.add_node("chat", self._chat_node)
        
        workflow.set_entry_point("chat")
        workflow.add_edge("chat", END)
        
        return workflow.compile()
    
    async def _chat_node(self, state: ChatAgentState) -> NodeReturnType:
        """
        Chat node - generate response.
        
        Args:
            state: Current chat state
            
        Returns:
            Updated state with AI message added
        """
        self.logger.info("Executing chat node")
        
        try:
            messages = state.get("messages", [])
            
            if not messages:
                raise ValueError("No messages in state")
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "messages": [response],
                "error": None
            }
            
        except Exception as e:
            self.logger.error(f"Chat node error: {str(e)}", exc_info=True)
            
            error_msg = AIMessage(
                content="I apologize, but I encountered an error. Please try again."
            )
            return {
                "messages": [error_msg],
                "error": str(e)
            }
