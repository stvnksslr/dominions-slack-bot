from typing import Optional, List

from pydantic import BaseModel, Field

from src.models.snek_server_status import Era, ServerState


class SnekServerDetails(BaseModel):
    id: int
    name: str
    era: Era
    port: Optional[None]
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
    total_vp: Optional[int] = Field(alias="totalvp")
    required_vp: Optional[int] = Field(alias="requiredvp")
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
    deleted_at: Optional[None]
    status: int
    shortname: str
    summer_vp: bool = Field(alias="summervp")
    capital_vp: bool = Field(alias="capitalvp")
    cataclysm: Optional[int]
    globals: int
    story_events: int = Field(alias="storyevents")
    no_rand_research: bool = Field(alias="norandres")
    recruitment: int
    mods: List
    nation_rules: List

    class Config:
        allow_population_by_field_name = True
