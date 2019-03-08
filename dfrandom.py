#!/usr/bin/env python3


"""Generate a random GURPS Dungeon Fantasy character."""


import argparse
from collections import Counter
import copy
from enum import Enum, auto
import os
import random
import re
import xml.etree.ElementTree as et


class TraitType(Enum):
    PRIMARY_ATTRIBUTE = auto()
    SECONDARY_ATTRIBUTE = auto()
    ADVANTAGE = auto()
    DISADVANTAGE = auto()
    FEATURE = auto()
    SKILL = auto()
    SPELL = auto()

PA = TraitType.PRIMARY_ATTRIBUTE
SA = TraitType.SECONDARY_ATTRIBUTE
AD = TraitType.ADVANTAGE
DI = TraitType.DISADVANTAGE
FE = TraitType.FEATURE
SK = TraitType.SKILL
SP = TraitType.SPELL


def list_levels(name, cost, trait_type, num_levels, min_level=1):
    """Return a list of num_levels tuples, each with the name,
    cost, and trait_type of that level.

    name should have a %d in it for the level number.
    cost is per level
    """
    lst = []
    for level in range(min_level, min_level + num_levels):
        tup = (name % level, cost * level, trait_type)
        lst.append(tup)
    return lst


def list_self_control_levels(name, base_cost):
    """Return a list of num_levels tuples, each with the name,
    cost, and trait_type (always DI) of that level.

    name is just the base name.
    base_cost is for a self-control number of 12.
    """
    lst = []
    lst.append(("%s (15)" % name, int(0.5 * base_cost), DI))
    lst.append(("%s (12)" % name, base_cost, DI))
    lst.append(("%s (9)" % name, int(1.5 * base_cost), DI))
    lst.append(("%s (6)" % name, 2 * base_cost, DI))
    return lst


def list_self_control_levels2(name1, base_cost1, name2, base_cost2):
    """Return a list of num_levels tuples, each with the name and
    cost of that level, for two mutually-exclusive disads.
    """
    return list_self_control_levels(name1, base_cost1) + \
           list_self_control_levels(name2, base_cost2)


def pick_from_list(lst, points):
    """Pick traits totaling exactly points from the list.

    Return a list of tuples (trait name, cost)
    lst is a list of lists of tuples (trait, cost)
    chosen traits are removed from lst
    """
    original_lst = copy.deepcopy(lst)
    traits = []
    points_left = points
    while lst and points_left != 0:
        lst2 = random.choice(lst)
        lst.remove(lst2)
        while lst2:
            tup = random.choice(lst2)
            trait, cost, trait_type = tup
            if abs(cost) <= abs(points_left):
                traits.append((trait, cost, trait_type))
                points_left -= cost
                break
            else:
                lst2.remove(tup)
    if points_left != 0:
        # If we made a pick that couldn't get the points right, retry.
        return pick_from_list(original_lst, points)
    return traits


def pick_from_list_enforcing_prereqs(lst, points, original_traits):
    """Pick traits totaling exactly points from the list.

    Return a list of tuples (trait name, cost)
    lst is a list of lists of tuples (trait, cost)
    chosen traits are removed from lst
    """
    original_lst = copy.deepcopy(lst)
    traits = []
    points_left = points
    while lst and points_left != 0:
        lst2 = random.choice(lst)
        lst.remove(lst2)
        while lst2:
            tup = random.choice(lst2)
            trait, cost, trait_type = tup
            if (abs(cost) <= abs(points_left) and
              prereq_satisfied(trait, original_traits + traits)):
                traits.append((trait, cost, trait_type))
                points_left -= cost
                break
            else:
                lst2.remove(tup)
    if points_left != 0:
        # If we made a pick that couldn't get the points right, retry.
        return pick_from_list(original_lst, points)
    return traits


def next_skill_cost(cost):
    """Return the next higher skill cost after cost."""
    if cost == 0:
        return 1
    elif cost == 1:
        return 2
    elif cost == 2:
        return 4
    else:
        return cost + 4


def pick_or_improve_skills_from_list(skills, points, traits, min_cost=1):
    """Add points to skills, and modify traits in place.

    If a skill is already in traits then bring it up to the next
    level, if enough points remain.

    Otherwise add it at the 1-point level.

    :param skills is a set of skill names
    :param points int number of points to spend
    :param traits list of (trait name, points) tuples
    """
    points_left = points
    skills_lst = list(skills)
    while skills_lst and points_left > 0:
        skill_name = random.choice(skills_lst)
        for ii, skill_tup in enumerate(traits):
            (skill_name2, cost, trait_type) = skill_tup
            if skill_name2 == skill_name:
                cost2 = next_skill_cost(cost)
                difference = cost2 - cost
                if difference <= points_left:
                    traits[ii] = (skill_name2, cost2, trait_type)
                    points_left -= difference
                    break
        else:
            cost2 = min_cost
            traits.append((skill_name, cost2, trait_type))
            points_left -= cost2


# TODO trait type headings: attributes, advantages, disads, skills, spells
# Unfortunately there are some trait names that are reused across types
# (like Climbing is both a skill and a spell), so we need to go back and
# tag all traits by type
def print_traits(traits):
    total_cost = 0
    for name, cost, trait_type in traits:
        total_cost += cost
        print("%s [%d], %s" % (name, cost, trait_type))
    print("total points: %d" % total_cost)


def generate_barbarian():
    traits = [
        ("ST 17", 63, PA),
        ("DX 13", 60, PA),
        ("IQ 10", 0, PA),
        ("HT 13", 30, PA),
        ("HP 22", 9, SA),
        ("Will 10", 0, SA),
        ("Per 12", 10, SA),
        ("FP 13", 0, SA),
        ("Basic Speed 6.0", -10, SA),
        ("Basic Move 7", 0, SA),
        ("High Pain Threshold", 10, AD),
        ("Outdoorsman 4", 40, AD),
        ("Gigantism", 0, FE),
        ("Social Stigma (Minority Group)", -10, DI),
        ("Camouflage", 1, SK),
        ("Navigation (Land)", 2, SK),
        ("Tracking", 1, SK),
        ("Brawling", 1, SK),
        ("Stealth", 2, SK),
        ("Wrestling", 2, SK),
        ("Naturalist", 1, SK),
        ("Swimming", 1, SK),
        ("Hiking", 1, SK),
        ("Running", 1, SK),
        ("Fishing", 1, SK),
        ("Animal Handling (any)", 2, SK),
        ("Disguise (Animals)", 2, SK),
        ("Weather Sense", 2, SK),
        ("Intimidation", 2, SK),
    ]
    ads1 = [
        list_levels("ST +%d", 9, PA, 3),
        list_levels("HT +%d", 10, PA, 3),
        list_levels("Per +%d", 5, SA, 6),
        [("Absolute Direction", 5, AD)],
        list_levels("Acute Hearing %d", 2, AD, 5),
        list_levels("Acute Taste and Smell %d", 2, AD, 5),
        list_levels("Acute Touch %d", 2, AD, 5),
        list_levels("Acute Vision %d", 2, AD, 5),
        [("Alcohol Tolerance", 1, AD)],
        [("Animal Empathy", 5, AD)],
        list_levels("Animal Friend %d", 5, AD, 4),
        [("Combat Reflexes", 15, AD)],
        [("Fit", 5, AD), ("Very Fit", 15, AD)],
        list_levels("Hard to Kill %d", 2, AD, 5),
        list_levels("Hard to Subdue %d", 2, AD, 5),
        list_levels("Lifting ST %d", 3, AD, 3),
        [("Luck", 15, AD), ("Extraordinary Luck", 30, AD)],
        list_levels("Magic Resistance %d", 2, AD, 5),
        [("Rapid Healing", 5, AD), ("Very Rapid Healing", 15, AD)],
        [("Recovery", 10, AD)],
        [("Resistant to Disease 3", 3, AD),
         ("Resistant to Disease 8", 5, AD)],
        [("Resistant to Poison 3", 5, AD)],
        list_levels("Signature Gear %d", 1, AD, 10),
        [("Striking ST 1", 5, SA), ("Striking ST 2", 9, SA)],
        list_levels("Temperature Tolerance %d", 1, AD, 2),
        [("Weapon Bond", 1, AD)],
    ]
    traits.extend(pick_from_list(ads1, 30))

    disads1 = [
        [("Easy to Read", -10, DI)],
        list_self_control_levels("Gullibility", -10),
        [("Language: Spoken (Native) / Written (None)", -3, DI)],
        list_levels("Low TL %d", -5, DI, 2),
        [("Odious Personal Habit (Unrefined manners)", -5, DI)],
        list_self_control_levels("Phobia (Machinery)", -5),
        [("Wealth (Struggling)", -10, DI)],
    ]
    traits.extend(pick_from_list(disads1, -10))

    disads2 = [
        [("Appearance: Unattractive", -4, DI), ("Appearance: Ugly", -8, DI)],
        list_self_control_levels("Bad Temper", -10),
        list_self_control_levels("Berserk", -10),
        list_self_control_levels("Bloodlust", -10),
        list_self_control_levels2("Compulsive Carousing", -5,
                                  "Phobia (Crowds)", -15),
        list_self_control_levels("Gluttony", -5),
        list_levels("Ham-Fisted %d", -5, DI, 2),
        [("Horrible Hangovers", -1, DI)],
        list_self_control_levels("Impulsiveness", -10),
        list_self_control_levels("Overconfidence", -5),
        [("Sense of Duty (Adventuring companions)", -5, DI)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -20))

    skills1 = [
        [("Survival (Arctic)", 1, SK)],
        [("Survival (Desert)", 1, SK)],
        [("Survival (Island/Beach)", 1, SK)],
        [("Survival (Jungle)", 1, SK)],
        [("Survival (Mountain)", 1, SK)],
        [("Survival (Plains)", 1, SK)],
        [("Survival (Swampland)", 1, SK)],
        [("Survival (Woodlands)", 1, SK)],
    ]
    traits.extend(pick_from_list(skills1, 1))

    skills2 = [
        [("Thrown Weapon (Axe/Mace)", 4, SK)],
        [("Thrown Weapon (Harpoon)", 4, SK)],
        [("Thrown Weapon (Spear)", 4, SK)],
        [("Thrown Weapon (Stick)", 4, SK)],
        [("Bolas", 4, SK)],
        [("Bow", 4, SK)],
        [("Spear Thrower", 4, SK)],
        [("Throwing", 4, SK)],
    ]
    traits.extend(pick_from_list(skills2, 4))

    skills3 = [
        [("Axe/Mace", 8, SK), ("Broadsword", 8, SK), ("Spear", 8, SK), ("Flail", 8, SK)],
        [("Shield", 8, SK)],
        [("Polearm", 16, SK)],
        [("Spear", 16, SK)],
        [("Two-Handed Axe/Mace", 16, SK)],
        [("Two-Handed Sword", 16, SK)],
        [("Two-Handed Flail", 16, SK)],
    ]
    traits.extend(pick_from_list(skills3, 16))

    skills4 = [
        [("Mimicry (Animal Sounds)", 1, SK)],
        [("Mimicry (Bird Calls)", 1, SK)],
    ]
    traits.extend(pick_from_list(skills4, 1))

    skills5 = [
        [("Forced Entry", 1, SK)],
        [("Climbing", 1, SK)],
        [("First Aid", 1, SK)],
        [("Gesture", 1, SK)],
        [("Seamanship", 1, SK)],
        [("Carousing", 1, SK)],
        [("Lifting", 1, SK)],
        [("Skiing", 1, SK)],
        [("Observation", 1, SK)],
    ]
    traits.extend(pick_from_list(skills5, 4))
    return traits


