
def FalseAlarmRate(x):
    pass


def TruePositiveRate(x):
    pass # return recall


def DetectionRate(x):
    return TruePositiveRate(x) * (1 - FalseAlarmRate(x))