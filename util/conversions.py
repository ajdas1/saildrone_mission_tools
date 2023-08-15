
def coordinate_degrees_minutes_to_decimal(string: str):
    """
    Args: 
    - string: location in format DDMM.MMM

    Returns:
    - decimal representation of given location: DD.DDDD
    """
    
    flt = float(string)

    if flt > 0:
        deg = int(flt/100.)
        min = flt % 100
        res = float(deg) + float(min)/60
    elif flt < 0:
        deg = abs(int(flt/100))
        min = abs(flt) % 100
        res = - (float(deg) + float(min)/60)

    return res