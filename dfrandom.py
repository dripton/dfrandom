#!/usr/bin/env python3


"""Generate a random GURPS Dungeon Fantasy character."""

import argparse
from collections import Counter
import copy
import os
import random
import re
import xml.etree.ElementTree as et


def list_levels(name, cost, num_levels, min_level=1):
    """Return a list of num_levels tuples, each with the name and
    cost of that level.

    name should have a %d in it for the level number.
    cost is per level
    """
    lst = []
    for level in range(min_level, min_level + num_levels):
        tup = (name % level, cost * level)
        lst.append(tup)
    return lst


def list_self_control_levels(name, base_cost):
    """Return a list of num_levels tuples, each with the name and
    cost of that level.

    name is just the base name.
    base_cost is for a self-control number of 12.
    """
    lst = []
    lst.append(("%s (15)" % name, int(0.5 * base_cost)))
    lst.append(("%s (12)" % name, base_cost))
    lst.append(("%s (9)" % name, int(1.5 * base_cost)))
    lst.append(("%s (6)" % name, 2 * base_cost))
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
            trait, cost = tup
            if abs(cost) <= abs(points_left):
                traits.append((trait, cost))
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
            trait, cost = tup
            if (abs(cost) <= abs(points_left) and
              prereq_satisfied(trait, original_traits + traits)):
                traits.append((trait, cost))
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
    while skills_lst and points_left != 0:
        skill_name = random.choice(skills_lst)
        for ii, skill_tup in enumerate(traits):
            (skill_name2, cost) = skill_tup
            if skill_name2 == skill_name:
                cost2 = next_skill_cost(cost)
                difference = cost2 - cost
                if difference <= points_left:
                    traits[ii] = (skill_name2, cost2)
                    points_left -= difference
                    break
        else:
            cost2 = min_cost
            traits.append((skill_name, cost2))
            points_left -= cost2


# TODO trait type headings: attributes, advantages, disads, skills, spells
# Unfortunately there are some trait names that are reused across types
# (like Climbing is both a skill and a spell), so we need to go back and
# tag all traits by type
def print_traits(traits):
    total_cost = 0
    for name, cost in traits:
        total_cost += cost
        print("%s [%d]" % (name, cost))
    print("total points: %d" % total_cost)


def generate_barbarian():
    traits = [
        ("ST 17", 63),
        ("DX 13", 60),
        ("IQ 10", 0),
        ("HT 13", 30),
        ("HP 22", 9),
        ("Will 10", 0),
        ("Per 12", 10),
        ("FP 13", 0),
        ("Basic Speed 6.0", -10),
        ("Basic Move 7", 0),
        ("High Pain Threshold", 10),
        ("Outdoorsman 4", 40),
        ("Gigantism", 0),
        ("Social Stigma (Minority Group)", -10),
        ("Camouflage", 1),
        ("Navigation (Land)", 2),
        ("Tracking", 1),
        ("Brawling", 1),
        ("Stealth", 2),
        ("Wrestling", 2),
        ("Naturalist", 1),
        ("Swimming", 1),
        ("Hiking", 1),
        ("Running", 1),
        ("Fishing", 1),
        ("Animal Handling (any)", 2),
        ("Disguise (Animals)", 2),
        ("Weather Sense", 2),
        ("Intimidation", 2),
    ]
    ads1 = [
        list_levels("ST +%d", 9, 3),
        list_levels("HT +%d", 10, 3),
        list_levels("Per +%d", 5, 6),
        [("Absolute Direction", 5)],
        list_levels("Acute Hearing %d", 2, 5),
        list_levels("Acute Taste and Smell %d", 2, 5),
        list_levels("Acute Touch %d", 2, 5),
        list_levels("Acute Vision %d", 2, 5),
        [("Alcohol Tolerance", 1)],
        [("Animal Empathy", 5)],
        list_levels("Animal Friend %d", 5, 4),
        [("Combat Reflexes", 15)],
        [("Fit", 5), ("Very Fit", 15)],
        list_levels("Hard to Kill %d", 2, 5),
        list_levels("Hard to Subdue %d", 2, 5),
        list_levels("Lifting ST %d", 3, 3),
        [("Luck", 15), ("Extraordinary Luck", 30)],
        list_levels("Magic Resistance %d", 2, 5),
        [("Rapid Healing", 5), ("Very Rapid Healing", 15)],
        [("Recovery", 10)],
        [("Resistant to Disease 3", 3),
         ("Resistant to Disease 8", 5)],
        [("Resistant to Poison 3", 5)],
        list_levels("Signature Gear %d", 1, 10),
        [("Striking ST 1", 5), ("Striking ST 2", 9)],
        list_levels("Temperature Tolerance %d", 1, 2),
        [("Weapon Bond", 1)],
    ]
    traits.extend(pick_from_list(ads1, 30))

    disads1 = [
        [("Easy to Read", -10)],
        list_self_control_levels("Gullibility", -10),
        [("Language: Spoken (Native) / Written (None)", -3)],
        list_levels("Low TL %d", -5, 2),
        [("Odious Personal Habit (Unrefined manners)", -5)],
        list_self_control_levels("Phobia (Machinery)", -5),
        [("Wealth (Struggling)", -10)],
    ]
    traits.extend(pick_from_list(disads1, -10))

    disads2 = [
        [("Appearance: Unattractive", -4), ("Appearance: Ugly", -8)],
        list_self_control_levels("Bad Temper", -10),
        list_self_control_levels("Berserk", -10),
        list_self_control_levels("Bloodlust", -10),
        list_self_control_levels2("Compulsive Carousing", -5,
                                  "Phobia (Crowds)", -15),
        list_self_control_levels("Gluttony", -5),
        list_levels("Ham-Fisted %d", -5, 2),
        [("Horrible Hangovers", -1)],
        list_self_control_levels("Impulsiveness", -10),
        list_self_control_levels("Overconfidence", -5),
        [("Sense of Duty (Adventuring companions)", -5)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -20))

    skills1 = [
        [("Survival (Arctic)", 1)],
        [("Survival (Desert)", 1)],
        [("Survival (Island/Beach)", 1)],
        [("Survival (Jungle)", 1)],
        [("Survival (Mountain)", 1)],
        [("Survival (Plains)", 1)],
        [("Survival (Swampland)", 1)],
        [("Survival (Woodlands)", 1)],
    ]
    traits.extend(pick_from_list(skills1, 1))

    skills2 = [
        [("Thrown Weapon (Axe/Mace)", 4)],
        [("Thrown Weapon (Harpoon)", 4)],
        [("Thrown Weapon (Spear)", 4)],
        [("Thrown Weapon (Stick)", 4)],
        [("Bolas", 4)],
        [("Bow", 4)],
        [("Spear Thrower", 4)],
        [("Throwing", 4)],
    ]
    traits.extend(pick_from_list(skills2, 4))

    skills3 = [
        [("Axe/Mace", 8), ("Broadsword", 8), ("Spear", 8), ("Flail", 8)],
        [("Shield", 8)],
        [("Polearm", 16)],
        [("Spear", 16)],
        [("Two-Handed Axe/Mace", 16)],
        [("Two-Handed Sword", 16)],
        [("Two-Handed Flail", 16)],
    ]
    traits.extend(pick_from_list(skills3, 16))

    skills4 = [
        [("Mimicry (Animal Sounds)", 1)],
        [("Mimicry (Bird Calls)", 1)],
    ]
    traits.extend(pick_from_list(skills4, 1))

    skills5 = [
        [("Forced Entry", 1)],
        [("Climbing", 1)],
        [("First Aid", 1)],
        [("Gesture", 1)],
        [("Seamanship", 1)],
        [("Carousing", 1)],
        [("Lifting", 1)],
        [("Skiing", 1)],
        [("Observation", 1)],
    ]
    traits.extend(pick_from_list(skills5, 4))
    return traits


