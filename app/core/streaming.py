from typing import AsyncGenerator
import asyncio
import json


class StreamingResponse:
    @staticmethod
    async def stream_generator(
        content: AsyncGenerator[dict[str, any], None]
    ) -> AsyncGenerator[str, None]:
        """
        Convert StreamChunk dicts to SSE format.
        
        Args:
            content: AsyncGenerator yielding StreamChunk dicts
            
        Yields:
            SSE formatted strings: "data: {...}\n\n"
        """
        async for chunk in content:
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0)

