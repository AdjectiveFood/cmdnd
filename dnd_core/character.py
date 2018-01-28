from .dice import d, d_str, d20
import json
import os
from .const_data import *
from .action import Action

# TODO: attack bonus have finesse if the str is under 10. See mastiff vs raven
# PC ids must start with the PC_TOKEN const


char_cache = {}


def statModifier(stat):
    return (stat - 10) // 2


def statModifierStr(stat):
    mod = statModifier(stat)
    return ('+' if mod >= 0 else '') + str(mod)


class CharacterLoader:
    def __init__(self, root, monster_manual_dir):
        self.root = root
        self.monster_manual_dir = monster_manual_dir

    def getFilenameFromMonsterId(self, m_id):
        if len(m_id) > 0:
            filename = self.monster_manual_dir + m_id[0].lower() + '.json'
            if not os.path.exists(filename):
                raise(Exception('There is no monster in the {} file'.format(m_id[0])))
            return filename

    def loadMonster(self, m_id, name=None):
        global char_cache

        if m_id in char_cache:
            template = char_cache[m_id]
        else:
            json_file = self.getFilenameFromMonsterId(m_id)
            with open(json_file) as json_data:
                all_data = json.load(json_data)
                char_cache = {**char_cache, **all_data}
                if m_id in all_data:
                    template = all_data[m_id]
                else:
                    raise(Exception(m_id + ' not found in ' + json_file))

        default_name = template['default_name'] if 'default_name' in template else m_id
        name = name if name is not None else ' '.join([w.capitalize() for w in default_name.replace('_', ' ').split(' ')])
        return Character(name, template, m_id)

    def loadMonsterFromEncounter(encounter_data):
        character = load(encounter_data['template_file'], encounter_data['template_id'], encounter_data['name'])
        character.max_hp = encounter_data['max_hp']
        character.cur_hp = encounter_data['cur_hp']
        character.tmp_hp = encounter_data['tmp_hp']