def generate_bard():
    traits = [
        ("ST 11", 10),
        ("DX 12", 40),
        ("IQ 14", 80),
        ("HT 11", 10),
        ("HP 11", 0),
        ("Will 14", 0),
        ("Per 14", 0),
        ("FP 11", 0),
        ("Basic Speed 6.0", 5),
        ("Basic Move 6", 0),
        ("Bardic Talent 2", 16),
        ("Charisma 1", 5),
        ("Musical Ability 2", 10),
        ("Voice", 10),
        ("Acting", 2),
        ("Diplomacy", 1),
        ("Fast-Talk", 1),
        ("Musical Instrument (any)", 2),
        ("Performance", 1),
        ("Public Speaking", 1),
        ("Singing", 1),
        ("Fast-Draw (any)", 1),
        ("Stealth", 2),
        ("Current Affairs (any)", 1),
        ("Savoir-Faire (High Society)", 1),
        ("Interrogation", 1),
        ("Merchant", 1),
        ("Propaganda", 1),
        ("Streetwise", 1),
        ("Musical Composition", 1),
        ("Carousing", 1),
        ("Intimidation", 1),
        ("Detect Lies", 1),
        ("Heraldry", 1),
        ("Poetry", 1),
    ]

    build_spell_prereqs(allowed_colleges=allowed_bard_colleges)
    convert_magery_to_bardic_talent()
    add_special_bard_skills_to_spell_prereqs()

    ads1 = [
        [("Empathy (PM)", 11)],
        [("Mimicry (PM)", 7)],
        [("Mind Control (PM)", 35)],
        [("Rapier Wit (PM)", 4)],
        [("Speak With Animals (PM)", 18)],
        [("Subsonic Speech (PM)", 7)],
        [("Telecommunication (Telesend, PM)", 21)],
        [("Terror (PM)", 21)],
        [("Ultrasonic Speech (PM)", 7)],
    ]
    for spell in spell_to_prereq_function:
        ads1.append([(spell, 1)])
    traits.extend(pick_from_list_enforcing_prereqs(ads1, 25, traits))

    ads2 = [
        [("DX +1", 20)],
        [("IQ +1", 20)],
        list_levels("FP +%d", 3, 8),
        [("Basic Speed +1", 20)],
        list_levels("Acute Hearing %d", 2, 5),
        [("Appearance: Attractive", 4), ("Appearance: Handsome", 12),
         ("Appearance: Very Handsome", 16)],
        list_levels("Bardic Talent %d", 8, 2, min_level=3),
        list_levels("Charisma %d", 5, 5, min_level=2),
        [("Cultural Adaptability", 10)],
        [("Eidetic Memory", 5), ("Photographic Memory", 10)],
        [("Honest Face", 1),],
        [("Language Talent", 10),],
        [("Language (Spoken: Broken / Written: None)", 1)],
        [("Language (Spoken: None / Written: Broken)", 1)],
        [("Language (Spoken: Accented / Written: None)", 2)],
        [("Language (Spoken: Broken / Written: Broken)", 2)],
        [("Language (Spoken: None / Written: Accented)", 2)],
        [("Language (Spoken: Native / Written: None)", 3)],
        [("Language (Spoken: Accented / Written: Broken)", 3)],
        [("Language (Spoken: Broken / Written: Accented)", 3)],
        [("Language (Spoken: None / Written: Native)", 3)],
        [("Language (Spoken: Native / Written: Broken)", 4)],
        [("Language (Spoken: Accented / Written: Accented)", 4)],
        [("Language (Spoken: Broken / Written: Native)", 4)],
        [("Language (Spoken: Native / Written: Accented)", 5)],
        [("Language (Spoken: Accented / Written: Native)", 5)],
        [("Language (Spoken: Native / Written: Native)", 6)],
        [("Luck", 15), ("Extraordinary Luck", 30)],
        list_levels("Musical Ability %d", 5, 2, min_level=3),
        [("No Hangover", 1)],
        [("Penetrating Voice", 1)],
        list_levels("Signature Gear %d", 1, 10),
        [("Smooth Operator 1", 15)],
        [("Social Chameleon", 5)],
        [("Wealth (Comfortable)", 10), ("Wealth (Wealthy)", 20)],
        [("Wild Talent 1", 20)],
    ]
    ads2.extend(ads1)
    traits.extend(pick_from_list(ads2, 25))

    disads1 = [
        list_self_control_levels2("Chummy", -5, "Gregarious", -10),
        list_self_control_levels("Compulsive Carousing", -5),
        list_self_control_levels("Lecherousness", -15),
        [("Sense of Duty (Adventuring companions)", -5)],
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
        [("Code of Honor (Gentleman's)", -10)],
        list_self_control_levels("Compulsive Lying", -15),
        [("Odious Personal Habit (Continuous singing or strumming)", -5)],
        list_self_control_levels("Post-Combat Shakes", -5),
    ]
    disads3.extend(disads2)
    traits.extend(pick_from_list(disads3, -20))

    skills1 = [
        [("Rapier", 12), ("Saber", 12), ("Shortsword", 12), ("Smallsword", 12)],
        [("Rapier", 8), ("Saber", 8), ("Shortsword", 8), ("Smallsword", 8)],
        [("Shield (Buckler)", 4), ("Cloak", 4), ("Main-Gauche", 4)],
    ]
    traits.extend(pick_from_list(skills1, 12))

    skills2 = [
        [("Thrown Weapon (Knife)", 2)],
        [("Bow", 2)],
        [("Throwing", 2)],
    ]
    traits.extend(pick_from_list(skills2, 2))

    skills3 = [
        [("Climbing", 1)],
        [("Dancing", 1)],
        [("Acrobatics", 1)],
        [("Slight of Hand", 1)],
        [("First Aid", 1)],
        [("Gesture", 1)],
        [("Connoisseur (any)", 1)],
        [("Disguise", 1)],
        [("Teaching", 1)],
        [("Writing", 1)],
        [("Mimicry (Speech)", 1)],
        [("Ventriloquism", 1)],
        [("Hiking", 1)],
        [("Sex Appeal", 1)],
        [("Scrounging", 1)],
        [("Observation", 1)],
    ]
    traits.extend(pick_from_list(skills3, 6))

    special_skills = []
    for spell in spell_to_prereq_function:
        if (spell, 1) not in traits:
            special_skills.append([(spell, 1)])
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
    for trait_name, cost in traits:
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
    for trait_name, cost in traits:
        bare_name = trait_name_to_bare_name.get(trait_name)
        if bare_name in bare_names_done:
            pass
        elif bare_name is None:
            traits2.append((trait_name, cost))
        else:
            level = bare_name_to_level[bare_name]
            trait_name2 = "%s %d" % (bare_name, level)
            cost2 = bare_name_to_cost[bare_name]
            traits2.append((trait_name2, cost2))
            bare_names_done.add(bare_name)
    return traits2


