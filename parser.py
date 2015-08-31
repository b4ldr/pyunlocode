#!/usr/bin/env python
#
# Create on : 2015/08/31
#
# @author : Falldog
#
import csv
from defines import DELIMITER, ENCODING, QUOT_CHAR


def boolean(b):
    """ for SQLite boolean used """
    return '1' if b else '0'


class SubdivisionParser(object):
    def __init__(self):
        pass

    def parse(self, cursor, filepath):
        """
        Columns :
            CountryCode, SubdivisionCode, SubdivisionName, Type?
        """
        with open(filepath, 'rb') as f:
            data_reader = csv.reader(f, delimiter=DELIMITER, quotechar=QUOT_CHAR)
            for row in data_reader:
                country_code, subdivision_code, subdivision_name, _type = row
                subdivision_name = subdivision_name.decode(ENCODING)
                cursor.execute(
                    "INSERT OR REPLACE INTO subdivision VALUES (?,?,?)",
                    (country_code,
                     subdivision_code,
                     subdivision_name,
                     )
                )


class CodeParser(object):
    def __init__(self):
        pass

    def parse(self, cursor, filepath):
        """
        Columns :
            Change, CountryCode, LocationCode, LocationName, LocationName without Diacritics,
            Subdivision, Function, Status, Date, IATA, Coordinate, Remark

        Column - Change:
            + (newly added);
            X (to be removed);
            | (changed);
            # (name changed);
            = (reference entry);
            ! (US location with duplicate IATA code)
        Column - Date:
            ym
        Column - Coordinate:
            (DDMM[N/S] DDDMM[W/E])
        """

        with open(filepath, 'rb') as f:
            data_reader = csv.reader(f, delimiter=DELIMITER, quotechar=QUOT_CHAR)
            for row in data_reader:
                change = row[0]
                if change == 'X':  # skip removed item
                    continue
                elif change == '=':  # skip reference entry ex: "Peking = Beijing"
                    continue

                change, country_code, location_code, location_name, location_name_wo_diacritics, subdivision, function, status, date, iata, coordinate, remark = row

                if location_name and location_name[0] == '.':  # country name
                    name = location_name.decode(ENCODING)[1:]  # filter the first char "."
                    name = name.split(',')[0]
                    cursor.execute(
                        "INSERT OR REPLACE INTO country VALUES (?,?)",
                        (country_code, name)
                    )

                else:  # location name
                    if not location_code:
                        print '*** skip unknow location code record : %s' % row
                        continue

                    remark = remark.decode(ENCODING)
                    is_port = '1' in function
                    is_airport = '4' in function
                    is_rail_terminal = '2' in function
                    is_road_terminal = '3' in function
                    is_postal_exchange_office = '5' in function
                    is_border_cross = 'B' in function

                    cursor.execute(
                        "INSERT OR REPLACE INTO location VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (country_code,
                         location_code,
                         location_name_wo_diacritics,
                         subdivision,
                         status,
                         iata,
                         coordinate,
                         remark,
                         boolean(is_port),
                         boolean(is_airport),
                         boolean(is_road_terminal),
                         boolean(is_rail_terminal),
                         boolean(is_postal_exchange_office),
                         boolean(is_border_cross),
                         )
                    )


