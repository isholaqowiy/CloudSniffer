import json
import logging
import asyncio
from typing import Dict, Any
from openai import AsyncOpenAI
from config.config import settings
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class DetectionReportSchema(BaseModel):
    ai_probability: int = Field(..., description="The calculated probability percentage that this content was AI generated.")
    human_probability: int = Field(..., description="The calculated probability percentage that this content was human written.")
    confidence: str = Field(..., description="High, Medium, or Low confidence levels.")
    verdict: str = Field(..., description="Final assessment: AI-generated, Human-written, or Mixed.")
    analysis: list[str] = Field(..., description="Array detailing structured analytical explanations.")
    recommendation: str = Field(..., description="Practical recommendation for the instructor.")

class OpenAIDetectorService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze_text(self, text: str, retries: int = 2) -> Dict[str, Any]:
        truncated_text = text[:6000] # Safe execution token boundaries for gpt-4o-mini frameworks
        
        system_prompt = (
            "You are an expert academic forensics analyzer specialized in detecting linguistic characteristics "
            "of large language models. Analyze the provided assignment text for structural anomalies, "
            "predictability vectors, and uniformity. You must respond using a strict structural JSON output schema matching "
            "the properties required by the caller."
        )
        
        user_prompt = f"Analyze the following student text segment and return full forensic validation details:\n\n{truncated_text}"
        
        for attempt in range(retries + 1):
            try:
                response = await asyncio.wait_for(
                    self.client.beta.chat.completions.parse(
                        model=settings.OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        response_format=DetectionReportSchema,
                        temperature=0.2
                    ),
                    timeout=25.0
                )
                
                parsed_payload = response.choices[0].message.parsed
                if parsed_payload:
                    return parsed_payload.model_dump()
                raise ValueError("Parsed execution payload structure returned empty allocations.")
                
            except asyncio.TimeoutError:
                logger.warning(f"Timeout occurred during OpenAI evaluation pipeline call (Attempt {attempt + 1}).")
                if attempt == retries:
                    raise
            except Exception as e:
                logger.error(f"Error handling internal execution mapping inside OpenAI module: {e}")
                if attempt == retries:
                    return self._fallback_report()
                await asyncio.sleep(1.5)

    def _fallback_report(self) -> Dict[str, Any]:
        return {
            "ai_probability": 50,
            "human_probability": 50,
            "confidence": "Low",
            "verdict": "Mixed",
            "analysis": ["OpenAI engine structural fallback triggered during transient service exceptions."],
            "recommendation": "Review the artifact manually while system connects recovery paths."
        }
