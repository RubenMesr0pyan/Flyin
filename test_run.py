from fly_in.parser import MapParser

parser = MapParser()
parsed_map = parser.parse("maps/example.txt")

print(f"Drones: {parsed_map.nb_drones}")
print(f"Start hub: {parsed_map.start_hub}")
print(f"End hub: {parsed_map.end_hub}")
print(f"Total zones: {parsed_map.graph.zone_count()}")
print(f"Total connections: {parsed_map.graph.connection_count()}")