from .dice import d, d_str, d20
from .const_data import *


class Action:
    def __init__(self, name, template):
        self.name = name
        self.to_hit = template['to_hit'] if 'to_hit' in template else None
        if 'damage' in template:
            self.damage = template['damage']
            self.damage_type = template['damage_type']
        else:
            self.damage = None
            self.damage_type = None
        self.range = template['range'] if 'range' in template else None
        self.save = Save(template['save']) if 'save' in template else None
        self.description = template['description'] if 'description' in template else None

    def __str__(self):
        action_str = self.name.capitalize() + ': '
        if self.to_hit is not None:
            action_str += '+' + str(self.to_hit) + ' to hit'
        if self.damage is not None:
            action_str += ' for {} {}'.format(self.damage, '/'.join(self.damage_type))
        if self.save is not None:
            action_str += '\n' + str(self.save)
        if self.description is not None:
            action_str += self.description
        return action_str


class Save:
    def __init__(self, template):
        self.dc = template['dc']
        self.ability = template['ability']
        self.save_pass = template['pass']['description']
        self.save_fail = template['fail']

    def failSave(self):
        fail_str = []
        if 'damage' in self.save_fail:
            fail_str.append(self.save_fail['damage'] + ' ' + '/'.join(self.save_fail['damage_type']))

        if 'condition' in self.save_fail:
            condition_str = self.save_fail['condition']
            condition_str += ' for ' + self.save_fail['duration'] if 'duration' in self.save_fail else ''
            fail_str.append(condition_str)
        return ' AND '.join(fail_str)

    def __str__(self):
        return '\tDC {} {}\n\tPass: {}\n\tFail: {}'.format(self.dc, self.ability, self.failSave(), self.save_pass)
