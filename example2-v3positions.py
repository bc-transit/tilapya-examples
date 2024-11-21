
# 2024-11-19

from config_auth import api_key

from google.transit import gtfs_realtime_pb2
import requests


base_url="https://gtfsapi.translink.ca/v3"

pos_url="%s/gtfsposition?apikey=%s" % (base_url, api_key)
trip_url="%s/gtfsrealtime?apikey=%s" % (base_url, api_key)

feed_url=trip_url
feed_url=pos_url

feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get(feed_url)
feed.ParseFromString(response.content)

if type(response.content) is bytes:
  log_resp_msg = "response bytes size: %d" % len(response.content)
else:
  log_resp_msg = "response not bytes: %s" % str(type(response.content))

entity_count = 0
for entity in feed.entity:
  entity_count += 1
  if entity.HasField('trip_update'):
    print(entity.trip_update)

print("entity_count: ", entity_count)
print(log_resp_msg)


''' 1st entity for: pos_url, count 1094, size 100k+
id: "14121555"
vehicle {
  trip {
    trip_id: "14121555"
    start_date: "20241119"
    schedule_relationship: SCHEDULED
    route_id: "30055"
    direction_id: 0
  }
  position {
    latitude: 49.2865486
    longitude: -123.140617
  }
  current_stop_sequence: 1
  current_status: IN_TRANSIT_TO
  timestamp: 1732034580
  stop_id: "1"
  vehicle {
    id: "19533"
    label: "19533"
  }
}
'''

''' 1st entity for: trip_url, count 959, bytes 800k+
id: "13997563"
is_deleted: false
trip_update {
  trip {
    trip_id: "13997563"
    start_date: "20241119"
    schedule_relationship: SCHEDULED
    route_id: "6612"
    direction_id: 0
  }
  stop_time_update {
    stop_sequence: 24
    arrival {
      delay: 392
      time: 1732035098
    }
    departure {
      delay: 392
      time: 1732035098
    }
    stop_id: "73"
    schedule_relationship: SCHEDULED
  }
  stop_time_update {
    stop_sequence: 25
    arrival {
      delay: 432
      time: 1732035194
    }
    departure {
      delay: 432
      time: 1732035194
    }
    stop_id: "75"
    schedule_relationship: SCHEDULED
  }
  stop_time_update {
    stop_sequence: 26
    arrival {
      delay: 514
      time: 1732035359
    }
    departure {
      delay: 514
      time: 1732035359
    }
    stop_id: "29"
    schedule_relationship: SCHEDULED
  }
  stop_time_update {
    stop_sequence: 27
    arrival {
      delay: 541
      time: 1732035419
    }
    departure {
      delay: 541
      time: 1732035419
    }
    stop_id: "12603"
    schedule_relationship: SCHEDULED
  }
  stop_time_update {
    stop_sequence: 28
    arrival {
      delay: 570
      time: 1732035489
    }
    departure {
      delay: 570
      time: 1732035489
    }
    stop_id: "30"
    schedule_relationship: SCHEDULED
  }
  stop_time_update {
    stop_sequence: 29
    arrival {
      delay: 602
      time: 1732035557
    }
    departure {
      delay: 602
      time: 1732035557
    }
    stop_id: "31"
    schedule_relationship: SCHEDULED
  }
  vehicle {
    id: "21017"
    label: "21017"
  }
}
'''

