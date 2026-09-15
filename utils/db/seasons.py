import datetime as dt
from dataclasses import dataclass


@dataclass
class Season:
    name: str
    start: dt.datetime
    end: dt.datetime

    def get_datetime_query(self) -> dict[str, dict[str, dt.datetime]]:
        return {"datetime": {"$gte": self.start, "$lte": self.end}}


def create_season(year_start: int, year_end: int) -> Season:
    return Season(
        name=f"Hala {year_start}/{year_end}",
        start=dt.datetime(year=year_start, month=9, day=1, tzinfo=dt.UTC),
        end=dt.datetime(year=year_end, month=4, day=30, tzinfo=dt.UTC),
    )


class Seasons:
    INDOOR_25_26 = create_season(2025, 2026)
    INDOOR_26_27 = create_season(2026, 2027)

    @classmethod
    def list_all(cls) -> list[Season]:
        return [cls.INDOOR_25_26, cls.INDOOR_26_27]

    @staticmethod
    def from_datetime(dt: dt.datetime) -> Season:
        for season in Seasons.list_all():
            if season.start <= dt <= season.end:
                return season
        raise ValueError(f"No season found for datetime {dt}")
