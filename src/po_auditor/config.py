import os
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Database
    db_path: str = Field(default="enterprise.db")

    # OpenAI-Compatible LLM Configuration
    llm_api_key: Optional[SecretStr] = Field(default=None, validation_alias="LLM_API_KEY", description="API Key for OpenAI-compatible LLM")
    llm_base_url: Optional[str] = Field(default=None, validation_alias="LLM_BASE_URL", description="Base URL for OpenAI-compatible API (e.g. https://api.openai.com/v1)")
    llm_model: str = Field(default="gpt-4o-mini", validation_alias="LLM_MODEL", description="LLM Model Name (e.g. gpt-4o-mini, gpt-4o, deepseek-chat)")
    llm_temperature: float = Field(default=0.0, validation_alias="LLM_TEMPERATURE", description="Sampling temperature")

    # Fallback to API_KEY if LLM_API_KEY is not set
    api_key: Optional[SecretStr] = Field(default=None, validation_alias="API_KEY", description="Legacy API Key fallback")

    def get_effective_api_key(self) -> Optional[SecretStr]:
        return self.llm_api_key or self.api_key

    def print_config(self) -> None:
        """พิมพ์ Config ออกมาก่อนรัน โดย Mask ข้อมูลความลับตามมาตรฐาน AGENTS.md"""
        eff_key = self.get_effective_api_key()
        masked_key = "None (Using Built-in Local Engine)"
        engine_mode = "Built-in Local Audit Engine"
        if eff_key and eff_key.get_secret_value():
            raw = eff_key.get_secret_value()
            masked_key = f"***{raw[-4:]}" if len(raw) >= 4 else "***"
            engine_mode = f"OpenAI-Compatible LLM ({self.llm_model})"

        base_url_disp = self.llm_base_url or "Default (https://api.openai.com/v1)"

        print("=" * 50)
        print("  SMART PO & INVOICE AUDITOR CONFIGURATION")
        print("=" * 50)
        print(f"Host              : {self.host}")
        print(f"Port              : {self.port}")
        print(f"Database Path     : {self.db_path}")
        print(f"Active Engine     : {engine_mode}")
        print(f"LLM Base URL      : {base_url_disp}")
        print(f"LLM Model         : {self.llm_model}")
        print(f"LLM API Key       : {masked_key}")
        print("=" * 50)


def load_and_print_config() -> Settings:
    settings = Settings()
    settings.print_config()
    return settings
