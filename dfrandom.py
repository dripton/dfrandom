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
        list_self_control_levels("Overconfidence", -10),
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

    print_traits(traits)


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
        [("Honesty", -10)],
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

    if "Power Investiture 4" in traits or "Power Investiture 5" in traits:
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
        if "Power Investiture 5" in traits:
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

    print_traits(traits)


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
        [("Vow (Never Sleep Indoors)", -5)],
        [("Wealth (Struggling)", -10), ("Wealth (Poor)", -15)],
    ]
    traits.extend(pick_from_list(disads1, -20))

    disads2 = [
        [("Intolerance (Urbanites)", -5)],
        list_self_control_levels("Loner", -5),
        [("No Sense of Humor", -10)],
        [("Odious Personal Habit (Dirty Hippy)", -5)],
        list_self_control_levels("Overconfidence", -5),
        list_self_control_levels("Phobia (Crowds)", -5),
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

    # TODO Avoid duplicate Hidden Lore
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
    traits.extend(pick_from_list(skills5, 5))

    if "Power Investiture 4" in traits or "Power Investiture 5" in traits:
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
        if "Power Investiture 5" in traits:
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

    print_traits(traits)

def generate_holy_warrior():
    pass

def generate_knight():
    pass

def generate_martial_artist():
    pass

def generate_scout():
    pass

def generate_swashbuckler():
    pass

def generate_thief():
    pass

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
    fn = template_to_fn[template]
    fn()


if __name__ == "__main__":
    main()
