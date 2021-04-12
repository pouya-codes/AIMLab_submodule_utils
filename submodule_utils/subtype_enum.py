from enum import Enum

class BinaryEnum(Enum):
    Normal = 0
    Other = 0
    MucinousBorderlineTumor = 0
    Necrosis = 0
    Stroma = 0
    Tumor = 1

class ECPromiseSubtypeEnum(Enum):
    MMRD = 0
    P53ABN = 1
    P53WT = 2
    POLE = 3

class OvarianSubtypeEnum(Enum):
   CC = 0
   LGSC = 1
   EC = 2
   MC = 3
   HGSC = 4
