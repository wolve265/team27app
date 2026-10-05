import datetime as dt
from collections.abc import Sequence
from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class Season:
    name: str
    start: dt.datetime
    end: dt.datetime
    game_cost: int
    game_cost_per_player: int

    def get_datetime_query(self) -> dict[str, dict[str, dt.datetime]]:
        return {"datetime": {"$gte": self.start, "$lte": self.end}}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Season):
            return NotImplemented
        return self.name == other.name


def _create_season(
    year_start: int,
    year_end: int,
    game_cost: int = -1,
    game_cost_per_player: int = -1,
    name: str | None = None,
) -> Season:
    return Season(
        name=name or f"Hala {year_start}/{year_end}",
        start=dt.datetime(
            year=year_start, month=9, day=1, hour=0, minute=0, second=0, tzinfo=dt.UTC
        ),
        end=dt.datetime(
            year=year_end, month=8, day=31, hour=23, minute=59, second=59, tzinfo=dt.UTC
        ),
        game_cost=game_cost,
        game_cost_per_player=game_cost_per_player,
    )


class Seasons:
    INDOOR_25_26 = _create_season(
        year_start=2025, year_end=2026, game_cost=150, game_cost_per_player=15
    )
    INDOOR_26_27 = _create_season(
        year_start=2026, year_end=2027, game_cost=150, game_cost_per_player=15
    )
    FIRST = INDOOR_25_26
    LAST = INDOOR_26_27

    @classmethod
    def list_all(cls) -> list[Season]:
        return [cls.INDOOR_25_26, cls.INDOOR_26_27]

    @staticmethod
    def from_datetime(datetime: dt.datetime) -> Season:
        for season in Seasons.list_all():
            if season.start <= datetime <= season.end:
                return season
        raise ValueError(f"No season found for datetime {datetime}")


def merge_seasons(seasons: Sequence[Season]) -> Season:
    if not seasons:
        return _create_season(2025, 2025, name="Brak sezonu")
    start = min(s.start for s in seasons)
    end = max(s.end for s in seasons)
    name = f"Hala {start.year}/{end.year}"
    game_cost = sum(s.game_cost for s in seasons) // len(seasons)
    game_cost_per_player = sum(s.game_cost_per_player for s in seasons) // len(seasons)
    return Season(
        name=name,
        start=start,
        end=end,
        game_cost=game_cost,
        game_cost_per_player=game_cost_per_player,
    )


def st_seasons() -> list[Season]:
    return st.pills(
        "Sezony",
        key="selected_seasons",
        options=sorted(Seasons.list_all(), key=lambda s: s.end, reverse=True),
        selection_mode="multi",
        default=[Seasons.LAST],
        format_func=lambda s: s.name,
        persist_state="session",
    )
