import asyncio
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn


app = FastAPI(title="Prompt Improvement Server", description="MCP server for improving user prompts")


class PromptRequest(BaseModel):
    user_prompt: str
    context: str = ""


class PromptResponse(BaseModel):
    improved_prompt: str


async def read_improvement_prompt() -> str:
    """Read the improvement prompt from the dedicated file."""
    prompt_file = Path(__file__).parent / "improvement_prompt.md"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    return "Improve the following prompt to be clearer and more effective:"


@app.post("/improve-prompt", response_model=PromptResponse)
async def improve_prompt(request: PromptRequest):
    """Improve a user's prompt using AI sampling."""
    if not request.user_prompt:
        raise HTTPException(status_code=400, detail="No prompt provided to improve")
    
    try:
        # Use local sampling-based improvement
        improved_prompt = await improve_prompt_locally(request.user_prompt, request.context)
        return PromptResponse(improved_prompt=improved_prompt)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error improving prompt: {str(e)}")


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
    
    # Add specificity
    if len(enhanced.split()) < 10:
        enhanced += ". Please provide detailed steps and examples."
    
    # Add context if provided
    if context:
        enhanced += f"\n\nContext: {context}"
    
    # Add format requirements for code requests
    if any(word in enhanced.lower() for word in ['code', 'function', 'script']):
        enhanced += "\n\nPlease include:\n- Clear comments explaining the code\n- Error handling where appropriate\n- Example usage"
    
    # Add constraints for better results
    enhanced += "\n\nEnsure the response is practical and actionable."
    
    return enhanced


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Prompt Improvement Server",
        "description": "Send POST requests to /improve-prompt with your prompt to get improvements",
        "example": {
            "user_prompt": "Write code",
            "context": "Python web application"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)