def generate_cleric():
    traits = [
        ("ST 12", 20),
        ("DX 12", 40),
        ("IQ 14", 80),
        ("HT 12", 20),
        ("HP 12", 0),
        ("Will 14", 0),
        ("Per 14", 0),
        ("FP 12", 0),
        ("Basic Speed 6.0", 0),
        ("Basic Move 6", 0),
        ("Clerical Investment", 5),
        ("Power Investiture 3", 30),
        ("Esoteric Medicine (Holy)", 4),
        ("Exorcism", 4),
        ("First Aid", 1),
        ("Occultism", 1),
        ("Public Speaking", 1),
        ("Teaching", 1),
        ("Diagnosis", 1),
        ("Theology", 1),
        ("Religious Ritual", 1),
        ("Surgery", 2),
        ("Meditation", 1),
    ]
    spells = [
        # PI 1
        [("Armor", 1)],
        [("Aura", 1)],
        [("Body-Reading", 1)],
        [("Bravery", 1)],
        [("Cleansing", 1)],
        [("Coolness", 1)],
        [("Detect Magic", 1)],
        [("Detect Poison", 1)],
        [("Final Rest", 1)],
        [("Lend Energy", 1)],
        [("Lend Vitality", 1)],
        [("Light", 1)],
        [("Might", 1)],
        [("Minor Healing", 1)],
        [("Purify Air", 1)],
        [("Purify Water", 1)],
        [("Recover Energy", 1)],
        [("Sense Life", 1)],
        [("Sense Spirit", 1)],
        [("Share Vitality", 1)],
        [("Shield", 1)],
        [("Silence", 1)],
        [("Stop Bleeding", 1)],
        [("Test Food", 1)],
        [("Thunderclap", 1)],
        [("Umbrella", 1)],
        [("Vigor", 1)],
        [("Warmth", 1)],
        [("Watchdog", 1)],
        # PI 2
        [("Awaken", 1)],
        [("Clean", 1)],
        [("Command", 1)],
        [("Compel Truth", 1)],
        [("Continual Light", 1)],
        [("Create Water", 1)],
        [("Glow", 1)],
        [("Great Voice", 1)],
        [("Healing Slumber", 1)],
        [("Major Healing", 1)],
        [("Peaceful Sleep", 1)],
        [("Persuasion", 1)],
        [("Purify Food", 1)],
        [("Relieve Sickness", 1)],
        [("Remove Contagion", 1)],
        [("Resist Acid", 1)],
        [("Resist Cold", 1)],
        [("Resist Disease", 1)],
        [("Resist Fire", 1)],
        [("Resist Lightning", 1)],
        [("Resist Pain", 1)],
        [("Resist Poison", 1)],
        [("Resist Pressure", 1)],
        [("Restore Hearing", 1)],
        [("Restore Memory", 1)],
        [("Restore Sight", 1)],
        [("Restore Speech", 1)],
        [("Seeker", 1)],
        [("Soilproof", 1)],
        [("Stop Spasm", 1)],
        [("Summon Spirit", 1)],
        [("Truthsayer", 1)],
        [("Turn Spirit", 1)],
        [("Turn Zombie", 1)],
        [("Wall of Light", 1)],
        # PI 3
        [("Affect Spirits", 1)],
        [("Astral Vision", 1)],
        [("Breathe Water", 1)],
        [("Command Spirit", 1)],
        [("Create Food", 1)],
        [("Cure Disease", 1)],
        [("Dispel Possession", 1)],
        [("Flaming Weapon", 1)],
        [("Great Healing", 1)],
        [("Magic Resistance", 1)],
        [("Neutralize Poison", 1)],
        [("Oath", 1)],
        [("Relieve Madness", 1)],
        [("Relieve Paralysis", 1)],
        [("Repel Spirits", 1)],
        [("Restoration", 1)],
        [("See Secrets", 1)],
        [("Silver Tongue", 1)],
        [("Stone to Flesh", 1)],
        [("Stop Paralysis", 1)],
        [("Strengthen Will", 1)],
        [("Sunbolt", 1)],
        [("Sunlight", 1)],
        [("Suspended Animation", 1)],
        [("Water to Wine", 1)],
        [("Wisdom", 1)],
    ]
    ads1 = [
        [("Ally (Divine servent, PM, Summonable, 12-)", 19),
         ("Ally (Divine servent, PM, Summonable, 15-)", 29)],
        [("Detect evil (PM)", 18),
         ("Detect good (PM)", 18),
         ("Detect supernatural beings (PM)", 18),
         ("Ally (Divine servent, PM, Summonable, 15-)", 29)],
        [("Healing (Faith Healing, PM)", 33)],
        [("Intuition (PM)", 14)],
        [("Oracle (PM)", 14)],
        [("Patron (Deity, PM, Special Abilities, Highly Accessible, 6-)", 36),
         ("Patron (Deity, PM, Special Abilities, Highly Accessible, 9-)", 72)],
        [("Resistant to Evil Supernatural Powers (PM) 3", 5),
         ("Resistant to Evil Supernatural Powers (PM) 8", 7)],
        [("Spirit Empathy (PM)", 9)],
        [("True Faith (PM, Turning)", 24)],
    ]
    ads1.extend(spells)
    # TODO Add PI 4 spells if PI 4 is selected.  (No points left after PI 5.)
    traits.extend(pick_from_list(ads1, 25))

    ads2 = [
        list_levels("ST +%d", 10, 2),
        [("DX +1", 20)],
        [("IQ +1", 20)],
        list_levels("HT +%d", 10, 2),
        list_levels("Will +%d", 5, 4),
        list_levels("FP +%d", 3, 6),
        list_levels("Fearlessness %d", 2, 5),
        [("Unfazeable", 15)],
        list_levels("Healer %d", 10, 2),
        [("Language (Spoken: Broken / Written: None)", 1)],
        [("Language (Spoken: None / Written: Broken)", 1)],
        [("Language (Spoken: Accented / Written: None)", 2)],
        [("Language (Spoken: Broken / Written: Broken)", 2)],
        [("Language (Spoken: None / Written: Accented)", 2)],
        [("Language (Spoken: Native / Written: None)", 3)],
        [("Language (Spoken: Accented / Written: Broken)", 3)],
        [("Language (Spoken: Broken / Written: Accented)", 3)],
        [("Language (Spoken: None / Written: Native)", 3)],
        [("Language (Spoken: Native / Written: Broken)", 4)],
        [("Language (Spoken: Accented / Written: Accented)", 4)],
        [("Language (Spoken: Broken / Written: Native)", 4)],
        [("Language (Spoken: Native / Written: Accented)", 5)],
        [("Language (Spoken: Accented / Written: Native)", 5)],
        [("Language (Spoken: Native / Written: Native)", 6)],
        [("Luck", 15)],
        list_levels("Mind Shield %d", 4, 5),
        list_levels("Power Investiture %d", 10, 2, min_level=4),
        [("Resistant to Disease (PM) 3", 3),
         ("Resistant to Disease (PM) 8", 5)],
        list_levels("Signature Gear %d", 1, 10),
    ]
    ads2.extend(ads1)
    traits.extend(pick_from_list(ads2, 20))

    disads1 = [
        [("Honesty (12)", -10)],
        [("Sense of Duty (Coreligionists)", -10)],
        [("Vow (No edged weapons)", -10)],
    ]
    traits.extend(pick_from_list(disads1, -10))

    disads2 = [
        [("Disciplines of Faith (Ritualism)", -5),
         ("Disciplines of Faith (Ritualism)", -10),
         ("Disciplines of Faith (Mysticism)", -5),
         ("Disciplines of Faith (Mysticism)", -10)],
        [("Fanaticism", -15)],
        [("Intolerance (Evil religions)", -5),
         ("Intolerance (All other religions)", -10)],
        [("Vow (Chastity)", -5), ("Vow (Vegetarianism)", -5)],
        [("Wealth (Struggling)", -10), ("Wealth (Poor)", -15)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    disads3 = [
        list_self_control_levels("Charitable", -15),
        list_self_control_levels("Compulsive Generosity", -5) +\
            list_self_control_levels("Miserliness", -10),
        list_self_control_levels("Gluttony", -5),
        list_self_control_levels("Overconfidence", -5),
        [("Overweight", -1), ("Fat", -3)],
        list_self_control_levels("Selfless", -5),
        [("Sense of Duty (Adventuring companions)", -5)],
        [("Stubbornness", -5)],
        list_self_control_levels("Truthfulness", -5),
        [("Weirdness Magnet", -15)],
    ]
    disads3.extend(disads2)
    traits.extend(pick_from_list(disads3, -25))

    skills1 = [
        [("Innate Attack", 4)],
        [("Throwing", 4)],
        [("Sling", 4)],
    ]
    traits.extend(pick_from_list(skills1, 4))

    skills2 = [
        [("Axe/Mace", 8), ("Broadsword", 8), ("Flail", 8)],
        [("Shield", 4)],
        [("Staff", 12)],
    ]
    traits.extend(pick_from_list(skills2, 12))

    skills3 = [
        [("Hidden Lore (Demons)", 1)],
        [("Hidden Lore (Spirits)", 1)],
        [("Hidden Lore (Undead)", 1)],
    ]
    traits.extend(pick_from_list(skills3, 1))

    skills4 = [
        [("Climbing", 1)],
        [("Stealth", 1)],
        [("Gesture", 1)],
        [("Panhandling", 1)],
        [("Savoir-Faire (High Society)", 1)],
        [("Research", 1)],
        [("Writing", 1)],
        [("Hiking", 1)],
        [("Scrounging", 1)],
        [("Observation", 1)],
        [("Search", 1)],
    ]
    traits.extend(pick_from_list(skills4, 5))

    trait_names = set((trait[0] for trait in traits))
    if ("Power Investiture 4" in trait_names or
        "Power Investiture 5" in trait_names):
        spells.extend([
            [("Astral Block", 1)],
            [("Banish", 1)],
            [("Continual Sunlight", 1)],
            [("Dispel Magic", 1)],
            [("Divination", 1)],
            [("Essential Food", 1)],
            [("Gift of Letters", 1)],
            [("Gift of Tongues", 1)],
            [("Instant Neutralize Poison", 1)],
            [("Instant Restoration", 1)],
            [("Monk's Banquet", 1)],
            [("Regeneration", 1)],
            [("Suspend Curse", 1)],
            [("Vigil", 1)],
        ])
        if "Power Investiture 5" in trait_names:
            spells.extend([
                [("Bless", 1)],
                [("Curse", 1)],
                [("Earthquake", 1)],
                [("Entrap Spirit", 1)],
                [("Instant Regeneration", 1)],
                [("Pentagram", 1)],
                [("Remove Curse", 1)],
                [("Storm", 1)],
                [("Suspend Mana", 1)],
            ])
    traits.extend(pick_from_list(spells, 20))
    return traits


def generate_druid():
    traits = [
        ("ST 11", 10),
        ("DX 12", 40),
        ("IQ 14", 80),
        ("HT 13", 30),
        ("HP 11", 0),
        ("Will 14", 0),
        ("Per 14", 0),
        ("FP 13", 0),
        ("Basic Speed 6.0", -5),
        ("Basic Move 6", 0),
        ("Green Thumb 1", 5),
        ("Power Investiture (Druidic) 3", 30),
        ("Esoteric Medicine (Druidic)", 4),
        ("Herb Lore", 4),
        ("Naturalist", 2),
        ("Camouflage", 1),
        ("Animal Handling (any)", 1),
        ("Disguise (Animals)", 1),
        ("Weather Sense", 1),
        ("Pharmacy (Herbal)", 1),
        ("Religious Ritual (Druidic)", 1),
        ("Theology (Druidic)", 1),
        ("Veterinary", 1),
        ("Climbing", 2),
        ("Stealth", 2),
        ("Hiking", 1),
    ]

    spells = [
        # PI 1
        [("Beast-Rouser", 1)],
        [("Beast-Soother", 1)],
        [("Detect Magic", 1)],
        [("Detect Poison", 1)],
        [("Extinguish Fire", 1)],
        [("Find Direction", 1)],
        [("Hawk Vision", 1)],
        [("Identify Plant", 1)],
        [("Master", 1)],
        [("No-Smell", 1)],
        [("Purify Air", 1)],
        [("Purify Earth", 1)],
        [("Purify Water", 1)],
        [("Quick March", 1)],
        [("Recover Energy", 1)],
        [("Seek Coastline", 1)],
        [("Seek Earth", 1)],
        [("Seek Food", 1)],
        [("Seek Pass", 1)],
        [("Seek Plant", 1)],
        [("Seek Water", 1)],
        [("Sense Life", 1)],
        [("Tell Position", 1)],
        [("Umbrella", 1)],
        # PI 2
        [("Animal Control", 1)],
        [("Beast Link", 1)],
        [("Beast Seeker", 1)],
        [("Beast Speech", 1)],
        [("Bless Plants", 1)],
        [("Cure Disease", 1)],
        [("Fog", 1)],
        [("Frost", 1)],
        [("Heal Plant", 1)],
        [("Hide Path", 1)],
        [("Know Location", 1)],
        [("Light Tread", 1)],
        [("Mystic Mist", 1)],
        [("Neutralize Poison", 1)],
        [("Pathfinder", 1)],
        [("Plant Growth", 1)],
        [("Plant Vision", 1)],
        [("Pollen Cloud", 1)],
        [("Predict Earth Movement", 1)],
        [("Predict Weather", 1)],
        [("Purify Food", 1)],
        [("Repel Animal", 1)],
        [("Rider", 1)],
        [("Rider Within", 1)],
        [("Shape Air", 1)],
        [("Shape Earth", 1)],
        [("Shape Plant", 1)],
        [("Shape Water", 1)],
        [("Spider Silk", 1)],
        [("Wall of Wind", 1)],
        [("Weather Dome", 1)],
        [("Windstorm", 1)],
        # PI 3
        [("Animate Plant", 1)],
        [("Beast Summoning", 1)],
        [("Blossom", 1)],
        [("Breathe Water", 1)],
        [("Clouds", 1)],
        [("Conceal", 1)],
        [("Create Plant", 1)],
        [("False Tracks", 1)],
        [("Forest Warning", 1)],
        [("Freeze", 1)],
        [("Instant Neutralize Poison", 1)],
        [("Melt Ice", 1)],
        [("Plant Control", 1)],
        [("Plant Sense", 1)],
        [("Plant Speech", 1)],
        [("Protect Animal", 1)],
        [("Rain", 1)],
        [("Rain of Nuts", 1)],
        [("Rejuvenate Plant", 1)],
        [("Remember Path", 1)],
        [("Resist Cold", 1)],
        [("Resist Lightning", 1)],
        [("Resist Pressure", 1)],
        [("Snow", 1)],
        [("Snow Shoes", 1)],
        [("Summon Elemental", 1)],
        [("Tangle Growth", 1)],
        [("Walk Through Plants", 1)],
        [("Walk Through Wood", 1)],
        [("Water Vision", 1)],
        [("Waves", 1)],
        [("Whirlpool", 1)],
        [("Wind", 1)],
    ]
    ads1 = [
        [("Ally (Nature spirit or totem beast, PM, Summonable, 12-)", 19),
         ("Ally (Nature spirit or totem beast, PM, Summonable, 15-)", 29)],
        [("Animal Empathy (PM)", 5)],
        [("Channeling (PM, Nature Spirits)", 4)],
        [("Damage Resistance 1 (Limited Elemental, PM)", 4),
         ("Damage Resistance 2 (Limited Elemental, PM)", 7)],
        [("Detect (Plants, PM)", 18),
         ("Detect (Animals, PM)", 18),
         ("Detect (Anything Alive, PM)", 27)],
        [("Medium (PM, Nature Spirits)", 4)],
        [("Mind Control (Animals Only, PM)", 33)],
        [("Plant Empathy (PM)", 5)],
        [("Speak With Animals (PM)", 23)],
        [("Speak With Plants (PM)", 14)],
        [("Terrain Adaptation (Ice, PM)", 5),
         ("Terrain Adaptation (Mud, PM)", 5),
         ("Terrain Adaptation (Snow, PM)", 5)],
    ]
    ads1.extend(spells)
    # TODO Add PI 4 spells if PI 4 is selected.  (No points left after PI 5.)
    traits.extend(pick_from_list(ads1, 20))

    ads2 = [
        [("IQ +1", 20)],
        list_levels("HT +%d", 10, 2),
        list_levels("Per +%d", 5, 4),
        list_levels("FP +%d", 3, 6),
        list_levels("Animal Friend %d", 5, 4),
        list_levels("Green Thumb %d", 5, 3, min_level=2),
        list_levels("Healer %d", 10, 2),
        [("Intuition", 15)],
        [("Luck", 15)],
        list_levels("Mind Shield %d", 4, 5),
        list_levels("Outdoorsman %d", 10, 2),
        list_levels("Power Investiture (Druidic) %d", 10, 2, min_level=4),
        [("Resistant to Disease (PM) 3", 3),
         ("Resistant to Disease (PM) 8", 5)],
        list_levels("Signature Gear %d", 1, 10),
        [("Spirit Empathy", 10)],
    ]
    ads2.extend(ads1)
    traits.extend(pick_from_list(ads2, 20))

    disads1 = [
        [("Disciplines of Faith (Ritualism)", -5),
         ("Disciplines of Faith (Ritualism)", -10),
         ("Disciplines of Faith (Mysticism)", -5),
         ("Disciplines of Faith (Mysticism)", -10)],
        [("Sense of Duty (Wild Nature)", -15)],
        [("Vow (Vegetarianism)", -5)],
        [("Vow (Never Sleep Indoors)", -10)],
        [("Wealth (Struggling)", -10), ("Wealth (Poor)", -15)],
    ]
    traits.extend(pick_from_list(disads1, -20))

    disads2 = [
        [("Intolerance (Urbanites)", -5)],
        list_self_control_levels("Loner", -5),
        [("No Sense of Humor", -10)],
        [("Odious Personal Habit (Dirty Hippy)", -5)],
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels("Phobia (Crowds)", -15),
        list_self_control_levels("Phobia (Fire)", -5),
        list_self_control_levels("Phobia (Machinery)", -5),
        [("Stubbornness", -5)],
        [("Weirdness Magnet", -15)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -25))

    skills1 = [
        [("Innate Attack", 4)],
        [("Thrown Weapon (Spear)", 4)],
        [("Thrown Weapon (Stick)", 4)],
        [("Bolas", 4)],
        [("Lasso", 4)],
        [("Throwing", 4)],
        [("Blowpipe", 4)],
        [("Net", 4)],
        [("Sling", 4)],
    ]
    traits.extend(pick_from_list(skills1, 4))

    skills2 = [
        [("Axe/Mace", 8), ("Broadsword", 8), ("Shortsword", 8), ("Spear", 8)],
        [("Shield", 4)],
        [("Spear", 12)],
        [("Staff", 12)],
    ]
    traits.extend(pick_from_list(skills2, 12))

    skills3 = [
        [("Hidden Lore (Elementals)", 1)],
        [("Hidden Lore (Faeries)", 1)],
        [("Hidden Lore (Nature Spirits)", 1)],
    ]
    traits.extend(pick_from_list(skills3, 1))

    skills4 = [
        [("Mimicry (Animal Sounds)", 1)],
        [("Mimicry (Bird Calls)", 1)],
    ]
    traits.extend(pick_from_list(skills4, 1))

    skills5 = [
        [("Survival (Arctic)", 1)],
        [("Survival (Desert)", 1)],
        [("Survival (Island/Beach)", 1)],
        [("Survival (Jungle)", 1)],
        [("Survival (Mountain)", 1)],
        [("Survival (Plains)", 1)],
        [("Survival (Swampland)", 1)],
        [("Survival (Woodlands)", 1)],
    ]
    traits.extend(pick_from_list(skills5, 1))

    skills5 = [
        [("Knife", 1)],
        [("First Aid", 1)],
        [("Gesture", 1)],
        [("Animal Handling (any other)", 1)],
        [("Hidden Lore (Elementals)", 1)],
        [("Hidden Lore (Faeries)", 1)],
        [("Hidden Lore (Nature Spirits)", 1)],
        [("Teaching", 1)],
        [("Diagnosis", 1)],
        [("Poisons", 1)],
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
            [("Beast Possession", 1)],
            [("Blight", 1)],
            [("Body of Slime", 1)],
            [("Body of Water", 1)],
            [("Body of Wind", 1)],
            [("Body of Wood", 1)],
            [("Control Elemental", 1)],
            [("Create Animal", 1)],
            [("Create Spring", 1)],
            [("Dispel Magic", 1)],
            [("Dry Spring", 1)],
            [("Frostbite", 1)],
            [("Hail", 1)],
            [("Lightning", 1)],
            [("Plant Form", 1)],
            [("Sandstorm", 1)],
            [("Shapeshifting", 1)],
            [("Storm", 1)],
            [("Strike Barren", 1)],
            [("Tide", 1)],
            [("Wither Plant", 1)],
        ])
        if "Power Investiture (Druidic) 5" in trait_names:
            spells.extend([
                [("Alter Terrain", 1)],
                [("Arboreal Immurement", 1)],
                [("Create Elemental", 1)],
                [("Entombment", 1)],
                [("Partial Shapeshifting", 1)],
                [("Permanent Beast Possession", 1)],
                [("Permanent Shapeshifting", 1)],
                [("Plant Form Other", 1)],
                [("Shapeshift Others", 1)],
            ])
    traits.extend(pick_from_list(spells, 20))
    return traits


def generate_holy_warrior():
    traits = [
        ("ST 13", 30),
        ("DX 13", 60),
        ("IQ 12", 40),
        ("HT 13", 30),
        ("HP 13", 0),
        ("Will 14", 10),
        ("Per 12", 0),
        ("FP 13", 0),
        ("Basic Speed 6.0", -10),
        ("Basic Move 6", 0),
        ("Born War Leader 1", 5),
        ("Holiness 2", 10),
        ("Shtick (Foes slain personally can't rise as undead)", 1),
        ("Exorcism", 4),
        ("Brawling", 2),
        ("Wrestling", 4),
        ("Leadership", 1),
        ("Physiology (monster type)", 4),
        ("Psychology (monster type)", 4),
        ("Strategy", 2),
        ("Tactics", 2),
        ("Intimidation", 1),
        ("Religious Ritual", 1),
        ("Theology", 1),
        ("Meditation", 1),
        ("Esoteric Medicine (Holy)", 1),
    ]

    ads1 = [
        [("Higher Purpose (Slay Demons)", 5),
         ("Higher Purpose (Slay Undead)", 5)],
    ]
    traits.extend(pick_from_list(ads1, 5))

    # Merge the two lists since extra points can go either way.
    ads2 = [
        [("Ally (Divine servent, PM, Summonable, 12-)", 19),
         ("Ally (Divine servent, PM, Summonable, 15-)", 29)],
        [("Detect evil (PM)", 18),
         ("Detect good (PM)", 18),
         ("Detect supernatural beings (PM)", 18),
         ("Ally (Divine servent, PM, Summonable, 15-)", 29)],
        [("Healing (Faith Healing, PM)", 33)],
        [("Intuition (PM)", 14)],
        [("Oracle (PM)", 14)],
        [("Patron (Deity, PM, Special Abilities, Highly Accessible, 6-)", 36),
         ("Patron (Deity, PM, Special Abilities, Highly Accessible, 9-)", 72)],
        [("Resistant to Evil Supernatural Powers (PM) 3", 5),
         ("Resistant to Evil Supernatural Powers (PM) 8", 7)],
        [("Spirit Empathy (PM)", 9)],
        [("True Faith (PM, Turning)", 24)],
        list_levels("ST +%d", 10, 2),
        [("DX +1", 20)],
        list_levels("HT +%d", 10, 2),
        list_levels("HP +%d", 2, 3),
        list_levels("Will +%d", 5, 5),
        list_levels("Born War Leader %d", 5, 3, min_level=2),
        [("Combat Reflexes", 15)],
        [("Enhanced Block 1", 5)],
        [("Enhanced Parry 1 (One Melee Weapon Skill)", 5)],
        list_levels("Fearlessness %d", 2, 5),
        [("Unfazeable", 15)],
        list_levels("Hard to Kill %d", 2, 5),
        list_levels("Hard to Subdue %d", 2, 5),
        [("High Pain Threshold", 10)],
        [("Higher Purpose (Slay Demons)", 5),
         ("Higher Purpose (Slay Undead)", 5)],
        list_levels("Holiness %d", 5, 2, min_level=3),
        [("Luck", 15)],
        list_levels("Magic Resistance %d", 2, 5),
        [("Rapid Healing", 5)],
        [("Recovery", 10)],
        [("Resistant to Disease 3", 3),
         ("Resistant to Disease 8", 5)],
        [("Resistant to Poison 3", 5)],
        list_levels("Signature Gear %d", 1, 10),
        list_levels("Striking ST %d", 5, 2),
        [("Weapon Bond", 1)],
    ]
    ads2.extend(ads1)
    # Avoid duplicate Higher Purpose
    for trait in traits:
        if trait in ads2:
            ads2.remove(trait)
    traits.extend(pick_from_list(ads2, 50))

    disads1 = [
        [("Honesty (12)", -10)],
        [("Sense of Duty (Good entities)", -10)],
        [("Vow (Own no more than horse can carry)", -10)],
    ]
    traits.extend(pick_from_list(disads1, -10))

    disads2 = [
        list_self_control_levels("Charitable", -15),
        list_self_control_levels("Compulsive Generosity", -5),
        list_self_control_levels("Compulsive Vowing", -5),
        [("Disciplines of Faith (Ritualism)", -5),
         ("Disciplines of Faith (Ritualism)", -10),
         ("Disciplines of Faith (Mysticism)", -5),
         ("Disciplines of Faith (Mysticism)", -10)],
        [("Fanaticism", -15)],
        [("Intolerance (Evil religions)", -5),
         ("Intolerance (All other religions)", -10)],
        list_self_control_levels("Selfless", -5),
        list_self_control_levels("Truthfulness", -5),
        [("Vow (Chastity)", -5)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    disads3 = [
        list_self_control_levels("Bloodlust", -10),
        [("Code of Honor (Chivalry)", -15)],
        [("Easy to Read", -10)],
        [("No Sense of Humor", -10)],
        list_self_control_levels("Overconfidence", -5),
        [("Sense of Duty (Adventuring companions)", -5)],
        [("Stubbornness", -5)],
    ]
    disads3.extend(disads2)
    traits.extend(pick_from_list(disads3, -15))

    skills1 = [
        [("Hidden Lore (Demons)", 2)],
        [("Hidden Lore (Undead)", 2)],
    ]
    traits.extend(pick_from_list(skills1, 2))

    skills2 = [
        [("Crossbow", 4)],
        [("Thrown Weapon (Axe/Mace)", 4)],
        [("Thrown Weapon (Spear)", 4)],
        [("Throwing", 4)],
    ]
    traits.extend(pick_from_list(skills2, 4))

    skills3 = [
        [("Axe/Mace", 12), ("Broadsword", 12), ("Spear", 12), ("Flail", 12)],
        [("Shield", 8)],
        [("Polearm", 20)],
        [("Spear", 20)],
        [("Two-Handed Sword", 20)],
    ]
    traits.extend(pick_from_list(skills3, 20))

    skills4 = [
        [("Fast-Draw (any)", 1)],
        [("Climbing", 1)],
        [("Lance", 1)],
        [("Riding (Horse)", 1)],
        [("Stealth", 1)],
        [("First Aid", 1)],
        [("Gesture", 1)],
        [("Interrogation", 1)],
        [("Physiology (other monster type)", 1)],
        [("Psychology (other monster type)", 1)],
        [("Hiking", 1)],
        [("Observation", 1)],
    ]
    traits.extend(pick_from_list(skills4, 5))
    return traits


def generate_knight():
    traits = [
        ("ST 14", 40),
        ("DX 14", 80),
        ("IQ 10", 0),
        ("HT 13", 30),
        ("HP 14", 0),
        ("Will 10", 0),
        ("Per 10", 0),
        ("FP 13", 0),
        ("Basic Speed 6.0", -15),
        ("Basic Move 6", 0),
        ("Born War Leader 2", 10),
        ("Combat Reflexes", 15),
        ("High Pain Threshold", 10),
        ("Fast-Draw (any)", 1),
        ("Knife", 1),
        ("Shield", 4),
        ("Connoisseur (Weapons)", 4),
        ("Leadership", 1),
        ("Strategy", 2),
        ("Tactics", 2),
    ]

    ads1 = [
        list_levels("ST +%d", 10, 6),
        list_levels("DX +%d", 20, 3),
        list_levels("HT +%d", 10, 6),
        list_levels("HP +%d", 2, 4),
        list_levels("Basic Speed +%d", 20, 2),
        [("Alcohol Tolerance", 1)],
        list_levels("Born War Leader %d", 5, 2, min_level=3),
        [("Enhanced Block 1", 5)],
        [("Enhanced Parry 1 (One Melee Weapon Skill)", 5)],
        list_levels("Fearlessness %d", 2, 5),
        [("Fit", 5), ("Very Fit", 15)],
        list_levels("Hard to Kill %d", 2, 5),
        list_levels("Hard to Subdue %d", 2, 5),
        [("Luck", 15), ("Extraordinary Luck", 30)],
        [("Penetrating Voice", 1)],
        [("Rapid Healing", 5)],
        [("Recovery", 10)],
        list_levels("Signature Gear %d", 1, 10),
        list_levels("Striking ST %d", 5, 2),
        [("Weapon Bond", 1)],
        [("Weapon Master (One weapon)", 20),
         ("Weapon Master (Two weapons normally used together)", 25),
         ("Weapon Master (Small class of weapons)", 30),
         ("Weapon Master (Medium class of weapons)", 35),
         ("Weapon Master (Large class of weapons)", 40),
         ("Weapon Master (All muscle-powered weapons)", 40)],
    ]
    traits.extend(pick_from_list(ads1, 60))

    disads1 = [
        list_self_control_levels("Bad Temper", -10),
        list_self_control_levels("Bloodlust", -10),
        [("Code of Honor (Pirate's)", -5), ("Code of Honor (Soldier's)", -10),
         ("Code of Honor (Chivalry)", -15)],
        list_self_control_levels(
          "Obsession (Slay some specific type of monster)", -5),
        [("One Eye", -15)],
        [("Sense of Duty (Nation)", -10)],
        [("Vow (Never resist a challenge to combat)", -10)],
        [("Wounded", -5)],
    ]
    traits.extend(pick_from_list(disads1, -20))

    disads2 = [
        list_self_control_levels("Bully", -10),
        list_self_control_levels("Compulsive Carousing", -5),
        list_self_control_levels("Greed", -15),
        list_self_control_levels("Honesty", -10),
        list_self_control_levels("Lecherousness", -15),
        list_self_control_levels("Overconfidence", -5),
        [("Sense of Duty (Adventuring companions)", -5)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    skills1 = [
        [("Brawling", 2)],
        [("Boxing", 2)],
    ]
    traits.extend(pick_from_list(skills1, 2))

    skills2 = [
        [("Sumo Wrestling", 2)],
        [("Wrestling", 2)],
    ]
    traits.extend(pick_from_list(skills2, 2))

    skills3 = [
        [("Crossbow", 4)],
        [("Thrown Weapon (Axe/Mace)", 4)],
        [("Thrown Weapon (Spear)", 4)],
        [("Bow", 4)],
        [("Throwing", 4)],
        [("Sling", 4)],
    ]
    traits.extend(pick_from_list(skills3, 4))

    skills4 = [
        [("Axe/Mace", 24)],
        [("Broadsword", 24)],
        [("Polearm", 24)],
        [("Shortsword", 24)],
        [("Spear", 24)],
        [("Two-Handed Sword", 24)],
        [("Flail", 24)],
        [("Axe/Mace", 12)],
        [("Broadsword", 12)],
        [("Polearm", 12)],
        [("Shortsword", 12)],
        [("Spear", 12)],
        [("Two-Handed Sword", 12)],
        [("Flail", 12)],
        [("Axe/Mace", 8)],
        [("Broadsword", 8)],
        [("Lance", 8)],
        [("Polearm", 8)],
        [("Riding (Horse)", 8)],
        [("Shortsword", 8)],
        [("Spear", 8)],
        [("Two-Handed Sword", 8)],
        [("Flail", 8)],
    ]
    traits.extend(pick_from_list(skills4, 24))

    skills5 = [
        [("Armoury (Body Armor)", 4)],
        [("Armoury (Melee Weapons)", 4)],
    ]
    traits.extend(pick_from_list(skills5, 4))

    skills6 = [
        [("Forced Entry", 1)],
        [("Climbing", 1)],
        [("Stealth", 1)],
        [("First Aid", 1)],
        [("Gesture", 1)],
        [("Savoir-Faire (High Society)", 1)],
        [("Gambling", 1)],
        [("Heraldry", 1)],
        [("Streetwise", 1)],
        [("Carousing", 1)],
        [("Hiking", 1)],
        [("Intimidation", 1)],
        [("Scrounging", 1)],
        [("Observation", 1)],
    ]
    traits.extend(pick_from_list(skills6, 4))
    return traits


def generate_martial_artist():
    traits = [
        ("ST 11", 10),
        ("DX 16", 120),
        ("IQ 10", 0),
        ("HT 12", 20),
        ("HP 11", 0),
        ("Will 11", 5),
        ("Per 10", 0),
        ("FP 12", 0),
        ("Basic Speed 7.0", 0),
        ("Basic Move 8", 5),
        ("Chi Talent 2", 30),
        ("Trained by a Master", 30),
        ("Disciples of Faith (Chi Rituals)", -10),
        ("Jumping", 1),
        ("Acrobatics", 2),
        ("Judo", 2),
        ("Karate", 2),
        ("Stealth", 1),
        ("Meditation", 2),
        ("Tactics", 4),
    ]

    special_skills = [
        [("Immovable Stance", 2)],
        [("Light Walk", 2)],
        [("Parry Missile Weapons", 2)],
        [("Push", 2)],
        [("Breaking Blow", 2)],
        [("Flying Leap", 2)],
        [("Pressure Points", 2)],
        [("Breath Control", 2)],
        [("Kiai", 2)],
        [("Body Control", 2)],
        [("Mental Strength", 2)],
        [("Mind Block", 2)],
        [("Autohypnosis", 2)],
        [("Power Blow", 2)],
        [("Esoteric Medicine", 2)],
        [("Blind Fighting", 2)],
    ]

    ads1 = [
        [("Catfall (PM)", 9)],
        [("DR 1 (Tough Skin, PM)", 3), ("DR 2 (Touch Skin, PM)", 5)],
        [("Danger Sense (PM)", 14)],
        [("Enhanced Move 0.5 (Ground, PM)", 9),
         ("Enhanced Move 1 (Ground, PM)", 18)],
        [("Extra Attack 1 (PM)", 23), ("Extra Attack 2 (PM)", 45)],
        [("Metabolism Control 1 (PM)", 5), ("Metabolism Control 2 (PM)", 9),
         ("Metabolism Control 3 (PM)", 14), ("Metabolism Control 4 (PM)", 18),
         ("Metabolism Control 5 (PM)", 23)],
        [("Perfect Balance (PM)", 14)],
        [("Regeneration (Slow, PM)", 9),
         ("Regeneration (Regular, PM)", 23),
         ("Regeneration (Fast, PM)", 45)],
        [("Resistant to Metabolic Hazards +3 (PM)", 9),
         ("Resistant to Metabolic Hazards +8 (PM)", 14)],
        [("Striking ST 1 (PM)", 5), ("Striking ST 2 (PM)", 9)],
        list_levels("Super Jump %d (PM)", 9, 2),
    ]
    ads1.extend(special_skills[:])
    traits.extend(pick_from_list(ads1, 20))

    ads2 = [
        list_levels("ST +%d", 10, 2),
        [("DX +1", 20)],
        [("IQ +1", 20)],
        list_levels("HT +%d", 10, 2),
        list_levels("Will +%d", 5, 4),
        list_levels("Per +%d", 5, 4),
        list_levels("FP +%d", 3, 6),
        [("Basic Speed +1", 20)],
        list_levels("Basic Move +%d", 5, 2),
        [("Ambidexterity", 5)],
        [("Chi Talent 3", 15)],
        [("Combat Reflexes", 15)],
        [("Enhanced Dodge 1", 15)],
        list_levels("Enhanced Parry %d (Unarmed)", 5, 2),
        [("Fit", 5), ("Very Fit", 15)],
        [("Flexibility", 5), ("Double-Jointed", 15)],
        [("High Pain Threshold", 10)],
        [("Luck", 15)],
        list_levels("Magic Resistance %d", 2, 5),
        list_levels("Mind Shield %d", 4, 5),
        list_levels("Signature Gear %d", 1, 10),
        [("Unfazeable", 15)],
        [("Weapon Bond", 1)],
        [("Weapon Master (One exotic weapon)", 20)],
        [("Wild Talent 1", 20)],
    ]
    ads2.extend(ads1)
    traits.extend(pick_from_list(ads2, 20))

    disads1 = [
        [("Code of Honor (Bushido)", -15)],
        list_self_control_levels("Compulsive Vowing", -5),
        list_self_control_levels("Honesty", -10),
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels(
          "Obsession (Perfect my art at any cost!)", -10),
        [("Social Stigma (Minority Group)", -10)],
        [("Vow (Vegetarianism)", -5)],
        [("Vow (Silence)", -10)],
        [("Vow (Always Fight Unarmed)", -15)],
        [("Wealth (Struggling)", -10), ("Wealth (Poor)", -15),
         ("Wealth (Dead Broke)", -25)],
    ]
    traits.extend(pick_from_list(disads1, -25))

    disads2 = [
        [("Callous (12)", -5)],
        list_self_control_levels("Loner", -5),
        [("No Sense of Humor", -10)],
        list_self_control_levels("Overconfidence", -5),
        [("Sense of Duty (Adventuring companions)", -5)],
        [("Stubbornness", -5)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    skills1 = [
        [("Thrown Weapon (Dart)", 1)],
        [("Thrown Weapon (Knife)", 1)],
        [("Thrown Weapon (Shuriken)", 1)],
        [("Throwing", 1)],
        [("Blowpipe", 1)],
        [("Sling", 1)],
    ]
    traits.extend(pick_from_list(skills1, 1))

    melee_option = random.randrange(3)
    if melee_option == 0:
        skills2 = [
            [("Knife", 4)],
            [("Axe/Mace", 4)],
            [("Jitte/Sai", 4)],
            [("Shortsword", 4)],
            [("Smallsword", 4)],
            [("Staff", 4)],
            [("Tonfa", 4)],
            [("Flail", 4)],
            [("Kusari", 4)],
        ]
        traits.extend(pick_from_list(skills2, 8))
    elif melee_option == 1:
        skills3 = [
            [("Knife", 4)],
            [("Axe/Mace", 4)],
            [("Jitte/Sai", 4)],
            [("Shortsword", 4)],
            [("Smallsword", 4)],
            [("Staff", 4)],
            [("Tonfa", 4)],
            [("Flail", 4)],
            [("Kusari", 4)],
        ]
        traits.extend(pick_from_list(skills3, 4))
        traits = [(name, cost) for (name, cost) in traits
                  if name != "Judo" and name != "Karate"]
        traits.append(("Judo", 4))
        traits.append(("Karate", 4))
    else:
        traits = [(name, cost) for (name, cost) in traits
                  if name != "Judo" and name != "Karate"]
        if random.randrange(2) == 0:
            traits.append(("Judo", 8))
            traits.append(("Karate", 4))
        else:
            traits.append(("Judo", 4))
            traits.append(("Karate", 8))

    skills4 = [
        [("Fast-Draw (any)", 1)],
        [("Climbing", 1)],
        [("First Aid", 1)],
        [("Gesture", 1)],
        [("Teaching", 1)],
        [("Hiking", 1)],
        [("Running", 1)],
        [("Intimidation", 1)],
        [("Observation", 1)],
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
        for (name, cost) in traits:
            if name == "Flying Leap":
                traits.remove((name, cost))
                break
        remaining_special_skill_names = list(special_skill_names - trait_names -
                                             {"Flying Leap"})
        name2 = random.choice(remaining_special_skill_names)
        traits.append((name2, cost))
    return traits


def generate_scout():
    traits = [
        ("ST 13", 30),
        ("DX 14", 80),
        ("IQ 11", 20),
        ("HT 12", 20),
        ("HP 13", 0),
        ("Will 11", 0),
        ("Per 14", 15),
        ("FP 12", 0),
        ("Basic Speed 7.0", 10),
        ("Basic Move 7", 0),
        ("Heroic Archer", 20),
        ("Outdoorsman 2", 20),
    ]

    ads1 = [
        list_levels("ST +%d", 10, 2),
        [("DX +1", 20)],
        list_levels("HT +%d", 10, 2),
        list_levels("Per +%d", 5, 4),
        [("Basic Speed +1", 20)],
        list_levels("Basic Move +%d", 5, 3),
        [("Absolute Direction", 5)],
        list_levels("Acute Vision %d", 2, 5),
        [("Combat Reflexes", 15)],
        [("Danger Sense", 15)],
        [("Fit", 5), ("Very Fit", 15)],
        [("High Pain Threshold", 10)],
        [("Luck", 15)],
        list_levels("Night Vision %d", 1, 9),
        list_levels("Outdoorsman %d", 10, 2, min_level=3),
        [("Peripheral Vision", 15)],
        [("Rapid Healing", 5)],
        list_levels("Signature Gear %d", 1, 10),
        [("Weapon Bond", 1)],
        [("Weapon Master (Bow)", 20)],
    ]
    traits.extend(pick_from_list(ads1, 20))

    disads1 = [
        list_self_control_levels("Bloodlust", -10),
        [("Callous (12)", -5)],
        list_self_control_levels("Greed", -15),
        list_self_control_levels("Honesty", -10),
        list_self_control_levels("Overconfidence", -5),
        [("Sense of Duty (Adventuring companions)", -5)],
        [("Stubbornness", -5)],
    ]
    traits.extend(pick_from_list(disads1, -15))

    disads2 = [
        [("Code of Honor (Pirate's)", -5), ("Code of Honor (Soldier's)", -10)],
        [("Intolerance (Urbanites)", -5)],
        list_self_control_levels("Loner", -5),
        [("No Sense of Humor", -10)],
        [("Odious Personal Habit (Unwashed bushwhacker)", -5)],
        [("Paranoia", -10)],
        list_self_control_levels("Phobia (Crowds)", -15),
        [("Social Stigma (Disowned)", -5)],
        [("Vow (Never Sleep Indoors)", -10)],
        [("Vow (Own no more than what can be carried)", -10)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -35))

    fixed_skills = [
        [("Bow", 16)],
        [("Camouflage", 2)],
        [("Fast-Draw (Arrow)", 1)],
        [("Observation", 2)],
        [("Tracking", 2)],
        [("Climbing", 1)],
        [("Stealth", 1)],
        [("Gesture", 2)],
        [("Cartography", 4)],
        [("Shadowing", 4)],
        [("Traps", 4)],
        [("Mimicry (Bird Calls)", 2)],
        [("Hiking", 2)],
    ]
    for fixed_skill in fixed_skills:
        traits.append(fixed_skill[0])

    skills1 = [
        [("Broadsword", 12), ("Shortsword", 12), ("Spear", 12), ("Staff", 12)],
        [("Broadsword", 8), ("Shortsword", 8), ("Spear", 8)],
        [("Shield", 4)],
    ]

    skills2 = [
        [("Navigation (Land)", 1)],
        [("Navigation (Sea)", 1)],
    ]

    skills3 = [
        [("Survival (Arctic)", 1)],
        [("Survival (Desert)", 1)],
        [("Survival (Island/Beach)", 1)],
        [("Survival (Jungle)", 1)],
        [("Survival (Mountain)", 1)],
        [("Survival (Plains)", 1)],
        [("Survival (Swampland)", 1)],
        [("Survival (Woodlands)", 1)],
    ]

    skills4 = [
        [("Brawling", 1)],
        [("Fast-Draw (any other)", 1)],
        [("Garrote", 1)],
        [("Jumping", 1)],
        [("Knife", 1)],
        [("Knot-Tying", 1)],
        [("Boating (Unpowered)", 1)],
        [("Riding (Horse)", 1)],
        [("Throwing", 1)],
        [("Wrestling", 1)],
        [("First Aid", 1)],
        [("Seamanship", 1)],
        [("Armoury (Missile Weapons)", 1)],
        [("Prospecting", 1)],
        [("Weather Sense", 1)],
        [("Swimming", 1)],
        [("Running", 1)],
        [("Skiing", 1)],
        [("Search", 1)],
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
        ("ST 11", 10),
        ("DX 15", 100),
        ("IQ 10", 0),
        ("HT 13", 30),
        ("HP 11", 0),
        ("Will 10", 0),
        ("Per 10", 0),
        ("FP 13", 0),
        ("Basic Speed 7.0", 0),
        ("Basic Move 7", 0),
        ("Combat Reflexes", 15),
        ("Enhanced Parry (Weapon of choice) 1", 5),
        ("Luck", 15),
        ("Weapon Bond (Any starting weapon)", 1),
        ("Weapon Master (Weapon of choice) 1", 20),
        ("Jumping", 1),
        ("Fast-Draw (Knife)", 1),
        ("Fast-Draw (Sword)", 1),
        ("Acrobatics", 4),
        ("Wrestling", 2),
        ("Stealth", 1),
        ("Carousing", 1),
    ]

    ads1 = [
        list_levels("ST +%d", 10, 6),
        list_levels("DX +%d", 20, 3),
        list_levels("Basic Speed +%d", 20, 2),
        list_levels("Basic Move +%d", 5, 3),
        [("Alcohol Tolerance", 1)],
        [("Ambidexterity", 5)],
        [("Appearance: Attractive", 4), ("Appearance: Handsome", 12),
         ("Appearance: Very Handsome", 16)],
        list_levels("Charisma %d", 5, 5),
        [("Daredevil", 15)],
        [("Enhanced Dodge", 15)],
        list_levels("Enhanced Parry %d (Weapon of Choice)", 5, 2, min_level=2),
        [("Extra Attack 1", 25)],
        [("No Hangover", 1)],
        [("Perfect Balance", 15)],
        [("Rapier Wit", 5)],
        list_levels("Serendipity %d", 15, 4),
        list_levels("Signature Gear %d", 1, 10),
        list_levels("Striking ST %d", 5, 2),
        [("Extraordinary Luck", 15), ("Ridiculous Luck", 45)],
    ]
    traits.extend(pick_from_list(ads1, 60))

    disads1 = [
        [("Code of Honor (Pirate's)", -5),
         ("Code of Honor (Gentleman's)", -10)],
        list_self_control_levels(
          "Obsession (Become the best swordsman in the world)", -10),
        [("Vow (Use only weapon of choice)", -5)],
        [("Vow (Never resist a challenge to combat)", -10)],
        [("Vow (Challenge every swordsman to combat)", -15)],
        [("Vow (Never wear armor)", -15)],
        [("Wounded", -5)],
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
        [("One Eye", -15)],
        [("Sense of Duty (Adventuring companions)", -5)],
        [("Wounded", -5)],
    ]
    disads3.extend(disads2)
    traits.extend(pick_from_list(disads3, -20))

    skills1 = [
        [("Thrown Weapon (Knife)", 2)],
        [("Throwing", 2)],
    ]
    traits.extend(pick_from_list(skills1, 2))

    skills2 = [
        [("Broadsword", 20), ("Rapier", 20), ("Saber", 20),
         ("Shortsword", 20), ("Smallsword", 20)],
        [("Broadsword", 16), ("Rapier", 16), ("Saber", 16),
         ("Shortsword", 16), ("Smallsword", 16)],
        [("Broadsword", 12), ("Rapier", 12), ("Saber", 12),
         ("Shortsword", 12), ("Smallsword", 12)],
        [("Shield (Buckler)", 8), ("Cloak", 8), ("Main-Gauche", 8)],
        [("Shield (Buckler)", 4), ("Cloak", 4), ("Main-Gauche", 4)],
    ]
    traits.extend(pick_from_list(skills2, 20))

    skills3 = [
        [("Brawling", 2)],
        [("Boxing", 2)],
    ]
    traits.extend(pick_from_list(skills3, 2))

    skills4 = [
        [("Savoir-Faire (High Society)", 2)],
        [("Streetwise", 2)],
    ]
    traits.extend(pick_from_list(skills4, 2))

    skills5 = [
        [("Fast-Draw (any other)", 1)],
        [("Climbing", 1)],
        [("First Aid", 1)],
        [("Gesture", 1)],
        [("Seamanship", 1)],
        [("Connoisseur (any)", 1)],
        [("Fast-Talk", 1)],
        [("Gambling", 1)],
        [("Hiking", 1)],
        [("Sex Appeal", 1)],
        [("Intimidation", 1)],
        [("Scrounging", 1)],
        [("Search", 1)],
    ]
    traits.extend(pick_from_list(skills5, 7))
    return traits


def generate_thief():
    traits = [
        ("ST 11", 10),
        ("DX 15", 100),
        ("IQ 13", 60),
        ("HT 11", 10),
        ("HP 11", 0),
        ("Will 13", 0),
        ("Per 14", 5),
        ("FP 11", 0),
        ("Basic Speed 6.0", -10),
        ("Basic Move 7", 5),
        ("Flexibility", 5),
        ("High Manual Dexterity 1", 5),
        ("Perfect Balance", 15),
    ]

    ads1 = [
        [("DX +1", 20)],
        [("IQ +1", 20)],
        list_levels("Per +%d", 5, 6),
        [("Basic Speed +1", 20)],
        list_levels("Basic Move +%d", 5, 2),
        [("Ambidexterity", 5)],
        [("Catfall", 10)],
        [("Combat Reflexes", 15)],
        [("Danger Sense", 15)],
        list_levels("Enhanced Dodge %d", 15, 2),
        list_levels("Gizmos %d", 5, 3),
        list_levels("High Manual Dexterity %d", 5, 3, min_level=2),
        [("Honest Face", 1)],
        [("Luck", 15), ("Extraordinary Luck", 30)],
        list_levels("Night Vision %d", 1, 9),
        [("Peripheral Vision", 15)],
        list_levels("Serendipity %d", 15, 2),
        list_levels("Signature Gear %d", 1, 10),
        list_levels("Striking ST %d (Only on surprise attack)", 2, 2),
        [("Wealth (Comfortable)", 10), ("Wealth (Wealthy)", 20)],
        [("Double-Jointed", 10)],
    ]
    traits.extend(pick_from_list(ads1, 30))

    disads1 = [
        [("Greed (12)", -15)],
        [("Kleptomania (12)", -15)],
        [("Trickster (12)", -15)],
    ]
    traits.extend(pick_from_list(disads1, -15))

    disads2 = [
        [("Callous (12)", -5)],
        [("Code of Honor (Pirate's)", -5)],
        [("Curious", -5)],
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
        [("Laziness", -10)],
        list_self_control_levels("Lecherousness", -15),
        list_self_control_levels("Loner", -5),
        [("One Eye", -15)],
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels("Post-Combat Shakes", -5),
        [("Sense of Duty (Adventuring companions)", -5)],
        [("Skinny", -5)],
        [("Social Stigma (Criminal Record)", -5)],
    ]
    disads3.extend(disads1)
    disads3.extend(disads2)
    traits.extend(pick_from_list(disads3, -20))

    fixed_skills = [
        [("Forced Entry", 1)],
        [("Climbing", 1)],
        [("Filch", 2)],
        [("Stealth", 12)],
        [("Escape", 1)],
        [("Pickpocket", 2)],
        [("Lockpicking", 4)],
        [("Traps", 4)],
        [("Acrobatics", 1)],
        [("Sleight of Hand", 1)],
        [("Gesture", 1)],
        [("Holdout", 2)],
        [("Shadowing", 2)],
        [("Smuggling", 2)],
        [("Streetwise", 2)],
        [("Search", 2)],
        [("Urban Survival", 2)],
        [("Brawling", 1)],
        [("Gambling", 1)],
        [("Carousing", 1)],
    ]
    for fixed_skill in fixed_skills:
        traits.append(fixed_skill[0])

    skills1 = [
        [("Rapier", 2), ("Saber", 2), ("Shortsword", 2), ("Smallsword", 2)],
        [("Rapier", 1), ("Saber", 1), ("Shortsword", 1), ("Smallsword", 1)],
        [("Shield (Buckler)", 1), ("Cloak", 1), ("Main-Gauche", 1)],
    ]

    skills2 = [
        [("Crossbow", 1)],
        [("Thrown Weapon (Knife)", 1)],
        [("Bow", 1)],
        [("Throwing", 1)],
        [("Sling", 1)],
    ]

    skills3 = [
        [("Fast-Draw (any)", 1)],
        [("Garrote", 1)],
        [("First Aid", 1)],
        [("Panhandling", 1)],
        [("Seamanship", 1)],
        [("Cartography", 1)],
        [("Connoisseur (any)", 1)],
        [("Disguise", 1)],
        [("Fast-Talk", 1)],
        [("Merchant", 1)],
        [("Counterfeiting", 1)],
        [("Forgery", 1)],
        [("Poisons", 1)],
        [("Hiking", 1)],
        [("Scrounging", 1)],
        [("Lip Reading", 1)],
        [("Observation", 1)],
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
            traits.append((spell, 1))
            trait_names.add(spell)
            return


# TODO support multiple languages
# Maybe language as leveled 1-30 or 2-30, then split it up
# TODO effect of Language Talent
def generate_wizard():
    traits = [
        ("ST 10", 0),
        ("DX 12", 40),
        ("IQ 15", 100),
        ("HT 11", 10),
        ("HP 10", 0),
        ("Will 15", 0),
        ("Per 12", -15),
        ("FP 14", 9),
        ("Basic Speed 6.0", 5),
        ("Basic Move 6", 0),
        ("Magery 3", 35),
        ("Occultism", 2),
        ("Alchemy", 8),
        ("Thaumatology", 1),
        ("Hazardous Materials (Magical)", 1),
        ("Research", 1),
        ("Speed-Reading", 1),
        ("Teaching", 1),
        ("Writing", 1),
        ("Meditation", 2),
    ]

    build_spell_prereqs()

    ads1 = [
        [("DX +1", 20)],
        [("IQ +1", 20)],
        list_levels("Will +%d", 5, 5),
        list_levels("FP +%d", 3, 10),
        [("Eidetic Memory", 5), ("Photographic Memory", 10)],
        list_levels("Gizmos %d", 5, 3),
        [("Intuition", 15)],
        [("Language Talent", 10)],
        [("Language (Spoken: Broken / Written: None)", 1)],
        [("Language (Spoken: None / Written: Broken)", 1)],
        [("Language (Spoken: Accented / Written: None)", 2)],
        [("Language (Spoken: Broken / Written: Broken)", 2)],
        [("Language (Spoken: None / Written: Accented)", 2)],
        [("Language (Spoken: Native / Written: None)", 3)],
        [("Language (Spoken: Accented / Written: Broken)", 3)],
        [("Language (Spoken: Broken / Written: Accented)", 3)],
        [("Language (Spoken: None / Written: Native)", 3)],
        [("Language (Spoken: Native / Written: Broken)", 4)],
        [("Language (Spoken: Accented / Written: Accented)", 4)],
        [("Language (Spoken: Broken / Written: Native)", 4)],
        [("Language (Spoken: Native / Written: Accented)", 5)],
        [("Language (Spoken: Accented / Written: Native)", 5)],
        [("Language (Spoken: Native / Written: Native)", 6)],
        [("Luck", 15), ("Extraordinary Luck", 30)],
        list_levels("Magery %d", 10, 3, min_level=4),
        list_levels("Mind Shield %d", 4, 5),
        list_levels("Signature Gear %d", 1, 10),
        [("Spirit Empathy", 10)],
        [("Wild Talent 1 (Retention, Focused, Magical)", 21)],
    ]
    traits.extend(pick_from_list(ads1, 30))

    disads1 = [
        list_self_control_levels("Curious", -5),
        [("Frightens Animals", -10)],
        list_self_control_levels(
          "Obsession (Become the world's most powerful wizard, a lich, etc.)",
           -10),
        list_self_control_levels("Pyromania", -5),
        [("Skinny", -5)],
        [("Social Stigma (Excommunicated)", -10)],
        [("Unfit", -5), ("Very Unfit", -15)],
        list_levels("Unnatural Features %d", -1, 5),
        [("Weirdness Magnet", -15)],
    ]
    traits.extend(pick_from_list(disads1, -15))

    disads2 = [
        [("Absent-Mindedness", -15)],
        list_self_control_levels("Bad Temper", -10),
        [("Clueless", -10)],
        [("Combat Paralysis", -15)],
        list_self_control_levels("Cowardice", -10),
        [("Hard of Hearing", -15)],
        [("Klutz", -5), ("Total Klutz", -15)],
        list_self_control_levels("Loner", -5),
        [("Low Pain Threshold", -10)],
        [("Nervous Stomach", -1)],
        [("Oblivious", -5)],
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels("Post-Combat Shakes", -5),
        [("Sense of Duty (Adventuring companions)", -5)],
        [("Stubbornness", -5)],
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -20))

    skills1 = [
        [("Hidden Lore (Demons)", 2), ("Hidden Lore (Magic Items)", 2),
         ("Hidden Lore (Magical Writings)", 2), ("Hidden Lore (Spirits)", 2)],
    ]
    traits.extend(pick_from_list(skills1, 2))

    skills2 = [
        [("Smallsword", 4)],
        [("Shield (Buckler)", 4)],
        [("Staff", 8)],
    ]
    traits.extend(pick_from_list(skills2, 8))

    skills3 = [
        [("Innate Attack (any)", 4)],
        [("Thrown Weapon (Dart)", 4)],
        [("Throwing", 4)],
        [("Sling", 4)],
    ]
    traits.extend(pick_from_list(skills3, 4))

    skills4 = [
        [("Fast-Draw (Potion)", 1)],
        [("Climbing", 1)],
        [("Stealth", 1)],
        [("Body Sense", 1)],
        [("First Aid", 1)],
        [("Gesture", 1)],
        [("Savoir-Faire (High Society)", 1)],
        [("Cartography", 1)],
        [("Hidden Lore (Demons)", 1)],
        [("Hidden Lore (Magic Items)", 1)],
        [("Hidden Lore (Magical Writings)", 1)],
        [("Hidden Lore (Spirits)", 1)],
        [("Diplomacy", 1)],
        [("Physiology (monster type)", 1)],
        [("Strategy", 1)],
        [("Hiking", 1)],
        [("Scrounging", 1)],
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
