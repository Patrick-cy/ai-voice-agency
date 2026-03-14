"""Configuration management for AI Voice Agency."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Application
    app_base_url: str = "http://localhost:8000"
    log_level: str = "INFO"

    # Agent
    system_prompt: str = (
        "You are a helpful AI voice assistant at our agency. "
        "You answer concisely because responses are read aloud. "
        "Keep answers under 3 sentences unless more detail is needed."
    )
    max_conversation_turns: int = 10


settings = Settings()
