"""Full Kenya-market vehicle taxonomy seed data.

Structure:
    MAKES = {
        "Make Name": {
            "popularity": int,          # ordering weight (Toyota first)
            "models": {
                "Model Name": {
                    "aliases": [...],   # search aliases / old-URL redirects
                    "gens": [
                        (code, year_from, year_to, body_type,
                         [trim, ...],
                         [(engine_display, engine_code, fuel, cc), ...]),
                    ],
                },
            },
        },
    }

year_to == 9999 (OPEN_YEAR) means still in production.
Variants are created as trim x engine over the generation's year span.
Add images later via admin — this file is data only.
"""

OPEN = 9999

MAKES = {
    # ------------------------------------------------------------------ TOYOTA
    "Toyota": {
        "popularity": 100,
        "models": {
            "Land Cruiser Prado": {
                "aliases": ["Prado", "LC Prado"],
                "gens": [
                    ("J120", 2002, 2009, "SUV", ["TX", "VX"],
                     [("2.7L Petrol", "2TR-FE", "petrol", 2694),
                      ("3.0L Diesel", "1KD-FTV", "diesel", 2982)]),
                    ("J150", 2009, 2023, "SUV", ["TX", "TX-L", "VX"],
                     [("2.8L Diesel", "1GD-FTV", "diesel", 2755),
                      ("4.0L Petrol", "1GR-FE", "petrol", 3956)]),
                    ("J250", 2024, OPEN, "SUV", ["TX", "VX", "First Edition"],
                     [("2.8L Diesel", "1GD-FTV", "diesel", 2755),
                      ("2.4L Turbo Hybrid", "T24A-FTS", "hybrid", 2393)]),
                ],
            },
            "Land Cruiser": {
                "aliases": ["LC", "Land Cruiser V8", "LC200", "LC300"],
                "gens": [
                    ("J100", 1998, 2007, "SUV", ["GX", "VX"],
                     [("4.2L Diesel", "1HD-FTE", "diesel", 4164),
                      ("4.7L Petrol", "2UZ-FE", "petrol", 4664)]),
                    ("J200", 2007, 2021, "SUV", ["GX", "VX", "ZX"],
                     [("4.5L V8 Diesel", "1VD-FTV", "diesel", 4461),
                      ("4.6L Petrol", "1UR-FE", "petrol", 4608)]),
                    ("J300", 2021, OPEN, "SUV", ["GX", "VX", "ZX", "GR Sport"],
                     [("3.3L V6 Diesel", "F33A-FTV", "diesel", 3346),
                      ("3.5L V6 Twin Turbo", "V35A-FTS", "petrol", 3445)]),
                ],
            },
            "Land Cruiser 70": {
                "aliases": ["LC70", "Land Cruiser Pickup"],
                "gens": [
                    ("J70", 1999, OPEN, "Pickup", ["Single Cab", "Double Cab", "Troop Carrier"],
                     [("4.2L Diesel", "1HZ", "diesel", 4164),
                      ("4.5L V8 Diesel", "1VD-FTV", "diesel", 4461),
                      ("2.8L Diesel", "1GD-FTV", "diesel", 2755)]),
                ],
            },
            "Harrier": {
                "aliases": ["Harrier"],
                "gens": [
                    ("XU30", 2003, 2013, "SUV", ["240G", "300G"],
                     [("2.4L Petrol", "2AZ-FE", "petrol", 2362),
                      ("3.0L Petrol", "1MZ-FE", "petrol", 2994)]),
                    ("XU60", 2013, 2020, "SUV", ["Elegance", "Premium", "Grand"],
                     [("2.0L Petrol", "3ZR-FAE", "petrol", 1986),
                      ("2.5L Hybrid", "2AR-FXE", "hybrid", 2494)]),
                    ("XU80", 2020, OPEN, "SUV", ["S", "G", "Z"],
                     [("2.0L Petrol", "M20A-FKS", "petrol", 1987),
                      ("2.5L Hybrid", "A25A-FXS", "hybrid", 2487)]),
                ],
            },
            "Hilux": {
                "aliases": ["Hilux Vigo", "Hilux Revo"],
                "gens": [
                    ("AN10 Vigo", 2004, 2015, "Pickup", ["Single Cab", "Double Cab"],
                     [("2.5L Diesel", "2KD-FTV", "diesel", 2494),
                      ("3.0L Diesel", "1KD-FTV", "diesel", 2982)]),
                    ("GUN125 Revo", 2015, OPEN, "Pickup", ["Single Cab", "Double Cab", "GR Sport"],
                     [("2.4L Diesel", "2GD-FTV", "diesel", 2393),
                      ("2.8L Diesel", "1GD-FTV", "diesel", 2755)]),
                ],
            },
            "Fortuner": {
                "aliases": ["Fortuner"],
                "gens": [
                    ("AN50", 2005, 2015, "SUV", ["G", "V"],
                     [("2.5L Diesel", "2KD-FTV", "diesel", 2494),
                      ("3.0L Diesel", "1KD-FTV", "diesel", 2982)]),
                    ("AN160", 2015, OPEN, "SUV", ["G", "V", "GR Sport"],
                     [("2.4L Diesel", "2GD-FTV", "diesel", 2393),
                      ("2.8L Diesel", "1GD-FTV", "diesel", 2755)]),
                ],
            },
            "RAV4": {
                "aliases": ["RAV4", "RAV 4"],
                "gens": [
                    ("XA30", 2005, 2012, "SUV", ["Standard", "Sport"],
                     [("2.4L Petrol", "2AZ-FE", "petrol", 2362)]),
                    ("XA40", 2012, 2018, "SUV", ["Standard", "Premium"],
                     [("2.0L Petrol", "3ZR-FAE", "petrol", 1986)]),
                    ("XA50", 2018, OPEN, "SUV", ["X", "G", "Adventure"],
                     [("2.0L Petrol", "M20A-FKS", "petrol", 1987),
                      ("2.5L Hybrid", "A25A-FXS", "hybrid", 2487)]),
                ],
            },
            "Vitz": {
                "aliases": ["Vitz", "Yaris"],
                "gens": [
                    ("XP90", 2005, 2010, "Hatchback", ["F", "RS"],
                     [("1.0L Petrol", "1KR-FE", "petrol", 996),
                      ("1.3L Petrol", "2SZ-FE", "petrol", 1296)]),
                    ("XP130", 2010, 2020, "Hatchback", ["F", "Jewela", "RS"],
                     [("1.0L Petrol", "1KR-FE", "petrol", 996),
                      ("1.3L Petrol", "1NR-FE", "petrol", 1329)]),
                ],
            },
            "Aqua": {
                "aliases": ["Aqua", "Prius C"],
                "gens": [
                    ("NHP10", 2011, 2021, "Hatchback", ["S", "G"],
                     [("1.5L Hybrid", "1NZ-FXE", "hybrid", 1496)]),
                    ("XP210", 2021, OPEN, "Hatchback", ["S", "G", "Z"],
                     [("1.5L Hybrid", "M15A-FXE", "hybrid", 1490)]),
                ],
            },
            "Corolla Fielder": {
                "aliases": ["Fielder"],
                "gens": [
                    ("E140", 2006, 2012, "Wagon", ["X", "S"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496),
                      ("1.8L Petrol", "2ZR-FE", "petrol", 1797)]),
                    ("E160", 2012, OPEN, "Wagon", ["X", "G", "WxB"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496),
                      ("1.5L Hybrid", "1NZ-FXE", "hybrid", 1496)]),
                ],
            },
            "Corolla Axio": {
                "aliases": ["Axio"],
                "gens": [
                    ("E140", 2006, 2012, "Sedan", ["X", "G"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496)]),
                    ("E160", 2012, OPEN, "Sedan", ["X", "G", "WxB"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496),
                      ("1.5L Hybrid", "1NZ-FXE", "hybrid", 1496)]),
                ],
            },
            "Premio": {
                "aliases": ["Premio"],
                "gens": [
                    ("T240", 2001, 2007, "Sedan", ["F", "X"],
                     [("1.8L Petrol", "1ZZ-FE", "petrol", 1794),
                      ("2.0L Petrol", "1AZ-FSE", "petrol", 1998)]),
                    ("T260", 2007, 2021, "Sedan", ["F", "G", "EX"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496),
                      ("1.8L Petrol", "2ZR-FAE", "petrol", 1797),
                      ("2.0L Petrol", "3ZR-FAE", "petrol", 1986)]),
                ],
            },
            "Allion": {
                "aliases": ["Allion"],
                "gens": [
                    ("T240", 2001, 2007, "Sedan", ["A15", "A18"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496),
                      ("1.8L Petrol", "1ZZ-FE", "petrol", 1794)]),
                    ("T260", 2007, 2021, "Sedan", ["A15", "A18", "A20"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496),
                      ("1.8L Petrol", "2ZR-FAE", "petrol", 1797)]),
                ],
            },
            "Probox": {
                "aliases": ["Probox"],
                "gens": [
                    ("XP50", 2002, 2014, "Van", ["DX", "GL"],
                     [("1.3L Petrol", "2NZ-FE", "petrol", 1298),
                      ("1.5L Petrol", "1NZ-FE", "petrol", 1496)]),
                    ("XP160", 2014, OPEN, "Van", ["DX", "GL", "F"],
                     [("1.3L Petrol", "1NR-FE", "petrol", 1329),
                      ("1.5L Petrol", "1NZ-FE", "petrol", 1496),
                      ("1.5L Hybrid", "1NZ-FXE", "hybrid", 1496)]),
                ],
            },
            "Succeed": {
                "aliases": ["Succeed"],
                "gens": [
                    ("XP50", 2002, 2014, "Van", ["U", "UL"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496)]),
                    ("XP160", 2014, 2020, "Van", ["U", "UL", "TX"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496)]),
                ],
            },
            "Noah": {
                "aliases": ["Noah", "Voxy"],
                "gens": [
                    ("R70", 2007, 2014, "Van", ["X", "G"],
                     [("2.0L Petrol", "3ZR-FE", "petrol", 1986)]),
                    ("R80", 2014, 2022, "Van", ["X", "G", "Si"],
                     [("2.0L Petrol", "3ZR-FAE", "petrol", 1986),
                      ("1.8L Hybrid", "2ZR-FXE", "hybrid", 1797)]),
                    ("R90", 2022, OPEN, "Van", ["X", "G", "S-Z"],
                     [("2.0L Petrol", "M20A-FKS", "petrol", 1987),
                      ("1.8L Hybrid", "2ZR-FXE", "hybrid", 1797)]),
                ],
            },
            "Alphard": {
                "aliases": ["Alphard", "Vellfire"],
                "gens": [
                    ("AH20", 2008, 2015, "Van", ["240", "350"],
                     [("2.4L Petrol", "2AZ-FE", "petrol", 2362),
                      ("3.5L Petrol", "2GR-FE", "petrol", 3456)]),
                    ("AH30", 2015, 2023, "Van", ["X", "G", "Executive Lounge"],
                     [("2.5L Petrol", "2AR-FE", "petrol", 2493),
                      ("2.5L Hybrid", "2AR-FXE", "hybrid", 2494)]),
                ],
            },
            "Sienta": {
                "aliases": ["Sienta"],
                "gens": [
                    ("XP170", 2015, 2022, "Van", ["X", "G"],
                     [("1.5L Petrol", "2NR-FKE", "petrol", 1496),
                      ("1.5L Hybrid", "1NZ-FXE", "hybrid", 1496)]),
                ],
            },
            "Wish": {
                "aliases": ["Wish"],
                "gens": [
                    ("AE10", 2003, 2009, "Wagon", ["X", "G"],
                     [("1.8L Petrol", "1ZZ-FE", "petrol", 1794)]),
                    ("AE20", 2009, 2017, "Wagon", ["X", "S"],
                     [("1.8L Petrol", "2ZR-FAE", "petrol", 1797),
                      ("2.0L Petrol", "3ZR-FAE", "petrol", 1986)]),
                ],
            },
            "Passo": {
                "aliases": ["Passo"],
                "gens": [
                    ("AC10", 2004, 2010, "Hatchback", ["X", "G"],
                     [("1.0L Petrol", "1KR-FE", "petrol", 996)]),
                    ("AC30", 2010, 2016, "Hatchback", ["X", "G", "Hana"],
                     [("1.0L Petrol", "1KR-FE", "petrol", 996),
                      ("1.3L Petrol", "1NR-FE", "petrol", 1329)]),
                    ("AC700", 2016, 2023, "Hatchback", ["X", "Moda"],
                     [("1.0L Petrol", "1KR-FE", "petrol", 996)]),
                ],
            },
            "Camry": {
                "aliases": ["Camry"],
                "gens": [
                    ("XV40", 2006, 2011, "Sedan", ["G", "Prestige"],
                     [("2.4L Petrol", "2AZ-FE", "petrol", 2362)]),
                    ("XV50", 2011, 2017, "Sedan", ["G", "Prestige"],
                     [("2.5L Petrol", "2AR-FE", "petrol", 2493),
                      ("2.5L Hybrid", "2AR-FXE", "hybrid", 2494)]),
                    ("XV70", 2017, OPEN, "Sedan", ["G", "Sport", "Hybrid"],
                     [("2.5L Petrol", "A25A-FKS", "petrol", 2487),
                      ("2.5L Hybrid", "A25A-FXS", "hybrid", 2487)]),
                ],
            },
            "Mark X": {
                "aliases": ["Mark X"],
                "gens": [
                    ("X120", 2004, 2009, "Sedan", ["250G", "300G"],
                     [("2.5L Petrol", "4GR-FSE", "petrol", 2499),
                      ("3.0L Petrol", "3GR-FSE", "petrol", 2994)]),
                    ("X130", 2009, 2019, "Sedan", ["250G", "350S"],
                     [("2.5L Petrol", "4GR-FSE", "petrol", 2499),
                      ("3.5L Petrol", "2GR-FSE", "petrol", 3456)]),
                ],
            },
            "Crown": {
                "aliases": ["Crown"],
                "gens": [
                    ("S200", 2008, 2012, "Sedan", ["Royal", "Athlete"],
                     [("2.5L Petrol", "4GR-FSE", "petrol", 2499),
                      ("3.5L Hybrid", "2GR-FSE", "hybrid", 3456)]),
                    ("S210", 2012, 2018, "Sedan", ["Royal", "Athlete"],
                     [("2.5L Hybrid", "2AR-FSE", "hybrid", 2493)]),
                ],
            },
            "C-HR": {
                "aliases": ["CHR", "C-HR"],
                "gens": [
                    ("AX10", 2016, 2023, "SUV", ["S", "G"],
                     [("1.2L Turbo", "8NR-FTS", "petrol", 1196),
                      ("1.8L Hybrid", "2ZR-FXE", "hybrid", 1797)]),
                ],
            },
            "Corolla Cross": {
                "aliases": ["Corolla Cross"],
                "gens": [
                    ("XG10", 2020, OPEN, "SUV", ["G", "S", "Z"],
                     [("1.8L Petrol", "2ZR-FE", "petrol", 1797),
                      ("1.8L Hybrid", "2ZR-FXE", "hybrid", 1797)]),
                ],
            },
            "Rush": {
                "aliases": ["Rush"],
                "gens": [
                    ("J200", 2006, 2016, "SUV", ["G", "X"],
                     [("1.5L Petrol", "3SZ-VE", "petrol", 1495)]),
                    ("F800", 2017, OPEN, "SUV", ["G", "S"],
                     [("1.5L Petrol", "2NR-VE", "petrol", 1496)]),
                ],
            },
            "Vanguard": {
                "aliases": ["Vanguard"],
                "gens": [
                    ("XA33", 2007, 2013, "SUV", ["240S", "350S"],
                     [("2.4L Petrol", "2AZ-FE", "petrol", 2362),
                      ("3.5L Petrol", "2GR-FE", "petrol", 3456)]),
                ],
            },
            "Ractis": {
                "aliases": ["Ractis"],
                "gens": [
                    ("XP100", 2005, 2010, "Hatchback", ["X", "G"],
                     [("1.3L Petrol", "2SZ-FE", "petrol", 1296),
                      ("1.5L Petrol", "1NZ-FE", "petrol", 1496)]),
                    ("XP120", 2010, 2016, "Hatchback", ["X", "G", "S"],
                     [("1.3L Petrol", "1NR-FE", "petrol", 1329),
                      ("1.5L Petrol", "1NZ-FE", "petrol", 1496)]),
                ],
            },
            "Belta": {
                "aliases": ["Belta"],
                "gens": [
                    ("XP90", 2005, 2012, "Sedan", ["X", "G"],
                     [("1.0L Petrol", "1KR-FE", "petrol", 996),
                      ("1.3L Petrol", "2SZ-FE", "petrol", 1296)]),
                ],
            },
            "Auris": {
                "aliases": ["Auris"],
                "gens": [
                    ("E150", 2006, 2012, "Hatchback", ["150X", "180G"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496),
                      ("1.8L Petrol", "2ZR-FE", "petrol", 1797)]),
                    ("E180", 2012, 2018, "Hatchback", ["150X", "Hybrid"],
                     [("1.5L Petrol", "1NZ-FE", "petrol", 1496),
                      ("1.8L Hybrid", "2ZR-FXE", "hybrid", 1797)]),
                ],
            },
            "Hiace": {
                "aliases": ["Hiace", "Matatu"],
                "gens": [
                    ("H200", 2004, 2019, "Van", ["DX", "GL", "Commuter"],
                     [("2.5L Diesel", "2KD-FTV", "diesel", 2494),
                      ("3.0L Diesel", "1KD-FTV", "diesel", 2982)]),
                    ("H300", 2019, OPEN, "Van", ["DX", "GL", "Commuter"],
                     [("2.8L Diesel", "1GD-FTV", "diesel", 2755)]),
                ],
            },
            "Coaster": {
                "aliases": ["Coaster"],
                "gens": [
                    ("B40", 1993, 2016, "Bus", ["Standard", "Deluxe"],
                     [("4.2L Diesel", "1HZ", "diesel", 4164)]),
                    ("B60", 2016, OPEN, "Bus", ["Standard", "Deluxe"],
                     [("4.0L Diesel", "N04C-UP", "diesel", 4009)]),
                ],
            },
            "Dyna": {
                "aliases": ["Dyna"],
                "gens": [
                    ("Y200", 2001, OPEN, "Truck", ["Standard Cab"],
                     [("4.0L Diesel", "N04C", "diesel", 4009),
                      ("3.0L Diesel", "1KD-FTV", "diesel", 2982)]),
                ],
            },
            "Townace": {
                "aliases": ["Townace", "Liteace"],
                "gens": [
                    ("S400", 2008, OPEN, "Van", ["DX", "GL"],
                     [("1.5L Petrol", "3SZ-VE", "petrol", 1495)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------------ NISSAN
    "Nissan": {
        "popularity": 90,
        "models": {
            "Note": {
                "aliases": ["Note"],
                "gens": [
                    ("E11", 2004, 2012, "Hatchback", ["S", "Rider"],
                     [("1.5L Petrol", "HR15DE", "petrol", 1498)]),
                    ("E12", 2012, 2020, "Hatchback", ["S", "Medalist", "Nismo"],
                     [("1.2L Petrol", "HR12DDR", "petrol", 1198),
                      ("1.2L e-POWER", "HR12DE-EM57", "hybrid", 1198)]),
                    ("E13", 2020, OPEN, "Hatchback", ["S", "X"],
                     [("1.2L e-POWER", "HR12DE-EM47", "hybrid", 1198)]),
                ],
            },
            "March": {
                "aliases": ["March", "Micra"],
                "gens": [
                    ("K12", 2002, 2010, "Hatchback", ["12S", "12SR"],
                     [("1.2L Petrol", "CR12DE", "petrol", 1240)]),
                    ("K13", 2010, 2022, "Hatchback", ["S", "G"],
                     [("1.2L Petrol", "HR12DE", "petrol", 1198)]),
                ],
            },
            "X-Trail": {
                "aliases": ["Xtrail", "X Trail"],
                "gens": [
                    ("T30", 2000, 2007, "SUV", ["S", "X"],
                     [("2.0L Petrol", "QR20DE", "petrol", 1998)]),
                    ("T31", 2007, 2013, "SUV", ["20S", "20X"],
                     [("2.0L Petrol", "MR20DE", "petrol", 1997)]),
                    ("T32", 2013, 2022, "SUV", ["20S", "20X", "Mode Premier"],
                     [("2.0L Petrol", "MR20DD", "petrol", 1997),
                      ("2.0L Hybrid", "MR20DD-HM34", "hybrid", 1997)]),
                ],
            },
            "Qashqai": {
                "aliases": ["Dualis", "Qashqai"],
                "gens": [
                    ("J10", 2006, 2013, "SUV", ["20S", "20G"],
                     [("2.0L Petrol", "MR20DE", "petrol", 1997)]),
                    ("J11", 2013, 2021, "SUV", ["S", "X"],
                     [("2.0L Petrol", "MR20DD", "petrol", 1997)]),
                ],
            },
            "Juke": {
                "aliases": ["Juke"],
                "gens": [
                    ("F15", 2010, 2019, "SUV", ["15RX", "16GT"],
                     [("1.5L Petrol", "HR15DE", "petrol", 1498),
                      ("1.6L Turbo", "MR16DDT", "petrol", 1618)]),
                ],
            },
            "Sylphy": {
                "aliases": ["Sylphy", "Bluebird Sylphy"],
                "gens": [
                    ("G11", 2005, 2012, "Sedan", ["15S", "20M"],
                     [("1.5L Petrol", "HR15DE", "petrol", 1498),
                      ("2.0L Petrol", "MR20DE", "petrol", 1997)]),
                    ("B17", 2012, 2020, "Sedan", ["S", "X", "G"],
                     [("1.8L Petrol", "MRA8DE", "petrol", 1798)]),
                ],
            },
            "Teana": {
                "aliases": ["Teana"],
                "gens": [
                    ("J32", 2008, 2014, "Sedan", ["250XL", "250XV"],
                     [("2.5L Petrol", "VQ25DE", "petrol", 2496)]),
                    ("L33", 2014, 2020, "Sedan", ["XL", "XV"],
                     [("2.5L Petrol", "QR25DE", "petrol", 2488)]),
                ],
            },
            "Serena": {
                "aliases": ["Serena"],
                "gens": [
                    ("C25", 2005, 2010, "Van", ["20S", "20G"],
                     [("2.0L Petrol", "MR20DE", "petrol", 1997)]),
                    ("C26", 2010, 2016, "Van", ["20S", "Highway Star"],
                     [("2.0L Petrol", "MR20DD", "petrol", 1997)]),
                    ("C27", 2016, 2022, "Van", ["X", "Highway Star", "e-POWER"],
                     [("2.0L Petrol", "MR20DD", "petrol", 1997),
                      ("1.2L e-POWER", "HR12DE-EM57", "hybrid", 1198)]),
                ],
            },
            "Navara": {
                "aliases": ["Navara", "NP300"],
                "gens": [
                    ("D40", 2004, 2015, "Pickup", ["SE", "LE"],
                     [("2.5L Diesel", "YD25DDTi", "diesel", 2488)]),
                    ("D23", 2014, OPEN, "Pickup", ["SE", "LE", "Pro-4X"],
                     [("2.5L Diesel", "YD25DDTi", "diesel", 2488),
                      ("2.3L Twin Turbo Diesel", "YS23DDTT", "diesel", 2298)]),
                ],
            },
            "Hardbody": {
                "aliases": ["Hardbody", "D22"],
                "gens": [
                    ("D22", 1997, 2015, "Pickup", ["Single Cab", "Double Cab"],
                     [("2.4L Petrol", "KA24DE", "petrol", 2389),
                      ("2.7L Diesel", "TD27", "diesel", 2663)]),
                ],
            },
            "Patrol": {
                "aliases": ["Patrol"],
                "gens": [
                    ("Y61", 1997, 2016, "SUV", ["GL", "GRX"],
                     [("4.2L Diesel", "TD42", "diesel", 4169),
                      ("4.8L Petrol", "TB48DE", "petrol", 4759)]),
                    ("Y62", 2010, OPEN, "SUV", ["XE", "SE", "LE"],
                     [("5.6L Petrol", "VK56VD", "petrol", 5552)]),
                ],
            },
            "Wingroad": {
                "aliases": ["Wingroad"],
                "gens": [
                    ("Y12", 2005, 2018, "Wagon", ["15M", "15RX"],
                     [("1.5L Petrol", "HR15DE", "petrol", 1498)]),
                ],
            },
            "AD Van": {
                "aliases": ["AD", "AD Van"],
                "gens": [
                    ("Y12", 2006, OPEN, "Van", ["DX", "VE"],
                     [("1.5L Petrol", "HR15DE", "petrol", 1498)]),
                ],
            },
            "Caravan": {
                "aliases": ["Caravan", "Urvan", "NV350"],
                "gens": [
                    ("E25", 2001, 2012, "Van", ["DX", "GX"],
                     [("3.0L Diesel", "ZD30DD", "diesel", 2953)]),
                    ("E26", 2012, OPEN, "Van", ["DX", "Premium GX"],
                     [("2.5L Diesel", "YD25DDTi", "diesel", 2488)]),
                ],
            },
            "Leaf": {
                "aliases": ["Leaf"],
                "gens": [
                    ("ZE0", 2010, 2017, "Hatchback", ["S", "X", "G"],
                     [("EV 24-30kWh", "EM57", "electric", None)]),
                    ("ZE1", 2017, OPEN, "Hatchback", ["S", "X", "e+"],
                     [("EV 40-62kWh", "EM57", "electric", None)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------------ MAZDA
    "Mazda": {
        "popularity": 85,
        "models": {
            "Demio": {
                "aliases": ["Demio", "Mazda2"],
                "gens": [
                    ("DE", 2007, 2014, "Hatchback", ["13C", "15C", "Sport"],
                     [("1.3L Petrol", "ZJ-VE", "petrol", 1349),
                      ("1.5L Petrol", "ZY-VE", "petrol", 1498)]),
                    ("DJ", 2014, 2023, "Hatchback", ["13C", "15C", "XD"],
                     [("1.3L Petrol", "P3-VPS", "petrol", 1298),
                      ("1.5L Diesel", "S5-DPTS", "diesel", 1498)]),
                ],
            },
            "Axela": {
                "aliases": ["Axela", "Mazda3"],
                "gens": [
                    ("BK", 2003, 2009, "Sedan", ["15C", "20S"],
                     [("1.5L Petrol", "ZY-VE", "petrol", 1498),
                      ("2.0L Petrol", "LF-DE", "petrol", 1999)]),
                    ("BL", 2009, 2013, "Sedan", ["15C", "20S"],
                     [("1.5L Petrol", "ZY-VE", "petrol", 1498),
                      ("2.0L Petrol", "LF-VDS", "petrol", 1999)]),
                    ("BM", 2013, 2019, "Sedan", ["15S", "20S", "XD"],
                     [("1.5L Petrol", "P5-VPS", "petrol", 1496),
                      ("2.2L Diesel", "SH-VPTS", "diesel", 2191)]),
                ],
            },
            "Atenza": {
                "aliases": ["Atenza", "Mazda6"],
                "gens": [
                    ("GH", 2007, 2012, "Sedan", ["20S", "25S"],
                     [("2.0L Petrol", "LF-VE", "petrol", 1999),
                      ("2.5L Petrol", "L5-VE", "petrol", 2488)]),
                    ("GJ", 2012, OPEN, "Sedan", ["20S", "25S", "XD"],
                     [("2.0L Petrol", "PE-VPR", "petrol", 1997),
                      ("2.2L Diesel", "SH-VPTR", "diesel", 2191)]),
                ],
            },
            "CX-3": {
                "aliases": ["CX3"],
                "gens": [
                    ("DK", 2015, OPEN, "SUV", ["20S", "XD"],
                     [("2.0L Petrol", "PE-VPS", "petrol", 1998),
                      ("1.8L Diesel", "S8-DPTS", "diesel", 1756)]),
                ],
            },
            "CX-5": {
                "aliases": ["CX5"],
                "gens": [
                    ("KE", 2012, 2017, "SUV", ["20S", "25S", "XD"],
                     [("2.0L Petrol", "PE-VPS", "petrol", 1998),
                      ("2.2L Diesel", "SH-VPTS", "diesel", 2191)]),
                    ("KF", 2017, OPEN, "SUV", ["20S", "25S", "XD"],
                     [("2.0L Petrol", "PE-VPS", "petrol", 1998),
                      ("2.5L Petrol", "PY-VPS", "petrol", 2488),
                      ("2.2L Diesel", "SH-VPTS", "diesel", 2191)]),
                ],
            },
            "CX-30": {
                "aliases": ["CX30"],
                "gens": [
                    ("DM", 2019, OPEN, "SUV", ["20S", "XD"],
                     [("2.0L Petrol", "PE-VPS", "petrol", 1998),
                      ("1.8L Diesel", "S8-DPTS", "diesel", 1756)]),
                ],
            },
            "Premacy": {
                "aliases": ["Premacy", "Mazda5"],
                "gens": [
                    ("CR", 2005, 2010, "Van", ["20S", "20Z"],
                     [("2.0L Petrol", "LF-DE", "petrol", 1999)]),
                    ("CW", 2010, 2018, "Van", ["20S", "20E"],
                     [("2.0L Petrol", "LF-VDS", "petrol", 1999)]),
                ],
            },
            "Bongo": {
                "aliases": ["Bongo"],
                "gens": [
                    ("SK", 1999, 2020, "Van", ["DX", "GL"],
                     [("1.8L Petrol", "F8", "petrol", 1789),
                      ("2.0L Diesel", "RF", "diesel", 1998)]),
                ],
            },
            "BT-50": {
                "aliases": ["BT50"],
                "gens": [
                    ("UP", 2011, 2020, "Pickup", ["Single Cab", "Double Cab"],
                     [("2.2L Diesel", "P4-AT", "diesel", 2198),
                      ("3.2L Diesel", "P5-AT", "diesel", 3198)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------------ HONDA
    "Honda": {
        "popularity": 80,
        "models": {
            "Fit": {
                "aliases": ["Fit", "Jazz"],
                "gens": [
                    ("GD", 2001, 2008, "Hatchback", ["A", "W"],
                     [("1.3L Petrol", "L13A", "petrol", 1339)]),
                    ("GE", 2007, 2014, "Hatchback", ["G", "RS"],
                     [("1.3L Petrol", "L13A", "petrol", 1339),
                      ("1.5L Petrol", "L15A", "petrol", 1497)]),
                    ("GK", 2013, 2020, "Hatchback", ["13G", "15X", "Hybrid"],
                     [("1.3L Petrol", "L13B", "petrol", 1317),
                      ("1.5L Hybrid", "LEB", "hybrid", 1496)]),
                    ("GR", 2020, OPEN, "Hatchback", ["Basic", "Home", "e:HEV"],
                     [("1.3L Petrol", "L13B", "petrol", 1317),
                      ("1.5L e:HEV", "LEB-H5", "hybrid", 1496)]),
                ],
            },
            "Vezel": {
                "aliases": ["Vezel", "HR-V"],
                "gens": [
                    ("RU", 2013, 2021, "SUV", ["G", "X", "Hybrid Z"],
                     [("1.5L Petrol", "L15B", "petrol", 1496),
                      ("1.5L Hybrid", "LEB", "hybrid", 1496)]),
                    ("RV", 2021, OPEN, "SUV", ["G", "e:HEV X", "e:HEV Z"],
                     [("1.5L Petrol", "L15Z", "petrol", 1496),
                      ("1.5L e:HEV", "LEC-H5", "hybrid", 1496)]),
                ],
            },
            "CR-V": {
                "aliases": ["CRV"],
                "gens": [
                    ("RE", 2006, 2011, "SUV", ["ZL", "ZX"],
                     [("2.4L Petrol", "K24A", "petrol", 2354)]),
                    ("RM", 2011, 2016, "SUV", ["20G", "24G"],
                     [("2.0L Petrol", "R20A", "petrol", 1997),
                      ("2.4L Petrol", "K24A", "petrol", 2354)]),
                    ("RW", 2016, 2022, "SUV", ["EX", "Hybrid EX"],
                     [("1.5L Turbo", "L15B7", "petrol", 1498),
                      ("2.0L Hybrid", "LFA", "hybrid", 1993)]),
                ],
            },
            "Civic": {
                "aliases": ["Civic"],
                "gens": [
                    ("FD", 2005, 2011, "Sedan", ["1.8G", "2.0S"],
                     [("1.8L Petrol", "R18A", "petrol", 1799)]),
                    ("FC", 2015, 2021, "Sedan", ["EX", "RS"],
                     [("1.5L Turbo", "L15B7", "petrol", 1498)]),
                ],
            },
            "Accord": {
                "aliases": ["Accord"],
                "gens": [
                    ("CL", 2002, 2008, "Sedan", ["20A", "24T"],
                     [("2.0L Petrol", "K20A", "petrol", 1998),
                      ("2.4L Petrol", "K24A", "petrol", 2354)]),
                    ("CR", 2013, 2020, "Sedan", ["EX", "Hybrid"],
                     [("2.0L Hybrid", "LFA", "hybrid", 1993)]),
                ],
            },
            "Stream": {
                "aliases": ["Stream"],
                "gens": [
                    ("RN6", 2006, 2014, "Wagon", ["X", "RSZ"],
                     [("1.8L Petrol", "R18A", "petrol", 1799),
                      ("2.0L Petrol", "R20A", "petrol", 1997)]),
                ],
            },
            "Freed": {
                "aliases": ["Freed"],
                "gens": [
                    ("GB3", 2008, 2016, "Van", ["G", "Flex"],
                     [("1.5L Petrol", "L15A", "petrol", 1497)]),
                    ("GB5", 2016, OPEN, "Van", ["G", "Hybrid G"],
                     [("1.5L Petrol", "L15B", "petrol", 1496),
                      ("1.5L Hybrid", "LEB", "hybrid", 1496)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------------ SUBARU
    "Subaru": {
        "popularity": 78,
        "models": {
            "Impreza": {
                "aliases": ["Impreza", "WRX"],
                "gens": [
                    ("GD", 2000, 2007, "Sedan", ["1.5i", "WRX", "STI"],
                     [("1.5L Petrol", "EJ15", "petrol", 1493),
                      ("2.0L Turbo", "EJ20", "petrol", 1994)]),
                    ("GH", 2007, 2011, "Hatchback", ["1.5i", "S-GT"],
                     [("1.5L Petrol", "EL15", "petrol", 1498),
                      ("2.0L Turbo", "EJ20", "petrol", 1994)]),
                    ("GJ", 2011, 2016, "Sedan", ["1.6i", "2.0i"],
                     [("1.6L Petrol", "FB16", "petrol", 1599),
                      ("2.0L Petrol", "FB20", "petrol", 1995)]),
                    ("GT", 2016, 2023, "Hatchback", ["1.6i-L", "2.0i-S"],
                     [("1.6L Petrol", "FB16", "petrol", 1599),
                      ("2.0L Petrol", "FB20", "petrol", 1995)]),
                ],
            },
            "Legacy": {
                "aliases": ["Legacy", "B4"],
                "gens": [
                    ("BL", 2003, 2009, "Sedan", ["2.0i", "2.0GT"],
                     [("2.0L Petrol", "EJ20", "petrol", 1994),
                      ("2.0L Turbo", "EJ20X", "petrol", 1994)]),
                    ("BM", 2009, 2014, "Sedan", ["2.5i", "2.5GT"],
                     [("2.5L Petrol", "EJ25", "petrol", 2457)]),
                    ("BN", 2014, 2020, "Sedan", ["B4 Limited"],
                     [("2.5L Petrol", "FB25", "petrol", 2498)]),
                ],
            },
            "Forester": {
                "aliases": ["Forester"],
                "gens": [
                    ("SG", 2002, 2008, "SUV", ["X", "XT"],
                     [("2.0L Petrol", "EJ20", "petrol", 1994),
                      ("2.0L Turbo", "EJ20", "petrol", 1994)]),
                    ("SH", 2008, 2012, "SUV", ["X", "XT"],
                     [("2.0L Petrol", "EJ20", "petrol", 1994),
                      ("2.0L Turbo", "EJ20", "petrol", 1994)]),
                    ("SJ", 2012, 2018, "SUV", ["2.0i", "XT"],
                     [("2.0L Petrol", "FB20", "petrol", 1995),
                      ("2.0L Turbo", "FA20", "petrol", 1998)]),
                    ("SK", 2018, OPEN, "SUV", ["Touring", "X-Edition", "e-BOXER"],
                     [("2.5L Petrol", "FB25", "petrol", 2498),
                      ("2.0L e-BOXER", "FB20-MHEV", "hybrid", 1995)]),
                ],
            },
            "Outback": {
                "aliases": ["Outback"],
                "gens": [
                    ("BR", 2009, 2014, "Wagon", ["2.5i", "3.6R"],
                     [("2.5L Petrol", "EJ25", "petrol", 2457)]),
                    ("BS", 2014, 2020, "Wagon", ["Limited"],
                     [("2.5L Petrol", "FB25", "petrol", 2498)]),
                ],
            },
            "XV": {
                "aliases": ["XV", "Crosstrek"],
                "gens": [
                    ("GP", 2012, 2017, "SUV", ["2.0i", "2.0i-L"],
                     [("2.0L Petrol", "FB20", "petrol", 1995)]),
                    ("GT", 2017, 2023, "SUV", ["2.0i-L", "e-BOXER"],
                     [("2.0L Petrol", "FB20", "petrol", 1995),
                      ("2.0L e-BOXER", "FB20-MHEV", "hybrid", 1995)]),
                ],
            },
            "Levorg": {
                "aliases": ["Levorg"],
                "gens": [
                    ("VM", 2014, 2020, "Wagon", ["1.6GT", "2.0GT-S"],
                     [("1.6L Turbo", "FB16-DIT", "petrol", 1599),
                      ("2.0L Turbo", "FA20-DIT", "petrol", 1998)]),
                ],
            },
        },
    },
    # -------------------------------------------------------------- MITSUBISHI
    "Mitsubishi": {
        "popularity": 75,
        "models": {
            "Lancer": {
                "aliases": ["Lancer", "Lancer EX"],
                "gens": [
                    ("CS", 2000, 2009, "Sedan", ["GLX", "Evolution"],
                     [("1.6L Petrol", "4G18", "petrol", 1584),
                      ("2.0L Turbo", "4G63T", "petrol", 1997)]),
                    ("CY", 2007, 2017, "Sedan", ["GLX", "GT"],
                     [("1.8L Petrol", "4B10", "petrol", 1798),
                      ("2.0L Petrol", "4B11", "petrol", 1998)]),
                ],
            },
            "Outlander": {
                "aliases": ["Outlander", "Airtrek"],
                "gens": [
                    ("CW", 2005, 2012, "SUV", ["20G", "24G"],
                     [("2.4L Petrol", "4B12", "petrol", 2360)]),
                    ("GF", 2012, 2021, "SUV", ["20G", "24G", "PHEV"],
                     [("2.0L Petrol", "4J11", "petrol", 1998),
                      ("2.0L PHEV", "4B11-PHEV", "hybrid", 1998)]),
                ],
            },
            "RVR": {
                "aliases": ["RVR", "ASX"],
                "gens": [
                    ("GA", 2010, OPEN, "SUV", ["M", "G"],
                     [("1.8L Petrol", "4B10", "petrol", 1798)]),
                ],
            },
            "Pajero": {
                "aliases": ["Pajero", "Montero"],
                "gens": [
                    ("V60", 1999, 2006, "SUV", ["GLS", "Exceed"],
                     [("3.2L Diesel", "4M41", "diesel", 3200)]),
                    ("V80", 2006, 2021, "SUV", ["GLS", "Exceed"],
                     [("3.2L Diesel", "4M41", "diesel", 3200),
                      ("3.8L Petrol", "6G75", "petrol", 3828)]),
                ],
            },
            "Pajero Sport": {
                "aliases": ["Pajero Sport", "Challenger"],
                "gens": [
                    ("QE", 2015, OPEN, "SUV", ["GLX", "GLS"],
                     [("2.4L Diesel", "4N15", "diesel", 2442)]),
                ],
            },
            "L200": {
                "aliases": ["L200", "Triton"],
                "gens": [
                    ("KB", 2005, 2015, "Pickup", ["Single Cab", "Double Cab"],
                     [("2.5L Diesel", "4D56", "diesel", 2477)]),
                    ("KL", 2015, OPEN, "Pickup", ["Single Cab", "Double Cab"],
                     [("2.4L Diesel", "4N15", "diesel", 2442)]),
                ],
            },
            "Canter": {
                "aliases": ["Canter", "Fuso Canter"],
                "gens": [
                    ("FE7", 2002, 2010, "Truck", ["Standard", "Wide Cab"],
                     [("4.9L Diesel", "4M50", "diesel", 4899)]),
                    ("FE8", 2010, OPEN, "Truck", ["Standard", "Wide Cab"],
                     [("3.0L Diesel", "4P10", "diesel", 2998)]),
                ],
            },
            "Fuso Fighter": {
                "aliases": ["Fighter", "Fuso"],
                "gens": [
                    ("FK", 2002, OPEN, "Truck", ["Standard"],
                     [("7.5L Diesel", "6M60", "diesel", 7545)]),
                ],
            },
            "Rosa": {
                "aliases": ["Rosa"],
                "gens": [
                    ("BE6", 1997, OPEN, "Bus", ["Standard", "Deluxe"],
                     [("4.9L Diesel", "4M50", "diesel", 4899)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------------ SUZUKI
    "Suzuki": {
        "popularity": 70,
        "models": {
            "Swift": {
                "aliases": ["Swift"],
                "gens": [
                    ("ZC31", 2004, 2010, "Hatchback", ["XG", "Sport"],
                     [("1.3L Petrol", "M13A", "petrol", 1328),
                      ("1.6L Petrol", "M16A", "petrol", 1586)]),
                    ("ZC72", 2010, 2017, "Hatchback", ["XG", "RS"],
                     [("1.2L Petrol", "K12B", "petrol", 1242)]),
                    ("ZC33", 2017, OPEN, "Hatchback", ["XG", "RS", "Sport"],
                     [("1.2L Petrol", "K12C", "petrol", 1242),
                      ("1.4L Turbo", "K14C", "petrol", 1371)]),
                ],
            },
            "Alto": {
                "aliases": ["Alto"],
                "gens": [
                    ("HA25", 2009, 2014, "Hatchback", ["F", "G"],
                     [("0.66L Petrol", "K6A", "petrol", 658)]),
                    ("HA36", 2014, 2021, "Hatchback", ["F", "L", "X"],
                     [("0.66L Petrol", "R06A", "petrol", 658)]),
                ],
            },
            "Jimny": {
                "aliases": ["Jimny"],
                "gens": [
                    ("JB43", 1998, 2018, "SUV", ["XG", "XC"],
                     [("1.3L Petrol", "M13A", "petrol", 1328)]),
                    ("JB64", 2018, OPEN, "SUV", ["XG", "XC"],
                     [("0.66L Turbo", "R06A", "petrol", 658),
                      ("1.5L Petrol", "K15B", "petrol", 1462)]),
                ],
            },
            "Vitara": {
                "aliases": ["Vitara", "Escudo"],
                "gens": [
                    ("LY", 2015, OPEN, "SUV", ["GL", "GLX"],
                     [("1.6L Petrol", "M16A", "petrol", 1586),
                      ("1.4L Turbo", "K14C", "petrol", 1371)]),
                ],
            },
            "Every": {
                "aliases": ["Every"],
                "gens": [
                    ("DA17", 2015, OPEN, "Van", ["PA", "PC", "GA"],
                     [("0.66L Petrol", "R06A", "petrol", 658)]),
                ],
            },
            "Baleno": {
                "aliases": ["Baleno"],
                "gens": [
                    ("WB", 2015, OPEN, "Hatchback", ["GL", "GLX"],
                     [("1.4L Petrol", "K14B", "petrol", 1373)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------------ ISUZU
    "Isuzu": {
        "popularity": 68,
        "models": {
            "D-Max": {
                "aliases": ["Dmax", "D Max"],
                "gens": [
                    ("TFR 1st Gen", 2002, 2012, "Pickup", ["Single Cab", "Double Cab"],
                     [("2.5L Diesel", "4JA1", "diesel", 2499),
                      ("3.0L Diesel", "4JJ1", "diesel", 2999)]),
                    ("TFS 2nd Gen", 2012, 2019, "Pickup", ["Single Cab", "Double Cab", "LS"],
                     [("2.5L Diesel", "4JK1", "diesel", 2499),
                      ("3.0L Diesel", "4JJ1", "diesel", 2999)]),
                    ("RG 3rd Gen", 2019, OPEN, "Pickup", ["Single Cab", "Double Cab", "V-Cross"],
                     [("1.9L Diesel", "RZ4E", "diesel", 1898),
                      ("3.0L Diesel", "4JJ3", "diesel", 2999)]),
                ],
            },
            "MU-X": {
                "aliases": ["MUX", "MU X"],
                "gens": [
                    ("1st Gen", 2013, 2020, "SUV", ["LS", "LS-T"],
                     [("3.0L Diesel", "4JJ1", "diesel", 2999)]),
                    ("2nd Gen", 2020, OPEN, "SUV", ["LS", "LS-T"],
                     [("3.0L Diesel", "4JJ3", "diesel", 2999)]),
                ],
            },
            "ELF": {
                "aliases": ["ELF", "NKR", "NPR"],
                "gens": [
                    ("NKR/NPR", 1999, OPEN, "Truck", ["NKR", "NPR", "NQR"],
                     [("4.6L Diesel", "4HG1", "diesel", 4570),
                      ("5.2L Diesel", "4HK1", "diesel", 5193)]),
                ],
            },
            "FRR": {
                "aliases": ["FRR", "FSR"],
                "gens": [
                    ("F-Series", 2003, OPEN, "Truck", ["FRR", "FSR", "FTR"],
                     [("5.2L Diesel", "4HK1", "diesel", 5193),
                      ("7.8L Diesel", "6HK1", "diesel", 7790)]),
                ],
            },
            "NQR Bus": {
                "aliases": ["NQR", "Isuzu Bus"],
                "gens": [
                    ("NQR", 2005, OPEN, "Bus", ["33-Seater", "51-Seater"],
                     [("5.2L Diesel", "4HK1", "diesel", 5193)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------ MERCEDES-BENZ
    "Mercedes-Benz": {
        "popularity": 65,
        "models": {
            "C-Class": {
                "aliases": ["C Class", "C180", "C200"],
                "gens": [
                    ("W204", 2007, 2014, "Sedan", ["C180", "C200", "C250"],
                     [("1.8L Petrol", "M271", "petrol", 1796)]),
                    ("W205", 2014, 2021, "Sedan", ["C180", "C200", "C300"],
                     [("1.6L Turbo", "M274", "petrol", 1595),
                      ("2.0L Turbo", "M274", "petrol", 1991)]),
                    ("W206", 2021, OPEN, "Sedan", ["C180", "C200", "C300"],
                     [("1.5L Turbo MHEV", "M254", "petrol", 1496)]),
                ],
            },
            "E-Class": {
                "aliases": ["E Class", "E200", "E250"],
                "gens": [
                    ("W211", 2002, 2009, "Sedan", ["E200", "E240", "E280"],
                     [("1.8L Petrol", "M271", "petrol", 1796),
                      ("2.6L Petrol", "M112", "petrol", 2597)]),
                    ("W212", 2009, 2016, "Sedan", ["E200", "E250", "E300"],
                     [("1.8L Petrol", "M271", "petrol", 1796),
                      ("2.0L Turbo", "M274", "petrol", 1991)]),
                    ("W213", 2016, 2023, "Sedan", ["E200", "E300", "E350e"],
                     [("2.0L Turbo", "M264", "petrol", 1991)]),
                ],
            },
            "GLE": {
                "aliases": ["GLE", "ML"],
                "gens": [
                    ("W166", 2011, 2019, "SUV", ["ML250", "ML350", "GLE350"],
                     [("2.1L Diesel", "OM651", "diesel", 2143),
                      ("3.0L Diesel", "OM642", "diesel", 2987)]),
                    ("V167", 2019, OPEN, "SUV", ["GLE300d", "GLE450"],
                     [("2.0L Diesel", "OM654", "diesel", 1950),
                      ("3.0L MHEV", "M256", "petrol", 2999)]),
                ],
            },
            "GLC": {
                "aliases": ["GLC"],
                "gens": [
                    ("X253", 2015, 2022, "SUV", ["GLC250", "GLC300"],
                     [("2.0L Turbo", "M274", "petrol", 1991)]),
                ],
            },
            "Sprinter": {
                "aliases": ["Sprinter"],
                "gens": [
                    ("W906", 2006, 2018, "Van", ["313", "316", "519"],
                     [("2.1L Diesel", "OM651", "diesel", 2143)]),
                    ("W907", 2018, OPEN, "Van", ["314", "317", "519"],
                     [("2.0L Diesel", "OM654", "diesel", 1950)]),
                ],
            },
            "Actros": {
                "aliases": ["Actros"],
                "gens": [
                    ("MP3", 2008, 2011, "Truck", ["1844", "2544"],
                     [("12L Diesel", "OM501", "diesel", 11946)]),
                    ("MP4", 2011, OPEN, "Truck", ["1845", "2545"],
                     [("12.8L Diesel", "OM471", "diesel", 12809)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------------ BMW
    "BMW": {
        "popularity": 60,
        "models": {
            "3 Series": {
                "aliases": ["320i", "3 Series"],
                "gens": [
                    ("E90", 2005, 2012, "Sedan", ["320i", "325i", "330i"],
                     [("2.0L Petrol", "N46", "petrol", 1995),
                      ("3.0L Petrol", "N52", "petrol", 2996)]),
                    ("F30", 2012, 2019, "Sedan", ["316i", "320i", "328i"],
                     [("1.6L Turbo", "N13", "petrol", 1598),
                      ("2.0L Turbo", "N20", "petrol", 1997)]),
                    ("G20", 2019, OPEN, "Sedan", ["318i", "320i", "330i"],
                     [("2.0L Turbo", "B48", "petrol", 1998)]),
                ],
            },
            "5 Series": {
                "aliases": ["520i", "5 Series"],
                "gens": [
                    ("E60", 2003, 2010, "Sedan", ["523i", "525i", "530i"],
                     [("2.5L Petrol", "N52", "petrol", 2497)]),
                    ("F10", 2010, 2017, "Sedan", ["520i", "523i", "528i"],
                     [("2.0L Turbo", "N20", "petrol", 1997)]),
                    ("G30", 2017, 2023, "Sedan", ["520i", "530i", "530e"],
                     [("2.0L Turbo", "B48", "petrol", 1998)]),
                ],
            },
            "X3": {
                "aliases": ["X3"],
                "gens": [
                    ("F25", 2010, 2017, "SUV", ["xDrive20i", "xDrive28i"],
                     [("2.0L Turbo", "N20", "petrol", 1997)]),
                    ("G01", 2017, OPEN, "SUV", ["xDrive20i", "xDrive30i"],
                     [("2.0L Turbo", "B48", "petrol", 1998)]),
                ],
            },
            "X5": {
                "aliases": ["X5"],
                "gens": [
                    ("E70", 2006, 2013, "SUV", ["xDrive30i", "xDrive35d"],
                     [("3.0L Petrol", "N52", "petrol", 2996),
                      ("3.0L Diesel", "M57", "diesel", 2993)]),
                    ("F15", 2013, 2018, "SUV", ["xDrive25d", "xDrive35i"],
                     [("2.0L Diesel", "N47", "diesel", 1995),
                      ("3.0L Turbo", "N55", "petrol", 2979)]),
                    ("G05", 2018, OPEN, "SUV", ["xDrive30d", "xDrive40i"],
                     [("3.0L Diesel", "B57", "diesel", 2993),
                      ("3.0L Turbo", "B58", "petrol", 2998)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------- VOLKSWAGEN
    "Volkswagen": {
        "popularity": 58,
        "models": {
            "Golf": {
                "aliases": ["Golf", "Golf GTI"],
                "gens": [
                    ("Mk5", 2003, 2009, "Hatchback", ["Trendline", "GTI"],
                     [("1.6L Petrol", "BSE", "petrol", 1595),
                      ("2.0L Turbo", "BWA", "petrol", 1984)]),
                    ("Mk6", 2009, 2013, "Hatchback", ["Trendline", "GTI"],
                     [("1.4L TSI", "CAXA", "petrol", 1390),
                      ("2.0L Turbo", "CCZB", "petrol", 1984)]),
                    ("Mk7", 2013, 2020, "Hatchback", ["Trendline", "Highline", "GTI"],
                     [("1.4L TSI", "CZCA", "petrol", 1395),
                      ("2.0L Turbo", "CHHB", "petrol", 1984)]),
                ],
            },
            "Polo": {
                "aliases": ["Polo", "Polo Vivo"],
                "gens": [
                    ("9N", 2002, 2009, "Hatchback", ["Trendline", "Comfortline"],
                     [("1.4L Petrol", "BBY", "petrol", 1390)]),
                    ("6R", 2009, 2017, "Hatchback", ["Trendline", "Comfortline", "GTI"],
                     [("1.2L TSI", "CBZB", "petrol", 1197),
                      ("1.4L Petrol", "CGGB", "petrol", 1390)]),
                    ("AW", 2017, OPEN, "Hatchback", ["Trendline", "Comfortline", "GTI"],
                     [("1.0L TSI", "CHZB", "petrol", 999)]),
                ],
            },
            "Passat": {
                "aliases": ["Passat"],
                "gens": [
                    ("B6", 2005, 2010, "Sedan", ["Trendline", "Highline"],
                     [("2.0L TSI", "BWA", "petrol", 1984)]),
                    ("B7", 2010, 2015, "Sedan", ["Comfortline", "Highline"],
                     [("1.8L TSI", "CDAB", "petrol", 1798)]),
                    ("B8", 2015, 2023, "Sedan", ["Comfortline", "Highline"],
                     [("1.4L TSI", "CZEA", "petrol", 1395),
                      ("2.0L TSI", "CHHB", "petrol", 1984)]),
                ],
            },
            "Tiguan": {
                "aliases": ["Tiguan"],
                "gens": [
                    ("5N", 2007, 2016, "SUV", ["Trend & Fun", "Sport & Style"],
                     [("2.0L TSI", "CAWA", "petrol", 1984)]),
                    ("AD1", 2016, OPEN, "SUV", ["Trendline", "Highline", "R-Line"],
                     [("1.4L TSI", "CZDA", "petrol", 1395),
                      ("2.0L TSI", "CZPA", "petrol", 1984)]),
                ],
            },
            "Touareg": {
                "aliases": ["Touareg"],
                "gens": [
                    ("7L", 2002, 2010, "SUV", ["V6", "V8", "TDI"],
                     [("3.2L Petrol", "AZZ", "petrol", 3189),
                      ("3.0L TDI", "BKS", "diesel", 2967)]),
                    ("7P", 2010, 2018, "SUV", ["V6 TSI", "V6 TDI"],
                     [("3.6L Petrol", "CGRA", "petrol", 3597),
                      ("3.0L TDI", "CRCA", "diesel", 2967)]),
                ],
            },
            "Amarok": {
                "aliases": ["Amarok"],
                "gens": [
                    ("2H", 2010, 2022, "Pickup", ["Trendline", "Highline"],
                     [("2.0L BiTDI", "CDCA", "diesel", 1968),
                      ("3.0L V6 TDI", "DDXC", "diesel", 2967)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------------ FORD
    "Ford": {
        "popularity": 55,
        "models": {
            "Ranger": {
                "aliases": ["Ranger"],
                "gens": [
                    ("T6 PX", 2011, 2022, "Pickup", ["XL", "XLT", "Wildtrak", "Raptor"],
                     [("2.2L Diesel", "P4AT", "diesel", 2198),
                      ("3.2L Diesel", "P5AT", "diesel", 3198),
                      ("2.0L BiTurbo", "YN2S", "diesel", 1996)]),
                    ("Next-Gen P703", 2022, OPEN, "Pickup", ["XL", "XLT", "Wildtrak", "Raptor"],
                     [("2.0L BiTurbo", "YN2S", "diesel", 1996),
                      ("3.0L V6 Diesel", "ZSD-EcoBlue", "diesel", 2993)]),
                ],
            },
            "Everest": {
                "aliases": ["Everest"],
                "gens": [
                    ("U375", 2015, 2022, "SUV", ["Trend", "Titanium"],
                     [("2.2L Diesel", "P4AT", "diesel", 2198),
                      ("3.2L Diesel", "P5AT", "diesel", 3198)]),
                ],
            },
            "Focus": {
                "aliases": ["Focus"],
                "gens": [
                    ("Mk2", 2004, 2011, "Hatchback", ["Ambiente", "Trend"],
                     [("1.6L Petrol", "HXDA", "petrol", 1596)]),
                    ("Mk3", 2011, 2018, "Hatchback", ["Trend", "Titanium"],
                     [("1.6L Petrol", "PNDA", "petrol", 1596),
                      ("2.0L Petrol", "XQDA", "petrol", 1999)]),
                ],
            },
            "EcoSport": {
                "aliases": ["EcoSport"],
                "gens": [
                    ("B515", 2013, 2022, "SUV", ["Ambiente", "Trend", "Titanium"],
                     [("1.5L Petrol", "UEJA", "petrol", 1498)]),
                ],
            },
        },
    },
    # ----------------------------------------------------------------- HYUNDAI
    "Hyundai": {
        "popularity": 50,
        "models": {
            "Tucson": {
                "aliases": ["Tucson"],
                "gens": [
                    ("TL", 2015, 2020, "SUV", ["GL", "GLS"],
                     [("2.0L Petrol", "G4NA", "petrol", 1999),
                      ("2.0L Diesel", "D4HA", "diesel", 1995)]),
                    ("NX4", 2020, OPEN, "SUV", ["Premium", "Elite"],
                     [("2.0L Petrol", "G4NA", "petrol", 1999)]),
                ],
            },
            "Santa Fe": {
                "aliases": ["Santa Fe", "Santafe"],
                "gens": [
                    ("DM", 2012, 2018, "SUV", ["GLS", "Exclusive"],
                     [("2.2L Diesel", "D4HB", "diesel", 2199)]),
                    ("TM", 2018, OPEN, "SUV", ["Premium", "Calligraphy"],
                     [("2.2L Diesel", "D4HB", "diesel", 2199)]),
                ],
            },
            "i10": {
                "aliases": ["i10", "Grand i10"],
                "gens": [
                    ("IA", 2013, 2019, "Hatchback", ["Motion", "Fluid"],
                     [("1.0L Petrol", "G3LA", "petrol", 998),
                      ("1.2L Petrol", "G4LA", "petrol", 1197)]),
                ],
            },
            "H-1": {
                "aliases": ["H1", "Starex"],
                "gens": [
                    ("TQ", 2007, 2021, "Van", ["GL", "GLS"],
                     [("2.5L Diesel", "D4CB", "diesel", 2497)]),
                ],
            },
        },
    },
    # -------------------------------------------------------------------- KIA
    "Kia": {
        "popularity": 48,
        "models": {
            "Sportage": {
                "aliases": ["Sportage"],
                "gens": [
                    ("QL", 2015, 2021, "SUV", ["LX", "EX"],
                     [("2.0L Petrol", "G4NA", "petrol", 1999),
                      ("2.0L Diesel", "D4HA", "diesel", 1995)]),
                    ("NQ5", 2021, OPEN, "SUV", ["LX", "EX", "GT-Line"],
                     [("2.0L Petrol", "G4NA", "petrol", 1999)]),
                ],
            },
            "Sorento": {
                "aliases": ["Sorento"],
                "gens": [
                    ("UM", 2014, 2020, "SUV", ["LX", "EX"],
                     [("2.2L Diesel", "D4HB", "diesel", 2199)]),
                    ("MQ4", 2020, OPEN, "SUV", ["LX", "EX", "SX"],
                     [("2.2L Diesel", "D4HE", "diesel", 2151)]),
                ],
            },
            "Rio": {
                "aliases": ["Rio"],
                "gens": [
                    ("YB", 2017, 2023, "Hatchback", ["LX", "EX"],
                     [("1.4L Petrol", "G4LC", "petrol", 1368)]),
                ],
            },
            "Picanto": {
                "aliases": ["Picanto"],
                "gens": [
                    ("JA", 2017, OPEN, "Hatchback", ["LX", "EX", "GT-Line"],
                     [("1.0L Petrol", "G3LD", "petrol", 998),
                      ("1.2L Petrol", "G4LA", "petrol", 1197)]),
                ],
            },
            "Seltos": {
                "aliases": ["Seltos"],
                "gens": [
                    ("SP2", 2019, OPEN, "SUV", ["LX", "EX", "GT-Line"],
                     [("1.5L Petrol", "G4FL", "petrol", 1497)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------------- AUDI
    "Audi": {
        "popularity": 45,
        "models": {
            "A3": {
                "aliases": ["A3"],
                "gens": [
                    ("8P", 2003, 2013, "Hatchback", ["1.6", "2.0 TFSI"],
                     [("1.6L Petrol", "BSE", "petrol", 1595),
                      ("2.0L TFSI", "BWA", "petrol", 1984)]),
                    ("8V", 2013, 2020, "Hatchback", ["1.4 TFSI", "2.0 TFSI"],
                     [("1.4L TFSI", "CXSB", "petrol", 1395)]),
                ],
            },
            "A4": {
                "aliases": ["A4"],
                "gens": [
                    ("B7", 2004, 2008, "Sedan", ["1.8T", "2.0 TFSI"],
                     [("1.8L Turbo", "BFB", "petrol", 1781),
                      ("2.0L TFSI", "BGB", "petrol", 1984)]),
                    ("B8", 2008, 2016, "Sedan", ["1.8 TFSI", "2.0 TFSI"],
                     [("1.8L TFSI", "CDHB", "petrol", 1798),
                      ("2.0L TFSI", "CDNC", "petrol", 1984)]),
                    ("B9", 2016, OPEN, "Sedan", ["35 TFSI", "40 TFSI"],
                     [("2.0L TFSI", "CYRB", "petrol", 1984)]),
                ],
            },
            "Q5": {
                "aliases": ["Q5"],
                "gens": [
                    ("8R", 2008, 2017, "SUV", ["2.0 TFSI", "3.0 TDI"],
                     [("2.0L TFSI", "CDNC", "petrol", 1984),
                      ("3.0L TDI", "CCWA", "diesel", 2967)]),
                    ("FY", 2017, OPEN, "SUV", ["40 TFSI", "45 TFSI"],
                     [("2.0L TFSI", "DBPA", "petrol", 1984)]),
                ],
            },
            "Q7": {
                "aliases": ["Q7"],
                "gens": [
                    ("4L", 2005, 2015, "SUV", ["3.6 FSI", "3.0 TDI"],
                     [("3.6L Petrol", "BHK", "petrol", 3597),
                      ("3.0L TDI", "CASA", "diesel", 2967)]),
                    ("4M", 2015, OPEN, "SUV", ["45 TDI", "55 TFSI"],
                     [("3.0L TDI", "CRTC", "diesel", 2967)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------- LAND ROVER
    "Land Rover": {
        "popularity": 44,
        "models": {
            "Defender": {
                "aliases": ["Defender"],
                "gens": [
                    ("L316", 1990, 2016, "SUV", ["90", "110", "130"],
                     [("2.2L Diesel", "DT224", "diesel", 2198),
                      ("2.4L Diesel", "DT244", "diesel", 2402)]),
                    ("L663", 2020, OPEN, "SUV", ["90", "110", "130"],
                     [("2.0L Diesel", "D200", "diesel", 1999),
                      ("3.0L MHEV Diesel", "D300", "diesel", 2996)]),
                ],
            },
            "Discovery": {
                "aliases": ["Discovery", "Disco"],
                "gens": [
                    ("Discovery 3", 2004, 2009, "SUV", ["S", "SE", "HSE"],
                     [("2.7L TDV6", "276DT", "diesel", 2720)]),
                    ("Discovery 4", 2009, 2017, "SUV", ["S", "SE", "HSE"],
                     [("3.0L TDV6", "306DT", "diesel", 2993)]),
                    ("Discovery 5", 2017, OPEN, "SUV", ["S", "SE", "HSE"],
                     [("3.0L Diesel", "306DT", "diesel", 2993),
                      ("2.0L Petrol", "PT204", "petrol", 1997)]),
                ],
            },
            "Range Rover Sport": {
                "aliases": ["RR Sport", "Range Rover Sport"],
                "gens": [
                    ("L320", 2005, 2013, "SUV", ["HSE", "Supercharged"],
                     [("2.7L TDV6", "276DT", "diesel", 2720),
                      ("4.2L Supercharged", "428PS", "petrol", 4197)]),
                    ("L494", 2013, 2022, "SUV", ["HSE", "Autobiography"],
                     [("3.0L SDV6", "306DT", "diesel", 2993)]),
                ],
            },
            "Range Rover Evoque": {
                "aliases": ["Evoque"],
                "gens": [
                    ("L538", 2011, 2019, "SUV", ["Pure", "Dynamic"],
                     [("2.0L Petrol", "204PT", "petrol", 1999),
                      ("2.2L Diesel", "224DT", "diesel", 2179)]),
                    ("L551", 2019, OPEN, "SUV", ["S", "SE", "HSE"],
                     [("2.0L MHEV Petrol", "P200", "petrol", 1997)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------------ LEXUS
    "Lexus": {
        "popularity": 40,
        "models": {
            "RX": {
                "aliases": ["RX", "RX350"],
                "gens": [
                    ("AL10", 2008, 2015, "SUV", ["RX270", "RX350", "RX450h"],
                     [("2.7L Petrol", "1AR-FE", "petrol", 2672),
                      ("3.5L Hybrid", "2GR-FXE", "hybrid", 3456)]),
                    ("AL20", 2015, 2022, "SUV", ["RX200t", "RX350", "RX450h"],
                     [("2.0L Turbo", "8AR-FTS", "petrol", 1998),
                      ("3.5L Hybrid", "2GR-FXS", "hybrid", 3456)]),
                ],
            },
            "LX": {
                "aliases": ["LX", "LX570"],
                "gens": [
                    ("J200", 2007, 2021, "SUV", ["LX570"],
                     [("5.7L Petrol", "3UR-FE", "petrol", 5663)]),
                    ("J310", 2021, OPEN, "SUV", ["LX500d", "LX600"],
                     [("3.3L Diesel", "F33A-FTV", "diesel", 3346),
                      ("3.5L Twin Turbo", "V35A-FTS", "petrol", 3445)]),
                ],
            },
            "NX": {
                "aliases": ["NX", "NX200t"],
                "gens": [
                    ("AZ10", 2014, 2021, "SUV", ["NX200t", "NX300h"],
                     [("2.0L Turbo", "8AR-FTS", "petrol", 1998),
                      ("2.5L Hybrid", "2AR-FXE", "hybrid", 2494)]),
                ],
            },
        },
    },
    # ----------------------------------------------------------------- PEUGEOT
    "Peugeot": {
        "popularity": 35,
        "models": {
            "208": {
                "aliases": ["208"],
                "gens": [
                    ("A9", 2012, 2019, "Hatchback", ["Active", "Allure"],
                     [("1.2L Petrol", "EB2", "petrol", 1199)]),
                    ("P21", 2019, OPEN, "Hatchback", ["Active", "Allure", "GT"],
                     [("1.2L Turbo", "EB2ADT", "petrol", 1199)]),
                ],
            },
            "308": {
                "aliases": ["308"],
                "gens": [
                    ("T9", 2013, 2021, "Hatchback", ["Active", "Allure"],
                     [("1.2L Turbo", "EB2DT", "petrol", 1199),
                      ("1.6L Diesel", "DV6C", "diesel", 1560)]),
                ],
            },
            "3008": {
                "aliases": ["3008"],
                "gens": [
                    ("P84", 2016, OPEN, "SUV", ["Active", "Allure", "GT"],
                     [("1.2L Turbo", "EB2ADTS", "petrol", 1199),
                      ("1.6L Turbo", "EP6FDT", "petrol", 1598)]),
                ],
            },
            "Partner": {
                "aliases": ["Partner"],
                "gens": [
                    ("B9", 2008, 2018, "Van", ["Standard", "Long"],
                     [("1.6L Diesel", "DV6", "diesel", 1560)]),
                ],
            },
        },
    },
    # ------------------------------------------------------------ MOTORCYCLES
    "Bajaj": {
        "popularity": 30,
        "models": {
            "Boxer": {
                "aliases": ["Boxer", "Boda"],
                "gens": [
                    ("BM100", 2010, OPEN, "Motorcycle", ["Standard"],
                     [("100cc Petrol", "BM100", "petrol", 99)]),
                    ("BM150", 2013, OPEN, "Motorcycle", ["Standard", "X"],
                     [("150cc Petrol", "BM150", "petrol", 144)]),
                ],
            },
            "Pulsar": {
                "aliases": ["Pulsar"],
                "gens": [
                    ("NS125", 2017, OPEN, "Motorcycle", ["Standard"],
                     [("125cc Petrol", "NS125", "petrol", 124)]),
                    ("NS200", 2012, OPEN, "Motorcycle", ["Standard"],
                     [("200cc Petrol", "NS200", "petrol", 199)]),
                ],
            },
        },
    },
    "TVS": {
        "popularity": 28,
        "models": {
            "HLX": {
                "aliases": ["HLX"],
                "gens": [
                    ("HLX 125", 2015, OPEN, "Motorcycle", ["Standard", "Plus"],
                     [("125cc Petrol", "HLX125", "petrol", 124)]),
                    ("HLX 150", 2016, OPEN, "Motorcycle", ["Standard", "X"],
                     [("150cc Petrol", "HLX150", "petrol", 147)]),
                ],
            },
            "Star": {
                "aliases": ["Star HLX", "Star City"],
                "gens": [
                    ("Star 100", 2012, OPEN, "Motorcycle", ["Standard"],
                     [("100cc Petrol", "STAR100", "petrol", 99)]),
                ],
            },
        },
    },
    "Honda Motorcycles": {
        "popularity": 26,
        "models": {
            "Ace": {
                "aliases": ["Ace", "CB125"],
                "gens": [
                    ("CB125 ACE", 2013, OPEN, "Motorcycle", ["Standard", "Deluxe"],
                     [("125cc Petrol", "CB125", "petrol", 124)]),
                ],
            },
            "XL": {
                "aliases": ["XL125"],
                "gens": [
                    ("XL125", 2005, OPEN, "Motorcycle", ["Standard"],
                     [("125cc Petrol", "XL125", "petrol", 124)]),
                ],
            },
        },
    },
}


# ---------------------------------------------------------------------------
# Parts category tree: (name, google_product_category, [children])
# All slugs are auto-generated and must stay globally unique — they appear in
# vehicle+category URLs (/car-parts/.../brake-pads/).
# ---------------------------------------------------------------------------
GPC_VP = "Vehicles & Parts > Vehicle Parts & Accessories"

CATEGORY_TREE = [
    ("Engine Parts", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Engine Parts", [
        "Engine Mounts", "Timing Belts & Chains", "Gaskets & Seals",
        "Pistons & Rings", "Turbochargers", "Engine Valves", "Camshafts & Crankshafts",
    ]),
    ("Filters", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Engine Parts", [
        "Oil Filters", "Air Filters", "Fuel Filters", "Cabin Filters",
    ]),
    ("Braking System", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Braking", [
        "Brake Pads", "Brake Discs", "Brake Drums", "Brake Shoes",
        "Brake Calipers", "Brake Master Cylinders", "Wheel Cylinders",
        "ABS Sensors", "Brake Hoses & Lines",
    ]),
    ("Suspension & Steering", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Suspension Parts", [
        "Shock Absorbers", "Coil Springs", "Leaf Springs", "Control Arms",
        "Ball Joints", "Tie Rod Ends", "Stabilizer Links", "Bushings",
        "Steering Racks", "Wheel Bearings", "Wheel Hubs",
    ]),
    ("Transmission & Drivetrain", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Transmission & Drivetrain Parts", [
        "Clutch Kits", "CV Joints & Driveshafts", "Gearbox Mounts",
        "Differentials", "Transmission Filters", "Propeller Shafts",
    ]),
    ("Cooling System", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Engine Parts", [
        "Radiators", "Water Pumps", "Thermostats", "Cooling Fans",
        "Radiator Hoses", "Expansion Tanks", "Intercoolers",
    ]),
    ("Electrical & Ignition", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Electronics", [
        "Batteries", "Alternators", "Starter Motors", "Spark Plugs",
        "Glow Plugs", "Ignition Coils", "Engine Sensors", "Fuses & Relays",
        "Wiring Harnesses",
    ]),
    ("Lighting", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Lighting", [
        "Headlights", "Tail Lights", "Fog Lights", "Indicator Lights",
        "Bulbs & LEDs", "Light Switches & Stalks",
    ]),
    ("Body & Exterior", f"{GPC_VP} > Motor Vehicle Parts", [
        "Bumpers", "Fenders", "Side Mirrors", "Grilles", "Door Handles",
        "Windscreens & Glass", "Wiper Blades", "Wiper Motors",
        "Bonnets & Tailgates", "Mud Flaps",
    ]),
    ("Interior", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Interior Fittings", [
        "Seat Covers", "Floor Mats", "Steering Wheel Covers", "Gear Knobs",
        "Dashboard Parts", "Window Regulators",
    ]),
    ("Exhaust System", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Exhaust", [
        "Silencers & Mufflers", "Catalytic Converters", "Exhaust Pipes",
        "Exhaust Manifolds", "Lambda Sensors",
    ]),
    ("Fuel System", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Fuel Systems", [
        "Fuel Pumps", "Fuel Injectors", "Carburetors", "Fuel Tanks & Caps",
    ]),
    ("Air Conditioning", f"{GPC_VP} > Motor Vehicle Parts > Motor Vehicle Climate Control", [
        "AC Compressors", "AC Condensers", "Blower Motors", "AC Filters & Driers",
    ]),
    ("Wheels & Tyres", f"{GPC_VP} > Vehicle Wheels & Wheel Parts", [
        "Tyres", "Rims", "Wheel Nuts & Locks", "Wheel Covers", "Tyre Repair Kits",
    ]),
    ("Service Kits & Lubricants", f"{GPC_VP} > Vehicle Maintenance, Care & Decor", [
        "Engine Oils", "Transmission Fluids", "Brake Fluids", "Coolants",
        "Greases", "Additives", "Full Service Kits",
    ]),
    ("Motorcycle Parts", f"{GPC_VP} > Motor Vehicle Parts", [
        "Motorcycle Chains & Sprockets", "Motorcycle Brake Shoes",
        "Motorcycle Tyres & Tubes", "Motorcycle Batteries",
        "Motorcycle Cables", "Motorcycle Mirrors", "Motorcycle Spark Plugs",
    ]),
    ("Truck & Bus Parts", f"{GPC_VP} > Motor Vehicle Parts", [
        "Air Brake Parts", "Truck Leaf Springs", "Clutch Boosters",
        "Truck Filters", "Truck Mirrors", "Truck Lighting",
    ]),
    ("Accessories", f"{GPC_VP} > Vehicle Safety & Security", [
        "Car Care & Cleaning", "Phone Holders & Chargers", "Dash Cameras",
        "Car Alarms & Security", "Roof Racks & Carriers", "Towing Equipment",
        "First Aid & Emergency", "Seat Belts & Safety",
    ]),
]

# kind="general" — non-fitment catalog (BUILD_PLAN: laptops, phones drop in
# with the same models/offers/feeds and skip fitment entirely).
GENERAL_CATEGORY_TREE = [
    ("Laptops", "Electronics > Computers > Laptops", []),
    ("Phones", "Electronics > Communications > Telephony > Mobile Phones", []),
    ("Electronics Accessories", "Electronics > Electronics Accessories", []),
]
