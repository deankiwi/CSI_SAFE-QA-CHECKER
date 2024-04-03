import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import safe_to_json


def test_safe_to_json_1():
    """to return dictionary with key as table name and value as list of dictionaries"""
    data = safe_to_json(
        """TABLE:  "test table 1"
   "Two Dimensional Only"=No   "Rigid Diaphragm At Top"=No   
 
TABLE:  "test table 2"
   "Mesh Option"=Rectangular   "Use Localized Meshing"=Yes"""
    )
    print(data)
    assert data == {
        "test table 1": [
            {"Two Dimensional Only": "No", "Rigid Diaphragm At Top": "No"}
        ],
        "test table 2": [
            {"Mesh Option": "Rectangular", "Use Localized Meshing": "Yes"}
        ],
    }


def test_safe_to_json_2():
    """Check when '_' is at the end of the line that it continues to the next line"""
    data = safe_to_json(
        """TABLE:  "test table 1"
   "Two Dimensional Only"=No   "Rigid Diaphragm At Top"=No_
   Mesh Option"=Rectangular   "Use Localized Meshing"=Yes
   """
    )
    print(data)
    assert data == {
        "test table 1": [
            {
                "Two Dimensional Only": "No",
                "Rigid Diaphragm At Top": "No",
                "Mesh Option": "Rectangular",
                "Use Localized Meshing": "Yes",
            }
        ]
    }
