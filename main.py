from os import execlp
import sys

exp = sys.argv[1]

result = 0
subs = []
if exp[0] == ' ' and (exp[1] == "+" or exp[1] == "-"):
    print('erro')
    sys.exit()

exp = exp.replace(" ", '')

print(exp)
if '+' in exp:
    if '-' in exp:

        list = exp.split('+')
        print(list)
        for i in list:
            if '-' not in i:
                result += int(i)
            else:

                subs.append(i)

        subs = '+'.join(subs)

    else:

        list = exp.split('+')
        for i in list:
            result += int(i)

if '-' in exp:
    print(subs)
    if len(subs) == 0:
        list = exp.split('-')

    else:

        list = subs.split('-')
        for i in list:
            if '+' in i:
                result += int(i.split('+')[-1])
                result -= int(i.split('+')[0])
                list.remove(i)

    result += int(list[0])
    for i in range(1, len(list)):
        result -= int(list[i])


print(result)
