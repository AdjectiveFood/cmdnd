SEPARATOR = ''.join('─' for i in range(78))


def boxStrings(lines):
    boxed_string = ['┌' + SEPARATOR + '┐']
    for line in lines:
        line = fitConsole(line, 78)
        for s in line.splitlines():
            if SEPARATOR == s:
                s = '├' + s + '┤'
            else:
                s = '│' + s
                while(len(s) < 79):
                    s += ' '
                s += '│'
            boxed_string.append(s)
    boxed_string.append('└' + SEPARATOR + '┘')
    return boxed_string


def fitConsole(string, max_length=80):
    sub_strings = []
    words = string.split(' ')
    cur_line = ''
    while(len(words) > 0):
        while(len(cur_line + words[0]) < max_length - 2):
            cur_line += ' ' + words[0]
            words = words[1:]
            if(len(words) == 0):
                break
        if(cur_line == ''):
            cur_line += words[0]
            if(len(words) > 0):
                words = words[1:]
        sub_strings.append(cur_line)
        cur_line = ''
    return '\n '.join(sub_strings)
