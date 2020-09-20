import csv
import datetime
import model


def main():
    laps = calculate_laptime('2020-09-19_am_chambley.csv', model.TRACKS[1])
    #laps = calculate_laptime('2020-07-13_am_mettet.csv', model.TRACKS[0])
    for lap in laps:
        print(lap)


def calculate_laptime(file, track: model.Track):
    laps = []
    with open('csv/'+file, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        a = track.start_line_a
        b = track.start_line_b

        c = None
        d = None

        lower_limit = -0.5
        upper_limit = 1.5
        line_crossed = []

        row = next(reader)
        while(row):
            timestamp = float(row[0])
            latitute = float(row[1])
            longitude = float(row[2])
            speed = float(row[3])

            d = model.Position(latitude = latitute, longitude = longitude)

            if c and d:
                alpha = coeff(a, b, c, d)
                beta = coeff(c, d, a, b)
                if alpha and beta and alpha > lower_limit and alpha < upper_limit and beta > lower_limit and beta < upper_limit:
                    row.append(alpha)
                    row.append(beta)
                    add_lap(line_crossed, row)
            c = d

            try:
                row = next(reader)
            except Exception as e:
                break
        
        last = None
        i = 0
        for line in line_crossed:
            if last:
                delta = datetime.timedelta(seconds = float(line[0]) - float(last[0]))
                laps.append(delta)
            last = line
            i = i + 1
        return laps


def add_lap(line_crossed, row):
    size = len(line_crossed)
    if size > 0:
        delta = datetime.timedelta(seconds = float(row[0]) - float(line_crossed[size - 1][0]))
        if delta.seconds > 10:
            line_crossed.append(row)
    else:
        line_crossed.append(row)


def coeff(a : model.Position, b : model.Position, c : model.Position, d : model.Position):
    try:
        return  ((c.latitude - a.latitude) * (d.longitude - c.longitude) - (c.longitude - a.longitude) * (d.latitude - c.latitude)) \
                / ((b.latitude - a.latitude) * (d.longitude - c.longitude) - (b.longitude - a.longitude) * (d.latitude - c.latitude))
    except ZeroDivisionError:
        return None


if __name__ == "__main__":
    main()