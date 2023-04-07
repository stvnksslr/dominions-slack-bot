
from pydantic import BaseModel, Field

from src.models.snek_server_status import Era


class SnekServerDetails(BaseModel):
    game_id: int = Field(alias="id")
    name: str
    era: Era
    port: None
    hours: int
    hall_of_fame: int = Field(alias="hofsize")
    independents_strength: int = Field(alias="indepstr")
    magic_sites: int = Field(alias="magicsites")
    event_rarity: int = Field(alias="eventrarity")
    richness: int
    resources: int
    starting_province: int = Field(alias="startprov")
    victory_condition: int = Field(alias="victorycond")
    required_ap: int = Field(alias="requiredap")
    lvl_1_thrones: int = Field(alias="lvl1thrones")
    lvl_2_thrones: int = Field(alias="lvl2thrones")
    lvl_3_thrones: int = Field(alias="lvl3thrones")
    total_vp: int | None = Field(alias="totalvp")
    required_vp: int | None = Field(alias="requiredvp")
    state: int
    user_id: int
    research: int
    supplies: int
    renaming: bool
    team_game: bool = Field(alias="teamgame")
    no_art_rest: bool = Field(alias="noartrest")
    clustered: bool
    score_graphs: bool = Field(alias="scoregraphs")
    no_nation_info: bool = Field(alias="nonationinfo")
    map_id: int
    deleted_at: None
    status: int
    shortname: str
    summer_vp: bool = Field(alias="summervp")
    capital_vp: bool = Field(alias="capitalvp")
    cataclysm: int | None
    max_globals: int = Field(alias="globals")
    story_events: int = Field(alias="storyevents")
    no_rand_research: bool = Field(alias="norandres")
    recruitment: int
    mods: list
    nation_rules: list

    class Config:
        allow_population_by_field_name = True