def generate_bard():
    traits = [
        ("ST 11", 10, PA),
        ("DX 12", 40, PA),
        ("IQ 14", 80, PA),
        ("HT 11", 10, PA),
        ("HP 11", 0, SA),
        ("Will 14", 0, SA),
        ("Per 14", 0, SA),
        ("FP 11", 0, SA),
        ("Basic Speed 6.0", 5, SA),
        ("Basic Move 6", 0, SA),
        ("Bardic Talent 2", 16, AD),
        ("Charisma 1", 5, AD),
        ("Musical Ability 2", 10, AD),
        ("Voice", 10, AD),
        ("Acting", 2, SK),
        ("Diplomacy", 1, SK),
        ("Fast-Talk", 1, SK),
        ("Musical Instrument (any)", 2, SK),
        ("Performance", 1, SK),
        ("Public Speaking", 1, SK),
        ("Singing", 1, SK),
        ("Fast-Draw (any)", 1, SK),
        ("Stealth", 2, SK),
        ("Current Affairs (any)", 1, SK),
        ("Savoir-Faire (High Society)", 1, SK),
        ("Interrogation", 1, SK),
        ("Merchant", 1, SK),
        ("Propaganda", 1, SK),
        ("Streetwise", 1, SK),
        ("Musical Composition", 1, SK),
        ("Carousing", 1, SK),
        ("Intimidation", 1, SK),
        ("Detect Lies", 1, SK),
        ("Heraldry", 1, SK),
        ("Poetry", 1, SK),
    ]

    build_spell_prereqs(allowed_colleges=allowed_bard_colleges)
    convert_magery_to_bardic_talent()
    add_special_bard_skills_to_spell_prereqs()

    ads1 = [
        [("Empathy (PM)", 11, AD)],
        [("Mimicry (PM)", 7, AD)],
        [("Mind Control (PM)", 35, AD)],
        [("Rapier Wit (PM)", 4, AD)],
        [("Speak With Animals (PM)", 18, AD)],
        [("Subsonic Speech (PM)", 7, AD)],
        [("Telecommunication (Telesend, PM)", 21, AD)],
        [("Terror (PM)", 21, AD)],
        [("Ultrasonic Speech (PM)", 7, AD)],
    ]
    for spell in spell_to_prereq_function:
        ads1.append([(spell, 1, SP)])
    traits.extend(pick_from_list_enforcing_prereqs(ads1, 25, traits))

    ads2 = [
        [("DX +1", 20, PA)],
        [("IQ +1", 20, PA)],
        list_levels("FP +%d", 3, SA, 8),
        [("Basic Speed +1", 20, SA)],
        list_levels("Acute Hearing %d", 2, AD, 5),
        [("Appearance: Attractive", 4, AD), ("Appearance: Handsome", 12, AD),
         ("Appearance: Very Handsome", 16, AD)],
        list_levels("Bardic Talent %d", 8, AD, 2, min_level=3),
        list_levels("Charisma %d", 5, AD, 5, min_level=2),
        [("Cultural Adaptability", 10, AD)],
        [("Eidetic Memory", 5, AD), ("Photographic Memory", 10, AD)],
        [("Honest Face", 1, AD),],
        [("Language Talent", 10, AD),],
        [("Language (Spoken: Broken / Written: None)", 1, AD)],
        [("Language (Spoken: None / Written: Broken)", 1, AD)],
        [("Language (Spoken: Accented / Written: None)", 2, AD)],
        [("Language (Spoken: Broken / Written: Broken)", 2, AD)],
        [("Language (Spoken: None / Written: Accented)", 2, AD)],
        [("Language (Spoken: Native / Written: None)", 3, AD)],
        [("Language (Spoken: Accented / Written: Broken)", 3, AD)],
        [("Language (Spoken: Broken / Written: Accented)", 3, AD)],
        [("Language (Spoken: None / Written: Native)", 3, AD)],
        [("Language (Spoken: Native / Written: Broken)", 4, AD)],
        [("Language (Spoken: Accented / Written: Accented)", 4, AD)],
        [("Language (Spoken: Broken / Written: Native)", 4, AD)],
        [("Language (Spoken: Native / Written: Accented)", 5, AD)],
        [("Language (Spoken: Accented / Written: Native)", 5, AD)],
        [("Language (Spoken: Native / Written: Native)", 6, AD)],
        [("Luck", 15), ("Extraordinary Luck", 30, AD)],
        list_levels("Musical Ability %d", 5, AD, 2, min_level=3),
        [("No Hangover", 1, AD)],
        [("Penetrating Voice", 1, AD)],
        list_levels("Signature Gear %d", 1, AD, 10),
        [("Smooth Operator 1", 15, AD)],
        [("Social Chameleon", 5, AD)],
        [("Wealth (Comfortable)", 10, AD), ("Wealth (Wealthy)", 20, AD)],
        [("Wild Talent 1", 20, AD)],
    ]
    ads2.extend(ads1)
    traits.extend(pick_from_list(ads2, 25))

    disads1 = [
        list_self_control_levels2("Chummy", -5, "Gregarious", -10),
        list_self_control_levels("Compulsive Carousing", -5),
        list_self_control_levels("Lecherousness", -15),
        [("Sense of Duty (Adventuring companions)", -5, DI)],
        list_self_control_levels("Xenophilia", -10),
    ]
    traits.extend(pick_from_list(disads1, -15))

    disads2 = [
        list_self_control_levels("Curious", -5),
        list_self_control_levels("Impulsiveness", -10),
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels("Trickster", -15),
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    disads3 = [
        [("Code of Honor (Gentleman's)", -10, DI)],
        list_self_control_levels("Compulsive Lying", -15),
        [("Odious Personal Habit (Continuous singing or strumming)", -5, DI)],
        list_self_control_levels("Post-Combat Shakes", -5),
    ]
    disads3.extend(disads2)
    traits.extend(pick_from_list(disads3, -20))

    skills1 = [
        [("Rapier", 12, SK), ("Saber", 12, SK), ("Shortsword", 12, SK), ("Smallsword", 12, SK)],
        [("Rapier", 8, SK), ("Saber", 8, SK), ("Shortsword", 8, SK), ("Smallsword", 8, SK)],
        [("Shield (Buckler)", 4, SK), ("Cloak", 4, SK), ("Main-Gauche", 4, SK)],
    ]
    traits.extend(pick_from_list(skills1, 12))

    skills2 = [
        [("Thrown Weapon (Knife)", 2, SK)],
        [("Bow", 2, SK)],
        [("Throwing", 2, SK)],
    ]
    traits.extend(pick_from_list(skills2, 2))

    skills3 = [
        [("Climbing", 1, SK)],
        [("Dancing", 1, SK)],
        [("Acrobatics", 1, SK)],
        [("Slight of Hand", 1, SK)],
        [("First Aid", 1, SK)],
        [("Gesture", 1, SK)],
        [("Connoisseur (any)", 1, SK)],
        [("Disguise", 1, SK)],
        [("Teaching", 1, SK)],
        [("Writing", 1, SK)],
        [("Mimicry (Speech)", 1, SK)],
        [("Ventriloquism", 1, SK)],
        [("Hiking", 1, SK)],
        [("Sex Appeal", 1, SK)],
        [("Scrounging", 1, SK)],
        [("Observation", 1, SK)],
    ]
    traits.extend(pick_from_list(skills3, 6))

    special_skills = []
    for spell in spell_to_prereq_function:
        if (spell, 1, SP) not in traits:
            special_skills.append([(spell, 1, SP)])
    traits.extend(pick_from_list_enforcing_prereqs(special_skills, 20, traits))

    return traits


def merge_traits(traits):
    """Merge traits like "ST 12" and "ST +2" or "Magery 3" and "Magery 4".

    Return a new traits list of (name, cost) tuples.
    """
    bare_name_to_level = {}
    bare_name_to_cost = {}
    trait_name_to_bare_name = {}
    plus_pat = "(.*) \+(\d+)$"
    level_pat = "(.*) ([0-9.]+)$"
    for trait_name, cost, trait_type in traits:
        # Look for trait names like "ST +2"
        match = re.search(plus_pat, trait_name)
        if match:
            bare_name = match.group(1)
            plus_level = int(match.group(2))
            bare_name_to_level[bare_name] += plus_level
            bare_name_to_cost[bare_name] += cost
            trait_name_to_bare_name[trait_name] = bare_name
        else:
            # Look for trait names like "Magery 3" or "Basic Speed 6.5"
            match = re.search(level_pat, trait_name)
            if match:
                bare_name = match.group(1)
                str_level = match.group(2)
                if "." in str_level:
                    level = float(str_level)
                else:
                    level = int(str_level)
                bare_name_to_level[bare_name] = max(bare_name_to_level.get(
                  bare_name, 0), level)
                bare_name_to_cost[bare_name] = bare_name_to_cost.get(
                  bare_name, 0) + cost
                trait_name_to_bare_name[trait_name] = bare_name

    traits2 = []
    bare_names_done = set()
    for trait_name, cost, trait_type in traits:
        bare_name = trait_name_to_bare_name.get(trait_name)
        if bare_name in bare_names_done:
            pass
        elif bare_name is None:
            traits2.append((trait_name, cost, trait_type))
        else:
            level = bare_name_to_level[bare_name]
            trait_name2 = "%s %d" % (bare_name, level)
            cost2 = bare_name_to_cost[bare_name]
            traits2.append((trait_name2, cost2, trait_type))
            bare_names_done.add(bare_name)
    return traits2


def generate_cleric():
    traits = [
        ("ST 12", 20, PA),
        ("DX 12", 40, PA),
        ("IQ 14", 80, PA),
        ("HT 12", 20, PA),
        ("HP 12", 0, SA),
        ("Will 14", 0, SA),
        ("Per 14", 0, SA),
        ("FP 12", 0, SA),
        ("Basic Speed 6.0", 0, SA),
        ("Basic Move 6", 0, SA),
        ("Clerical Investment", 5, AD),
        ("Power Investiture 3", 30, AD),
        ("Esoteric Medicine (Holy)", 4, AD),
        ("Exorcism", 4, AD),
        ("First Aid", 1, SK),
        ("Occultism", 1, SK),
        ("Public Speaking", 1, SK),
        ("Teaching", 1, SK),
        ("Diagnosis", 1, SK),
        ("Theology", 1, SK),
        ("Religious Ritual", 1, SK),
        ("Surgery", 2, SK),
        ("Meditation", 1, SK),
    ]
    spells = [
        # PI 1
        [("Armor", 1, SP)],
        [("Aura", 1, SP)],
        [("Body-Reading", 1, SP)],
        [("Bravery", 1, SP)],
        [("Cleansing", 1, SP)],
        [("Coolness", 1, SP)],
        [("Detect Magic", 1, SP)],
        [("Detect Poison", 1, SP)],
        [("Final Rest", 1, SP)],
        [("Lend Energy", 1, SP)],
        [("Lend Vitality", 1, SP)],
        [("Light", 1, SP)],
        [("Might", 1, SP)],
        [("Minor Healing", 1, SP)],
        [("Purify Air", 1, SP)],
        [("Purify Water", 1, SP)],
        [("Recover Energy", 1, SP)],
        [("Sense Life", 1, SP)],
        [("Sense Spirit", 1, SP)],
        [("Share Vitality", 1, SP)],
        [("Shield", 1, SP)],
        [("Silence", 1, SP)],
        [("Stop Bleeding", 1, SP)],
        [("Test Food", 1, SP)],
        [("Thunderclap", 1, SP)],
        [("Umbrella", 1, SP)],
        [("Vigor", 1, SP)],
        [("Warmth", 1, SP)],
        [("Watchdog", 1, SP)],
        # PI 2
        [("Awaken", 1, SP)],
        [("Clean", 1, SP)],
        [("Command", 1, SP)],
        [("Compel Truth", 1, SP)],
        [("Continual Light", 1, SP)],
        [("Create Water", 1, SP)],
        [("Glow", 1, SP)],
        [("Great Voice", 1, SP)],
        [("Healing Slumber", 1, SP)],
        [("Major Healing", 1, SP)],
        [("Peaceful Sleep", 1, SP)],
        [("Persuasion", 1, SP)],
        [("Purify Food", 1, SP)],
        [("Relieve Sickness", 1, SP)],
        [("Remove Contagion", 1, SP)],
        [("Resist Acid", 1, SP)],
        [("Resist Cold", 1, SP)],
        [("Resist Disease", 1, SP)],
        [("Resist Fire", 1, SP)],
        [("Resist Lightning", 1, SP)],
        [("Resist Pain", 1, SP)],
        [("Resist Poison", 1, SP)],
        [("Resist Pressure", 1, SP)],
        [("Restore Hearing", 1, SP)],
        [("Restore Memory", 1, SP)],
        [("Restore Sight", 1, SP)],
        [("Restore Speech", 1, SP)],
        [("Seeker", 1, SP)],
        [("Soilproof", 1, SP)],
        [("Stop Spasm", 1, SP)],
        [("Summon Spirit", 1, SP)],
        [("Truthsayer", 1, SP)],
        [("Turn Spirit", 1, SP)],
        [("Turn Zombie", 1, SP)],
        [("Wall of Light", 1, SP)],
        # PI 3
        [("Affect Spirits", 1, SP)],
        [("Astral Vision", 1, SP)],
        [("Breathe Water", 1, SP)],
        [("Command Spirit", 1, SP)],
        [("Create Food", 1, SP)],
        [("Cure Disease", 1, SP)],
        [("Dispel Possession", 1, SP)],
        [("Flaming Weapon", 1, SP)],
        [("Great Healing", 1, SP)],
        [("Magic Resistance", 1, SP)],
        [("Neutralize Poison", 1, SP)],
        [("Oath", 1, SP)],
        [("Relieve Madness", 1, SP)],
        [("Relieve Paralysis", 1, SP)],
        [("Repel Spirits", 1, SP)],
        [("Restoration", 1, SP)],
        [("See Secrets", 1, SP)],
        [("Silver Tongue", 1, SP)],
        [("Stone to Flesh", 1, SP)],
        [("Stop Paralysis", 1, SP)],
        [("Strengthen Will", 1, SP)],
        [("Sunbolt", 1, SP)],
        [("Sunlight", 1, SP)],
        [("Suspended Animation", 1, SP)],
        [("Water to Wine", 1, SP)],
        [("Wisdom", 1, SP)],
    ]
    ads1 = [
        [("Ally (Divine servent, PM, Summonable, 12-)", 19, AD),
         ("Ally (Divine servent, PM, Summonable, 15-)", 29, AD)],
        [("Detect evil (PM)", 18, AD),
         ("Detect good (PM)", 18, AD),
         ("Detect supernatural beings (PM)", 18, AD),
         ("Ally (Divine servent, PM, Summonable, 15-)", 29, AD)],
        [("Healing (Faith Healing, PM)", 33, AD)],
        [("Intuition (PM)", 14, AD)],
        [("Oracle (PM)", 14, AD)],
        [("Patron (Deity, PM, Special Abilities, Highly Accessible, 6-)", 36, AD),
         ("Patron (Deity, PM, Special Abilities, Highly Accessible, 9-)", 72, AD)],
        [("Resistant to Evil Supernatural Powers (PM) 3", 5, AD),
         ("Resistant to Evil Supernatural Powers (PM) 8", 7, AD)],
        [("Spirit Empathy (PM)", 9, AD)],
        [("True Faith (PM, Turning)", 24, AD)],
    ]
    ads1.extend(spells)
    # TODO Add PI 4 spells if PI 4 is selected.  (No points left after PI 5.)
    traits.extend(pick_from_list(ads1, 25))

    ads2 = [
        list_levels("ST +%d", 10, PA, 2),
        [("DX +1", 20, PA)],
        [("IQ +1", 20, PA)],
        list_levels("HT +%d", 10, PA, 2),
        list_levels("Will +%d", 5, SA, 4),
        list_levels("FP +%d", 3, SA, 6),
        list_levels("Fearlessness %d", 2, AD, 5),
        [("Unfazeable", 15, AD)],
        list_levels("Healer %d", 10, AD, 2),
        [("Language (Spoken: Broken / Written: None)", 1, AD)],
        [("Language (Spoken: None / Written: Broken)", 1, AD)],
        [("Language (Spoken: Accented / Written: None)", 2, AD)],
        [("Language (Spoken: Broken / Written: Broken)", 2, AD)],
        [("Language (Spoken: None / Written: Accented)", 2, AD)],
        [("Language (Spoken: Native / Written: None)", 3, AD)],
        [("Language (Spoken: Accented / Written: Broken)", 3, AD)],
        [("Language (Spoken: Broken / Written: Accented)", 3, AD)],
        [("Language (Spoken: None / Written: Native)", 3, AD)],
        [("Language (Spoken: Native / Written: Broken)", 4, AD)],
        [("Language (Spoken: Accented / Written: Accented)", 4, AD)],
        [("Language (Spoken: Broken / Written: Native)", 4, AD)],
        [("Language (Spoken: Native / Written: Accented)", 5, AD)],
        [("Language (Spoken: Accented / Written: Native)", 5, AD)],
        [("Language (Spoken: Native / Written: Native)", 6, AD)],
        [("Luck", 15, AD)],
        list_levels("Mind Shield %d", 4, AD, 5),
        list_levels("Power Investiture %d", 10, AD, 2, min_level=4),
        [("Resistant to Disease (PM) 3", 3, AD),
         ("Resistant to Disease (PM) 8", 5, AD)],
        list_levels("Signature Gear %d", 1, AD, 10),
    ]
    ads2.extend(ads1)
    traits.extend(pick_from_list(ads2, 20))

    disads1 = [
        [("Honesty (12)", -10, DI)],
        [("Sense of Duty (Coreligionists)", -10, DI)],
        [("Vow (No edged weapons)", -10, DI)],
    ]
    traits.extend(pick_from_list(disads1, -10))

    disads2 = [
        [("Disciplines of Faith (Ritualism)", -5, DI),
         ("Disciplines of Faith (Ritualism)", -10, DI),
         ("Disciplines of Faith (Mysticism)", -5, DI),
         ("Disciplines of Faith (Mysticism)", -10, DI)],
        [("Fanaticism", -15, DI)],
        [("Intolerance (Evil religions)", -5, DI),
         ("Intolerance (All other religions)", -10, DI)],
        [("Vow (Chastity)", -5, DI), ("Vow (Vegetarianism)", -5, DI)],
        [("Wealth (Struggling)", -10, DI), ("Wealth (Poor)", -15, DI)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    disads3 = [
        list_self_control_levels("Charitable", -15),
        list_self_control_levels("Compulsive Generosity", -5) +\
            list_self_control_levels("Miserliness", -10),
        list_self_control_levels("Gluttony", -5),
        list_self_control_levels("Overconfidence", -5),
        [("Overweight", -1, DI), ("Fat", -3, DI)],
        list_self_control_levels("Selfless", -5),
        [("Sense of Duty (Adventuring companions)", -5, DI)],
        [("Stubbornness", -5, DI)],
        list_self_control_levels("Truthfulness", -5),
        [("Weirdness Magnet", -15, DI)],
    ]
    disads3.extend(disads2)
    traits.extend(pick_from_list(disads3, -25))

    skills1 = [
        [("Innate Attack", 4, SK)],
        [("Throwing", 4, SK)],
        [("Sling", 4, SK)],
    ]
    traits.extend(pick_from_list(skills1, 4))

    skills2 = [
        [("Axe/Mace", 8, SK), ("Broadsword", 8, SK), ("Flail", 8, SK)],
        [("Shield", 4, SK)],
        [("Staff", 12, SK)],
    ]
    traits.extend(pick_from_list(skills2, 12))

    skills3 = [
        [("Hidden Lore (Demons)", 1, SK)],
        [("Hidden Lore (Spirits)", 1, SK)],
        [("Hidden Lore (Undead)", 1, SK)],
    ]
    traits.extend(pick_from_list(skills3, 1))

    skills4 = [
        [("Climbing", 1, SK)],
        [("Stealth", 1, SK)],
        [("Gesture", 1, SK)],
        [("Panhandling", 1, SK)],
        [("Savoir-Faire (High Society)", 1, SK)],
        [("Research", 1, SK)],
        [("Writing", 1, SK)],
        [("Hiking", 1, SK)],
        [("Scrounging", 1, SK)],
        [("Observation", 1, SK)],
        [("Search", 1, SK)],
    ]
    traits.extend(pick_from_list(skills4, 5))

    trait_names = set((trait[0] for trait in traits))
    if ("Power Investiture 4" in trait_names or
        "Power Investiture 5" in trait_names):
        spells.extend([
            [("Astral Block", 1, SP)],
            [("Banish", 1, SP)],
            [("Continual Sunlight", 1, SP)],
            [("Dispel Magic", 1, SP)],
            [("Divination", 1, SP)],
            [("Essential Food", 1, SP)],
            [("Gift of Letters", 1, SP)],
            [("Gift of Tongues", 1, SP)],
            [("Instant Neutralize Poison", 1, SP)],
            [("Instant Restoration", 1, SP)],
            [("Monk's Banquet", 1, SP)],
            [("Regeneration", 1, SP)],
            [("Suspend Curse", 1, SP)],
            [("Vigil", 1, SP)],
        ])
        if "Power Investiture 5" in trait_names:
            spells.extend([
                [("Bless", 1, SP)],
                [("Curse", 1, SP)],
                [("Earthquake", 1, SP)],
                [("Entrap Spirit", 1, SP)],
                [("Instant Regeneration", 1, SP)],
                [("Pentagram", 1, SP)],
                [("Remove Curse", 1, SP)],
                [("Storm", 1, SP)],
                [("Suspend Mana", 1, SP)],
            ])
    traits.extend(pick_from_list(spells, 20))
    return traits


def generate_druid():
    traits = [
        ("ST 11", 10, PA),
        ("DX 12", 40, PA),
        ("IQ 14", 80, PA),
        ("HT 13", 30, PA),
        ("HP 11", 0, SA),
        ("Will 14", 0, SA),
        ("Per 14", 0, SA),
        ("FP 13", 0, SA),
        ("Basic Speed 6.0", -5, SA),
        ("Basic Move 6", 0, SA),
        ("Green Thumb 1", 5, AD),
        ("Power Investiture (Druidic) 3", 30, AD),
        ("Esoteric Medicine (Druidic)", 4, SK),
        ("Herb Lore", 4, SK),
        ("Naturalist", 2, SK),
        ("Camouflage", 1, SK),
        ("Animal Handling (any)", 1, SK),
        ("Disguise (Animals)", 1, SK),
        ("Weather Sense", 1, SK),
        ("Pharmacy (Herbal)", 1, SK),
        ("Religious Ritual (Druidic)", 1, SK),
        ("Theology (Druidic)", 1, SK),
        ("Veterinary", 1, SK),
        ("Climbing", 2, SK),
        ("Stealth", 2, SK),
        ("Hiking", 1, SK),
    ]

    spells = [
        # PI 1
        [("Beast-Rouser", 1, SP)],
        [("Beast-Soother", 1, SP)],
        [("Detect Magic", 1, SP)],
        [("Detect Poison", 1, SP)],
        [("Extinguish Fire", 1, SP)],
        [("Find Direction", 1, SP)],
        [("Hawk Vision", 1, SP)],
        [("Identify Plant", 1, SP)],
        [("Master", 1, SP)],
        [("No-Smell", 1, SP)],
        [("Purify Air", 1, SP)],
        [("Purify Earth", 1, SP)],
        [("Purify Water", 1, SP)],
        [("Quick March", 1, SP)],
        [("Recover Energy", 1, SP)],
        [("Seek Coastline", 1, SP)],
        [("Seek Earth", 1, SP)],
        [("Seek Food", 1, SP)],
        [("Seek Pass", 1, SP)],
        [("Seek Plant", 1, SP)],
        [("Seek Water", 1, SP)],
        [("Sense Life", 1, SP)],
        [("Tell Position", 1, SP)],
        [("Umbrella", 1, SP)],
        # PI 2
        [("Animal Control", 1, SP)],
        [("Beast Link", 1, SP)],
        [("Beast Seeker", 1, SP)],
        [("Beast Speech", 1, SP)],
        [("Bless Plants", 1, SP)],
        [("Cure Disease", 1, SP)],
        [("Fog", 1, SP)],
        [("Frost", 1, SP)],
        [("Heal Plant", 1, SP)],
        [("Hide Path", 1, SP)],
        [("Know Location", 1, SP)],
        [("Light Tread", 1, SP)],
        [("Mystic Mist", 1, SP)],
        [("Neutralize Poison", 1, SP)],
        [("Pathfinder", 1, SP)],
        [("Plant Growth", 1, SP)],
        [("Plant Vision", 1, SP)],
        [("Pollen Cloud", 1, SP)],
        [("Predict Earth Movement", 1, SP)],
        [("Predict Weather", 1, SP)],
        [("Purify Food", 1, SP)],
        [("Repel Animal", 1, SP)],
        [("Rider", 1, SP)],
        [("Rider Within", 1, SP)],
        [("Shape Air", 1, SP)],
        [("Shape Earth", 1, SP)],
        [("Shape Plant", 1, SP)],
        [("Shape Water", 1, SP)],
        [("Spider Silk", 1, SP)],
        [("Wall of Wind", 1, SP)],
        [("Weather Dome", 1, SP)],
        [("Windstorm", 1, SP)],
        # PI 3
        [("Animate Plant", 1, SP)],
        [("Beast Summoning", 1, SP)],
        [("Blossom", 1, SP)],
        [("Breathe Water", 1, SP)],
        [("Clouds", 1, SP)],
        [("Conceal", 1, SP)],
        [("Create Plant", 1, SP)],
        [("False Tracks", 1, SP)],
        [("Forest Warning", 1, SP)],
        [("Freeze", 1, SP)],
        [("Instant Neutralize Poison", 1, SP)],
        [("Melt Ice", 1, SP)],
        [("Plant Control", 1, SP)],
        [("Plant Sense", 1, SP)],
        [("Plant Speech", 1, SP)],
        [("Protect Animal", 1, SP)],
        [("Rain", 1, SP)],
        [("Rain of Nuts", 1, SP)],
        [("Rejuvenate Plant", 1, SP)],
        [("Remember Path", 1, SP)],
        [("Resist Cold", 1, SP)],
        [("Resist Lightning", 1, SP)],
        [("Resist Pressure", 1, SP)],
        [("Snow", 1, SP)],
        [("Snow Shoes", 1, SP)],
        [("Summon Elemental", 1, SP)],
        [("Tangle Growth", 1, SP)],
        [("Walk Through Plants", 1, SP)],
        [("Walk Through Wood", 1, SP)],
        [("Water Vision", 1, SP)],
        [("Waves", 1, SP)],
        [("Whirlpool", 1, SP)],
        [("Wind", 1, SP)],
    ]
    ads1 = [
        [("Ally (Nature spirit or totem beast, PM, Summonable, 12-)", 19, AD),
         ("Ally (Nature spirit or totem beast, PM, Summonable, 15-)", 29, AD)],
        [("Animal Empathy (PM)", 5, AD)],
        [("Channeling (PM, Nature Spirits)", 4, AD)],
        [("Damage Resistance 1 (Limited Elemental, PM)", 4, AD),
         ("Damage Resistance 2 (Limited Elemental, PM)", 7, AD)],
        [("Detect (Plants, PM)", 18, AD),
         ("Detect (Animals, PM)", 18, AD),
         ("Detect (Anything Alive, PM)", 27, AD)],
        [("Medium (PM, Nature Spirits)", 4, AD)],
        [("Mind Control (Animals Only, PM)", 33, AD)],
        [("Plant Empathy (PM)", 5, AD)],
        [("Speak With Animals (PM)", 23, AD)],
        [("Speak With Plants (PM)", 14, AD)],
        [("Terrain Adaptation (Ice, PM)", 5, AD),
         ("Terrain Adaptation (Mud, PM)", 5, AD),
         ("Terrain Adaptation (Snow, PM)", 5, AD)],
    ]
    ads1.extend(spells)
    # TODO Add PI 4 spells if PI 4 is selected.  (No points left after PI 5.)
    traits.extend(pick_from_list(ads1, 20))

    ads2 = [
        [("IQ +1", 20, PA)],
        list_levels("HT +%d", 10, PA, 2),
        list_levels("Per +%d", 5, SA, 4),
        list_levels("FP +%d", 3, SA, 6),
        list_levels("Animal Friend %d", 5, AD, 4),
        list_levels("Green Thumb %d", 5, AD, 3, min_level=2),
        list_levels("Healer %d", 10, AD, 2),
        [("Intuition", 15, AD)],
        [("Luck", 15, AD)],
        list_levels("Mind Shield %d", 4, AD, 5),
        list_levels("Outdoorsman %d", 10, AD, 2),
        list_levels("Power Investiture (Druidic) %d", 10, AD, 2, min_level=4),
        [("Resistant to Disease (PM) 3", 3, AD),
         ("Resistant to Disease (PM) 8", 5, AD)],
        list_levels("Signature Gear %d", 1, AD, 10),
        [("Spirit Empathy", 10, AD)],
    ]
    ads2.extend(ads1)
    traits.extend(pick_from_list(ads2, 20))

    disads1 = [
        [("Disciplines of Faith (Ritualism)", -5, DI),
         ("Disciplines of Faith (Ritualism)", -10, DI),
         ("Disciplines of Faith (Mysticism)", -5, DI),
         ("Disciplines of Faith (Mysticism)", -10, DI)],
        [("Sense of Duty (Wild Nature)", -15, DI)],
        [("Vow (Vegetarianism)", -5, DI)],
        [("Vow (Never Sleep Indoors)", -10, DI)],
        [("Wealth (Struggling)", -10, DI), ("Wealth (Poor)", -15, DI)],
    ]
    traits.extend(pick_from_list(disads1, -20))

    disads2 = [
        [("Intolerance (Urbanites)", -5, DI)],
        list_self_control_levels("Loner", -5),
        [("No Sense of Humor", -10, DI)],
        [("Odious Personal Habit (Dirty Hippy)", -5, DI)],
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels("Phobia (Crowds)", -15),
        list_self_control_levels("Phobia (Fire)", -5),
        list_self_control_levels("Phobia (Machinery)", -5),
        [("Stubbornness", -5, DI)],
        [("Weirdness Magnet", -15, DI)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -25))

    skills1 = [
        [("Innate Attack", 4, SK)],
        [("Thrown Weapon (Spear)", 4, SK)],
        [("Thrown Weapon (Stick)", 4, SK)],
        [("Bolas", 4, SK)],
        [("Lasso", 4, SK)],
        [("Throwing", 4, SK)],
        [("Blowpipe", 4, SK)],
        [("Net", 4, SK)],
        [("Sling", 4, SK)],
    ]
    traits.extend(pick_from_list(skills1, 4))

    skills2 = [
        [("Axe/Mace", 8, SK), ("Broadsword", 8, SK), ("Shortsword", 8, SK), ("Spear", 8, SK)],
        [("Shield", 4, SK)],
        [("Spear", 12, SK)],
        [("Staff", 12, SK)],
    ]
    traits.extend(pick_from_list(skills2, 12))

    skills3 = [
        [("Hidden Lore (Elementals)", 1, SK)],
        [("Hidden Lore (Faeries)", 1, SK)],
        [("Hidden Lore (Nature Spirits)", 1, SK)],
    ]
    traits.extend(pick_from_list(skills3, 1))

    skills4 = [
        [("Mimicry (Animal Sounds)", 1, SK)],
        [("Mimicry (Bird Calls)", 1, SK)],
    ]
    traits.extend(pick_from_list(skills4, 1))

    skills5 = [
        [("Survival (Arctic)", 1, SK)],
        [("Survival (Desert)", 1, SK)],
        [("Survival (Island/Beach)", 1, SK)],
        [("Survival (Jungle)", 1, SK)],
        [("Survival (Mountain)", 1, SK)],
        [("Survival (Plains)", 1, SK)],
        [("Survival (Swampland)", 1, SK)],
        [("Survival (Woodlands)", 1, SK)],
    ]
    traits.extend(pick_from_list(skills5, 1))

    skills5 = [
        [("Knife", 1, SK)],
        [("First Aid", 1, SK)],
        [("Gesture", 1, SK)],
        [("Animal Handling (any other)", 1, SK)],
        [("Hidden Lore (Elementals)", 1, SK)],
        [("Hidden Lore (Faeries)", 1, SK)],
        [("Hidden Lore (Nature Spirits)", 1, SK)],
        [("Teaching", 1, SK)],
        [("Diagnosis", 1, SK)],
        [("Poisons", 1, SK)],
    ]
    # Avoid duplicate Hidden Lore
    for trait in traits:
        if trait in skills5:
            skills5.remove(trait)
    traits.extend(pick_from_list(skills5, 3))

    trait_names = set((trait[0] for trait in traits))
    if ("Power Investiture (Druidic) 4" in trait_names or
        "Power Investiture (Druidic) 5" in trait_names):
        spells.extend([
            [("Beast Possession", 1, SP)],
            [("Blight", 1, SP)],
            [("Body of Slime", 1, SP)],
            [("Body of Water", 1, SP)],
            [("Body of Wind", 1, SP)],
            [("Body of Wood", 1, SP)],
            [("Control Elemental", 1, SP)],
            [("Create Animal", 1, SP)],
            [("Create Spring", 1, SP)],
            [("Dispel Magic", 1, SP)],
            [("Dry Spring", 1, SP)],
            [("Frostbite", 1, SP)],
            [("Hail", 1, SP)],
            [("Lightning", 1, SP)],
            [("Plant Form", 1, SP)],
            [("Sandstorm", 1, SP)],
            [("Shapeshifting", 1, SP)],
            [("Storm", 1, SP)],
            [("Strike Barren", 1, SP)],
            [("Tide", 1, SP)],
            [("Wither Plant", 1, SP)],
        ])
        if "Power Investiture (Druidic) 5" in trait_names:
            spells.extend([
                [("Alter Terrain", 1, SP)],
                [("Arboreal Immurement", 1, SP)],
                [("Create Elemental", 1, SP)],
                [("Entombment", 1, SP)],
                [("Partial Shapeshifting", 1, SP)],
                [("Permanent Beast Possession", 1, SP)],
                [("Permanent Shapeshifting", 1, SP)],
                [("Plant Form Other", 1, SP)],
                [("Shapeshift Others", 1, SP)],
            ])
    traits.extend(pick_from_list(spells, 20))
    return traits


def generate_holy_warrior():
    traits = [
        ("ST 13", 30, PA),
        ("DX 13", 60, PA),
        ("IQ 12", 40, PA),
        ("HT 13", 30, PA),
        ("HP 13", 0, SA),
        ("Will 14", 10, SA),
        ("Per 12", 0, SA),
        ("FP 13", 0, SA),
        ("Basic Speed 6.0", -10, SA),
        ("Basic Move 6", 0, SA),
        ("Born War Leader 1", 5, AD),
        ("Holiness 2", 10, AD),
        ("Shtick (Foes slain personally can't rise as undead)", 1, AD),
        ("Exorcism", 4, SK),
        ("Brawling", 2, SK),
        ("Wrestling", 4, SK),
        ("Leadership", 1, SK),
        ("Physiology (monster type)", 4, SK),
        ("Psychology (monster type)", 4, SK),
        ("Strategy", 2, SK),
        ("Tactics", 2, SK),
        ("Intimidation", 1, SK),
        ("Religious Ritual", 1, SK),
        ("Theology", 1, SK),
        ("Meditation", 1, SK),
        ("Esoteric Medicine (Holy)", 1, SK),
    ]

    ads1 = [
        [("Higher Purpose (Slay Demons)", 5, SK),
         ("Higher Purpose (Slay Undead)", 5, SK)],
    ]
    traits.extend(pick_from_list(ads1, 5))

    # Merge the two lists since extra points can go either way.
    ads2 = [
        [("Ally (Divine servent, PM, Summonable, 12-)", 19, AD),
         ("Ally (Divine servent, PM, Summonable, 15-)", 29, AD)],
        [("Detect evil (PM)", 18, AD),
         ("Detect good (PM)", 18, AD),
         ("Detect supernatural beings (PM)", 18, AD),
         ("Ally (Divine servent, PM, Summonable, 15-)", 29, AD)],
        [("Healing (Faith Healing, PM)", 33, AD)],
        [("Intuition (PM)", 14, AD)],
        [("Oracle (PM)", 14, AD)],
        [("Patron (Deity, PM, Special Abilities, Highly Accessible, 6-)", 36, AD),
         ("Patron (Deity, PM, Special Abilities, Highly Accessible, 9-)", 72, AD)],
        [("Resistant to Evil Supernatural Powers (PM) 3", 5, AD),
         ("Resistant to Evil Supernatural Powers (PM) 8", 7, AD)],
        [("Spirit Empathy (PM)", 9, AD)],
        [("True Faith (PM, Turning)", 24, AD)],
        list_levels("ST +%d", 10, PA, 2),
        [("DX +1", 20, PA)],
        list_levels("HT +%d", 10, PA, 2),
        list_levels("HP +%d", 2, PA, 3),
        list_levels("Will +%d", 5, SA, 5),
        list_levels("Born War Leader %d", 5, AD, 3, min_level=2),
        [("Combat Reflexes", 15, AD)],
        [("Enhanced Block 1", 5, AD)],
        [("Enhanced Parry 1 (One Melee Weapon Skill)", 5, AD)],
        list_levels("Fearlessness %d", 2, AD, 5),
        [("Unfazeable", 15, AD)],
        list_levels("Hard to Kill %d", 2, AD, 5),
        list_levels("Hard to Subdue %d", 2, AD, 5),
        [("High Pain Threshold", 10, AD)],
        [("Higher Purpose (Slay Demons)", 5, AD),
         ("Higher Purpose (Slay Undead)", 5, AD)],
        list_levels("Holiness %d", 5, AD, 2, min_level=3),
        [("Luck", 15, AD)],
        list_levels("Magic Resistance %d", 2, AD, 5),
        [("Rapid Healing", 5, AD)],
        [("Recovery", 10, AD)],
        [("Resistant to Disease 3", 3, AD),
         ("Resistant to Disease 8", 5, AD)],
        [("Resistant to Poison 3", 5, AD)],
        list_levels("Signature Gear %d", 1, AD, 10),
        list_levels("Striking ST %d", 5, AD, 2),
        [("Weapon Bond", 1, AD)],
    ]
    ads2.extend(ads1)
    # Avoid duplicate Higher Purpose
    for trait in traits:
        if trait in ads2:
            ads2.remove(trait)
    traits.extend(pick_from_list(ads2, 50))

    disads1 = [
        [("Honesty (12)", -10, DI)],
        [("Sense of Duty (Good entities)", -10, DI)],
        [("Vow (Own no more than horse can carry)", -10, DI)],
    ]
    traits.extend(pick_from_list(disads1, -10))

    disads2 = [
        list_self_control_levels("Charitable", -15),
        list_self_control_levels("Compulsive Generosity", -5),
        list_self_control_levels("Compulsive Vowing", -5),
        [("Disciplines of Faith (Ritualism)", -5, DI),
         ("Disciplines of Faith (Ritualism)", -10, DI),
         ("Disciplines of Faith (Mysticism)", -5, DI),
         ("Disciplines of Faith (Mysticism)", -10, DI)],
        [("Fanaticism", -15, DI)],
        [("Intolerance (Evil religions)", -5, DI),
         ("Intolerance (All other religions)", -10, DI)],
        list_self_control_levels("Selfless", -5),
        list_self_control_levels("Truthfulness", -5),
        [("Vow (Chastity)", -5, DI)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    disads3 = [
        list_self_control_levels("Bloodlust", -10),
        [("Code of Honor (Chivalry)", -15, DI)],
        [("Easy to Read", -10, DI)],
        [("No Sense of Humor", -10, DI)],
        list_self_control_levels("Overconfidence", -5),
        [("Sense of Duty (Adventuring companions)", -5, DI)],
        [("Stubbornness", -5, DI)],
    ]
    disads3.extend(disads2)
    traits.extend(pick_from_list(disads3, -15))

    skills1 = [
        [("Hidden Lore (Demons)", 2, SK)],
        [("Hidden Lore (Undead)", 2, SK)],
    ]
    traits.extend(pick_from_list(skills1, 2))

    skills2 = [
        [("Crossbow", 4, SK)],
        [("Thrown Weapon (Axe/Mace)", 4, SK)],
        [("Thrown Weapon (Spear)", 4, SK)],
        [("Throwing", 4, SK)],
    ]
    traits.extend(pick_from_list(skills2, 4))

    skills3 = [
        [("Axe/Mace", 12, SK), ("Broadsword", 12, SK), ("Spear", 12, SK), ("Flail", 12, SK)],
        [("Shield", 8, SK)],
        [("Polearm", 20, SK)],
        [("Spear", 20, SK)],
        [("Two-Handed Sword", 20, SK)],
    ]
    traits.extend(pick_from_list(skills3, 20))

    skills4 = [
        [("Fast-Draw (any)", 1, SK)],
        [("Climbing", 1, SK)],
        [("Lance", 1, SK)],
        [("Riding (Horse)", 1, SK)],
        [("Stealth", 1, SK)],
        [("First Aid", 1, SK)],
        [("Gesture", 1, SK)],
        [("Interrogation", 1, SK)],
        [("Physiology (other monster type)", 1, SK)],
        [("Psychology (other monster type)", 1, SK)],
        [("Hiking", 1, SK)],
        [("Observation", 1, SK)],
    ]
    traits.extend(pick_from_list(skills4, 5))
    return traits


def generate_knight():
    traits = [
        ("ST 14", 40, PA),
        ("DX 14", 80, PA),
        ("IQ 10", 0, PA),
        ("HT 13", 30, PA),
        ("HP 14", 0, SA),
        ("Will 10", 0, SA),
        ("Per 10", 0, SA),
        ("FP 13", 0, SA),
        ("Basic Speed 6.0", -15, SA),
        ("Basic Move 6", 0, SA),
        ("Born War Leader 2", 10, AD),
        ("Combat Reflexes", 15, AD),
        ("High Pain Threshold", 10, AD),
        ("Fast-Draw (any)", 1, SK),
        ("Knife", 1, SK),
        ("Shield", 4, SK),
        ("Connoisseur (Weapons)", 4, SK),
        ("Leadership", 1, SK),
        ("Strategy", 2, SK),
        ("Tactics", 2, SK),
    ]

    ads1 = [
        list_levels("ST +%d", 10, PA, 6),
        list_levels("DX +%d", 20, PA, 3),
        list_levels("HT +%d", 10, PA, 6),
        list_levels("HP +%d", 2, SA, 4),
        list_levels("Basic Speed +%d", 20, SA, 2),
        [("Alcohol Tolerance", 1, AD)],
        list_levels("Born War Leader %d", 5, AD, 2, min_level=3),
        [("Enhanced Block 1", 5, AD)],
        [("Enhanced Parry 1 (One Melee Weapon Skill)", 5, AD)],
        list_levels("Fearlessness %d", 2, AD, 5),
        [("Fit", 5, AD), ("Very Fit", 15, AD)],
        list_levels("Hard to Kill %d", 2, AD, 5),
        list_levels("Hard to Subdue %d", 2, AD, 5),
        [("Luck", 15, AD), ("Extraordinary Luck", 30, AD)],
        [("Penetrating Voice", 1, AD)],
        [("Rapid Healing", 5, AD)],
        [("Recovery", 10, AD)],
        list_levels("Signature Gear %d", 1, AD, 10),
        list_levels("Striking ST %d", 5, AD, 2),
        [("Weapon Bond", 1, AD)],
        [("Weapon Master (One weapon)", 20, AD),
         ("Weapon Master (Two weapons normally used together)", 25, AD),
         ("Weapon Master (Small class of weapons)", 30, AD),
         ("Weapon Master (Medium class of weapons)", 35, AD),
         ("Weapon Master (Large class of weapons)", 40, AD),
         ("Weapon Master (All muscle-powered weapons)", 45, AD)],
    ]
    traits.extend(pick_from_list(ads1, 60))

    disads1 = [
        list_self_control_levels("Bad Temper", -10),
        list_self_control_levels("Bloodlust", -10),
        [("Code of Honor (Pirate's)", -5, DI), ("Code of Honor (Soldier's)", -10, DI),
         ("Code of Honor (Chivalry)", -15, DI)],
        list_self_control_levels(
          "Obsession (Slay some specific type of monster)", -5),
        [("One Eye", -15, DI)],
        [("Sense of Duty (Nation)", -10, DI)],
        [("Vow (Never resist a challenge to combat)", -10, DI)],
        [("Wounded", -5, DI)],
    ]
    traits.extend(pick_from_list(disads1, -20))

    disads2 = [
        list_self_control_levels("Bully", -10),
        list_self_control_levels("Compulsive Carousing", -5),
        list_self_control_levels("Greed", -15),
        list_self_control_levels("Honesty", -10),
        list_self_control_levels("Lecherousness", -15),
        list_self_control_levels("Overconfidence", -5),
        [("Sense of Duty (Adventuring companions)", -5, DI)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    skills1 = [
        [("Brawling", 2, SK)],
        [("Boxing", 2, SK)],
    ]
    traits.extend(pick_from_list(skills1, 2))

    skills2 = [
        [("Sumo Wrestling", 2, SK)],
        [("Wrestling", 2, SK)],
    ]
    traits.extend(pick_from_list(skills2, 2))

    skills3 = [
        [("Crossbow", 4, SK)],
        [("Thrown Weapon (Axe/Mace)", 4, SK)],
        [("Thrown Weapon (Spear)", 4, SK)],
        [("Bow", 4, SK)],
        [("Throwing", 4, SK)],
        [("Sling", 4, SK)],
    ]
    traits.extend(pick_from_list(skills3, 4))

    skills4 = [
        [("Axe/Mace", 24, SK)],
        [("Broadsword", 24, SK)],
        [("Polearm", 24, SK)],
        [("Shortsword", 24, SK)],
        [("Spear", 24, SK)],
        [("Two-Handed Sword", 24, SK)],
        [("Flail", 24, SK)],
        [("Axe/Mace", 12, SK)],
        [("Broadsword", 12, SK)],
        [("Polearm", 12, SK)],
        [("Shortsword", 12, SK)],
        [("Spear", 12, SK)],
        [("Two-Handed Sword", 12, SK)],
        [("Flail", 12, SK)],
        [("Axe/Mace", 8, SK)],
        [("Broadsword", 8, SK)],
        [("Lance", 8, SK)],
        [("Polearm", 8, SK)],
        [("Riding (Horse)", 8, SK)],
        [("Shortsword", 8, SK)],
        [("Spear", 8, SK)],
        [("Two-Handed Sword", 8, SK)],
        [("Flail", 8, SK)],
    ]
    traits.extend(pick_from_list(skills4, 24))

    skills5 = [
        [("Armoury (Body Armor)", 4, SK)],
        [("Armoury (Melee Weapons)", 4, SK)],
    ]
    traits.extend(pick_from_list(skills5, 4))

    skills6 = [
        [("Forced Entry", 1, SK)],
        [("Climbing", 1, SK)],
        [("Stealth", 1, SK)],
        [("First Aid", 1, SK)],
        [("Gesture", 1, SK)],
        [("Savoir-Faire (High Society)", 1, SK)],
        [("Gambling", 1, SK)],
        [("Heraldry", 1, SK)],
        [("Streetwise", 1, SK)],
        [("Carousing", 1, SK)],
        [("Hiking", 1, SK)],
        [("Intimidation", 1, SK)],
        [("Scrounging", 1, SK)],
        [("Observation", 1, SK)],
    ]
    traits.extend(pick_from_list(skills6, 4))
    return traits


def generate_martial_artist():
    traits = [
        ("ST 11", 10, PA),
        ("DX 16", 120, PA),
        ("IQ 10", 0, PA),
        ("HT 12", 20, PA),
        ("HP 11", 0, SA),
        ("Will 11", 5, SA),
        ("Per 10", 0, SA),
        ("FP 12", 0, SA),
        ("Basic Speed 7.0", 0, SA),
        ("Basic Move 8", 5, SA),
        ("Chi Talent 2", 30, AD),
        ("Trained by a Master", 30, AD),
        ("Disciples of Faith (Chi Rituals)", -10, DI),
        ("Jumping", 1, SK),
        ("Acrobatics", 2, SK),
        ("Judo", 2, SK),
        ("Karate", 2, SK),
        ("Stealth", 1, SK),
        ("Meditation", 2, SK),
        ("Tactics", 4, SK),
    ]

    special_skills = [
        [("Immovable Stance", 2, SK)],
        [("Light Walk", 2, SK)],
        [("Parry Missile Weapons", 2, SK)],
        [("Push", 2, SK)],
        [("Breaking Blow", 2, SK)],
        [("Flying Leap", 2, SK)],
        [("Pressure Points", 2, SK)],
        [("Breath Control", 2, SK)],
        [("Kiai", 2, SK)],
        [("Body Control", 2, SK)],
        [("Mental Strength", 2, SK)],
        [("Mind Block", 2, SK)],
        [("Autohypnosis", 2, SK)],
        [("Power Blow", 2, SK)],
        [("Esoteric Medicine", 2, SK)],
        [("Blind Fighting", 2, SK)],
    ]

    ads1 = [
        [("Catfall (PM)", 9, AD)],
        [("DR 1 (Tough Skin, PM)", 3, AD), ("DR 2 (Touch Skin, PM)", 5, AD)],
        [("Danger Sense (PM)", 14, AD)],
        [("Enhanced Move 0.5 (Ground, PM)", 9, AD),
         ("Enhanced Move 1 (Ground, PM)", 18, AD)],
        [("Extra Attack 1 (PM)", 23, AD), ("Extra Attack 2 (PM)", 45, AD)],
        [("Metabolism Control 1 (PM)", 5, AD), ("Metabolism Control 2 (PM)", 9, AD),
         ("Metabolism Control 3 (PM)", 14, AD), ("Metabolism Control 4 (PM)", 18, AD),
         ("Metabolism Control 5 (PM)", 23, AD)],
        [("Perfect Balance (PM)", 14, AD)],
        [("Regeneration (Slow, PM)", 9, AD),
         ("Regeneration (Regular, PM)", 23, AD),
         ("Regeneration (Fast, PM)", 45, AD)],
        [("Resistant to Metabolic Hazards +3 (PM)", 9, AD),
         ("Resistant to Metabolic Hazards +8 (PM)", 14, AD)],
        [("Striking ST 1 (PM)", 5, AD), ("Striking ST 2 (PM)", 9, AD)],
        list_levels("Super Jump %d (PM)", 9, AD, 2),
    ]
    ads1.extend(special_skills[:])
    traits.extend(pick_from_list(ads1, 20))

    ads2 = [
        list_levels("ST +%d", 10, PA, 2),
        [("DX +1", 20, PA)],
        [("IQ +1", 20, PA)],
        list_levels("HT +%d", 10, PA, 2),
        list_levels("Will +%d", 5, SA, 4),
        list_levels("Per +%d", 5, SA, 4),
        list_levels("FP +%d", 3, SA, 6),
        [("Basic Speed +1", 20, SA)],
        list_levels("Basic Move +%d", 5, SA, 2),
        [("Ambidexterity", 5, AD)],
        [("Chi Talent 3", 15, AD)],
        [("Combat Reflexes", 15, AD)],
        [("Enhanced Dodge 1", 15, AD)],
        list_levels("Enhanced Parry %d (Unarmed)", 5, AD, 2),
        [("Fit", 5, AD), ("Very Fit", 15, AD)],
        [("Flexibility", 5, AD), ("Double-Jointed", 15, AD)],
        [("High Pain Threshold", 10, AD)],
        [("Luck", 15, AD)],
        list_levels("Magic Resistance %d", 2, AD, 5),
        list_levels("Mind Shield %d", 4, AD, 5),
        list_levels("Signature Gear %d", 1, AD, 10),
        [("Unfazeable", 15, AD)],
        [("Weapon Bond", 1, AD)],
        [("Weapon Master (One exotic weapon)", 20, AD)],
        [("Wild Talent 1", 20, AD)],
    ]
    ads2.extend(ads1)
    traits.extend(pick_from_list(ads2, 20))

    disads1 = [
        [("Code of Honor (Bushido)", -15, DI)],
        list_self_control_levels("Compulsive Vowing", -5),
        list_self_control_levels("Honesty", -10),
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels(
          "Obsession (Perfect my art at any cost!)", -10),
        [("Social Stigma (Minority Group)", -10, DI)],
        [("Vow (Vegetarianism)", -5, DI)],
        [("Vow (Silence)", -10, DI)],
        [("Vow (Always Fight Unarmed)", -15, DI)],
        [("Wealth (Struggling)", -10, DI), ("Wealth (Poor)", -15, DI),
         ("Wealth (Dead Broke)", -25, DI)],
    ]
    traits.extend(pick_from_list(disads1, -25))

    disads2 = [
        [("Callous (12)", -5, DI)],
        list_self_control_levels("Loner", -5),
        [("No Sense of Humor", -10, DI)],
        list_self_control_levels("Overconfidence", -5),
        [("Sense of Duty (Adventuring companions)", -5, DI)],
        [("Stubbornness", -5, DI)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    skills1 = [
        [("Thrown Weapon (Dart)", 1, SK)],
        [("Thrown Weapon (Knife)", 1, SK)],
        [("Thrown Weapon (Shuriken)", 1, SK)],
        [("Throwing", 1, SK)],
        [("Blowpipe", 1, SK)],
        [("Sling", 1, SK)],
    ]
    traits.extend(pick_from_list(skills1, 1))

    melee_option = random.randrange(3)
    if melee_option == 0:
        skills2 = [
            [("Knife", 4, SK)],
            [("Axe/Mace", 4, SK)],
            [("Jitte/Sai", 4, SK)],
            [("Shortsword", 4, SK)],
            [("Smallsword", 4, SK)],
            [("Staff", 4, SK)],
            [("Tonfa", 4, SK)],
            [("Flail", 4, SK)],
            [("Kusari", 4, SK)],
        ]
        traits.extend(pick_from_list(skills2, 8))
    elif melee_option == 1:
        skills3 = [
            [("Knife", 4, SK)],
            [("Axe/Mace", 4, SK)],
            [("Jitte/Sai", 4, SK)],
            [("Shortsword", 4, SK)],
            [("Smallsword", 4, SK)],
            [("Staff", 4, SK)],
            [("Tonfa", 4, SK)],
            [("Flail", 4, SK)],
            [("Kusari", 4, SK)],
        ]
        traits.extend(pick_from_list(skills3, 4))
        traits = [(name, cost, trait_type) for (name, cost, trait_type) in traits
                  if name != "Judo" and name != "Karate"]
        traits.append(("Judo", 4, SK))
        traits.append(("Karate", 4, SK))
    else:
        traits = [(name, cost, trait_type) for (name, cost, trait_type) in traits
                  if name != "Judo" and name != "Karate"]
        if random.randrange(2) == 0:
            traits.append(("Judo", 8, SK))
            traits.append(("Karate", 4, SK))
        else:
            traits.append(("Judo", 4, SK))
            traits.append(("Karate", 8, SK))

    skills4 = [
        [("Fast-Draw (any)", 1, SK)],
        [("Climbing", 1, SK)],
        [("First Aid", 1, SK)],
        [("Gesture", 1, SK)],
        [("Teaching", 1, SK)],
        [("Hiking", 1, SK)],
        [("Running", 1, SK)],
        [("Intimidation", 1, SK)],
        [("Observation", 1, SK)],
    ]
    traits.extend(pick_from_list(skills4, 3))

    special_skill_names = set()
    for lst in special_skills:
        for tup in lst:
            special_skill_names.add(tup[0])
    pick_or_improve_skills_from_list(special_skill_names, 14, traits,
                                     min_cost=2)

    # Prereq hack.
    trait_names = set((trait[0] for trait in traits))
    if "Flying Leap" in trait_names and "Power Blow" not in trait_names:
        total_cost = 0
        for (name, cost, trait_type) in traits:
            if name == "Flying Leap":
                total_cost += cost
                traits.remove((name, cost, trait_type))
        remaining_special_skill_names = list(special_skill_names - trait_names -
                                             {"Flying Leap"})
        name2 = random.choice(remaining_special_skill_names)
        traits.append((name2, total_cost, SK))
    return traits


def generate_scout():
    traits = [
        ("ST 13", 30, PA),
        ("DX 14", 80, PA),
        ("IQ 11", 20, PA),
        ("HT 12", 20, PA),
        ("HP 13", 0, SA),
        ("Will 11", 0, SA),
        ("Per 14", 15, SA),
        ("FP 12", 0, SA),
        ("Basic Speed 7.0", 10, SA),
        ("Basic Move 7", 0, SA),
        ("Heroic Archer", 20, AD),
        ("Outdoorsman 2", 20, AD),
    ]

    ads1 = [
        list_levels("ST +%d", 10, PA, 2),
        [("DX +1", 20, PA)],
        list_levels("HT +%d", 10, PA, 2),
        list_levels("Per +%d", 5, SA, 4),
        [("Basic Speed +1", 20, SA)],
        list_levels("Basic Move +%d", 5, SA, 3),
        [("Absolute Direction", 5, AD)],
        list_levels("Acute Vision %d", 2, AD, 5),
        [("Combat Reflexes", 15, AD)],
        [("Danger Sense", 15, AD)],
        [("Fit", 5, AD), ("Very Fit", 15, AD)],
        [("High Pain Threshold", 10, AD)],
        [("Luck", 15, AD)],
        list_levels("Night Vision %d", 1, AD, 9),
        list_levels("Outdoorsman %d", 10, AD, 2, min_level=3),
        [("Peripheral Vision", 15, AD)],
        [("Rapid Healing", 5, AD)],
        list_levels("Signature Gear %d", 1, AD, 10),
        [("Weapon Bond", 1, AD)],
        [("Weapon Master (Bow)", 20, AD)],
    ]
    traits.extend(pick_from_list(ads1, 20))

    disads1 = [
        list_self_control_levels("Bloodlust", -10),
        [("Callous (12)", -5, DI)],
        list_self_control_levels("Greed", -15),
        list_self_control_levels("Honesty", -10),
        list_self_control_levels("Overconfidence", -5),
        [("Sense of Duty (Adventuring companions)", -5, DI)],
        [("Stubbornness", -5, DI)],
    ]
    traits.extend(pick_from_list(disads1, -15))

    disads2 = [
        [("Code of Honor (Pirate's)", -5, DI), ("Code of Honor (Soldier's)", -10, DI)],
        [("Intolerance (Urbanites)", -5, DI)],
        list_self_control_levels("Loner", -5),
        [("No Sense of Humor", -10, DI)],
        [("Odious Personal Habit (Unwashed bushwhacker)", -5, DI)],
        [("Paranoia", -10, DI)],
        list_self_control_levels("Phobia (Crowds)", -15),
        [("Social Stigma (Disowned)", -5, DI)],
        [("Vow (Never Sleep Indoors)", -10, DI)],
        [("Vow (Own no more than what can be carried)", -10, DI)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -35))

    fixed_skills = [
        [("Bow", 16, SK)],
        [("Camouflage", 2, SK)],
        [("Fast-Draw (Arrow)", 1, SK)],
        [("Observation", 2, SK)],
        [("Tracking", 2, SK)],
        [("Climbing", 1, SK)],
        [("Stealth", 1, SK)],
        [("Gesture", 2, SK)],
        [("Cartography", 4, SK)],
        [("Shadowing", 4, SK)],
        [("Traps", 4, SK)],
        [("Mimicry (Bird Calls)", 2, SK)],
        [("Hiking", 2, SK)],
    ]
    for fixed_skill in fixed_skills:
        traits.append(fixed_skill[0])

    skills1 = [
        [("Broadsword", 12, SK), ("Shortsword", 12, SK), ("Spear", 12, SK), ("Staff", 12, SK)],
        [("Broadsword", 8, SK), ("Shortsword", 8, SK), ("Spear", 8, SK)],
        [("Shield", 4, SK)],
    ]

    skills2 = [
        [("Navigation (Land)", 1, SK)],
        [("Navigation (Sea)", 1, SK)],
    ]

    skills3 = [
        [("Survival (Arctic)", 1, SK)],
        [("Survival (Desert)", 1, SK)],
        [("Survival (Island/Beach)", 1, SK)],
        [("Survival (Jungle)", 1, SK)],
        [("Survival (Mountain)", 1, SK)],
        [("Survival (Plains)", 1, SK)],
        [("Survival (Swampland)", 1, SK)],
        [("Survival (Woodlands)", 1, SK)],
    ]

    skills4 = [
        [("Brawling", 1, SK)],
        [("Fast-Draw (any other)", 1, SK)],
        [("Garrote", 1, SK)],
        [("Jumping", 1, SK)],
        [("Knife", 1, SK)],
        [("Knot-Tying", 1, SK)],
        [("Boating (Unpowered)", 1, SK)],
        [("Riding (Horse)", 1, SK)],
        [("Throwing", 1, SK)],
        [("Wrestling", 1, SK)],
        [("First Aid", 1, SK)],
        [("Seamanship", 1, SK)],
        [("Armoury (Missile Weapons)", 1, SK)],
        [("Prospecting", 1, SK)],
        [("Weather Sense", 1, SK)],
        [("Swimming", 1, SK)],
        [("Running", 1, SK)],
        [("Skiing", 1, SK)],
        [("Search", 1, SK)],
    ]

    all_skills = set()
    for lst in [skills1, skills2, skills3, skills4, fixed_skills]:
        for lst2 in lst:
            for tup in lst2:
                all_skills.add(tup[0])

    traits.extend(pick_from_list(skills1, 12))
    traits.extend(pick_from_list(skills2, 1))
    traits.extend(pick_from_list(skills3, 1))

    pick_or_improve_skills_from_list(all_skills, 8, traits)
    return traits


def generate_swashbuckler():
    traits = [
        ("ST 11", 10, PA),
        ("DX 15", 100, PA),
        ("IQ 10", 0, PA),
        ("HT 13", 30, PA),
        ("HP 11", 0, SA),
        ("Will 10", 0, SA),
        ("Per 10", 0, SA),
        ("FP 13", 0, SA),
        ("Basic Speed 7.0", 0, SA),
        ("Basic Move 7", 0, SA),
        ("Combat Reflexes", 15, AD),
        ("Enhanced Parry (Weapon of choice) 1", 5, AD),
        ("Luck", 15, AD),
        ("Weapon Bond (Any starting weapon)", 1, AD),
        ("Weapon Master (Weapon of choice) 1", 20, AD),
        ("Jumping", 1, SK),
        ("Fast-Draw (Knife)", 1, SK),
        ("Fast-Draw (Sword)", 1, SK),
        ("Acrobatics", 4, SK),
        ("Wrestling", 2, SK),
        ("Stealth", 1, SK),
        ("Carousing", 1, SK),
    ]

    ads1 = [
        list_levels("ST +%d", 10, PA, 6),
        list_levels("DX +%d", 20, PA, 3),
        list_levels("Basic Speed +%d", 20, SA, 2),
        list_levels("Basic Move +%d", 5, SA, 3),
        [("Alcohol Tolerance", 1, AD)],
        [("Ambidexterity", 5, AD)],
        [("Appearance: Attractive", 4, AD), ("Appearance: Handsome", 12, AD),
         ("Appearance: Very Handsome", 16, AD)],
        list_levels("Charisma %d", 5, AD, 5),
        [("Daredevil", 15, AD)],
        [("Enhanced Dodge", 15, AD)],
        list_levels("Enhanced Parry %d (Weapon of Choice)", 5, AD, 2, min_level=2),
        [("Extra Attack 1", 25, AD)],
        [("No Hangover", 1, AD)],
        [("Perfect Balance", 15, AD)],
        [("Rapier Wit", 5, AD)],
        list_levels("Serendipity %d", 15, AD, 4),
        list_levels("Signature Gear %d", 1, AD, 10),
        list_levels("Striking ST %d", 5, AD, 2),
        [("Extraordinary Luck", 15, AD), ("Ridiculous Luck", 45, AD)],
    ]
    traits.extend(pick_from_list(ads1, 60))

    disads1 = [
        [("Code of Honor (Pirate's)", -5, DI),
         ("Code of Honor (Gentleman's)", -10, DI)],
        list_self_control_levels(
          "Obsession (Become the best swordsman in the world)", -10),
        [("Vow (Use only weapon of choice)", -5, DI)],
        [("Vow (Never resist a challenge to combat)", -10, DI)],
        [("Vow (Challenge every swordsman to combat)", -15, DI)],
        [("Vow (Never wear armor)", -15, DI)],
        [("Wounded", -5, DI)],
    ]
    traits.extend(pick_from_list(disads1, -15))

    disads2 = [
        list_self_control_levels("Impulsiveness", -10),
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels("Short Attention Span", -10),
        list_self_control_levels("Trickster", -15),
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    disads3 = [
        list_self_control_levels2("Chummy", -5, "Gregarious", -10),
        list_self_control_levels("Compulsive Carousing", -5),
        list_self_control_levels("Compulsive Spending", -5),
        list_self_control_levels("Greed", -15),
        list_self_control_levels("Jealousy", -10),
        list_self_control_levels("Lecherousness", -15),
        [("One Eye", -15, DI)],
        [("Sense of Duty (Adventuring companions)", -5, DI)],
        [("Wounded", -5, DI)],
    ]
    disads3.extend(disads2)
    traits.extend(pick_from_list(disads3, -20))

    skills1 = [
        [("Thrown Weapon (Knife)", 2, SK)],
        [("Throwing", 2, SK)],
    ]
    traits.extend(pick_from_list(skills1, 2))

    skills2 = [
        [("Broadsword", 20, SK), ("Rapier", 20, SK), ("Saber", 20, SK),
         ("Shortsword", 20, SK), ("Smallsword", 20, SK)],
        [("Broadsword", 16, SK), ("Rapier", 16, SK), ("Saber", 16, SK),
         ("Shortsword", 16, SK), ("Smallsword", 16, SK)],
        [("Broadsword", 12, SK), ("Rapier", 12, SK), ("Saber", 12, SK),
         ("Shortsword", 12, SK), ("Smallsword", 12, SK)],
        [("Shield (Buckler)", 8, SK), ("Cloak", 8, SK), ("Main-Gauche", 8, SK)],
        [("Shield (Buckler)", 4, SK), ("Cloak", 4, SK), ("Main-Gauche", 4, SK)],
    ]
    traits.extend(pick_from_list(skills2, 20))

    skills3 = [
        [("Brawling", 2, SK)],
        [("Boxing", 2, SK)],
    ]
    traits.extend(pick_from_list(skills3, 2))

    skills4 = [
        [("Savoir-Faire (High Society)", 2, SK)],
        [("Streetwise", 2, SK)],
    ]
    traits.extend(pick_from_list(skills4, 2))

    skills5 = [
        [("Fast-Draw (any other)", 1, SK)],
        [("Climbing", 1, SK)],
        [("First Aid", 1, SK)],
        [("Gesture", 1, SK)],
        [("Seamanship", 1, SK)],
        [("Connoisseur (any)", 1, SK)],
        [("Fast-Talk", 1, SK)],
        [("Gambling", 1, SK)],
        [("Hiking", 1, SK)],
        [("Sex Appeal", 1, SK)],
        [("Intimidation", 1, SK)],
        [("Scrounging", 1, SK)],
        [("Search", 1, SK)],
    ]
    traits.extend(pick_from_list(skills5, 7))
    return traits


def generate_thief():
    traits = [
        ("ST 11", 10, PA),
        ("DX 15", 100, PA),
        ("IQ 13", 60, PA),
        ("HT 11", 10, PA),
        ("HP 11", 0, SA),
        ("Will 13", 0, SA),
        ("Per 14", 5, SA),
        ("FP 11", 0, SA),
        ("Basic Speed 6.0", -10, SA),
        ("Basic Move 7", 5, SA),
        ("Flexibility", 5, AD),
        ("High Manual Dexterity 1", 5, AD),
        ("Perfect Balance", 15, AD),
    ]

    ads1 = [
        [("DX +1", 20, PA)],
        [("IQ +1", 20, PA)],
        list_levels("Per +%d", 5, SA, 6),
        [("Basic Speed +1", 20, SA)],
        list_levels("Basic Move +%d", 5, SA, 2),
        [("Ambidexterity", 5, AD)],
        [("Catfall", 10, AD)],
        [("Combat Reflexes", 15, AD)],
        [("Danger Sense", 15, AD)],
        list_levels("Enhanced Dodge %d", 15, AD, 2),
        list_levels("Gizmos %d", 5, AD, 3),
        list_levels("High Manual Dexterity %d", 5, AD, 3, min_level=2),
        [("Honest Face", 1, AD)],
        [("Luck", 15, AD), ("Extraordinary Luck", 30, AD)],
        list_levels("Night Vision %d", 1, AD, 9),
        [("Peripheral Vision", 15, AD)],
        list_levels("Serendipity %d", 15, AD, 2),
        list_levels("Signature Gear %d", 1, AD, 10),
        list_levels("Striking ST %d (Only on surprise attack)", 2, AD, 2),
        [("Wealth (Comfortable)", 10, AD), ("Wealth (Wealthy)", 20, AD)],
        [("Double-Jointed", 10, AD)],
    ]
    traits.extend(pick_from_list(ads1, 30))

    disads1 = [
        [("Greed (12)", -15, AD)],
        [("Kleptomania (12)", -15, AD)],
        [("Trickster (12)", -15, AD)],
    ]
    traits.extend(pick_from_list(disads1, -15))

    disads2 = [
        [("Callous (12)", -5, AD)],
        [("Code of Honor (Pirate's)", -5, AD)],
        [("Curious", -5, AD)],
    ]
    traits.extend(pick_from_list(disads2, -5))

    disads3 = [
        list_self_control_levels("Bad Temper", -10),
        list_self_control_levels("Bloodlust", -10),
        list_self_control_levels("Compulsive Carousing", -5),
        list_self_control_levels("Compulsive Gambling", -5),
        list_self_control_levels("Compulsive Lying", -15),
        list_self_control_levels("Compulsive Spending", -5),
        list_self_control_levels("Cowardice", -10),
        [("Laziness", -10, AD)],
        list_self_control_levels("Lecherousness", -15),
        list_self_control_levels("Loner", -5),
        [("One Eye", -15, AD)],
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels("Post-Combat Shakes", -5),
        [("Sense of Duty (Adventuring companions)", -5, AD)],
        [("Skinny", -5, AD)],
        [("Social Stigma (Criminal Record)", -5, AD)],
    ]
    disads3.extend(disads1)
    disads3.extend(disads2)
    traits.extend(pick_from_list(disads3, -20))

    fixed_skills = [
        [("Forced Entry", 1, SK)],
        [("Climbing", 1, SK)],
        [("Filch", 2, SK)],
        [("Stealth", 12, SK)],
        [("Escape", 1, SK)],
        [("Pickpocket", 2, SK)],
        [("Lockpicking", 4, SK)],
        [("Traps", 4, SK)],
        [("Acrobatics", 1, SK)],
        [("Sleight of Hand", 1, SK)],
        [("Gesture", 1, SK)],
        [("Holdout", 2, SK)],
        [("Shadowing", 2, SK)],
        [("Smuggling", 2, SK)],
        [("Streetwise", 2, SK)],
        [("Search", 2, SK)],
        [("Urban Survival", 2, SK)],
        [("Brawling", 1, SK)],
        [("Gambling", 1, SK)],
        [("Carousing", 1, SK)],
    ]
    for fixed_skill in fixed_skills:
        traits.append(fixed_skill[0])

    skills1 = [
        [("Rapier", 2, SK), ("Saber", 2, SK), ("Shortsword", 2, SK), ("Smallsword", 2, SK)],
        [("Rapier", 1, SK), ("Saber", 1, SK), ("Shortsword", 1, SK), ("Smallsword", 1, SK)],
        [("Shield (Buckler, SK)", 1, SK), ("Cloak", 1, SK), ("Main-Gauche", 1, SK)],
    ]

    skills2 = [
        [("Crossbow", 1, SK)],
        [("Thrown Weapon (Knife)", 1, SK)],
        [("Bow", 1, SK)],
        [("Throwing", 1, SK)],
        [("Sling", 1, SK)],
    ]

    skills3 = [
        [("Fast-Draw (any)", 1, SK)],
        [("Garrote", 1, SK)],
        [("First Aid", 1, SK)],
        [("Panhandling", 1, SK)],
        [("Seamanship", 1, SK)],
        [("Cartography", 1, SK)],
        [("Connoisseur (any)", 1, SK)],
        [("Disguise", 1, SK)],
        [("Fast-Talk", 1, SK)],
        [("Merchant", 1, SK)],
        [("Counterfeiting", 1, SK)],
        [("Forgery", 1, SK)],
        [("Poisons", 1, SK)],
        [("Hiking", 1, SK)],
        [("Scrounging", 1, SK)],
        [("Lip Reading", 1, SK)],
        [("Observation", 1, SK)],
    ]

    all_skills = set()
    for lst in [skills1, skills2, skills3, fixed_skills]:
        for lst2 in lst:
            for tup in lst2:
                all_skills.add(tup[0])

    traits.extend(pick_from_list(skills1, 2))
    traits.extend(pick_from_list(skills2, 1))

    pick_or_improve_skills_from_list(all_skills, 7, traits)
    return traits


# from http://forums.sjgames.com/showthread.php?t=110145
allowed_spells = {
    "Purify Air",
    "Seek Air",
    "Create Air",
    "No-Smell",
    "Stench",
    "Destroy Air",
    "Odor",
    "Shape Air",
    "Air Jet",
    "Air Vision",
    "Body of Air",
    "Devitalize Air",
    "Walk on Air",
    "Wall of Wind",
    "Windstorm",
    "Earth to Air",
    "Concussion",
    "Breathe Air",
    "Essential Air",
    "Air Vortex",
    "Sandstorm",
    "Body of Wind",
    "Summon Air Elemental",
    "Control Air Elemental",
    "Create Air Elemental",
    "Protect Animal",
    "Shapeshifting",
    "Shapeshift Others",
    "Climbing",
    "Itch",
    "Touch",
    "Perfume",
    "Spasm",
    "Stop Spasm",
    "Tickle",
    "Pain",
    "Clumsiness",
    "Hinder",
    "Rooted Feet",
    "Tanglefoot",
    "Roundabout",
    "Debility",
    "Frailty",
    "Might",
    "Grace",
    "Vigor",
    "Boost Dexterity",
    "Boost Health",
    "Boost Strength",
    "Boost Intelligence",
    "Stun",
    "Nauseate",
    "Retch",
    "Fumble",
    "Strike Dumb",
    "Strike Blind",
    "Strike Deaf",
    "Hunger",
    "Thirst",
    "Resist Pain",
    "Hold Breath",
    "Ambidexterity",
    "Balance",
    "Reflexes",
    "Cadence",
    "Hair Growth",
    "Haircut",
    "Sensitize",
    "Agonize",
    "Weaken Blood",
    "Strike Numb",
    "Choke",
    "Control Limb",
    "Paralyze Limb",
    "Total Paralysis",
    "Wither Limb",
    "Strike Barren",
    "Deathtouch",
    "Alter Voice",
    "Alter Visage",
    "Alter Body",
    "Lengthen Limb",
    "Decapitation",
    "Shrink",
    "Shrink Other",
    "Enlarge",
    "Enlarge Other",
    "Corpulence",
    "Gauntness",
    "Transform Body",
    "Transform Other",
    "Transmogrification",
    "Sense Foes",
    "Sense Life",
    "Sense Emotion",
    "Hide Emotion",
    "Persuasion",
    "Vexation",
    "Truthsayer",
    "Dream Viewing",
    "Dream Sending",
    "Dream Projection",
    "Hide Thoughts",
    "Lend Language",
    "Borrow Language",
    "Gift of Tongues",
    "Gift of Letters",
    "Mind-Reading",
    "Mind-Search",
    "Mind-Sending",
    "Telepathy",
    "Retrogression",
    "Lend Skill",
    "Borrow Skill",
    "Compel Truth",
    "Insignificance",
    "Presence",
    "Communication",
    "Soul Rider",
    "Control Person",
    "Possession",
    "Dispel Possession",
    "Permanent Possession",
    "Exchange Bodies",
    "Seek Earth",
    "Shape Earth",
    "Shape Stone",
    "Seek Pass",
    "Earth Vision",
    "Earth to Stone",
    "Create Earth",
    "Flesh to Stone",
    "Stone to Earth",
    "Predict Earth Movement",
    "Sand Jet",
    "Mud Jet",
    "Stone Missile",
    "Walk Through Earth",
    "Earth to Water",
    "Partial Petrifaction",
    "Rain of Stones",
    "Entombment",
    "Essential Earth",
    "Stone to Flesh",
    "Body of Stone",
    "Steelwraith",
    "Purify Earth",
    "Earthquake",
    "Volcano",
    "Alter Terrain",
    "Move Terrain",
    "Summon Earth Elemental",
    "Control Earth Elemental",
    "Create Earth Elemental",
    "Ignite Fire",
    "Seek Fire",
    "Create Fire",
    "Extinguish Fire",
    "Shape Fire",
    "Phantom Flame",
    "Fireproof",
    "Slow Fire",
    "Fast Fire",
    "Deflect Energy",
    "Flame Jet",
    "Smoke",
    "Heat",
    "Cold",
    "Rain of Fire",
    "Resist Fire",
    "Resist Cold",
    "Warmth",
    "Fireball",
    "Explosive Fireball",
    "Essential Flame",
    "Flaming Weapon",
    "Flaming Missiles",
    "Flaming Armor",
    "Fire Cloud",
    "Breathe Fire",
    "Burning Touch",
    "Body of Flames",
    "Burning Death",
    "Summon Fire Elemental",
    "Control Fire Elemental",
    "Create Fire Elemental",
    "Seek Food",
    "Test Food",
    "Decay",
    "Season",
    "Far-Tasting",
    "Mature",
    "Purify Food",
    "Cook",
    "Prepare Game",
    "Know Recipe",
    "Poison Food",
    "Preserve Food",
    "Create Food",
    "Essential Food",
    "Water to Wine",
    "Distill",
    "Fool's Banquet",
    "Monk's Banquet",
    "Timeslip",
    "Timeslip Other",
    "Planar Summons",
    "Planar Visit",
    "Plane Shift",
    "Plane Shift Other",
    "Phase",
    "Phase Other",
    "Beacon",
    "Trace Teleport",
    "Divert Teleport",
    "Create Door",
    "Seek Gate",
    "Scry Gate",
    "Control Gate",
    "Hide Object",
    "Sanctuary",
    "Lend Energy",
    "Lend Vitality",
    "Recover Energy",
    "Remove Contagion",
    "Resist Disease",
    "Resist Poison",
    "Minor Healing",
    "Relieve Madness",
    "Regeneration",
    "Instant Regeneration",
    "Halt Aging",
    "Youth",
    "Resurrection",
    "Simple Illusion",
    "Complex Illusion",
    "Perfect Illusion",
    "Illusion Shell",
    "Illusion Disguise",
    "Independence",
    "Know Illusion",
    "Control Illusion",
    "Dispel Illusion",
    "Inscribe",
    "Phantom",
    "Initiative",
    "Create Object",
    "Duplicate",
    "Create Servant",
    "Create Warrior",
    "Create Animal",
    "Create Mount",
    "Control Creation",
    "Dispel Creation",
    "Measurement",
    "Tell Time",
    "Alarm",
    "Far-Feeling",
    "Find Direction",
    "Tell Position",
    "Test Load",
    "Detect Magic",
    "Sense Mana",
    "Aura",
    "Identify Spell",
    "Mage Sight",
    "Mage Sense",
    "Seek Magic",
    "Analyze Magic",
    "Summon Shade",
    "Glass Wall",
    "Know Location",
    "Wizard Eye",
    "Invisible Wizard Eye",
    "Wizard Mouth",
    "Wizard Nose",
    "Wizard Hand",
    "Astral Vision",
    "Memorize",
    "Pathfinder",
    "Projection",
    "Seeker",
    "Trace",
    "History",
    "Ancient History",
    "Prehistory",
    "Reconstruct Spell",
    "Know True Shape",
    "Recall",
    "Remember Path",
    "See Secrets",
    "Scents of the Past",
    "Images of the Past",
    "Echoes of the Past",
    "Divination (Astrology)",
    "Divination (Augury)",
    "Divination (Cartomancy)",
    "Divination (Crystal-Gazing)",
    "Divination (Dactylomancy)",
    "Divination (Extispicy)",
    "Divination (Gastromancy)",
    "Divination (Geomancy)",
    "Divination (Lecanomancy)",
    "Divination (Numerology)",
    "Divination (Oneiromancy)",
    "Divination (Psysiognomy)",
    "Divination (Pyromancy)",
    "Divination (Sortilege)",
    "Divination (Symbol-Casting)",
    "Light",
    "Continual Light",
    "Colors",
    "Remove Shadow",
    "Shape Light",
    "Bright Vision",
    "Infravision",
    "Night Vision",
    "Hawk Vision",
    "Small Vision",
    "Dark Vision",
    "Darkness",
    "Blackout",
    "Glow",
    "Flash",
    "Gloom",
    "Light Jet",
    "Mirror",
    "Remove Reflection",
    "Wall of Light",
    "Blur",
    "Shape Darkness",
    "Hide",
    "See Invisible",
    "Mage Light",
    "Continual Mage Light",
    "Sunlight",
    "Continual Sunlight",
    "Invisibility",
    "Body of Shadow",
    "Sunbolt",
    "Inspired Creation",
    "Awaken Craft Spirit",
    "Find Weakness",
    "Weaken",
    "Restore",
    "Clean",
    "Soilproof",
    "Dye",
    "Copy",
    "Rejoin",
    "Shatter",
    "Animate Object",
    "Stiffen",
    "Knot",
    "Reshape",
    "Rive",
    "Ruin",
    "Explode",
    "Fasten",
    "Mapmaker",
    "Repair",
    "Shatterproof",
    "Sharpen",
    "Toughen",
    "Transparency",
    "Mystic Mark",
    "Weapon Self",
    "Transform Object",
    "Contract Object",
    "Extend Object",
    "Shrink Object",
    "Enlarge Object",
    "Disintegrate",
    "Counterspell",
    "Scryguard",
    "Suspend Spell",
    "Ward",
    "Conceal Magic",
    "Reflect",
    "Scrywall",
    "Great Ward",
    "False Aura",
    "Magic Resistance",
    "Scryfool",
    "Penetrating Spell",
    "Catch Spell",
    "Suspend Magic",
    "Displace Spell",
    "Spell Shield",
    "Spell Wall",
    "Pentagram",
    "Suspend Curse",
    "Suspend Mana",
    "Dispel Magic",
    "Lend Spell",
    "Remove Curse",
    "Charge Powerstone",
    "Spellguard",
    "Remove Aura",
    "Drain Mana",
    "Restore Mana",
    "Steal Spell",
    "Telecast",
    "Hang Spell",
    "Maintain Spell",
    "Throw Spell",
    "Bless",
    "Curse",
    "Suspend Magery",
    "Drain Magery",
    "Delay",
    "Link",
    "Reflex",
    "Keen Touch",
    "Keen Hearing",
    "Keen Vision",
    "Keen Taste and Smell",
    "Dull Touch",
    "Dull Hearing",
    "Dull Vision",
    "Dull Taste and Smell",
    "Alertness",
    "Dullness",
    "Fear",
    "Panic",
    "Terror",
    "Bravery",
    "Rear Vision",
    "Berserker",
    "Foolishness",
    "Daze",
    "Mental Stun",
    "Disorient",
    "Encrypt",
    "Fascinate",
    "Forgetfulness",
    "Sleep",
    "Wisdom",
    "Weaken Will",
    "Strengthen Will",
    "Loyalty",
    "Command",
    "Drunkenness",
    "Madness",
    "Emotion Control",
    "Mass Daze",
    "Mindlessness",
    "Compel Lie",
    "Lure",
    "Mass Sleep",
    "Peaceful Sleep",
    "Sickness",
    "Will Lock",
    "Oath",
    "Permanent Forgetfulness",
    "Vigil",
    "Charm",
    "Ecstasy",
    "Enthrall",
    "Permanent Madness",
    "False Memory",
    "Avoid",
    "Nightmare",
    "Hallucination",
    "Lesser Geas",
    "Suggestion",
    "Mass Suggestion",
    "Glib Tongue",
    "Enslave",
    "Great Hallucination",
    "Great Geas",
    "Haste",
    "Apportation",
    "Glue",
    "Grease",
    "Deflect Missile",
    "Hold Fast",
    "Increase Burden",
    "Jump",
    "Levitation",
    "Lighten Burden",
    "Locksmith",
    "Long March",
    "Poltergeist",
    "Quick March",
    "Slow Fall",
    "Wallwalker",
    "Dancing Object",
    "Distant Blow",
    "Lockmaster",
    "Manipulate",
    "Slow",
    "Undo",
    "Winged Knife",
    "Flight",
    "Light Tread",
    "Slide",
    "Flying Carpet",
    "Hawk Flight",
    "Ethereal Body",
    "Great Haste",
    "Pull",
    "Repel",
    "Swim",
    "Teleport",
    "Teleport Other",
    "Blink",
    "Blink Other",
    "Freedom",
    "Cloud-Walking",
    "Cloud-Vaulting",
    "Death Vision",
    "Sense Spirit",
    "Summon Spirit",
    "Animation",
    "Steal Energy",
    "Steal Vitality",
    "Materialize",
    "Solidify",
    "Affect Spirits",
    "Skull-Spirit",
    "Turn Spirit",
    "Zombie",
    "Control Zombie",
    "Turn Zombie",
    "Zombie Summoning",
    "Mass Zombie",
    "Slow Healing",
    "Stop Healing",
    "Command Spirit (Banshees)",
    "Command Spirit (Specters)",
    "Command Spirit (Manitous)",
    "Age",
    "Pestilence",
    "Evisceration",
    "Animate Shadow",
    "Rotting Death",
    "Soul Jar",
    "Summon Demon",
    "Banish",
    "Entrap Spirit",
    "Repel Spirits",
    "Bind Spirit (Banshees)",
    "Bind Spirit (Specters)",
    "Bind Spirit (Manitous)",
    "Steal Grace",
    "Steal Vigor",
    "Steal Might",
    "Steal Wisdom",
    "Steal Skill",
    "Steal Youth",
    "Steal Beauty",
    "Astral Block",
    "Lich",
    "Wraith",
    "Shape Plant",
    "Plant Growth",
    "Plant Vision",
    "Sense Danger",
    "Detect Poison",
    "Magelock",
    "Block",
    "Hardiness",
    "Watchdog",
    "Nightingale",
    "Sense Observation",
    "Shield",
    "Armor",
    "Turn Blade",
    "Bladeturning",
    "Missile Shield",
    "Catch Missile",
    "Reverse Missiles",
    "Return Missile",
    "Reflect Gaze",
    "Mystic Mist",
    "Shade",
    "Iron Arm",
    "Weather Dome",
    "Atmosphere Dome",
    "Resist Pressure",
    "Teleport Shield",
    "Force Dome",
    "Force Wall",
    "Utter Dome",
    "Utter Wall",
    "Sound",
    "Silence",
    "Sound Vision",
    "Thunderclap",
    "Voices",
    "Garble",
    "Imitate Voice",
    "Wall of Silence",
    "Hush",
    "Mage-Stealth",
    "Great Voice",
    "Noise",
    "Delayed Message",
    "Resist Sound",
    "Sound Jet",
    "Converse",
    "Far-Hearing",
    "Scribe",
    "Musical Scribe",
    "Message",
    "Silver Tongue",
    "Wizard Ear",
    "Invisible Wizard Ear",
    "Seek Machine",
    "Reveal Function",
    "Machine Control",
    "Machine Summoning",
    "Machine Speech",
    "Glitch",
    "Malfunction",
    "Schematic",
    "Rebuild",
    "Animate Machine",
    "Machine Possession",
    "Permanent Machine Possession",
    "Awaken Computer",
    "Seek Power",
    "Seek Fuel",
    "Test Fuel",
    "Preserve Fuel",
    "Purify Fuel",
    "Create Fuel",
    "Essential Fuel",
    "Stop Power",
    "Lend Power",
    "Propel",
    "Conduct Power",
    "Steal Power",
    "Draw Power",
    "Magnetic Vision",
    "Radio Hearing",
    "Spectrum Vision",
    "Seek Plastic",
    "Identify Metal",
    "Identify Plastic",
    "Shape Metal",
    "Shape Plastic",
    "Metal Vision",
    "Plastic Vision",
    "Body of Metal",
    "Body of Plastic",
    "Seek Water",
    "Seek Coastline",
    "Purify Water",
    "Create Water",
    "Destroy Water",
    "Icy Weapon",
    "Shape Water",
    "Umbrella",
    "Body of Water",
    "Foul Water",
    "Freeze",
    "Ice Slick",
    "Ice Sphere",
    "Icy Missiles",
    "Melt Ice",
    "Resist Water",
    "Snow Shoes",
    "Walk on Water",
    "Water Jet",
    "Water Vision",
    "Whirlpool",
    "Coolness",
    "Create Ice",
    "Dehydrate",
    "Ice Dagger",
    "Icy Touch",
    "Walk Through Water",
    "Dry Spring",
    "Essential Water",
    "Frostbite",
    "Snow Jet",
    "Breathe Water",
    "Body of Ice",
    "Boil Water",
    "Condense Steam",
    "Create Acid",
    "Create Spring",
    "Flesh to Ice",
    "Create Steam",
    "Resist Acid",
    "Geyser",
    "Rain of Acid",
    "Steam Jet",
    "Acid Ball",
    "Acid Jet",
    "Rain of Ice Daggers",
    "Icy Breath",
    "Breathe Steam",
    "Spit Acid",
    "Essential Acid",
    "Summon Water Elemental",
    "Control Water Elemental",
    "Create Water Elemental",
    "Frost",
    "Fog",
    "Predict Weather",
    "Waves",
    "Clouds",
    "Current",
    "Tide",
    "Wind",
    "Rain",
    "Snow",
    "Hail",
    "Warm",
    "Cool",
    "Storm",
    "Resist Lightning",
    "Lightning",
    "Explosive Lightning",
    "Lightning Whip",
    "Shocking Touch",
    "Spark Cloud",
    "Spark Storm",
    "Wall of Lightning",
    "Ball of Lightning",
    "Lightning Stare",
    "Body of Lightning",
    "Lightning Armor",
    "Lightning Weapon",
    "Lightning Missiles",
}


banned_colleges = {
    "Enchantment",
    "Weapon Enchantment",
    "Armor Enchantment",
    "Radiation",
}


allowed_bard_colleges = {
    "Communication",
    "Mind Control",
}


# dict of spell name to set of colleges to which it belongs
spell_to_colleges = None

# dict of spell name to a function that takes (traits, trait_names) as
# arguments and returns True iff the prereqs are satisfied
spell_to_prereq_function = None

# gcs_library/spell_list/spell/name
# gcs_library/spell_list/spell/categories/category
#   (don't use college as that has things like Air/Knowledge)
# gcs_library/spell_list/spell/prereq_list @all="yes" or "no"
# can nest prereq_list elements  - up to 3 deep in data
# spell_prereq @has="yes"
#   college_count @compare="at_least"10  (if twice, 2 spells from each)
# spell_prereq @has="yes"
#   <college compare="contains">air</college>
#   <quantity compare="at_least">5</college>
#   <name compare="is">aura</college>  (lowercase)
#   <name compare="starts with">seek power</college>
#   <name compare="contains">lightning</college>
# advantage_prereq @has="yes" or "no"
#   <name compare="is">magery</name>
#   <level compare="at_least">2</name>
#   <notes compare="contains">one college (gate)</name>
#   <notes compare="does not contain">one college</name>
# bug: geyser prereqs: create well should be create spring, quantity 5
#      should be on college water not create spring
#      should be college earth not name earth


def count_spell_colleges(traits):
    colleges = set()
    for tup in traits:
        name = tup[0]
        if name in spell_to_colleges:
            colleges.update(spell_to_colleges[name])
    return len(colleges)


def count_spells_from_each_college(traits):
    college_count = Counter()
    for tup in traits:
        name = tup[0]
        for college in spell_to_colleges.get(name, []):
            college_count[college] += 1
    return college_count


def count_spells_starting_with(traits, st):
    count = 0
    for tup in traits:
        name = tup[0].title()
        if name.startswith(st.title()) and name in spell_to_colleges:
            count += 1
    return count


def count_spells_containing(traits, st):
    count = 0
    for tup in traits:
        name = tup[0].title()
        if st.title() in name and name in spell_to_colleges:
            count += 1
    return count


def count_spells(traits):
    count = 0
    for tup in traits:
        name = tup[0].title()
        if name in spell_to_colleges:
            count += 1
    return count


def _parse_spell_prereq(el, function_name):
    """Parse a <spell_prereq> element and its children.

    Return a str of Python code that takes traits and trait_names as
    arguments and evaluates to True iff the prereqs are satisfied.
    """
    if len(el) == 1:
        child = el[0]
        if child.tag == "name":
            if child.get("compare") == "is":
                return """
def %s(traits, trait_names):
    return '''%s''' in trait_names
""" % (function_name, child.text.title())

            elif child.get("compare") == "contains":
                return """
def %s(traits, trait_names):
    for trait in trait_names:
        if '''%s'''.title() in trait.title():
            return True
    return False
""" % (function_name, child.text)

            elif child.get("compare") == "starts with":
                return """
def %s(traits, trait_names):
    for trait in trait_names:
        if trait.title().startswith('''%s'''):
            return True
    return False
""" % (function_name, child.text.title())

        elif child.tag == "college_count":
            if child.get("compare") == "at_least":
                return """
def %s(traits, trait_names):
    count = count_spell_colleges(traits)
    return count >= %d
""" % (function_name, int(child.text))

        elif child.tag == "college":

            if child.get("compare") == "contains":
                return """
def %s(traits, trait_names):
    counter = count_spells_from_each_college(traits)
    for college, quantity in counter.items():
        if '''%s''' in college.title() and quantity >= 1:
            return True
    return False
""" % (function_name, child.text.title())

            elif child.get("compare") == "is":
                return """
def %s(traits, trait_names):
    counter = count_spells_from_each_college(traits)
    return counter['''%s'''] >= 1
""" % (function_name, child.text)

    elif len(el) == 2:
        if el.find("college") is not None and el.find("quantity") is not None:
            college_el = el.find("college")
            quantity_el = el.find("quantity")
            if (college_el.get("compare") == "contains" and
              quantity_el.get("compare") == "at_least"):
                return """
def %s(traits, trait_names):
    counter = count_spells_from_each_college(traits)
    return counter['''%s'''] >= %d
""" % (function_name, college_el.text, int(quantity_el.text))

            elif (college_el.get("compare") == "is" and
              quantity_el.get("compare") == "at_least"):
                return """
def %s(traits, trait_names):
    counter = count_spells_from_each_college(traits)
    return counter['''%s'''] >= %d
""" % (function_name, college_el.text, int(quantity_el.text))

        elif el.find("name") is not None and el.find("quantity") is not None:
            name_el = el.find("name")
            quantity_el = el.find("quantity")

            if (name_el.get("compare") == "starts with" and
              quantity_el.get("compare") == "at_least"):
                return """
def %s(traits, trait_names):
    return count_spells_starting_with(traits, '''%s''') >= %d
""" % (function_name, name_el.text.title(), int(quantity_el.text))

            elif (name_el.get("compare") == "is" and
              quantity_el.get("compare") == "is"):
                return """
def %s(traits, trait_names):
    return '''%s''' in trait_names
""" % (function_name, name_el.text.title())

            elif (name_el.get("compare") == "contains" and
              quantity_el.get("compare") == "at_least"):
                return """
def %s(traits, trait_names):
    return count_spells_containing(traits, '''%s''') >= %d
""" % (function_name, name_el.text.title(), int(quantity_el.text))

            # XXX This will never be true.  Rider Within (@animal)
            elif (name_el.get("compare") == "is" and
                  quantity_el.get("compare") == "at_least"):
                return """
def %s(traits, trait_names):
    count = 0
    for trait in trait_names:
        if trait == '''%s''':
            count += 1
    return count >= %d
""" % (function_name, name_el.text.title(), int(quantity_el.text))

            elif (name_el.get("compare") == "is anything" and
                  quantity_el.get("compare") == "at_least"):
                return """
def %s(traits, trait_names):
    return count_spells(traits) >= %d
""" % (function_name, int(quantity_el.text))

        elif el.find("any") is not None and el.find("quantity") is not None:
            quantity_el = el.find("quantity")

            if quantity_el.get("compare") == "at_least":
                return """
def %s(traits, trait_names):
    return count_spells(traits) >= %d
""" % (function_name, int(quantity_el.text))

    assert False, "parse_spell_prereq %s" % et.tostring(el)


def _parse_advantage_prereq(el, function_name):
    """Parse a <advantage_prereq> element and its children.

    Return a str of Python code that takes traits and trait_names as
    arguments and evaluates to True iff the prereqs are satisfied.
    """
    if el.get("has") == "no":
        if len(el) == 2:
            name_el = el.find("name")
            notes_el = el.find("notes")
        if (name_el is not None and name_el.get("compare") == "starts with"
          and notes_el is not None and notes_el.get("compare") ==
                                                           "is anything"):
            return """
def %s(traits, trait_names):
    for trait_name in trait_names:
        if trait_name.title().startswith('''%s'''.title()):
            return False
    return True
""" % (function_name, name_el.text.title())

        elif (name_el is not None and name_el.get("compare") == "is"
          and notes_el is not None and notes_el.get("compare") ==
                                                           "is anything"):
            return """
def %s(traits, trait_names):
    for trait_name in trait_names:
        if trait_name.title() == '''%s'''.title():
            return False
    return True
""" % (function_name, name_el.text.title())

        elif (name_el is not None and name_el.get("compare") == "contains"
          and notes_el is not None and notes_el.get("compare") ==
                                                           "is anything"):
            return """
def %s(traits, trait_names):
    for trait_name in trait_names:
        if '''%s'''.title() in trait_name.title():
            return False
    return True
""" % (function_name, name_el.text.title())

    elif len(el) == 3:
        name_el = el.find("name")
        level_el = el.find("level")
        notes_el = el.find("notes")
        if (name_el is not None and name_el.get("compare") == "is" and
          level_el is not None and level_el.get("compare") == "at_least" and
          notes_el is not None and notes_el.get("compare") == "is anything"):
            return """
def %s(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''%s'''):
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= int('''%s''')
    return False
""" % (function_name, name_el.text.title(), level_el.text)

        elif (name_el is not None and name_el.get("compare") == "is" and
          level_el is not None and level_el.get("compare") == "at_least" and
          notes_el is not None and notes_el.get("compare") == "contains"):
            return """
def %s(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''%s''') and '''%s''' in trait:
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= int('''%s''')
    return False
""" % (function_name, name_el.text.title(), notes_el.text, level_el.text)

        elif (name_el is not None and name_el.get("compare") == "is" and
          level_el is not None and level_el.get("compare") == "at_least" and
          notes_el is not None and notes_el.get("compare") ==
                                                "does not contain"):
            return """
def %s(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''%s''') and '''%s''' not in trait:
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= int('''%s''')
    return False
""" % (function_name, name_el.text.title(), notes_el.text, level_el.text)

        elif (name_el is not None and name_el.get("compare") == "contains" and
          level_el is not None and level_el.get("compare") == "at_least" and
          notes_el is not None and notes_el.get("compare") == "is anything"):
            return """
def %s(traits, trait_names):
    for trait in trait_names:
        if '''%s''' in trait:
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= int('''%s''')
    return False
""" % (function_name, name_el.text.title(), level_el.text)

    elif len(el) == 2:
        name_el = el.find("name")
        notes_el = el.find("notes")
        if (name_el is not None and name_el.get("compare") == "is" and
          notes_el is not None and notes_el.get("compare") == "is anything"):
            return """
def %s(traits, trait_names):
    return '''%s''' in trait_names
""" % (function_name, name_el.text.title())

        elif (name_el is not None and name_el.get("compare") == "starts with"
          and notes_el is not None and notes_el.get("compare") == "contains"):
            return """
def %s(traits, trait_names):
    for trait_name in trait_names:
        if (trait_name.title().startswith('''%s'''.title()) and
          '''%s''' in trait_name.title()):
            return True
    return False
""" % (function_name, name_el.text.title(), notes_el.text)

        elif (name_el is not None and name_el.get("compare") == "contains" and
          notes_el is not None and notes_el.get("compare") == "is anything"):
            return """
def %s(traits, trait_names):
    for trait_name in trait_names:
        if '''%s'''.title() in trait_name.title():
            return True
    return False
""" % (function_name, name_el.text.title())

    assert False, "parse_advantage_prereq %s" % et.tostring(el)


def _parse_attribute_prereq(el, function_name):
    """Parse a <attribute_prereq> element and its children.

    Return a str of Python code that takes traits and trait_names as
    arguments and evaluates to True iff the prereqs are satisfied.
    """
    attr = el.get("which")
    compare = el.get("compare")
    level = int(el.text)
    if compare == "at_least":
        return """
def %s(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''%s '''):
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= %d
    return False
""" % (function_name, attr.upper(), level)
    assert False, "parse_attribute_prereq %s" % et.tostring(el)


def _parse_skill_prereq(el, function_name):
    """Parse a <skill_prereq> element and its children.

    Return a str of Python code that takes traits and trait_names as
    arguments and evaluates to True iff the prereqs are satisfied.
    """
    if len(el) == 3:
        name_el = el.find("name")
        level_el = el.find("level")
        specialization_el = el.find("specialization")
        if (name_el is not None and name_el.get("compare") == "is" and
          level_el is not None and level_el.get("compare") == "at_least" and
          specialization_el is not None and specialization_el.get("compare")
                                                            == "is anything"):
            return """
def %s(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''%s'''):
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= int('''%s''')
    return False
""" % (function_name, name_el.text.title(), level_el.text)

    elif len(el) == 2:
        name_el = el.find("name")
        specialization_el = el.find("specialization")
        if (name_el is not None and name_el.get("compare") == "is" and
          specialization_el is not None and specialization_el.get("compare")
                                                            == "is anything"):
            return """
def %s(traits, trait_names):
    return '''%s''' in trait_names
""" % (function_name, name_el.text.title())

    assert False, "parse_skill_prereq %s" % et.tostring(el)


and_or = """
def and_(*args):
    for arg in args:
        if not arg:
            return False
    return True


def or_(*args):
    for arg in args:
        if arg:
            return True
    return False
"""


function_name_incrementor = 0


def _parse_prereq_list(prereq_list_el, top_name):
    global function_name_incrementor
    sts = []
    sts.append(and_or)
    function_names = []
    for child in prereq_list_el:
        if child.tag == "prereq_list":
            function_name = "top_%d" % function_name_incrementor
            function_name_incrementor += 1
            function_names.append(function_name)
            st = _parse_prereq_list(child, function_name)
        else:
            function_name = "ppl_%d" % function_name_incrementor
            function_name_incrementor += 1
            function_names.append(function_name)
            if child.tag == "spell_prereq":
                st = _parse_spell_prereq(child, function_name)
            elif child.tag == "advantage_prereq":
                st = _parse_advantage_prereq(child, function_name)
            elif child.tag == "attribute_prereq":
                st = _parse_attribute_prereq(child, function_name)
            elif child.tag == "skill_prereq":
                st = _parse_skill_prereq(child, function_name)
            else:
                assert False, "unknown child tag %s" % child.tag
        sts.append(st)
    if prereq_list_el.get("all") == "yes":
        joiner = "and_"
    else:
        joiner = "or_"
    function_names_with_args = [
        function_name if "top" in function_name else
        "%s(traits, trait_names)" % function_name
        for function_name in function_names]
    call_line = "%s = %s(%s)" % (
                top_name, joiner, ", ".join(function_names_with_args))
    sts.append(call_line)
    sts.append("")
    blob = "\n".join(sts)
    return blob


def _parse_no_prereqs(prereq_list_el, top_name):
    """Return the text of a function that always returns True."""
    global function_name_incrementor
    function_name = "pnp_%s" % function_name_incrementor
    function_name_incrementor += 1
    return """
def %s(traits, trait_names):
    return True

%s = True""" % (function_name, top_name)


def build_spell_prereqs(allowed_colleges=None):
    """Fill in global dicts spell_to_colleges and spell_to_prereq_function."""
    global spell_to_colleges
    spell_to_colleges = {}
    global spell_to_prereq_function
    spell_to_prereq_function = {}
    dirname = os.path.dirname(__file__)
    filename = "Library__L.glb"
    path = os.path.abspath(os.path.join(dirname, filename))
    tree = et.parse(path)
    root_el = tree.getroot()
    spell_list_el = root_el.find("spell_list")
    for spell_el in spell_list_el.findall("spell"):
        name = spell_el.find("name").text
        if name not in allowed_spells:
            continue
        categories_el = spell_el.find("categories")
        colleges = set()
        for category_el in categories_el:
            college = category_el.text
            colleges.add(college)
        if allowed_colleges and not colleges.intersection(allowed_colleges):
            continue
        spell_to_colleges[name] = colleges
        prereq_list_el = spell_el.find("prereq_list")

        global function_name_incrementor
        top_name = "top_%d" % function_name_incrementor
        function_name_incrementor += 1

        if prereq_list_el is None:
            blob = _parse_no_prereqs(prereq_list_el, top_name)
        else:
            blob = _parse_prereq_list(prereq_list_el, top_name)
        spell_to_prereq_function[name] = blob


def add_special_bard_skills_to_spell_prereqs():
    """Add special bard skills to spell_to_colleges and
    spell_to_prereq_function."""
    global spell_to_colleges
    global spell_to_prereq_function
    special_skills = {"Hypnotism", "Musical Influence", "Persuade",
        "Suggest", "Sway Emotions", "Captivate"}
    dirname = os.path.dirname(__file__)
    filename = "Library__L.glb"
    path = os.path.abspath(os.path.join(dirname, filename))
    tree = et.parse(path)
    root_el = tree.getroot()
    skill_list_el = root_el.find("skill_list")
    for skill_el in skill_list_el.findall("spell"):
        name = skill_el.find("name").text
        if name not in special_skills:
            continue
        prereq_list_el = skill_el.find("prereq_list")
        global function_name_incrementor
        top_name = "top_%d" % function_name_incrementor
        function_name_incrementor += 1
        if prereq_list_el is None:
            blob = _parse_no_prereqs(prereq_list_el, top_name)
        else:
            blob = _parse_prereq_list(prereq_list_el, top_name)
        spell_to_prereq_function[name] = blob


def convert_magery_to_bardic_talent():
    """Bards treat Bardic Talent as Magery for their prereqs."""
    global spell_to_prereq_function
    for spell, blob in spell_to_prereq_function.items():
        if "magery" in blob:
            blob2 = blob.replace("magery", "bardic talent")
            spell_to_prereq_function[spell] = blob2


def prereq_satisfied(spell, traits):
    """Return True iff any prereqs for spell are satisfied."""
    trait_names = set((trait[0] for trait in traits))
    blob = spell_to_prereq_function.get(spell)
    if blob is None:
        return True
    lines = blob.strip().split("\n")
    tokens = lines[-1].strip().split()
    top_name = tokens[0]
    nsg = globals()
    nsl = locals()
    exec(blob, nsg, nsl)
    return bool(nsl[top_name])


def add_spell(traits, trait_names):
    """Add one spell to traits, at the one-point level."""
    while True:
        spell = random.choice(list(spell_to_prereq_function.keys()))
        if spell in trait_names:
            continue
        if prereq_satisfied(spell, traits):
            traits.append((spell, 1, SP))
            trait_names.add(spell)
            return


# TODO support multiple languages
# Maybe language as leveled 1-30 or 2-30, then split it up
# TODO effect of Language Talent
def generate_wizard():
    traits = [
        ("ST 10", 0, PA),
        ("DX 12", 40, PA),
        ("IQ 15", 100, PA),
        ("HT 11", 10, PA),
        ("HP 10", 0, SA),
        ("Will 15", 0, SA),
        ("Per 12", -15, SA),
        ("FP 14", 9, SA),
        ("Basic Speed 6.0", 5, SA),
        ("Basic Move 6", 0, SA),
        ("Magery 3", 35, AD),
        ("Occultism", 2, SK),
        ("Alchemy", 8, SK),
        ("Thaumatology", 1, SK),
        ("Hazardous Materials (Magical)", 1, SK),
        ("Research", 1, SK),
        ("Speed-Reading", 1, SK),
        ("Teaching", 1, SK),
        ("Writing", 1, SK),
        ("Meditation", 2, SK),
    ]

    build_spell_prereqs()

    ads1 = [
        [("DX +1", 20, PA)],
        [("IQ +1", 20, PA)],
        list_levels("Will +%d", 5, SA, 5),
        list_levels("FP +%d", 3, SA, 10),
        [("Eidetic Memory", 5, AD), ("Photographic Memory", 10, AD)],
        list_levels("Gizmos %d", 5, AD, 3),
        [("Intuition", 15, AD)],
        [("Language Talent", 10, AD)],
        [("Language (Spoken: Broken / Written: None)", 1, AD)],
        [("Language (Spoken: None / Written: Broken)", 1, AD)],
        [("Language (Spoken: Accented / Written: None)", 2, AD)],
        [("Language (Spoken: Broken / Written: Broken)", 2, AD)],
        [("Language (Spoken: None / Written: Accented)", 2, AD)],
        [("Language (Spoken: Native / Written: None)", 3, AD)],
        [("Language (Spoken: Accented / Written: Broken)", 3, AD)],
        [("Language (Spoken: Broken / Written: Accented)", 3, AD)],
        [("Language (Spoken: None / Written: Native)", 3, AD)],
        [("Language (Spoken: Native / Written: Broken)", 4, AD)],
        [("Language (Spoken: Accented / Written: Accented)", 4, AD)],
        [("Language (Spoken: Broken / Written: Native)", 4, AD)],
        [("Language (Spoken: Native / Written: Accented)", 5, AD)],
        [("Language (Spoken: Accented / Written: Native)", 5, AD)],
        [("Language (Spoken: Native / Written: Native)", 6, AD)],
        [("Luck", 15, AD), ("Extraordinary Luck", 30, AD)],
        list_levels("Magery %d", 10, AD, 3, min_level=4),
        list_levels("Mind Shield %d", 4, AD, 5),
        list_levels("Signature Gear %d", 1, AD, 10),
        [("Spirit Empathy", 10, AD)],
        [("Wild Talent 1 (Retention, Focused, Magical)", 21, AD)],
    ]
    traits.extend(pick_from_list(ads1, 30))

    disads1 = [
        list_self_control_levels("Curious", -5),
        [("Frightens Animals", -10, DI)],
        list_self_control_levels(
          "Obsession (Become the world's most powerful wizard, a lich, etc.)",
           -10),
        list_self_control_levels("Pyromania", -5),
        [("Skinny", -5, DI)],
        [("Social Stigma (Excommunicated)", -10, DI)],
        [("Unfit", -5, DI), ("Very Unfit", -15, DI)],
        list_levels("Unnatural Features %d", -1, DI, 5),
        [("Weirdness Magnet", -15, DI)],
    ]
    traits.extend(pick_from_list(disads1, -15))

    disads2 = [
        [("Absent-Mindedness", -15, DI)],
        list_self_control_levels("Bad Temper", -10),
        [("Clueless", -10, DI)],
        [("Combat Paralysis", -15, DI)],
        list_self_control_levels("Cowardice", -10),
        [("Hard of Hearing", -15, DI)],
        [("Klutz", -5, DI), ("Total Klutz", -15, DI)],
        list_self_control_levels("Loner", -5),
        [("Low Pain Threshold", -10, DI)],
        [("Nervous Stomach", -1, DI)],
        [("Oblivious", -5, DI)],
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels("Post-Combat Shakes", -5),
        [("Sense of Duty (Adventuring companions)", -5, DI)],
        [("Stubbornness", -5, DI)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -20))

    skills1 = [
        [("Hidden Lore (Demons)", 2, SK), ("Hidden Lore (Magic Items)", 2, SK),
         ("Hidden Lore (Magical Writings)", 2, SK), ("Hidden Lore (Spirits)", 2, SK)],
    ]
    traits.extend(pick_from_list(skills1, 2))

    skills2 = [
        [("Smallsword", 4, SK)],
        [("Shield (Buckler)", 4, SK)],
        [("Staff", 8, SK)],
    ]
    traits.extend(pick_from_list(skills2, 8))

    skills3 = [
        [("Innate Attack (any)", 4, SK)],
        [("Thrown Weapon (Dart)", 4, SK)],
        [("Throwing", 4, SK)],
        [("Sling", 4, SK)],
    ]
    traits.extend(pick_from_list(skills3, 4))

    skills4 = [
        [("Fast-Draw (Potion)", 1, SK)],
        [("Climbing", 1, SK)],
        [("Stealth", 1, SK)],
        [("Body Sense", 1, SK)],
        [("First Aid", 1, SK)],
        [("Gesture", 1, SK)],
        [("Savoir-Faire (High Society)", 1, SK)],
        [("Cartography", 1, SK)],
        [("Hidden Lore (Demons)", 1, SK)],
        [("Hidden Lore (Magic Items)", 1, SK)],
        [("Hidden Lore (Magical Writings)", 1, SK)],
        [("Hidden Lore (Spirits)", 1, SK)],
        [("Diplomacy", 1, SK)],
        [("Physiology (monster type)", 1, SK)],
        [("Strategy", 1, SK)],
        [("Hiking", 1, SK)],
        [("Scrounging", 1, SK)],
    ]
    # Remove duplicate Hidden Lore
    trait_names = set((trait[0] for trait in traits))
    for trait_name in trait_names:
        if (trait_name, 1) in skills4:
            skills4.remove((trait_name, 1))
    traits.extend(pick_from_list(skills4, 9))

    trait_names = set((trait[0] for trait in traits))
    for unused in range(30):
        add_spell(traits, trait_names)

    return traits


template_to_fn = {
    "barbarian": generate_barbarian,
    "bard": generate_bard,
    "cleric": generate_cleric,
    "druid": generate_druid,
    "holy_warrior": generate_holy_warrior,
    "knight": generate_knight,
    "martial_artist": generate_martial_artist,
    "scout": generate_scout,
    "swashbuckler": generate_swashbuckler,
    "thief": generate_thief,
    "wizard": generate_wizard,
}

templates = sorted(template_to_fn.keys())


def main():
    parser = argparse.ArgumentParser(description=
      "Generate a random GURPS Dungeon Fantasy character")
    parser.add_argument("--template", "-t",
      help="Character template to use (barbarian, bard, cleric, druid, "
           "holy_warrior, knight, martial_artist, scout, swashbuckler, "
           "thief, wizard)",
      default="random")
    args = parser.parse_args()
    template = args.template.lower()
    if template == "random":
        template = random.choice(templates)
    if template not in templates:
        raise argparse.ArgumentTypeError("Invalid template; must be one of %s"
          % ", ".join(templates + ["random"]))
    print(template.title())
    fn = template_to_fn[template]
    traits = fn()
    traits = merge_traits(traits)
    print_traits(traits)


if __name__ == "__main__":
    main()
