from pydantic import BaseModel, Field


class BrowserSettings(BaseModel):
    show_browser: bool = False

    delay_before_navigation_ms: int = Field(
        default=0,
        ge=0,
        le=60_000,
    )

    wait_after_load_ms: int = Field(
        default=3_000,
        ge=0,
        le=60_000,
    )

    scroll_enabled: bool = True

    scroll_amount: int = Field(
        default=800,
        ge=0,
        le=10_000,
    )

    wait_after_scroll_ms: int = Field(
        default=2_000,
        ge=0,
        le=60_000,
    )

    delay_after_navigation_ms: int = Field(
        default=0,
        ge=0,
        le=60_000,
    )

    navigation_timeout_ms: int = Field(
        default=30_000,
        ge=1_000,
        le=120_000,
    )
