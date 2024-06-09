PREFIXES = {
    "y": 1e-24,
    "z": 1e-21,
    "a": 1e-18,
    "f": 1e-15,
    "p": 1e-12,
    "n": 1e-9,
    "µ": 1e-6,
    "m": 1e-3,
    "": 1,
    "k": 1e3,
    "M": 1e6,
    "G": 1e9,
    "T": 1e12,
    "P": 1e15,
    "E": 1e18,
    "Z": 1e21,
    "Y": 1e24,
}

UNITS = ["N", "J", "m", "s", "N/s", "N/m"]


def get_current_units(column_name):

    s = column_name.split("[", 1)[1].split("]")[0]

    # Check for prefix
    if s[0] in PREFIXES.keys() and s[1:] in UNITS:
        return (s[0], s[1:])

    # Check for no prefix
    if s in UNITS:
        return ("", s)

    return ("", "")


def change_column_prefix(data, column_name, new_prefix):

    prefix, units = get_current_units(column_name)

    factor = PREFIXES[prefix] / PREFIXES[new_prefix]

    data[column_name] *= factor

    # Rename the column
    before = column_name.split("[", 1)[0]
    after = column_name.split("]", 1)[1]
    
    new_column_name = f"{before}[{new_prefix}{units}]{after}"

    data = data.rename(columns={column_name: new_column_name})

    return data
