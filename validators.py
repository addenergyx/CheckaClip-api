from pydantic import BaseModel, constr, Field, field_validator


class SearchRequest(BaseModel):
    search_term: constr(strip_whitespace=True, min_length=1, max_length=100)
    max_results: int = Field(default=5, ge=1, le=50)  # `ge` is greater than or equal, `le` is less than or equal

    @field_validator('max_results')
    def check_max_results(cls, value):
        if not 1 <= value <= 50:
            raise ValueError('max_results must be between 1 and 50')
        return value

    @field_validator('search_term')
    def check_string_term_length(cls, value):
        if not 1 <= len(value) <= 100:
            raise ValueError('String must be between 1 and 100')
        return value