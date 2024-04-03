from pyscript import document
import re
import checker
import utils


# TODO separate processing file into a separate file
# TODO end of line in file is done with " _", this effects the data processing. e.g. 'f12 Modifier': '1' becomes 'f12 Modifier': '1 _'
# TODO update other return messages to be link that of check_load_cases where if it isn't found it returns a message
def safe_checker(event) -> None:
    input_text = document.querySelector("#safe_file")
    english = input_text.value
    output_div = document.querySelector("#report")
    output_div.innerText = english

    data = utils.safe_to_json(english)
    check_names(data)


def check_names(data):
    checkbox = document.getElementById("show_warnings")
    if checkbox.checked:
        status = ["error", "warning"]
    else:
        status = ["error"]

    slabs = checker.check_slabs(data)
    material = checker.check_materials(data)
    load_groups_used = checker.check_loads(data)
    load_cases = checker.check_load_cases(data, load_groups_used)

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
