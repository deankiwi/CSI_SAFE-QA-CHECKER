import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from checker import (
    check_slabs,
    check_materials,
    check_loads,
    check_load_cases,
    extract_units,
    find_route_loads,
)
from utils import safe_to_json


def test_check_slabs_1():
    # TODO check slab for correct thickness and grade
    data = safe_to_json(
        """TABLE:  "SLAB PROPERTY DEFINITIONS"
   Name=S-225-C32/40   "Modeling Type"=Shell-Thick   "Property Type"=Slab   Material=C32/40   "Slab Thickness"=225   "Notional Size Type"=Auto   "Notional Auto Factor"=1   "f11 Modifier"=1   "f22 Modifier"=1   "f12 Modifier"=1 _
        "m11 Modifier"=0.25   "m22 Modifier"=0.25   "m12 Modifier"=0.25   "v13 Modifier"=1   "v23 Modifier"=1   "Mass Modifier"=1   "Weight Modifier"=1   Color=Blue   GUID=916b4a2d-f44d-4d9d-bc33-3c67db2235bb   Orthotropic?=No
        """
    )

    checks = check_slabs(data)

    assert checks == []


def test_check_slabs_2():
    # TODO check slab for incorrect thickness and grade
    data = safe_to_json(
        """TABLE:  "SLAB PROPERTY DEFINITIONS"
   Name=S-226-C32/40   "Modeling Type"=Shell-Thick   "Property Type"=Slab   Material=C32/40   "Slab Thickness"=225   "Notional Size Type"=Auto   "Notional Auto Factor"=1   "f11 Modifier"=1   "f22 Modifier"=1   "f12 Modifier"=1 _
        "m11 Modifier"=0.25   "m22 Modifier"=0.25   "m12 Modifier"=0.25   "v13 Modifier"=1   "v23 Modifier"=1   "Mass Modifier"=1   "Weight Modifier"=1   Color=Blue   GUID=916b4a2d-f44d-4d9d-bc33-3c67db2235bb   Orthotropic?=No
        """
    )

    checks = check_slabs(data)

    assert len(checks) == 1
    assert checks[0]["status"] == "error"
    assert (
        checks[0]["message"]
        == "❌ S-226-C32/40: Thickness defined (225)  does not match name (226)"
    )
    assert checks[0]["slab"] == data["SLAB PROPERTY DEFINITIONS"][0]


def test_check_slabs_3():
    # TODO check slab for incorrect name

    data = safe_to_json(
        """TABLE:  "SLAB PROPERTY DEFINITIONS"
   Name=FakeNameForTesting   "Modeling Type"=Shell-Thick   "Property Type"=Slab   Material=C32/40   "Slab Thickness"=225   "Notional Size Type"=Auto   "Notional Auto Factor"=1   "f11 Modifier"=1   "f22 Modifier"=1   "f12 Modifier"=1 _
        "m11 Modifier"=0.25   "m22 Modifier"=0.25   "m12 Modifier"=0.25   "v13 Modifier"=1   "v23 Modifier"=1   "Mass Modifier"=1   "Weight Modifier"=1   Color=Blue   GUID=916b4a2d-f44d-4d9d-bc33-3c67db2235bb   Orthotropic?=No
        """
    )

    checks = check_slabs(data)

    assert len(checks) == 1
    assert checks[0]["status"] == "warning"
    assert (
        checks[0]["message"]
        == "⚠️ FakeNameForTesting: Name does not follow standard naming convention. S-<thickness>-C<grade_c>/<grade_r>, unable to check thickness and grade."
    )
    assert checks[0]["slab"] == data["SLAB PROPERTY DEFINITIONS"][0]


def test_check_materials_1():
    # check material for correct grade
    data = safe_to_json(
        """TABLE:  "MATERIAL PROPERTIES - CONCRETE DATA"
   Material=C32/40   Fc=32   LtWtConc=No   IsUserFr=Yes   UserFr=3   SSCurveOpt=Mander   SSHysType=Concrete   SFc=0.00221914   SCap=0.005   FinalSlope=-0.1   FAngle=0   DAngle=0
   Material=C35/45   Fc=35   LtWtConc=No   IsUserFr=Yes   UserFr=3.2   SSCurveOpt=Mander   SSHysType=Concrete   SFc=0.00221914   SCap=0.005   FinalSlope=-0.1   FAngle=0   DAngle=0"""
    )

    checks = check_materials(data)
    assert checks == []


