#!/usr/bin/env python

"""Generate a random GURPS Dungeon Fantasy character."""

import argparse
import copy
import random


def list_levels(name, cost, num_levels, min_level=1):
    """Return a list of num_levels tuples, each with the name and
    cost of that level.

    name should have a %d in it for the level number.
    cost is per level
    """
    lst = []
    for level in xrange(min_level, min_level + num_levels):
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


def print_traits(traits):
    for name, cost in traits:
        print "%s [%d]" % (name, cost)


def generate_barbarian():
    traits = []
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
        list_levels("Lifting ST +%d", 3, 3),
        [("Luck", 15), ("Extraordinary Luck", 30)],
        list_levels("Magic Resistance %d", 2, 5),
        [("Rapid Healing", 5), ("Very Rapid Healing", 15)],
        [("Recovery", 10)],
        [("Resistant to Disease +3", 3),
         ("Resistant to Disease +8", 5)],
        [("Resistant to Poison +3", 5)],
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
    # TODO Needs wizard spell prerequisite data
    pass


def generate_cleric():
    traits = []
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
        [("Resistant to Evil Supernatural Powers (PM) +3", 5),
         ("Resistant to Evil Supernatural Powers (PM) +8", 7)],
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
        list_levels("Fearlessness +%d", 2, 5),
        [("Unfazeable", 15)],
        list_levels("Healer %d", 10, 2),
        [("Language (Spoken: Accented / Written: None)", 2)],
        [("Language (Spoken: Broken / Written: Broken)", 2)],
        [("Language (Spoken: None / Written: Accented)", 2)],
        [("Language: Spoken (Native) / Written (None)", 3)],
        [("Language: Spoken (Accented) / Written (Broken)", 3)],
        [("Language: Spoken (Broken) / Written (Accented)", 3)],
        [("Language: Spoken (None) / Written (Native)", 3)],
        [("Language (Spoken: Native / Written: Broken)", 4)],
        [("Language (Spoken: Accented / Written: Accented)", 4)],
        [("Language (Spoken: Broken / Written: Native)", 4)],
        [("Language (Spoken: Native / Written: Accented)", 5)],
        [("Language (Spoken: Accented / Written: Native)", 5)],
        [("Language (Spoken: Native / Written: Native)", 6)],
        [("Luck", 15)],
        list_levels("Mind Shield %d", 4, 5),
        list_levels("Power Investiture %d", 10, 2, min_level=4),
        [("Resistant to Disease (PM) +3", 3),
         ("Resistant to Disease (PM) +8", 5)],
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
    traits = []
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
        [("Resistant to Disease (PM) +3", 3),
         ("Resistant to Disease (PM) +8", 5)],
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
    traits.extend(pick_from_list(skills5, 5))

    trait_names = set((trait[0] for trait in traits))
    if ("Power Investiture 4" in trait_names or
        "Power Investiture 5" in trait_names):
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
        if "Power Investiture 5" in trait_names:
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
    traits = []
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
        [("Resistant to Evil Supernatural Powers (PM) +3", 5),
         ("Resistant to Evil Supernatural Powers (PM) +8", 7)],
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
        list_levels("Fearlessness +%d", 2, 5),
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
        [("Resistant to Disease +3", 3),
         ("Resistant to Disease +8", 5)],
        [("Resistant to Poison +3", 5)],
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
        [("Crossbow", 4)],
        [("Thrown Weapon (Axe/Mace)", 4)],
        [("Thrown Weapon (Spear)", 4)],
        [("Throwing", 4)],
    ]
    traits.extend(pick_from_list(skills1, 4))

    skills2 = [
        [("Axe/Mace", 12), ("Broadsword", 12), ("Spear", 12), ("Flail", 12)],
        [("Shield", 8)],
        [("Polearm", 20)],
        [("Spear", 20)],
        [("Two-Handed Sword", 20)],
    ]
    traits.extend(pick_from_list(skills2, 20))

    skills3 = [
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
    traits.extend(pick_from_list(skills3, 1))
    return traits


def generate_knight():
    traits = []
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
        list_levels("Fearlessness +%d", 2, 5),
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
        [("Armoury (Body Armor)", 1)],
        [("Armoury (Melee Weapons)", 1)],
    ]
    traits.extend(pick_from_list(skills5, 1))

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


# TODO Flying Leap requires Power Blow as a prereq
def generate_martial_artist():
    traits = []

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

    fixed_skills = [
        [("Jumping", 1)],
        [("Acrobatics", 2)],
        [("Judo", 2)],
        [("Karate", 2)],
        [("Stealth", 1)],
        [("Meditation", 2)],
        [("Tactics", 4)],
    ]
    for fixed_skill in fixed_skills:
        traits.append(fixed_skill[0])

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
                                             set(["Flying Leap"]))
        name2 = random.choice(remaining_special_skill_names)
        traits.append((name2, cost))
    return traits


def generate_scout():
    traits = []
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
    traits = []
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
        list_self_control_levels("Trickster", -10),
    ]
    disads2.extend(disads1)
    traits.extend(pick_from_list(disads2, -15))

    disads3 = [
        list_self_control_levels2("Chummy", -5, "Gregarious)", -10),
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
    traits = []
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

    print_traits(traits)


def generate_wizard():
    pass


template_to_fn = {
    "barbarian": generate_barbarian,
    "bard": generate_bard,
    "cleric": generate_cleric,
    "druid": generate_druid,
    "holy warrior": generate_holy_warrior,
    "knight": generate_knight,
    "martial artist": generate_martial_artist,
    "scout": generate_scout,
    "swashbuckler": generate_swashbuckler,
    "thief": generate_thief,
    "wizard": generate_wizard,
}

templates = sorted(template_to_fn.iterkeys())


def main():
    parser = argparse.ArgumentParser(description=
      "Generate a random GURPS Dungeon Fantasy character")
    parser.add_argument("--template", "-t", help="Character template to use",
                        default="random")
    args = parser.parse_args()
    template = args.template.lower()
    if template == "random":
        template = random.choice(templates)
    if template not in templates:
        raise argparse.ArgumentTypeError("Invalid template; must be one of %s"
          % ", ".join(templates + ["random"]))
    print template.title()
    fn = template_to_fn[template]
    traits = fn()
    print_traits(traits)


if __name__ == "__main__":
    main()
