# py.test

import xml.etree.ElementTree as et

import dfrandom


def test_parse_spell_prereq_name_is():
    xml = """
<spell_prereq has="yes">
    <name compare="is">light</name>
</spell_prereq>"""
    el = et.fromstring(xml)
    assert dfrandom._parse_spell_prereq(el, "f1") == \
"""
def f1(traits, trait_names):
    return '''Light''' in trait_names
"""


def test_parse_spell_prereq_name_college_count():
    xml = """<spell_prereq has="yes">
    <college_count compare="at_least">10</college_count>
</spell_prereq>
"""
    el = et.fromstring(xml)
    assert dfrandom._parse_spell_prereq(el, "f1") == \
"""
def f1(traits, trait_names):
    count = count_spell_colleges(traits)
    return count >= 10
"""

def test_parse_advantage_prereq():
    xml = """<advantage_prereq has="yes">
    <name compare="is">Magery</name>
    <notes compare="is anything"></notes>
    <level compare="at_least">3</level>
</advantage_prereq>
"""
    el = et.fromstring(xml)
    print dfrandom._parse_advantage_prereq(el, "f1")
    assert dfrandom._parse_advantage_prereq(el, "f1") == \
"""
def f1(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''Magery'''):
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= int('''3''')
    return False
"""


def test_parse_attribute_prereq():
    xml = '<attribute_prereq has="yes" which="iq" compare="at_least">13</attribute_prereq>'
    el = et.fromstring(xml)
    assert dfrandom._parse_attribute_prereq(el, "f1") == \
"""
def f1(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''IQ '''):
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= 13
    return False
"""


def test_parse_prereq_list():
    xml ="""
<prereq_list all="no">
    <advantage_prereq has="yes">
        <name compare="is">Magery</name>
        <notes compare="contains">one college (gate)</notes>
        <level compare="at_least">2</level>
    </advantage_prereq>
    <advantage_prereq has="yes">
        <name compare="is">Magery</name>
        <notes compare="does not contain">one college</notes>
        <level compare="at_least">2</level>
    </advantage_prereq>
</prereq_list>"""
    el = et.fromstring(xml)
    top_name = "top_0"
    dfrandom.function_name_incrementor = 1
    assert dfrandom._parse_prereq_list(el, top_name) == """
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


def ppl_1(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''Magery''') and '''one college (gate)''' in trait:
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= int('''2''')
    return False


def ppl_2(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''Magery''') and '''one college''' not in trait:
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= int('''2''')
    return False

top_0 = or_(ppl_1(traits, trait_names), ppl_2(traits, trait_names))
"""


def test_parse_prereq_list2():
    xml = """
<prereq_list all="yes">
    <spell_prereq has="yes">
        <college_count compare="at_least">10</college_count>
    </spell_prereq>
    <spell_prereq has="yes">
        <college_count compare="at_least">10</college_count>
    </spell_prereq>
    <attribute_prereq has="yes" which="iq" compare="at_least">13</attribute_prereq>
    <prereq_list all="no">
        <advantage_prereq has="yes">
            <name compare="is">Magery</name>
            <notes compare="contains">one college (gate)</notes>
            <level compare="at_least">2</level>
        </advantage_prereq>
        <advantage_prereq has="yes">
            <name compare="is">Magery</name>
            <notes compare="does not contain">one college</notes>
            <level compare="at_least">2</level>
        </advantage_prereq>
    </prereq_list>
</prereq_list>
"""
    el = et.fromstring(xml)
    top_name = "top_0"
    dfrandom.function_name_incrementor = 1
    assert dfrandom._parse_prereq_list(el, top_name) == """
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


def ppl_1(traits, trait_names):
    count = count_spell_colleges(traits)
    return count >= 10


def ppl_2(traits, trait_names):
    count = count_spell_colleges(traits)
    return count >= 10


def ppl_3(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''IQ '''):
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= 13
    return False


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


def ppl_5(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''Magery''') and '''one college (gate)''' in trait:
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= int('''2''')
    return False


def ppl_6(traits, trait_names):
    for trait in trait_names:
        if trait.startswith('''Magery''') and '''one college''' not in trait:
            regexp = "(\d+).*$"
            match = re.search(regexp, trait)
            if match:
                level = int(match.group(1))
                return level >= int('''2''')
    return False

top_4 = or_(ppl_5(traits, trait_names), ppl_6(traits, trait_names))

top_0 = and_(ppl_1(traits, trait_names), ppl_2(traits, trait_names), ppl_3(traits, trait_names), top_4)
"""


def test_add_spell():
    traits = [
        ("IQ 15", 100),
        ("Magery 3", 35),
    ]
    trait_names = set([trait[0] for trait in traits])
    dfrandom.build_spell_prereqs()
    NUM_SPELLS = 425
    for unused in xrange(NUM_SPELLS):
        dfrandom.add_spell(traits, trait_names)
    assert len(traits) == len(trait_names) == NUM_SPELLS + 2


def test_merge_traits_attr():
    traits = [
        ("ST 14", 40),
        ("ST +2", 20),
    ]
    assert dfrandom.merge_traits(traits) == [("ST 16", 60)]


def test_merge_traits_advantage():
    traits = [
        ("Magery 3", 35),
        ("Magery 4", 10),
    ]
    assert dfrandom.merge_traits(traits) == [("Magery 4", 45)]
