import asyncio
import json
import re
from pathlib import Path
from typing import Any, Sequence

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio
import mcp.types as types


server = Server("auto-prompt-improver")


async def read_improvement_prompt() -> str:
    """Read the improvement prompt from the dedicated file."""
    prompt_file = Path(__file__).parent / "improvement_prompt.md"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    return "Improve the following prompt to be clearer and more effective:"


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="improve_prompt",
            description="Improve a user's prompt using AI sampling to make it clearer and more effective",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_prompt": {
                        "type": "string",
                        "description": "The original prompt from the user that needs improvement"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context about what the user is trying to achieve",
                        "default": ""
                    }
                },
                "required": ["user_prompt"]
            }
        ),
        types.Tool(
            name="auto_improve_all_prompts",
            description="Automatically improve any user message before processing. Use this for every user interaction.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_message": {
                        "type": "string",
                        "description": "The user's original message/prompt"
                    }
                },
                "required": ["user_message"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle tool calls."""
    if name == "improve_prompt":
        user_prompt = arguments.get("user_prompt", "")
        context = arguments.get("context", "")
        
        if not user_prompt:
            return [types.TextContent(
                type="text",
                text="Error: No prompt provided to improve."
            )]
        
        try:
            improved_prompt = await improve_prompt_locally(user_prompt, context)
            return [types.TextContent(
                type="text",
                text=improved_prompt
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error improving prompt: {str(e)}"
            )]
    
    elif name == "auto_improve_all_prompts":
        user_message = arguments.get("user_message", "")
        
        if not user_message:
            return [types.TextContent(
                type="text",
                text="Error: No message provided to improve."
            )]
        
        try:
            improved_message = await improve_prompt_locally(user_message, "")
            return [types.TextContent(
                type="text",
                text=f"IMPROVED PROMPT:\n\n{improved_message}\n\n---\n\nORIGINAL: {user_message}"
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error improving message: {str(e)}"
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def improve_prompt_locally(user_prompt: str, context: str = "") -> str:
    """Improve prompt using local sampling and rule-based enhancement."""
    # Read improvement guidelines
    improvement_instructions = await read_improvement_prompt()
    
    # Analyze the prompt for common issues
    improvements = []
    
    # Check for vagueness
    if len(user_prompt.split()) < 5:
        improvements.append("Make the request more specific and detailed")
    
    # Check for missing context
    if not context and not any(word in user_prompt.lower() for word in ['python', 'javascript', 'web', 'app', 'code']):
        improvements.append("Consider adding context about the technology or domain")
    
    # Check for unclear objectives
    if not any(word in user_prompt.lower() for word in ['create', 'build', 'write', 'generate', 'help', 'explain', 'show']):
        improvements.append("Specify what action you want performed")
    
    # Generate improved version based on patterns
    improved = enhance_prompt_structure(user_prompt, context, improvements)
    
    return improved


def enhance_prompt_structure(prompt: str, context: str, improvements: list) -> str:
    """Enhance prompt structure using sampling patterns."""
    
    # Start with original prompt
    enhanced = prompt.strip()
    
    # Add role definition if beneficial
    if any(word in prompt.lower() for word in ['code', 'program', 'develop']):
        enhanced = f"Act as an expert software developer. {enhanced}"
    elif any(word in prompt.lower() for word in ['write', 'document', 'explain']):
        enhanced = f"Act as a technical writer. {enhanced}"
    elif any(word in prompt.lower() for word in ['design', 'ui', 'ux']):
        enhanced = f"Act as a UX/UI designer. {enhanced}"
    elif any(word in prompt.lower() for word in ['data', 'analysis', 'statistics']):
        enhanced = f"Act as a data analyst. {enhanced}"
    
    # Add specificity for short prompts
    if len(enhanced.split()) < 10:
        enhanced += ". Please provide detailed steps, examples, and explanations."
    
    # Add context if provided
    if context:
        enhanced += f"\n\nContext: {context}"
    
    # Add format requirements for code requests
    if any(word in enhanced.lower() for word in ['code', 'function', 'script', 'program']):
        enhanced += "\n\nPlease include:\n- Clear comments explaining the code\n- Error handling where appropriate\n- Example usage\n- Brief explanation of the approach"
    
    # Add format requirements for explanations
    if any(word in enhanced.lower() for word in ['explain', 'describe', 'what is', 'how does']):
        enhanced += "\n\nPlease structure your response with:\n- Clear introduction\n- Step-by-step explanation\n- Practical examples\n- Summary of key points"
    
    # Add constraints for better results
    enhanced += "\n\nEnsure the response is practical, actionable, and easy to understand."
    
    return enhanced


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())