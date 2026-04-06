metrics = [
    "RMS",
    "Max Peak",
    "Peak-to-Peak",
    "Crest Factor",
    "K Factor",
    "Impulse Factor",
    "Skewness",
    "Kurtosis",
    "Wind Speed Mean (m per s)",
    "Power Mean (kW)",
    "RPM Mean"
]


BEARINGS = {
    1: [
        {
            "Name": "Rotor_RBG",
            "TR": 79.46,
            "BPFO": 47.0,
            "BPFI": 63.0,
            "FTF": 0.5,
            "BSF2": 36.8667
        }
    ],
    3: [
        {
            "Name": "GBX_In_BRG1",
            "TR": 79.46,
            "BPFO": 30.9,
            "BPFI": 34.1,
            "FTF": 0.476,
            "BSF2": 20.7
        }
    ],
    5: [
        {
            "Name": "GBX_OUT_BRG2",
            "TR": 1,
            "BPFO": 7.7,
            "BPFI": 10.3,
            "FTF": 0.4,
            "BSF2": 6.6
        }
    ],
    6: [
        {
            "Name": "GBX_OUT_BRG1",
            "TR": 1,
            "BPFO": 20.7,
            "BPFI": 23.3,
            "FTF": 0.4,
            "BSF2": 15.5
        }
    ],
    7: [
        {
            "Name": "Gen_DE_BRG",
            "TR": 1,
            "BPFO": 3.66,
            "BPFI": 5.34,
            "FTF": 0.407,
            "BSF2": 5.168
        }
    ],
    8: [
        {
            "Name": "Gen_NDE_RBG",
            "TR": 1,
            "BPFO": 3.66,
            "BPFI": 5.34,
            "FTF": 0.407,
            "BSF2": 5.168
        }
    ]
}


GEARS = {
    6: [
        {
            "Name": "GBX-Out_Pinion",
            "Teeth_Number": 44,
            "TR": 1,
            "Mode": "gear_teeth",
            "Harmonics": [1, 2]
        }
    ],
    5: [
        {
            "Name": "GBX-Out_Wheel",
            "Teeth_Number": 111,
            "TR": 44 / 111,
            "Mode": "gear_teeth",
            "Harmonics": [1, 2]
        }
    ],
    4: [
        {
            "Name": "GBX-Mid_Sun",
            "TR": 6.109,
            "Mode": "gear_tr_only",
            "Harmonics": [1, 2, 3]
        }
    ]
}
