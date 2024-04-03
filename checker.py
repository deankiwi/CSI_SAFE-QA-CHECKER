import array
import re


def check_slabs(data) -> None:
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

    return checks


def check_materials(data) -> list:
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


def check_loads(data) -> list:
    # TODO check if load is accident defined twice
    load_groups_used = {"Gk": [], "Qk": [], "__other": []}

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
                load_groups_used["__other"].append(load["Name"])

    return load_groups_used


import json


def check_load_cases(data, load_groups_used={}) -> list:
    # split the name
    # check if it is in the default loading types
    # make set of unique Names
    load_combinations = {}
    if "LOAD COMBINATION DEFINITIONS" in data:
        # print(data["LOAD COMBINATION DEFINITIONS"])
        for load_case in data["LOAD COMBINATION DEFINITIONS"]:
            # print(load_case)
            # print(load_case["Name"])
            if load_case["Name"] not in load_combinations:
                load_combinations[load_case["Name"]] = [load_case]
            else:
                load_combinations[load_case["Name"]].append(load_case)
        print(json.dumps(load_combinations, sort_keys=True, indent=4))
        # check each load combination and all the loads stated in the name
        for load_name in load_combinations:
            # split the name into individual loads
            prefixes = [
                "ULS:",
                "uls:",
                "ULS",
                "uls",
                "SLS:",
                "sls:",
                "SLS",
                "sls",
                "COMB:",
                "comb:",
                "COMB",
                "comb",
            ]
            pattern = (
                r"^(" + "|".join(re.escape(prefix) for prefix in prefixes) + r")\s*"
            )
            print(load_name, "<--- load name")
            load_name = re.sub(pattern, "", load_name)
            print(load_name, "<--- load name updated")
            pattern = r"([-+]?\d*\.?\d+)([A-Za-z0-9]+)"
            matches = re.findall(pattern, load_name)
            print(matches, "<--- matches")
            result = []

            for match in matches:
                quantity = float(match[0]) if match[0] else 1
                unit = match[1]
                result.append([unit, quantity])
            print(result)

    else:
        return {"status": "error", "message": "❌ No load combinations found."}
    # print(load_groups_used)

def extract_units(string):
    # Regular expression pattern to match units and their quantities
    pattern =  r'(?:(?P<quantity>[-+]?\d*\.?\d+))?([A-Za-z0-9]+)'
    matches = re.findall(pattern, string)
    result = []

    for match in matches:
        quantity = float(match[0]) if match[0] else 1
        unit = match[1]
        result.append([unit, quantity])

    return result


def find_route_loads(load_name: str, load_groups_used: dict) -> array:
    route_loads = []
    if load_name in load_groups_used:
        for load in  load_groups_used[load_name]:
            route_loads.extend(find_route_loads(load, load_groups_used))
    else:
        return [load_name]
    return route_loads
