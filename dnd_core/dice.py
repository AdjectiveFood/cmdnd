from random import randrange


def d(type, time=1):
    return randrange(type) + 1 + d(type, time - 1) if time > 0 else 0


def d_advantage():
    (a, b) = (d(20), d(20))
    return a if a > b else b


def d_disadvantage():
    (a, b) = (d(20), d(20))
    return b if a > b else b


def d20(advantage=False, disadvantage=False):
    if advantage and disadvantage:
        return d(20)
    if advantage:
        roll = d_advantage()
    elif disadvantage:
        roll = d_disadvantage()
    else:
        roll = d(20)
    return roll


def d_str(dice_str):
    def resolve(operation):
        # print('resolve:', operation)
        if len(operation) > 3:
            return resolve([resolve(operation[:3])] + operation[3:])
        elif len(operation) == 3:
            (num1, operator, num2) = operation
            if operator == '+':
                return num1 + num2
            elif operator == '-':
                return num1 - num2
        elif len(operation) == 1:
            return operation[0]
        else:
            raise('fuck resolve')

    def tokenize(dice_str):
        parsed = []
        time = 0
        cur_num = 0

        def calc(c, t, parsed):
            if c > 0:
                result = c if t == 0 else d(c, t)
                parsed.append(result)

        for i, char in enumerate(dice_str):
            if char in [str(i) for i in range(10)]:
                cur_num = cur_num * 10 + int(char)
            elif char == 'd':
                if cur_num > 0:
                    time = cur_num
                else:
                    time = 1
                cur_num = 0
            elif char in '+-':
                calc(cur_num, time, parsed)
                cur_num = time = 0
                parsed.append(char)
        calc(cur_num, time, parsed)

        return parsed

    def locatePrenthesis(string):
        openenings = []
        closures = []
        for i, char in enumerate(string):
            if char == '(':
                openenings.append(i)
            elif char == ')':
                closures.append(i)

        return (openenings, closures)

    def findMatchingParenthesis(string, open_idx):
        count = 0
        cur_idx = open_idx

        for char in string[open_idx:]:
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
                if count == 0:
                    return cur_idx
            cur_idx += 1

        raise(Exception('no closing parenthesis'))

    def parse(dice_str):
        if len(dice_str) == 0:
            return []
        wrapper = []

        if '(' not in dice_str and ')' not in dice_str:
            return tokenize(dice_str)

        opening_idx = dice_str.index('(') if '(' in dice_str else -1
        if opening_idx == -1:
            raise(Exception('fuck parse'))

        closing_idx = findMatchingParenthesis(dice_str, opening_idx)

        wrapper = parse(dice_str[:opening_idx])
        wrapper.append(parse(dice_str[opening_idx + 1: closing_idx]))
        wrapper += parse(dice_str[closing_idx + 1:])

        return wrapper

    def isFlat(array):
        if not isinstance(array, list):
            return True

        for i in array:
            if isinstance(i, list):
                return False
        return True

    def flatten(parsed):
        flat = []
        for i in parsed:
            if isinstance(i, list):
                if(len(i) > 0):
                    flat.append(flatten(i))
            else:
                flat.append(i)

        if isFlat(flat):
            return resolve(flat)
        else:
            return flatten(flat)

    # print(dice_str)
    parsed = parse(dice_str)

    # print(parsed)
    return flatten(parsed)
