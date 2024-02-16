def float_to_int(x):
    return int(x + 0.5) if x >= 0 else int(x - 0.5)

CORDIC_SPEED_FACTOR = 15 #keep between 8 and 15
CORDIC_MATH_FRACTION_BITS = 16

EULER = float_to_int(2.71828182846 * (1 << CORDIC_MATH_FRACTION_BITS))
CORDIC_GAIN = float_to_int(0.607253 * (1 << CORDIC_MATH_FRACTION_BITS))
CORDIC_GAIN_HYPERBOLIC_VECTOR = float_to_int(0.82816 * (1 << CORDIC_MATH_FRACTION_BITS))
CORDIC_GAIN_HYPERBOLIC_CIRCULAR = float_to_int(1.64676 * (1 << CORDIC_MATH_FRACTION_BITS))
DECIMAL_TO_FP = 1 << CORDIC_MATH_FRACTION_BITS
PI = float_to_int(3.14159265359 * (1 << CORDIC_MATH_FRACTION_BITS))
ONE_EIGHTY_DIV_PI = float_to_int((180 / 3.14159265359) * (1 << CORDIC_MATH_FRACTION_BITS))
ONE_DIV_CORDIC_GAIN_HYPERBOLIC = float_to_int((1.0 / 0.82816) * (1 << CORDIC_MATH_FRACTION_BITS))


def float_to_int(value):
    return int(value * (1 << CORDIC_MATH_FRACTION_BITS))

LUT_CORDIC_ATAN = [
    float_to_int(45.0000),  # 45.000 degrees
    float_to_int(26.5651),  # 26.566 degrees
    float_to_int(14.0362),  # 14.036 degrees
    float_to_int(7.1250),   # 7.1250 degrees
    float_to_int(3.5763),   # 3.5763 degrees
    float_to_int(1.7899),   # 1.7899 degrees
    float_to_int(0.8952),   # 0.8952 degrees
    float_to_int(0.4476),   # 0.4476 degrees
    float_to_int(0.2238),   # 0.2238 degrees
    float_to_int(0.1119),   # 0.1119 degrees
    float_to_int(0.0560),   # 0.0560 degrees
    float_to_int(0.0280),   # 0.0280 degrees
    float_to_int(0.0140),   # 0.0140 degrees
    float_to_int(0.0070),   # 0.0070 degrees
    float_to_int(0.0035),   # 0.0035 degrees
]

def cordic_sin(theta):
    x = CORDIC_GAIN
    y = 0
    sumAngle = 0

    theta %= (360 << CORDIC_MATH_FRACTION_BITS)

    if theta > (90 << CORDIC_MATH_FRACTION_BITS):
        sumAngle = 180 << CORDIC_MATH_FRACTION_BITS
    if theta > (270 << CORDIC_MATH_FRACTION_BITS):
        sumAngle = 360 << CORDIC_MATH_FRACTION_BITS

    for i in range(CORDIC_SPEED_FACTOR):
        tempX = x
        if theta > sumAngle:
            # Rotate counter clockwise
            x -= y >> i
            y += tempX >> i
            sumAngle += LUT_CORDIC_ATAN[i]
        else:
            # Rotate clockwise
            x += y >> i
            y -= tempX >> i
            sumAngle -= LUT_CORDIC_ATAN[i]

    if (theta > (90 << CORDIC_MATH_FRACTION_BITS) and
            theta < (270 << CORDIC_MATH_FRACTION_BITS)):
        y = -y

    return y

def cordic_cos(theta):
    x = CORDIC_GAIN
    y = 0
    sumAngle = 0

    theta %= (360 << CORDIC_MATH_FRACTION_BITS)

    if theta > (90 << CORDIC_MATH_FRACTION_BITS):
        sumAngle = 180 << CORDIC_MATH_FRACTION_BITS
    if theta > (270 << CORDIC_MATH_FRACTION_BITS):
        sumAngle = 360 << CORDIC_MATH_FRACTION_BITS

    for i in range(CORDIC_SPEED_FACTOR):
        tempX = x
        if theta > sumAngle:
            # Rotate counter clockwise
            x -= y >> i
            y += tempX >> i
            sumAngle += LUT_CORDIC_ATAN[i]
        else:
            # Rotate clockwise
            x += y >> i
            y -= tempX >> i
            sumAngle -= LUT_CORDIC_ATAN[i]

    if (theta > (90 << CORDIC_MATH_FRACTION_BITS) and
            theta < (270 << CORDIC_MATH_FRACTION_BITS)):
        x = -x

    return x
