"""Typed, deterministic search profile configuration validation."""

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class ConstraintPolicy(StrEnum):
    HARD_REQUIREMENT = "HARD_REQUIREMENT"
    STRONG_PREFERENCE = "STRONG_PREFERENCE"
    SOFT_PREFERENCE = "SOFT_PREFERENCE"
    INFORMATIONAL = "INFORMATIONAL"
    IGNORE = "IGNORE"


class TargetRole(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    priority: int = Field(default=1, ge=1, le=100)
    aliases: list[str] = Field(default_factory=list, max_length=30)
    minimum_seniority: str | None = Field(default=None, max_length=64)
    maximum_seniority: str | None = Field(default=None, max_length=64)


class Locations(BaseModel):
    preferred: list[str] = Field(default_factory=list, max_length=50)
    acceptable: list[str] = Field(default_factory=list, max_length=50)
    excluded: list[str] = Field(default_factory=list, max_length=50)
    remote_policy: ConstraintPolicy = ConstraintPolicy.IGNORE
    hybrid_policy: ConstraintPolicy = ConstraintPolicy.IGNORE
    onsite_policy: ConstraintPolicy = ConstraintPolicy.IGNORE
    maximum_onsite_days: int | None = Field(default=None, ge=0, le=7)
    maximum_commute_miles: int | None = Field(default=None, ge=0, le=500)
    relocation_allowed: bool = False


class WorkAuthorization(BaseModel):
    sponsorship_required: bool = False
    sponsorship_policy: ConstraintPolicy = ConstraintPolicy.IGNORE
    clearance_policy: ConstraintPolicy = ConstraintPolicy.IGNORE
    reject_phrases: list[str] = Field(default_factory=list, max_length=50)
    positive_phrases: list[str] = Field(default_factory=list, max_length=50)


class Compensation(BaseModel):
    currency: str = Field(default="USD", min_length=3, max_length=3)
    minimum_base: int | None = Field(default=None, ge=0)
    preferred_base: int | None = Field(default=None, ge=0)
    minimum_total_compensation: int | None = Field(default=None, ge=0)
    below_minimum_policy: ConstraintPolicy = ConstraintPolicy.IGNORE

    @model_validator(mode="after")
    def validate_amounts(self) -> "Compensation":
        if (
            self.minimum_base is not None
            and self.preferred_base is not None
            and self.minimum_base > self.preferred_base
        ):
            raise ValueError("Minimum compensation cannot exceed preferred compensation.")
        return self


class EmploymentTypes(BaseModel):
    allowed: list[str] = Field(default_factory=list, max_length=10)
    policy: ConstraintPolicy = ConstraintPolicy.IGNORE


class SkillRequirement(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    policy: ConstraintPolicy = ConstraintPolicy.STRONG_PREFERENCE


class Skills(BaseModel):
    required: list[SkillRequirement] = Field(default_factory=list, max_length=50)
    preferred: list[str] = Field(default_factory=list, max_length=100)
    learning_interests: list[str] = Field(default_factory=list, max_length=100)
    excluded: list[str] = Field(default_factory=list, max_length=100)


class Companies(BaseModel):
    preferred_industries: list[str] = Field(default_factory=list, max_length=50)
    excluded_industries: list[str] = Field(default_factory=list, max_length=50)
    preferred_companies: list[str] = Field(default_factory=list, max_length=100)
    excluded_companies: list[str] = Field(default_factory=list, max_length=100)
    minimum_company_size: int | None = Field(default=None, ge=1)
    startups_allowed: bool = True


class Weights(BaseModel):
    core_technical_skills: int = Field(ge=0, le=100)
    distributed_systems: int = Field(ge=0, le=100)
    ai_alignment: int = Field(ge=0, le=100)
    domain_alignment: int = Field(ge=0, le=100)
    seniority: int = Field(ge=0, le=100)
    leadership: int = Field(ge=0, le=100)
    location: int = Field(ge=0, le=100)
    sponsorship: int = Field(ge=0, le=100)
    compensation: int = Field(ge=0, le=100)
    company_preference: int = Field(ge=0, le=100)

    @model_validator(mode="after")
    def validate_total(self) -> "Weights":
        if sum(self.model_dump().values()) != 100:
            raise ValueError("Weight total must equal 100.")
        return self


class Thresholds(BaseModel):
    apply_now: int = Field(ge=0, le=100)
    apply_selectively: int = Field(ge=0, le=100)
    manual_review: int = Field(ge=0, le=100)
    skip_below: int = Field(ge=0, le=100)

    @model_validator(mode="after")
    def validate_order(self) -> "Thresholds":
        if not (self.apply_now >= self.apply_selectively >= self.manual_review >= self.skip_below):
            raise ValueError("Thresholds must be descending.")
        return self


class Notifications(BaseModel):
    minimum_score: int = Field(ge=0, le=100)
    immediate_for_apply_now: bool = False
    daily_digest: bool = True


class SearchProfileConfiguration(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    active: bool = False
    target_roles: list[TargetRole] = Field(default_factory=list, max_length=30)
    excluded_titles: list[str] = Field(default_factory=list, max_length=100)
    locations: Locations = Field(default_factory=Locations)
    work_authorization: WorkAuthorization = Field(default_factory=WorkAuthorization)
    compensation: Compensation = Field(default_factory=Compensation)
    employment_types: EmploymentTypes = Field(default_factory=EmploymentTypes)
    skills: Skills = Field(default_factory=Skills)
    companies: Companies = Field(default_factory=Companies)
    weights: Weights
    thresholds: Thresholds
    notifications: Notifications

    @model_validator(mode="after")
    def validate_cross_field_constraints(self) -> "SearchProfileConfiguration":
        preferred = {location.casefold() for location in self.locations.preferred}
        excluded = {location.casefold() for location in self.locations.excluded}
        if preferred & excluded:
            raise ValueError("A location cannot appear in both preferred and excluded lists.")
        titles = {role.title.casefold() for role in self.target_roles}
        excluded_titles = {title.casefold() for title in self.excluded_titles}
        if titles & excluded_titles:
            raise ValueError("A title cannot appear in both target and excluded lists.")
        return self
