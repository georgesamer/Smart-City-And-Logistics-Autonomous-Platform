from models.map_graph import CityGridMap
from perception.vision_engine import VisionEngine


def test_vision_keeps_blocked_destination_accessible():
    city_map = CityGridMap(
        [
            [".", ".", ".", ".", "G"],
            [".", ".", ".", ".", "."],
            [".", ".", ".", "T", "."],
            ["V1", ".", "X", ".", "V2"],
        ]
    )

    updated = VisionEngine(city_map).verify_and_update_map((0, 4), "camera_feed_accident_block.png")

    # The verified target must remain reachable: classify it as traffic ('T'), not a hard obstacle ('X')
    assert updated is True
    assert city_map.grid[0][4] == "T"


def test_vision_marks_traffic_destination_as_traffic():
    city_map = CityGridMap(
        [
            [".", ".", ".", ".", "G"],
            [".", ".", ".", ".", "."],
            [".", ".", ".", "T", "."],
            ["V1", ".", "X", ".", "V2"],
        ]
    )

    updated = VisionEngine(city_map).verify_and_update_map((0, 4), "camera_feed_traffic_jam.png")

    assert updated is True
    assert city_map.grid[0][4] == "T"
