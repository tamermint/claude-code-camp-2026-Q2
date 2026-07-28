from pydantic import BaseModel, Field

from .constants import (ObjectAffectLocation, ObjectExtraEffect, ObjectType,
                        ObjectWear)
from .models import ExtraDescription, Flag
from .utils import _lookup_enum, lookup_value_to_dict, parse_flags, bitvector_to_numbers
import re


class Affect(BaseModel):
    """An affect that modifies a character attribute."""

    location: int = Field(..., description="Affect location code")
    note: str | None = Field(None, description="Human-readable location name")
    value: int = Field(..., description="Modifier value")

    @classmethod
    def from_fields(cls, extra_fields: list[str]) -> list["Affect"]:
        """Parse affects from the 'A' blocks in object data."""
        results = []
        for i, field in enumerate(extra_fields):
            if field == 'A':
                loc, value = (int(v) for v in extra_fields[i + 1].split())
                note = _lookup_enum(loc, ObjectAffectLocation)
                results.append(cls(location=loc, note=note, value=value))
        return results


def parse_extra_descriptions_from_fields(extra_fields: list[str]) -> list[ExtraDescription]:
    """Parse extra descriptions from the 'E' blocks in object data."""
    results = []
    i = 0
    while i < len(extra_fields):
        if extra_fields[i] == 'E':
            i += 1
            keywords = extra_fields[i].rstrip('~').split()
            i += 1
            desc_lines = []
            while i < len(extra_fields) and extra_fields[i] not in ('~', '$'):
                desc_lines.append(extra_fields[i])
                i += 1
            results.append(ExtraDescription(keywords=keywords, desc='\n'.join(desc_lines)))
        i += 1
    return results


class Object(BaseModel):
    """A CircleMUD object definition."""

    id: int = Field(..., description="Virtual number (VNUM)")
    aliases: list[str] = Field(..., description="Keywords for targeting the object")
    short_desc: str = Field(..., description="Name shown in inventory and actions")
    long_desc: str = Field(..., description="Description when object is on the ground")
    action_desc: str | None = Field(None, description="Description when used")
    type: Flag = Field(..., description="Object type (weapon, armor, etc.)")
    effects: list[Flag] = Field(default_factory=list, description="Extra effects (glow, hum, etc.)")
    wear: list[Flag] = Field(default_factory=list, description="Wear positions")
    values: list[int] = Field(..., description="Type-specific values")
    weight: int = Field(..., description="Object weight")
    cost: int = Field(..., description="Value in gold")
    rent: int = Field(..., description="Daily rent cost")
    affects: list[Affect] = Field(default_factory=list, description="Stat modifiers when worn")
    extra_descs: list[ExtraDescription] = Field(default_factory=list, description="Extra descriptions")
    triggers: list[int] = Field(default_factory=list, description="Attached DG trigger VNUMs")

    @classmethod
    def from_text(cls, text: str) -> "Object":
        """Parse a CircleMUD object definition from raw text."""
        text = text.strip()

        # 1. Extract VNUM safely, ignoring inline builder comments
        match_vnum = re.match(r"^(\d+)(.*)", text, re.DOTALL)
        if not match_vnum:
            raise ValueError("Could not extract VNUM from block")
        
        obj_id = int(match_vnum.group(1))
        remainder = match_vnum.group(2).strip()

        # 2. Extract the 4 strings using stateful regex, bypassing internal newlines
        match = re.match(r"(.*?)~(.*?)~(.*?)~(.*?)~", remainder, re.DOTALL)
        if not match:
            raise ValueError(f"Failed to find 4 tilde delimiters in object {obj_id}")

        aliases = match.group(1).strip().split()
        short_desc = match.group(2).strip()
        long_desc = match.group(3).strip()
        action_desc = match.group(4).strip() or None

        # 3. Process the remaining numerical and flag lines
        post_desc = remainder[match.end():].strip()
        fields = [line.rstrip() for line in post_desc.split('\n')]

        vector_fields = fields[0].split()
        type_flag = vector_fields[0]
        effects_bits = vector_fields[1] if len(vector_fields) > 1 else "0"
        wear_bitvector = vector_fields[5] if len(vector_fields) > 5 else vector_fields[-1]

        type_dict = lookup_value_to_dict(int(type_flag), ObjectType)
        obj_type = Flag(**type_dict)

        effects = parse_flags(effects_bits, ObjectExtraEffect)
        wear = parse_flags(wear_bitvector, ObjectWear)

        # 4. Safely extract values using the bitvector fix
        raw_values = fields[1].split()
        values = []
        for v in raw_values:
            if v.isdigit() or (v.startswith('-') and v[1:].isdigit()):
                values.append(int(v))
            else:
                decoded = sum(bitvector_to_numbers(v))
                values.append(decoded)

        # 5. Extract weight, cost, rent
        weight, cost, rent = (int(v) for v in fields[2].split()[:3])

        # 6. Pass the remaining lines to the Affect/ExtraDesc parsers
        affects = []
        extra_descs = []
        if len(fields) > 3:
            extra_fields = fields[3:]
            affects = Affect.from_fields(extra_fields)
            extra_descs = parse_extra_descriptions_from_fields(extra_fields)
            
        triggers = [
            int(field.split()[1])
            for field in fields[3:]
            if field.startswith("T ") and len(field.split()) > 1
        ]

        return cls(
            id=obj_id,
            aliases=aliases,
            short_desc=short_desc,
            long_desc=long_desc,
            action_desc=action_desc,
            type=obj_type,
            effects=effects,
            wear=wear,
            values=values,
            weight=weight,
            cost=cost,
            rent=rent,
            affects=affects,
            extra_descs=extra_descs,
            triggers=triggers,
        )