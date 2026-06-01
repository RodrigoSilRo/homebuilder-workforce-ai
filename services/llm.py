"""
LLM service — routes to OpenAI, Anthropic, AWS Bedrock, or rule-based fallback.

Priority order:
  1. OpenAI (OPENAI_API_KEY)
  2. Anthropic (ANTHROPIC_API_KEY)
  3. AWS Bedrock (AWS_ACCESS_KEY_ID + AWS_BEDROCK_MODEL)
  4. None → caller uses rule-based fallback

Usage:
    from services.llm import chat, has_llm, llm_provider
    result = chat(system="...", user="...")
    if result is None:
        result = rule_based_fallback()
"""
import os


def _clean(val: str) -> bool:
    return bool(val) and "your_" not in val


def get_llm(model: str = None):
    openai_key    = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    aws_key       = os.getenv("AWS_ACCESS_KEY_ID", "")
    bedrock_model = os.getenv("AWS_BEDROCK_MODEL", "anthropic.claude-haiku-4-5-20251001-v1:0")
    aws_region    = os.getenv("AWS_REGION", "us-east-1")

    if _clean(openai_key):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model or "gpt-4o-mini", temperature=0, api_key=openai_key)

    if _clean(anthropic_key):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model or "claude-haiku-4-5-20251001",
            temperature=0,
            api_key=anthropic_key,
        )

    if _clean(aws_key):
        try:
            from langchain_aws import ChatBedrock
            import boto3
            boto3.setup_default_session(
                aws_access_key_id     = aws_key,
                aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", ""),
                region_name           = aws_region,
            )
            return ChatBedrock(
                model_id   = model or bedrock_model,
                region_name= aws_region,
                model_kwargs={"temperature": 0, "max_tokens": 1024},
            )
        except Exception:
            pass

    return None


def has_llm() -> bool:
    for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        if _clean(os.getenv(key, "")):
            return True
    if _clean(os.getenv("AWS_ACCESS_KEY_ID", "")):
        return True
    return False


def llm_provider() -> str:
    """Returns the active LLM provider name for display in the UI."""
    if _clean(os.getenv("OPENAI_API_KEY", "")):
        return "OpenAI"
    if _clean(os.getenv("ANTHROPIC_API_KEY", "")):
        return "Anthropic"
    if _clean(os.getenv("AWS_ACCESS_KEY_ID", "")):
        return f"AWS Bedrock ({os.getenv('AWS_BEDROCK_MODEL', 'claude-haiku')})"
    return "rule-based"


def chat(system: str, user: str, model: str = None) -> str | None:
    """
    Single chat completion.
    Returns the response string, or None if no LLM is configured.
    Callers must handle None with a rule-based fallback.
    """
    llm = get_llm(model)
    if llm is None:
        return None
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
        return resp.content
    except Exception:
        return None
