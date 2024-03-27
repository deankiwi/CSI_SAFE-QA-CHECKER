from math import e
from pyscript import document
import re

data = {}


# TODO separate processing file into a separate file
# TODO end of line in file is done with " _", this effects the data processing. e.g. 'f12 Modifier': '1' becomes 'f12 Modifier': '1 _'
# TODO update other return messages to be link that of check_load_cases where if it isn't found it returns a message
def safe_checker(event) -> None:
    input_text = document.querySelector("#safe_file")
    english = input_text.value
    output_div = document.querySelector("#report")
    output_div.innerText = english

    current_table = None
    brokenLine = False

    for line in english.split("\n"):
        line = line.strip()
        print(line)
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
    print(data, "<--- DATA")
    # print(data['SLAB PROPERTY DEFINITIONS'][0])
    check_names()


def check_names():
    checkbox = document.getElementById("show_warnings")
    if checkbox.checked:
        status = ["error", "warning"]
    else:
        status = ["error"]

    slabs = check_slabs()
    material = check_materials()
    load_groups_used = check_loads()
    load_cases = check_load_cases(load_groups_used)

    output_div = document.querySelector("#report")
    output_div.innerText = " Slab Checks \n"
    output_div.innerText += "\n".join(
        [slab["message"] for slab in slabs if slab["status"] in status]
    )
    output_div.innerText += "\n\n Material Checks \n"

    output_div.innerText += "\n".join(
        [material["message"] for material in material if material["status"] in status]
    )

    output_div.innerText += "\n\n Load Checks \n"
    output_div.innerText += str(load_groups_used)


def check_slabs() -> None:
    # TODO check if concrete is light weight
    # TODO check if beam that is modeled as slab is correct depth
    checks = []
    if data["SLAB PROPERTY DEFINITIONS"]:

        for slab in data["SLAB PROPERTY DEFINITIONS"]:
            check = {}
            pattern = r"^S-\d+-C\d+/\d+"

            if re.match(pattern, slab["Name"]):
                # TODO check if correct values are used
                _, thickness, grade = slab["Name"].split("-")

                if slab["Slab Thickness"] != thickness:
                    check["status"] = "error"
                    check["message"] = (
                        f'❌ {slab["Name"]}: Thickness defined ({slab["Slab Thickness"]})  does not match name ({thickness})'
                    )
                    check["slab"] = slab

                elif slab["Material"] not in grade:
                    check["status"] = "error"
                    check["message"] = (
                        f'❌ {slab["Name"]}: Grade defined {slab["Material"]} does not match name ({grade})'
                    )
                    check["slab"] = slab

                # check if check is empty

                if len(check) > 0:
                    checks.append(check)

            else:
                checks.append(
                    {
                        "status": "warning",
                        "message": f"⚠️ {slab['Name']}: Name does not follow standard naming convention. S-<thickness>-C<grade_c>/<grade_r>, unable to check thickness and grade.",
                        "slab": slab,
                    }
                )
                print("not good")
    return checks


def check_materials() -> list:
    checks = []
    if data["MATERIAL PROPERTIES - CONCRETE DATA"]:

        for material in data["MATERIAL PROPERTIES - CONCRETE DATA"]:

            pattern = r"^C\d+/\d+"
            if re.match(pattern, material["Material"]):
                match = re.match(r"C(\d+)", material["Material"])
                grade = match.group(1)

                if material["Fc"] != grade:
                    checks.append(
                        {
                            "status": "error",
                            "message": f'❌ {material["Material"]}: Fc defined ({material["Fc"]}) does not match name ({grade})',
                            "material": material,
                        }
                    )
                    print("grade is correct")
            else:
                checks.append(
                    {
                        "status": "warning",
                        "message": f"⚠️ {material['Material']}: Name does not follow standard naming convention. C<grade_c>/<grade_r>, unable to check grade.",
                        "material": material,
                    }
                )
            if material["LtWtConc"] == "Yes":
                checks.append(
                    {
                        "status": "warning",
                        "message": f"⚠️ {material['Material']}: Lightweight concrete is used.",
                        "material": material,
                    }
                )

    return checks


# check what loads have been defined and build a list of loads should go into Gk, Qk


def check_loads() -> list:
    load_groups_used = {"Gk": [], "Qk": [], "other": []}

    default_loading_types = {
        "dead": "Gk",
        "dl": "Gk",
        "sdl": "Gk",
        "facade": "Gk",
        "façade": "Gk",
        "ll": "Qk",
        "live": "Qk",
    }
    if data["LOAD CASE DEFINITIONS - LINEAR STATIC"]:

        for load in data["LOAD CASE DEFINITIONS - LINEAR STATIC"]:

            if load["Name"].lower() in default_loading_types:
                load_groups_used[default_loading_types[load["Name"].lower()]].append(
                    load["Name"]
                )
            else:
                load_groups_used["other"].append(load["Name"])

    return load_groups_used


def check_load_cases(load_groups_used = {}) -> None:
    # split the name
    # check if it is in the default loading types
    # make set of unique Names
    load_combinations = {}
    if "LOAD COMBINATION DEFINITIONS" in data:
        print(data["LOAD COMBINATION DEFINITIONS"])
        for load_case in data["LOAD COMBINATION DEFINITIONS"]:
            print(load_case)
            print(load_case["Name"])
            if load_case["Name"] not in load_combinations:
                load_combinations[load_case["Name"]] = [load_case]
            else:
                load_combinations[load_case["Name"]].append(load_case)
        print(load_combinations)
        # check each load combination and all the loads stated in the name
        for load_name in load_combinations:
            # split the name into individual loads
            prefixes = ['ULS', 'uls', 'ULS:', 'uls:', 'SLS', 'sls', 'SLS:', 'sls:', 'COMB', 'comb', 'COMB:', 'comb:']
            pattern = r'^(' + '|'.join(re.escape(prefix) for prefix in prefixes) + r')\s*'
            print(load_name, "<--- load name")
            load_name = re.sub(pattern, '', load_name)
            print(load_name, "<--- load name updated")
            pattern = r'([-+]?\d*\.?\d+)([A-Za-z0-9]+)'
            matches = re.findall(pattern, load_name)
            result = []

            for match in matches:
                quantity = float(match[0]) if match[0] else 1
                unit = match[1]
                result.append([unit, quantity])
            print(result)




    else:
        return {"status": "error", "message": "❌ No load combinations found."}
    print(load_groups_used)
