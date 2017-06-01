import json


ITERATIONS = 5000


def main():
    count = 0
    fileno = 0
    with open('vevo.json', 'r') as file:
        isrclist = json.load(file)
        jsonlist = dict()
        for entry in isrclist.values():
            jsonlist.update({count: entry})
            count = count + 1
            if count == ITERATIONS:
                with open('vevo' + str(fileno) + '.json', 'w') as file:
                    json.dump(jsonlist, file)
                jsonlist = dict()
                count = 0
                fileno = fileno + 1
        with open('vevo' + str(fileno) + '.json', 'w') as file:
            json.dump(jsonlist, file)


if __name__ == '__main__':
    main()