class Character:
    def __init__(self, name, template, template_id, roll_hp=True):
        self.template_id = template_id
        self.name = name
        self.reference = (template['ref']['book'] + ' page ' + str(template['ref']['page'])) if 'ref' in template else None
        self.challenge = template['challenge']
        self.abilities = template['stat_block']
        for a in self.abilities:
            if a not in ABILITIES:
                raise(Exception(a + " is not an ability, check for typo you ding dong"))
        self.ac = template['ac']
        self.random_hp_str = template['hit_point']['random']
        if roll_hp:
            self.rollHp()
        else:
            self.resetHp(template['hit_point']['default'])
        self.speed = template['speed']
        self.languages = template['languages']
        self.skill_bonus = template['skill_bonus'] if 'skill_bonus' in template else {}

        # Saving Throw
        self.saving_throw = dict(zip(ABILITIES, [0, 0, 0, 0, 0, 0]))
        if 'saving_throw_proficiency' in template:
            for ability in template['saving_throw_proficiency']:
                if ability not in ABILITIES:
                    raise(Exception(ability + ' is not an ability. Check for typo you ding dong.'))
                else:
                    self.saving_throw[ability] += self.proficiency() + statModifier(self.abilities[ability])

        self.immunities = template['immunities'] if 'immunities' in template else []
        self.resistances = template['resistances'] if 'resistances' in template else []

        self.senses = template['senses']

        # Skills
        self.skills = template['skills'] if 'skills' in template else {'proficiency': [], 'expertise': []}
        if 'proficiency' not in self.skills:
            self.skills['proficiency'] = []
        if 'expertise' not in self.skills:
            self.skills['expertise'] = []

        # Special Abilities
        if 'special_abilities' in template:
            self.special_abilities = template['special_abilities']
        else:
            self.special_abilities = {}

        # Actions
        self.actions = []
        for name, action_template in template['actions'].items():
            self.actions.append(Action(name, action_template))

    def resetHp(self, max_hp=None):
        max_hp = self.max_hp if max_hp is None else max_hp
        self.max_hp = self.cur_hp = max_hp
        self.tmp_hp = 0

    def rollHp(self):
        self.resetHp(d_str(self.random_hp_str))

    def initiativeRoll(self, bonus):
        return d(20) + statModifier(self.abilities[A_DEX])

    def xpValue(self):
        if self.challenge == 0:
            return 0
        if 0 < self.challenge < 1:
            return [25, 50, 100][int((self.challenge * 8) // 2)]
        else:
            return [
                0,
                200, 450, 700, 1100, 1800,
                2300, 2900, 3900, 5000, 5900,
                7200, 8400, 10000, 11500, 13000,
                15000, 18000, 20000, 22000, 25000,
                33000, 41000, 50000, 62000, 75000,
                90000, 105000, 120000, 1655000, 155000
            ][self.challenge]

    def proficiency(self):
        if self.challenge < 5:
            return 2
        else:
            return ((self.challenge - 5) // 4) + 3

    def skillCheck(self, skill_name, advantage=False, disadvantage=False):
        if skill_name in SKILLS:
            roll = d20(advantage, disadvantage)
            result = roll + statModifier(self.abilities[SKILLS[skill_name]])
            result = result + self.proficiency() if skill_name in self.skills['proficiency'] else result
            result = result + self.proficiency() * 2 if skill_name in self.skills['expertise'] else result
            return result
        else:
            raise(Exception(skill_name + " isn't a skill, check for typo you ding dong."))

    def passivePerception(self, advantage=False, disadvantage=False):
        if advantage and disadvantage:
            advantage = disadvantage = False
        result = 10 + statModifier(self.abilities[A_WIS]) + self.skillMod('perception')
        result += 5 if advantage else 0
        result -= 5 if disadvantage else 0
        return result

    def skillMod(self, skill_name):
        result = statModifier(self.abilities[SKILLS[skill_name]])
        result = result + self.proficiency() if skill_name in self.skills['proficiency'] else result
        result = result + self.proficiency() * 2 if skill_name in self.skills['expertise'] else result
        return result

    def __str__(self):
        seperator = ''.join('-' for i in range(80))
        string = [
            seperator,
            self.name,
            self.template_id + (' ' + self.reference if self.reference is not None else ''),
            seperator,
            'Armor Class: {}'.format(self.ac),
            'Hit Points: {}/{} ({})'.format(self.cur_hp, self.max_hp, self.random_hp_str),
            'Speed: {}'.format(', '.join(['({}: {}ft)'.format(i, j) for i, j in self.speed.items()])),
            seperator,
            ' STR\t DEX\t CON\t INT\t WIS\t CHA',
            '\t'.join(['{} ({})'.format(*(self.abilities[a], statModifier(self.abilities[a]))) for a in ABILITIES]),
            seperator,
            ('Saving Throws: ' + ', '.join(['{} {}'.format(s.capitalize(), b) for s, b in self.saving_throw.items() if b > 0])),
            ('Skills: ' + ', '.join(['{} {}'.format(sn.capitalize(), self.skillMod(sn)) for sn in self.skills['proficiency'] + self.skills['expertise']])),
            ('Damage Immunities: ' + ', '.join(self.immunities)) if len(self.immunities) > 0 else '',
            ('Damage Resistances: ' + ', '.join(self.resistances)) if len(self.resistances) > 0 else '',
            'Senses: Passive Perception {}, {}'.format(self.passivePerception(), ', '.join(['({}: {}ft)'.format(i, j) for i, j in self.senses.items()])),
            'Languages: ' + ', '.join(self.languages),
            'Challenge: {} ({}xp)'.format(self.challenge, self.xpValue()),
            seperator,
            '\n'.join([name.capitalize() + ': ' + desc for name, desc in self.special_abilities.items()]),
            seperator,
            '\n'.join([str(a) for a in self.actions])
        ]

        string = [s for s in string if len(s) > 0]

        return '\n'.join(string)

    def toEncounterDict(self):
        # TODO: link to template
        return {
            "template_id": self.template_id,
            "name": self.name,
            "max_hp": self.max_hp,
            "cur_hp": self.cur_hp,
            "tmp_hp": self.tmp_hp
        }
