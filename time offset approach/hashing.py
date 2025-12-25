def hash_landmark(f1, f2, dt, freq_bin=10, time_bin=0.1):
    
    """
    Convert a landmark into a hash key.

    Parameters:
        f1 (float): anchor frequency in Hz
        f2 (float): target frequency in Hz
        dt (float): time difference in seconds
        freq_bin (int): frequency bin size (Hz)
        time_bin (float): time bin size (seconds)

    Returns:
        tuple: (f1_bin, f2_bin, dt_bin)
    """

    f1_bin = int(f1 // freq_bin)
    f2_bin = int(f2 // freq_bin)
    dt_bin = int(dt // time_bin)

    return (f1_bin, f2_bin, dt_bin)

