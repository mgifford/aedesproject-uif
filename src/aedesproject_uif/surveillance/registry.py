"""
Disease and vector registry for the unified surveillance system.

Defines vector types, disease types, and their associations, phenology, ecology,
and data sources.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


class VectorType(Enum):
    """Supported vector types."""
    MOSQUITO = "mosquito"
    TICK = "tick"
    RODENT = "rodent"
    BIRD = "bird"  # Migratory bird (reservoir)


class DiseaseType(Enum):
    """Colorado-relevant vector-borne and zoonotic diseases."""
    # Mosquito-borne
    WEST_NILE_VIRUS = "wnv"
    ST_LOUIS_ENCEPHALITIS = "sle"
    WESTERN_EQUINE_ENCEPHALITIS = "weev"
    LA_CROSSE_ENCEPHALITIS = "lacv"
    
    # Tick-borne
    LYME_DISEASE = "lyme"
    ROCKY_MOUNTAIN_SPOTTED_FEVER = "rmsf"
    COLORADO_TICK_FEVER = "ctf"
    TICK_BORNE_RELAPSING_FEVER = "tbrf"
    TULAREMIA = "tularemia"
    BABESIOSIS = "babesiosis"
    ANAPLASMOSIS = "anaplasmosis"
    POWASSAN_VIRUS = "powassan"
    
    # Rodent-borne
    PLAGUE = "plague"
    HANTAVIRUS = "hantavirus"
    
    # Other zoonotic
    AVIAN_INFLUENZA = "avian_flu"


@dataclass
class VectorEcology:
    """Ecological characteristics of a vector."""
    vector_type: VectorType
    scientific_names: List[str]
    primary_habitat: str
    activity_season: Tuple[int, int]  # (start_month, end_month)
    temperature_min_c: float  # Minimum for activity
    temperature_max_c: float  # Maximum for activity (optimal range)
    temperature_peak_c: float  # Peak activity temperature
    humidity_min_percent: float  # Minimum relative humidity
    primary_hosts: List[str]  # e.g., ["humans", "birds", "mammals"]
    phenology_description: str


@dataclass
class DiseaseCharacteristics:
    """Epidemiological and clinical characteristics of a disease."""
    disease_type: DiseaseType
    vector_types: List[VectorType]
    incubation_days: Tuple[int, int]  # (min, max) days
    case_fatality_rate: float  # Approximate CFR
    colorado_endemic: bool
    reportable: bool  # Nationally reportable disease
    description: str


class DiseaseVectorRegistry:
    """
    Centralized registry of disease-vector associations, ecology, and configurations.
    
    Enables dynamic disease/vector selection and provides metadata for feature engineering,
    risk scoring, and validation.
    """
    
    # Vector ecology definitions
    VECTOR_ECOLOGY = {
        VectorType.MOSQUITO: {
            "culex_tarsalis": VectorEcology(
                vector_type=VectorType.MOSQUITO,
                scientific_names=["Culex tarsalis"],
                primary_habitat="standing water, marshes, retention ponds",
                activity_season=(4, 10),  # April-October
                temperature_min_c=10.0,
                temperature_max_c=35.0,
                temperature_peak_c=25.0,
                humidity_min_percent=50.0,
                primary_hosts=["birds", "mammals", "humans"],
                phenology_description="Spring emergence at 50°F soil temp; adults overwinter; peak July-September"
            ),
        },
        VectorType.TICK: {
            "ixodes_scapularis": VectorEcology(
                vector_type=VectorType.TICK,
                scientific_names=["Ixodes scapularis"],
                primary_habitat="deciduous/mixed forest, brush, tall grass",
                activity_season=(3, 11),  # March-November (peaks spring & fall)
                temperature_min_c=4.0,  # Activity resumes
                temperature_max_c=32.0,
                temperature_peak_c=15.0,  # Fall & spring peaks (cool months)
                humidity_min_percent=70.0,  # High humidity requirement
                primary_hosts=["deer", "small mammals", "birds", "humans"],
                phenology_description="NOT established in Colorado — all local 'Lyme' risk is travel-associated. I. scapularis is present in eastern US; CO cases are travel-acquired. Larval (spring), nymphal (summer peak), adult (fall/spring) in endemic areas."
            ),
            "dermacentor_variabilis": VectorEcology(
                vector_type=VectorType.TICK,
                scientific_names=["Dermacentor variabilis"],
                primary_habitat="grassland, shrubland, forest edges, rural areas",
                activity_season=(4, 9),  # April-September
                temperature_min_c=10.0,
                temperature_max_c=32.0,
                temperature_peak_c=22.0,
                humidity_min_percent=35.0,
                primary_hosts=["dogs", "deer", "small mammals", "humans"],
                phenology_description="American dog tick; RMSF primary vector; adult activity April–August; wide geographic range including eastern Colorado plains and foothills"
            ),
            "dermacentor_andersoni": VectorEcology(
                vector_type=VectorType.TICK,
                scientific_names=["Dermacentor andersoni"],
                primary_habitat="semi-arid shrub, grassland, low elevation forest",
                activity_season=(3, 7),  # March-July
                temperature_min_c=10.0,
                temperature_max_c=30.0,
                temperature_peak_c=20.0,
                humidity_min_percent=40.0,  # More tolerant of dry conditions
                primary_hosts=["small mammals", "deer", "livestock", "humans"],
                phenology_description="Primarily nymphal & adult active spring/early summer; less questing in high heat; peaks April-May in Colorado"
            ),
        },
        VectorType.RODENT: {
            "peromyscus_maniculatus": VectorEcology(
                vector_type=VectorType.RODENT,
                scientific_names=["Peromyscus maniculatus", "Cynomys spp.", "Spermophilus spp."],
                primary_habitat="grassland, semi-arid shrub, prairie dog towns, agricultural edges",
                activity_season=(1, 12),  # Year-round; peak contact risk spring–fall
                temperature_min_c=-10.0,
                temperature_max_c=38.0,
                temperature_peak_c=18.0,
                humidity_min_percent=10.0,
                primary_hosts=["rodents", "humans (incidental)"],
                phenology_description="Year-round activity; human exposure peaks spring–fall via aerosolized droppings, contact with nesting material, or flea bites"
            ),
        },
        VectorType.BIRD: {
            "corvus_brachyrhynchos": VectorEcology(
                vector_type=VectorType.BIRD,
                scientific_names=["Corvus brachyrhynchos", "Passer domesticus", "Sturnus vulgaris"],
                primary_habitat="urban/suburban, riparian corridors, agricultural fields",
                activity_season=(4, 10),  # Peak amplification season
                temperature_min_c=5.0,
                temperature_max_c=40.0,
                temperature_peak_c=22.0,
                humidity_min_percent=20.0,
                primary_hosts=["birds (amplifying hosts)", "mammals (dead-end)"],
                phenology_description="Bridge vector amplification via Culex mosquitoes; corvid die-offs are a leading WNV sentinel event"
            ),
        },
    }

    # Disease characteristics
    DISEASE_CHARACTERISTICS = {
        DiseaseType.WEST_NILE_VIRUS: DiseaseCharacteristics(
            disease_type=DiseaseType.WEST_NILE_VIRUS,
            vector_types=[VectorType.MOSQUITO],
            incubation_days=(2, 14),
            case_fatality_rate=0.003,  # ~0.3% overall, higher in severe cases
            colorado_endemic=True,
            reportable=True,
            description="Arboviral infection transmitted by Culex mosquitoes; peak transmission July-September; neuroinvasive form in ~1% of infections"
        ),
        DiseaseType.LYME_DISEASE: DiseaseCharacteristics(
            disease_type=DiseaseType.LYME_DISEASE,
            vector_types=[VectorType.TICK],
            incubation_days=(3, 30),
            case_fatality_rate=0.0,  # Rare, but serious if untreated
            colorado_endemic=False,  # I. scapularis NOT established in CO; cases are travel-associated
            reportable=True,
            description="Tick-borne spirochete infection; Ixodes scapularis is NOT established in Colorado. CO Lyme cases are travel-acquired from endemic eastern/northern US regions. Local risk is via I. pacificus (western slope, rare). Use case counts as travel-exposure signal only."
        ),
        DiseaseType.ROCKY_MOUNTAIN_SPOTTED_FEVER: DiseaseCharacteristics(
            disease_type=DiseaseType.ROCKY_MOUNTAIN_SPOTTED_FEVER,
            vector_types=[VectorType.TICK],
            incubation_days=(2, 14),
            case_fatality_rate=0.01,  # ~1% if untreated, <0.1% with antibiotics
            colorado_endemic=True,
            reportable=True,
            description="Tick-borne rickettsial infection; peak transmission April-September; petechial rash, fever, headache common"
        ),
        DiseaseType.TULAREMIA: DiseaseCharacteristics(
            disease_type=DiseaseType.TULAREMIA,
            vector_types=[VectorType.TICK, VectorType.RODENT],
            incubation_days=(1, 14),
            case_fatality_rate=0.005,  # ~0.5% with treatment
            colorado_endemic=True,
            reportable=True,
            description="Zoonotic bacterial infection; tick-borne and via rodent contact; highly infectious"
        ),
        DiseaseType.PLAGUE: DiseaseCharacteristics(
            disease_type=DiseaseType.PLAGUE,
            vector_types=[VectorType.RODENT],
            incubation_days=(1, 6),
            case_fatality_rate=0.1,  # ~10% with treatment; >90% without
            colorado_endemic=True,
            reportable=True,
            description="Zoonotic bacterial infection of rodents and fleas; bubonic form most common; endemic in prairie dog colonies"
        ),
        DiseaseType.HANTAVIRUS: DiseaseCharacteristics(
            disease_type=DiseaseType.HANTAVIRUS,
            vector_types=[VectorType.RODENT],
            incubation_days=(7, 42),
            case_fatality_rate=0.38,  # ~38% case fatality for HPS (hantavirus pulmonary syndrome)
            colorado_endemic=True,
            reportable=True,
            description="Zoonotic viral infection from aerosolized rodent secretions; hantavirus pulmonary syndrome (HPS) is severe"
        ),
        DiseaseType.COLORADO_TICK_FEVER: DiseaseCharacteristics(
            disease_type=DiseaseType.COLORADO_TICK_FEVER,
            vector_types=[VectorType.TICK],
            incubation_days=(1, 14),
            case_fatality_rate=0.001,  # <0.1%; rare fatalities
            colorado_endemic=True,
            reportable=True,
            description="Arboviral infection (Coltivirus) transmitted by Dermacentor andersoni; endemic Rocky Mountain region; peak spring-early summer"
        ),
        DiseaseType.ANAPLASMOSIS: DiseaseCharacteristics(
            disease_type=DiseaseType.ANAPLASMOSIS,
            vector_types=[VectorType.TICK],
            incubation_days=(1, 14),
            case_fatality_rate=0.005,  # <1% with treatment
            colorado_endemic=True,
            reportable=True,
            description="Tick-borne bacterial infection (Anaplasma phagocytophilum); transmitted by Ixodes ticks; fever, headache, thrombocytopenia"
        ),
        DiseaseType.BABESIOSIS: DiseaseCharacteristics(
            disease_type=DiseaseType.BABESIOSIS,
            vector_types=[VectorType.TICK],
            incubation_days=(1, 9),
            case_fatality_rate=0.005,
            colorado_endemic=True,
            reportable=True,
            description="Tick-borne protozoan infection; co-transmitted with Lyme disease by Ixodes ticks; hemolytic anemia"
        ),
        DiseaseType.POWASSAN_VIRUS: DiseaseCharacteristics(
            disease_type=DiseaseType.POWASSAN_VIRUS,
            vector_types=[VectorType.TICK],
            incubation_days=(1, 36),
            case_fatality_rate=0.10,  # ~10% case fatality
            colorado_endemic=False,
            reportable=True,
            description="Rare tick-borne flavivirus; encephalitis; transmitted within minutes of tick attachment"
        ),
        DiseaseType.TICK_BORNE_RELAPSING_FEVER: DiseaseCharacteristics(
            disease_type=DiseaseType.TICK_BORNE_RELAPSING_FEVER,
            vector_types=[VectorType.TICK],
            incubation_days=(4, 18),
            case_fatality_rate=0.005,
            colorado_endemic=True,
            reportable=True,
            description="Soft-tick (Ornithodoros) transmitted spirochete infection; Colorado mountain cabins; recurring fever episodes"
        ),
    }
    
    # Disease-to-vector mapping
    DISEASE_VECTORS = {
        DiseaseType.WEST_NILE_VIRUS: [VectorType.MOSQUITO],
        DiseaseType.LYME_DISEASE: [VectorType.TICK],
        DiseaseType.ROCKY_MOUNTAIN_SPOTTED_FEVER: [VectorType.TICK],
        DiseaseType.COLORADO_TICK_FEVER: [VectorType.TICK],
        DiseaseType.TICK_BORNE_RELAPSING_FEVER: [VectorType.TICK],
        DiseaseType.TULAREMIA: [VectorType.TICK, VectorType.RODENT],
        DiseaseType.PLAGUE: [VectorType.RODENT],
        DiseaseType.HANTAVIRUS: [VectorType.RODENT],
    }
    
    @classmethod
    def get_vector_ecology(cls, vector_type: VectorType, species_key: Optional[str] = None) -> VectorEcology:
        """Retrieve vector ecology definition."""
        if vector_type not in cls.VECTOR_ECOLOGY:
            raise ValueError(f"Vector type {vector_type} not found in registry")
        
        ecology_dict = cls.VECTOR_ECOLOGY[vector_type]
        
        if species_key is None:
            # Return first available
            species_key = next(iter(ecology_dict.keys()))
        
        if species_key not in ecology_dict:
            raise ValueError(f"Vector species {species_key} not found")
        
        return ecology_dict[species_key]
    
    @classmethod
    def get_disease_characteristics(cls, disease_type: DiseaseType) -> DiseaseCharacteristics:
        """Retrieve disease characteristics."""
        if disease_type not in cls.DISEASE_CHARACTERISTICS:
            raise ValueError(f"Disease {disease_type} not found in registry")
        return cls.DISEASE_CHARACTERISTICS[disease_type]
    
    @classmethod
    def get_vectors_for_disease(cls, disease_type: DiseaseType) -> List[VectorType]:
        """Get vector types associated with a disease."""
        return cls.DISEASE_VECTORS.get(disease_type, [])
    
    @classmethod
    def list_diseases(cls, vector_type: Optional[VectorType] = None) -> List[DiseaseType]:
        """List all diseases, optionally filtered by vector type."""
        if vector_type is None:
            return list(cls.DISEASE_CHARACTERISTICS.keys())
        
        return [d for d, v in cls.DISEASE_VECTORS.items() if vector_type in v]
    
    @classmethod
    def list_vectors(cls) -> List[VectorType]:
        """List all supported vector types."""
        return list(cls.VECTOR_ECOLOGY.keys())
