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
    pass

def generate_cleric():
    pass

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
