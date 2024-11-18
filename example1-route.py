
from datetime import datetime
from requests import codes

from tilapya.errors import ErrorCodes as EC
from tilapya.errors import TransLinkAPIError
from tilapya.rtti import (RTTI, TRANSLINK_TZ, parse_last_update,
                          parse_leave_time, Stop)

from config_auth import api_key


def exam_get_buses(authed_rtti, route_number=None, all_buses=None):
    all_buses = authed_rtti.buses(route_number=route_number)
    assert len(all_buses) > 0

    if all_buses is not None and all_buses:
        return all_buses

    # BUG: 5 digit bus numbers are real, but we can't ask RTTI API for one.
    buses_with_usable_id = filter(lambda b: len(b.VehicleNo) <= 4, all_buses)
    #arbitrary_first_bus = next(buses_with_usable_id)

    all_usables = [x for x in buses_with_usable_id]
    assert len(all_usables) > 0

    arbitrary_first_bus = all_usables[0]
    bus = authed_rtti.bus(arbitrary_first_bus.VehicleNo)
    assert bus.VehicleNo == arbitrary_first_bus.VehicleNo

    return all_usables

def exam_route(authed_rtti, route_number, expect_route_number):
    route = authed_rtti.route(route_number)
    assert route.RouteNo == expect_route_number
    return route

def exam_stop_identity(authed_rtti, stop_number=53095):
    stop = authed_rtti.stop('%d' % stop_number)
    assert stop.StopNo == stop_number
    return stop

def exam_stops_with_results(authed_rtti, lat, long, radius, route):
    stops = authed_rtti.stops(lat=lat, long=long, radius_m=radius, route_number=route)
    assert len(stops) > 0
    return stops

def exam_stop_estimates_no_results(authed_rtti, stop_no, route_no):
    if type(stop_no) is int:
        stop_no = "%d" % stop_no
    if type(route_no) is int:
        route_no = "%d" % route_no
    estimates = authed_rtti.stop_estimates(stop_no, route_number=route_no)
    assert len(estimates) > 0
    return estimates


