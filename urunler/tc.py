def tc_kimlik_no_dogrula(tc):
    if not tc.isdigit() or len(tc) != 11 or tc[0] == '0':
        return False

    digits = list(map(int, tc))
    if len(digits) != 11:
        return False

    if (sum(digits[0:10]) % 10 != digits[10]):
        return False

    if (((sum(digits[0:9:2]) * 7) - sum(digits[1:8:2])) % 10 != digits[9]):
        return False

    return True

