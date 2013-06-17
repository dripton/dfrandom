#!/usr/bin/env python

"""Generate a random GURPS Dungeon Fantasy character."""

import argparse
import copy
import random


def list_levels(name, cost, num_levels):
    """Return a list of num_levels tuples, each with the name and
    cost of that level.

    name should have a %d in it for the level number.
    cost is per level
    """
    lst = []
    for level in xrange(1, num_levels + 1):
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
        [("Power Investiture 4", 10), ("Power Investiture 5", 20)],
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
    traits.extend(pick_from_list(disads2, -25))

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
    pass

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