if __name__ == "__main__":
    rtti = RTTI(api_key=api_key)
    while True: # scope

        # example 4, stop info, stop search
        if True:
            lat, lon = None, None   # base lat lon
            target_stop_no = None
            # 58436: lougheed bay 2 bus 152
            #        lat 49.247722, long -122.89515
            # 58434: lougheed bay 10 bus 109, N9
            # 58438: lougheed bay 4 bus 101
            # 53357: coquitlam central bay 9 bus 185 187
            #        lat 49.275316, lon -122.79883
            #        error: code 500
            #        'RTTI OpenAPI is currently experiencing technical issues'
            #        ' and is unavailable, please try again later.'
            #        to fix: add 0.0000011 to avoid the problem.
            # 60390: coq bay 14 bus 173 174
            #        lat 49.275276, lon -122.799074
            base_stop_no = 58436
            target_bus_no = 109
            target_bus_stop_found = None # int

            if type(base_stop_no) is int:
                print("Trying to determine base-stop location ...")
                rv = exam_stop_identity(rtti, stop_number=base_stop_no)
                if type(rv) is Stop:
                    lat = rv.Latitude
                    lon = rv.Longitude
                    # add 0.0000011.
                    # suspect when a float is accurate it hits bug on server sometimes.
                    lat += 0.0000011
                    lon += 0.0000011
                    print("OK !  base-stop at lat %.4f lon %.4f" % (lat, lon))
                else:
                    print("Failed !  base-stop location cannot be determined")
                    break # scope
            if type(lat) is float and type(lon) is float:
                print("Trying to list buses near base-stop location ...")
                rv = exam_stops_with_results(rtti, lat, lon, 100, None)
                if type(rv) is list and len(rv) > 0:
                    print("OK !  list of stops %d" % len(rv))
                    print("Trying to find target bus near base-stop location ...")
                    for x in rv:
                        if type(x) is not Stop:
                            print("Error, ")
                            break
                        # keys: StopNo, Name, BayNo, City, OnStreet, AtStreet, Latitude,
                        #       Longitude, WheelchairAccess, Distance, Routes
                        # Routes e.g.: '109,N9'
                        try:
                            routes = x.Routes
                            if type(routes) is str and len(routes) > 0:
                                tgt_str = "%d" % target_bus_no
                                idx1 = routes.find(tgt_str)
                                if idx1 >= 0:
                                    tmp_stop_no = x.StopNo
                                    if type(tmp_stop_no) is int:
                                        target_bus_stop_found = tmp_stop_no
                        except Exception as ex:
                            print("Exception ", repr(ex), "  with x ", repr(x))
                        except:
                            print("Exception unknown with x ", repr(x))
                        if target_bus_stop_found is not None:
                            break
                    if type(target_bus_stop_found) is int:
                        print("OK !  found target bus stop ", target_bus_stop_found)
                    else:
                        print("Failed !  target bus stop cannot be determined")
                else:
                    print("Failed !  list of stops cannot be determined")
            if type(target_bus_stop_found) is int:
                print("Trying to get next buses ...")
                ests = exam_stop_estimates_no_results(rtti,
                                                      target_bus_stop_found,
                                                      target_bus_no)
                if type(ests) is list and len(ests) > 0:
                    print("OK ! next buses: ")
                    # print(repr(ests))
                    # [StopEstimate(
                    #       RouteNo='109',
                    #       RouteName='NEW WESTMINSTER STN/LOUGHEED STN',
                    #       Direction='SOUTH',
                    #       RouteMap=RouteMap(Href='https://nb.translink.ca/geodata/109.kmz'),
                    #       Schedules=[Schedule(
                    #                   Pattern='SB1', Destination='NEW WEST STN',
                    #                   ExpectedLeaveTime=datetime.datetime(
                    #                       2024, 11, 19, 10, 31,
                    #                       tzinfo=<DstTzInfo 'America/Vancouver' PST-1 day,
                    #                               16:00:00 STD>),
                    #                   ExpectedCountdown=34, ScheduleStatus=' ', CancelledTrip=False,
                    #                   CancelledStop=False, AddedTrip=False, AddedStop=False,
                    #                   LastUpdate=datetime.datetime(
                    #                       2024, 11, 18, 9, 42, 48,
                    #                       tzinfo=<DstTzInfo 'America/Vancouver' PST-1 day,
                    #                               16:00:00 STD>)
                    #                          ),
                    #                  Schedule(
                    #                   Pattern='SB1', Destination='NEW WEST STN',
                    #                   ExpectedLeaveTime=datetime.datetime(
                    #                       2024, 11, 19, 11, 31,
                    #                       tzinfo=<DstTzInfo 'America/Vancouver' PST-1 day,
                    #                               16:00:00 STD>),
                    #                   ExpectedCountdown=94, ScheduleStatus='*', CancelledTrip=False,
                    #                   CancelledStop=False, AddedTrip=False, AddedStop=False,
                    #                   LastUpdate=datetime.datetime(
                    #                       2024, 11, 17, 12, 5, 3,
                    #                       tzinfo=<DstTzInfo 'America/Vancouver' PST-1 day,
                    #                               16:00:00 STD>)
                    #                           )
                    #                 ]
                    #              )]
                else:
                    print("Failed ! next buses")

        # example 3 # route info
        if False:
            rv = exam_route(rtti, '144', '144')
            print("Ok !")

        # example 2, all buses with routeNo=144
        if False:
            rv = exam_get_buses(rtti, route_number="144", all_buses=True)
            if type(rv) is list and len(rv) > 0:
                print("OK !  %d buses" % len(rv))
            else:
                print("Failed !")
                break # scope

        # example 1, all usable buses
        if False:
            rv = exam_get_buses(rtti)
            if type(rv) is list and len(rv) > 0:
                print("OK !  %d buses" % len(rv))
            else:
                print("Failed !")
                break # scope


        break # scope

