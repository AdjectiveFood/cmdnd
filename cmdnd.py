#!/usr/bin/env python3
import sys
import os
from dnd_core.character import CharacterLoader
from dnd_core.dice import d_str


ROOT = os.path.dirname(os.path.realpath(__file__)) + '/'
MM_ROOT = ROOT + 'monster_manual/'
print(ROOT)
char_loader = CharacterLoader(ROOT, MM_ROOT)


def showMonster(monster_id):
    monster = char_loader.loadMonster(monster_id)
    print(monster)


def roll(dice_string):
    print(str(d_str(dice_string)))


def test():
    monster = char_loader.loadMonster('giant_hill')
    for i in range(30):
        monster.challenge = i
        print(str(monster.challenge), str(monster.proficiency()))


def helpMe():
    max_len = max([len(o[1][1][0] + o[0]) + 10 for o in options.items()])
    title = 'Help'
    upper_bound = ''.join(['-' for i in range(max_len // 2 - len(title) + max_len % 2)])
    upper_bound += title
    upper_bound += ''.join(['-' for i in range(max_len // 2 - len(title) + max_len % 2)])
    print(upper_bound)
    for option, fn in sorted(options.items()):
        print('{0}:\t{1}'.format(option, '\n\t'.join(fn[1])))
    print(''.join(['-' for i in range(len(upper_bound))]))


prog_name = 'cmdnd'
options = {
    '-m': (showMonster, ['Print the stats of the specified monster', '{} -m [the monster id]'.format(prog_name)]),
    '-r': (roll, ['Roll the dice string', '{} -r [dice_string]'.format(prog_name)]),
    '-t': (test, [''])
}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        options[sys.argv[1]][0](*sys.argv[2:])
    else:
        helpMe()
