import re

# function SAFE text file to JSON


def safe_to_json(rawFile) -> dict:
    data = {}
    current_table = None
    brokenLine = False

    for line in rawFile.split("\n"):
        line = line.strip()

        if line.startswith("TABLE:"):
            current_table = line.split('"')[1]
            data[current_table] = []
        elif line.startswith("END TABLE DATA"):
            current_table = None
        elif current_table != None and ("=" in line):
            rowData = {}
            change_to_broken_line = False
            # regex to check if _ is at the end of the line
            if bool(re.search(r"_\s*$", line)):
                change_to_broken_line = True
                print(line)
                print("broken line")
                line = line[:-1]
                print(line)

            for eachValue in line.split("   "):
                key, value = eachValue.split("=", 1)

                rowData[key.strip().replace('"', "")] = value.strip().replace('"', "")
            if not brokenLine:
                data[current_table].append(rowData)
            else:
                # add row data to the last dictionary in array
                data[current_table][-1].update(rowData)
                brokenLine = False
            if change_to_broken_line:
                brokenLine = True
    return data
