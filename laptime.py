import csv
import datetime


class Position:
    def __init__(self, latitute, longitude):
        self.latitude = latitute
        self.longitude = longitude


def main():
    with open('csv/2020-07-13_pm_mettet.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        a = Position(50.300936, 4.649522)
        b = Position(50.300821, 4.649592)

        c = None
        d = None

        lower_limit = -0.2
        upper_limit = 1.2
        line_crossed = []

        for row in reader:
            timestamp = float(row[0])
            latitute = float(row[1])
            longitude = float(row[2])
            speed = float(row[3])

            d = Position(latitute, longitude)

            if c and d:
                alpha = coeff(a, b, c, d)
                beta = coeff(c, d, a, b)
                if alpha and beta and alpha > lower_limit and alpha < upper_limit and beta > lower_limit and beta < upper_limit:
                    row.append(alpha)
                    row.append(beta)
                    add_lap(line_crossed, row)
            c = d
        
        last = None
        i = 0
        for line in line_crossed:
            if last:
                delta = datetime.timedelta(seconds = float(line[0]) - float(last[0]))
                print("{:>2} - {}".format(i, delta))
            last = line
            i = i + 1


def add_lap(line_crossed, row):
    size = len(line_crossed)
    if size > 0:
        delta = datetime.timedelta(seconds = float(row[0]) - float(line_crossed[size - 1][0]))
        if delta.seconds > 10:
            line_crossed.append(row)
    else:
        line_crossed.append(row)


def coeff(a, b, c, d):
    try:
        return  ((c.latitude - a.latitude) * (d.longitude - c.longitude) - (c.longitude - a.longitude) * (d.latitude - c.latitude)) \
                / ((b.latitude - a.latitude) * (d.longitude - c.longitude) - (b.longitude - a.longitude) * (d.latitude - c.latitude))
    except ZeroDivisionError:
        return None


if __name__ == "__main__":
    main()