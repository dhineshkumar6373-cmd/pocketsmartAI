from typing import Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value: str, info):
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Passwords do not match")
        return value

class LoginRequest(BaseModel):
    username: str
    password: str

class HomeBudgetInput(BaseModel):
    total_budget: float = Field(gt=0, le=10_000_000)
    num_lights: int = Field(default=0, ge=0, le=100)
    num_fans: int = Field(default=0, ge=0, le=100)
    num_furniture: int = Field(default=0, ge=0, le=100)
    num_dining_tables: int = Field(default=0, ge=0, le=50)
    living_room: bool = False
    kitchen: bool = False
    bedroom: bool = False
    additional_requirements: str | None = Field(default=None, max_length=1000)

class PartyBudgetInput(BaseModel):
    total_budget: float = Field(gt=0, le=10_000_000)
    num_guests: int = Field(gt=0, le=5000)
    party_type: str = Field(min_length=2, max_length=100)
    venue_type: str | None = Field(default=None, max_length=100)
    needs_catering: bool = True
    needs_decoration: bool = True
    needs_entertainment: bool = True
    additional_requirements: str | None = Field(default=None, max_length=1000)

class JewelryBudgetInput(BaseModel):
    total_budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=100)
    preferences: str | None = Field(default=None, max_length=1000)

class RecommendationEnvelope(BaseModel):
    model_config = ConfigDict(extra="allow")
    data: dict[str, Any]
