# FILE: growforge/models.py
"""
GrowForge — Data classes and dict schemas for structured data.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Plant:
    id: int = 0
    name: str = ""
    strain_id: Optional[int] = None
    strain_name: str = ""
    plant_type: str = "Photoperiod"
    genetics_type: str = "Feminized"
    stage: str = "Germination"
    environment_id: Optional[int] = None
    mother_plant_id: Optional[int] = None
    breeder_cross_id: Optional[int] = None
    start_date: str = ""
    germ_date: Optional[str] = None
    veg_date: Optional[str] = None
    flower_date: Optional[str] = None
    harvest_date: Optional[str] = None
    pot_size: str = ""
    medium: str = ""
    notes: str = ""
    is_mother: bool = False
    is_active: bool = True
    yield_grams: float = 0.0


@dataclass
class Environment:
    id: int = 0
    name: str = ""
    env_type: str = "Indoor Tent"
    medium: str = "Soil (Organic)"
    light_type: str = "LED (Full Spectrum)"
    light_wattage: int = 0
    light_schedule: str = "18/6"
    tent_size: str = ""
    notes: str = ""


@dataclass
class Event:
    id: int = 0
    plant_id: Optional[int] = None
    environment_id: Optional[int] = None
    event_type: str = ""
    event_date: str = ""
    title: str = ""
    notes: str = ""
    ph: Optional[float] = None
    ec: Optional[float] = None
    ppm: Optional[float] = None
    temp: Optional[float] = None
    humidity: Optional[float] = None
    vpd: Optional[float] = None
    water_ml: Optional[float] = None
    nutrient_mix: str = ""
    photo_path: str = ""


@dataclass
class CloneBatch:
    id: int = 0
    mother_plant_id: int = 0
    batch_name: str = ""
    cut_date: str = ""
    rooting_method: str = ""
    medium: str = ""
    num_cuts: int = 0
    notes: str = ""


@dataclass
class Clone:
    id: int = 0
    batch_id: int = 0
    clone_name: str = ""
    stage: str = "Cut Taken"
    root_date: Optional[str] = None
    transplant_date: Optional[str] = None
    status: str = "Active"
    promoted_plant_id: Optional[int] = None
    notes: str = ""


@dataclass
class Cross:
    id: int = 0
    cross_name: str = ""
    mother_plant_id: Optional[int] = None
    father_plant_id: Optional[int] = None
    mother_strain: str = ""
    father_strain: str = ""
    pollination_date: Optional[str] = None
    seed_harvest_date: Optional[str] = None
    seed_count: int = 0
    generation: str = "F1"
    goals: str = ""
    notes: str = ""


@dataclass
class Phenotype:
    id: int = 0
    cross_id: Optional[int] = None
    plant_id: Optional[int] = None
    pheno_name: str = ""
    vigor_score: int = 5
    structure_score: int = 5
    yield_score: int = 5
    terpene_score: int = 5
    resin_score: int = 5
    pest_resistance_score: int = 5
    mold_resistance_score: int = 5
    bag_appeal_score: int = 5
    potency_score: int = 5
    flavor_score: int = 5
    overall_score: float = 5.0
    is_keeper: bool = False
    flowering_days: int = 0
    stretch_ratio: float = 0.0
    notes: str = ""


@dataclass
class Reminder:
    id: int = 0
    plant_id: Optional[int] = None
    environment_id: Optional[int] = None
    reminder_type: str = ""
    due_date: str = ""
    message: str = ""
    is_recurring: bool = False
    recurrence_days: int = 0
    is_completed: bool = False
    completed_at: Optional[str] = None


@dataclass
class Strain:
    id: int = 0
    name: str = ""
    breeder: str = ""
    strain_type: str = "Hybrid"
    genetics: str = ""
    flowering_weeks_min: int = 8
    flowering_weeks_max: int = 10
    thc_range: str = ""
    cbd_range: str = ""
    yield_indoor: str = ""
    yield_outdoor: str = ""
    difficulty: str = "Moderate"
    description: str = ""
    terpenes: str = ""
    effects: str = ""
    is_autoflower: bool = False
