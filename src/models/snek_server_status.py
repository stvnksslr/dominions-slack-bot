from enum import Enum


class ServerState(Enum):
    """
    Snek.Earth Server Status's
    """

    created: 0
    pretender_upload: 2
    started: 4


class Era(Enum):
    """
    Snek.Earth Era's
    """

    Early_Age = 0
    Middle_Age = 1
    Late_Age = 2


class NationType(Enum):
    """
    Snek.Earth Nation Type
    """

    Empty = 0
    Human = 1
    Bot = 2
    Independent = 3
    Closed = 253
    Defeated_this_turn = 254
    Defeated = 255
    eliminated_player = -1
    Defeated_Duplicate = -2


class TurnStatus(Enum):
    """
    Snek.Earth Player Turn Status
    """

    NotSubmitted = 0
    PartiallySubmitted = 1
    Submitted = 2