def test_check_materials_2():
    #  check material for incorrect name
    data = safe_to_json(
        """TABLE:  "MATERIAL PROPERTIES - CONCRETE DATA"
   Material=C32/40   Fc=40   LtWtConc=No   IsUserFr=Yes   UserFr=3   SSCurveOpt=Mander   SSHysType=Concrete   SFc=0.00221914   SCap=0.005   FinalSlope=-0.1   FAngle=0   DAngle=0
"""
    )

    checks = check_materials(data)

    assert checks == [
        {
            "status": "error",
            "message": "❌ C32/40: Fc defined (40) does not match name (32)",
            "material": {
                "Material": "C32/40",
                "Fc": "40",
                "LtWtConc": "No",
                "IsUserFr": "Yes",
                "UserFr": "3",
                "SSCurveOpt": "Mander",
                "SSHysType": "Concrete",
                "SFc": "0.00221914",
                "SCap": "0.005",
                "FinalSlope": "-0.1",
                "FAngle": "0",
                "DAngle": "0",
            },
        }
    ]


def test_check_materials_3():
    # check material if light weight is used

    data = safe_to_json(
        """TABLE:  "MATERIAL PROPERTIES - CONCRETE DATA"
   Material=C32/40   Fc=32   LtWtConc=Yes   IsUserFr=Yes   UserFr=3   SSCurveOpt=Mander   SSHysType=Concrete   SFc=0.00221914   SCap=0.005   FinalSlope=-0.1   FAngle=0   DAngle=0
"""
    )

    checks = check_materials(data)

    assert checks == [
        {
            "status": "warning",
            "message": "⚠️ C32/40: Lightweight concrete is used.",
            "material": {
                "Material": "C32/40",
                "Fc": "32",
                "LtWtConc": "Yes",
                "IsUserFr": "Yes",
                "UserFr": "3",
                "SSCurveOpt": "Mander",
                "SSHysType": "Concrete",
                "SFc": "0.00221914",
                "SCap": "0.005",
                "FinalSlope": "-0.1",
                "FAngle": "0",
                "DAngle": "0",
            },
        }
    ]


def test_check_loads_1():
    # checks loads to return list of grouped loads
    data = safe_to_json(
        """TABLE:  "LOAD CASE DEFINITIONS - LINEAR STATIC"
   Name=Dead   "Exclude Group"=None   "Initial Condition"=Unstressed   "Load Type"=Load   "Load Name"=Dead   "Load SF"=1   "Design Type"="Program Determined"   GUID=ac8bd02b-d41f-40b2-aff8-6aea8efab57e
   Name=FACADE   "Exclude Group"=None   "Initial Condition"=Unstressed   "Load Type"=Load   "Load Name"=FACADE   "Load SF"=1   "Design Type"="Program Determined"   GUID=8d043046-5805-40b0-a8b2-4d21a5420346
   Name=Live   "Exclude Group"=None   "Initial Condition"=Unstressed   "Load Type"=Load   "Load Name"=Live   "Load SF"=1   "Design Type"="Program Determined"   GUID=b964296b-0b66-4c12-9187-d908c01cbad6
   Name="Live - construction"   "Exclude Group"=None   "Initial Condition"=Unstressed   "Load Type"=Load   "Load Name"="Live - construction"   "Load SF"=1   "Design Type"="Program Determined"   GUID=1a6f476f-d578-4709-84cb-7b70af35e1a0
   Name=PROPPING   "Exclude Group"=None   "Initial Condition"=Unstressed   "Load Type"=Load   "Load Name"=PROPPING   "Load SF"=1   "Design Type"="Program Determined"   GUID=0da4a649-fc68-48e6-b7b6-7747de1ec614
   Name=SDL   "Exclude Group"=None   "Initial Condition"=Unstressed   "Load Type"=Load   "Load Name"=SDL   "Load SF"=1   "Design Type"="Program Determined"   GUID=8ffdb9b9-8d6d-44ff-80f8-38a074c775ca
"""
    )

    checks = check_loads(data)

    assert checks == {
        "Gk": ["Dead", "FACADE", "SDL"],
        "Qk": ["Live"],
        "__other": ["Live - construction", "PROPPING"],
    }


def test_find_route_loads_1():
    route_load = find_route_loads(
        "Gk",
        {
            "Gk": ["Dead", "FACADE", "SDL"],
        },
    )
    assert route_load == ["Dead", "FACADE", "SDL"]


def test_find_route_loads_2():
    """check for nested loads"""
    route_load = find_route_loads(
        "group1",
        {
            "group1": ["group2"],
            "group2": ["group3", "load"],
            "group3": ["Dead", "FACADE", "SDL"],
        },
    )
    print(route_load, "<---- route_load")
    assert route_load.sort() == ["load", "Dead", "FACADE", "SDL"].sort()

    """check for a route load"""


def test_check_load_cases_1():
    data = safe_to_json(
        """
TABLE:  "LOAD COMBINATION DEFINITIONS"
   Name=Gk   Type="Linear Add"   "Is Auto"=No   "Load Name"=Dead   SF=1   GUID=c04ed5c1-ee14-4cfe-a95b-4226a5ff5963
   Name=Gk   "Load Name"=SDL   SF=1
   Name=Gk   "Load Name"=FACADE   SF=1
Name="G+Q"   Type="Linear Add"   "Is Auto"=No   "Load Name"=Gk   SF=1   GUID=51e409c6-e04c-4881-a674-756dfa51965f
   Name="G+Q"   "Load Name"=Live   SF=1
                        """
    )
    # print(data)
    checks = check_load_cases(data)
    # print(checks, '<---- check')

def test_extract_units_1():
    units = extract_units("1G + 1Q")
    assert units == [['G',1.0], ['Q',1.0]]

def test_extract_units_2():
    units = extract_units("G")
    assert units == [['G',1.0]]

def test_extract_units_3():
    units = extract_units("G + Q")
    assert units == [['G',1.0], ['Q',1.0]]

def test_extract_units_4():
    units = extract_units("1.35G + 1.50Q")
    assert units == [['G',1.35], ['Q',1.50]]

def test_extract_units_5():
    units = extract_units("1.35Gk + 1.50Qk")
    assert units == [['Gk',1.35], ['Qk',1.50]]


exampleText = """
TABLE:  "LOAD COMBINATION DEFINITIONS"
   Name=Gk   Type="Linear Add"   "Is Auto"=No   "Load Name"=Dead   SF=1   GUID=c04ed5c1-ee14-4cfe-a95b-4226a5ff5963
   Name=Gk   "Load Name"=SDL   SF=1
   Name=Gk   "Load Name"=FACADE   SF=1
   Name="Pre caldding deflection"   Type="Linear Add"   "Is Auto"=No   "Load Name"="Case: 4: IC"   SF=1   GUID=b01d289e-dc7c-482f-a603-487723a7561c
   Name="Pre caldding deflection"   "Load Name"="Cracked: propping"   SF=1
   Name="Pre caldding deflection"   "Load Name"="Dead Cracked"   SF=-1
   Name="Quasi Perm Pod"   Type="Linear Add"   "Is Auto"=No   "Load Name"=Gk   SF=1   GUID=98a7edfe-9b11-42bf-a264-0249379abeb6
   Name="Quasi Perm Pod"   "Load Name"=Live   SF=0.6
   Name="Quasi Perm Res"   Type="Linear Add"   "Is Auto"=No   "Load Name"=Gk   SF=1   GUID=853e29d6-04f9-48ff-b832-eb4810558618
   Name="Quasi Perm Res"   "Load Name"=Live   SF=0.3
   Name="SLS: Gk + Qk"   Type="Linear Add"   "Is Auto"=No   "Load Name"=Gk   SF=1   GUID=51e409c6-e04c-4881-a674-756dfa51965f
   Name="SLS: Gk + Qk"   "Load Name"=Live   SF=1
   Name="SLS: Post Construction Deflection"   Type="Linear Add"   "Is Auto"=No   "Load Name"="SLS: Total Long Term Deflection"   SF=1   GUID=c506f2a9-4c14-4702-bd48-9f47d0efd8eb
   Name="SLS: Post Construction Deflection"   "Load Name"="Case: 4: IC"   SF=-1
   Name="SLS: Post Construction Deflection-1"   Type="Linear Add"   "Is Auto"=No   "Load Name"="SLS: Total Long Term Deflection"   SF=1   GUID=628a3833-f7a9-4a69-918d-d6f3293dc93a
   Name="SLS: Post Construction Deflection-1"   "Load Name"="Pre caldding deflection"   SF=-1
   Name="SLS: Total Long Term Deflection"   Type="Linear Add"   "Is Auto"=No   "Load Name"="Case: 3: LTPC"   SF=1   GUID=e5712b1d-d3d9-4516-a9f5-970a6ba0f3be
   Name="SLS: Total Long Term Deflection"   "Load Name"="Case 1: STFL"   SF=1
   Name="SLS: Total Long Term Deflection"   "Load Name"="Case 2: STPC"   SF=-1
   Name="ULS: 1.35Gk + 1.5Qk"   Type="Linear Add"   "Is Auto"=No   "Load Name"=Gk   SF=1.35   GUID=ec8df715-054c-4114-be54-8b1a2c577a49
   Name="ULS: 1.35Gk + 1.5Qk"   "Load Name"=Live   SF=1.5
"""
