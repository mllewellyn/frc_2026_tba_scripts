from secrets import TBA_API_KEY
import csv
from typing import Dict

from downloader import TBADataDownloader

BASE_URL = 'https://www.thebluealliance.com/api/v3'
YEAR = 2026


def get_2026_rankings():
    headers = {'X-TBA-Auth-Key': TBA_API_KEY}
    team_climb_totals: Dict[str, int] = {}
    # per-team climb type counts: team_key -> counts dict
    team_climb_counts: Dict[str, Dict[str, int]] = {}
    # (traversal_achieved, total_climb_points, event_code, match_id, color, teams, auto_points,
    #  endgame_points, description)
    match_climb_descriptions = []

    downloader = TBADataDownloader(BASE_URL, headers)

    event_keys = downloader.get_completed_event_keys(YEAR)
    if not event_keys:
        print(f"No completed events found for {YEAR}.")
        return

    for event_key in event_keys:
        matches = downloader.get_event_matches(event_key)
        if not matches:
            continue

        for match in matches:
            breakdown = match.get('score_breakdown')
            if not breakdown:
                continue

            match_key = match.get('key', 'unknown_match')
            for color in ['red', 'blue']:
                color_breakdown = breakdown.get(color) or {}
                traversal_achieved = bool(color_breakdown.get('traversalAchieved'))

                teams = match['alliances'][color]['team_keys']

                # Build a human-readable description of how points were scored
                auto_states = [
                    color_breakdown.get('autoTowerRobot1', 'None'),
                    color_breakdown.get('autoTowerRobot2', 'None'),
                    color_breakdown.get('autoTowerRobot3', 'None'),
                ]
                endgame_states = [
                    color_breakdown.get('endGameTowerRobot1', 'None'),
                    color_breakdown.get('endGameTowerRobot2', 'None'),
                    color_breakdown.get('endGameTowerRobot3', 'None'),
                ]

                # Allocate per-robot points based on 2026 game rules
                per_team_points = {team: 0 for team in teams}

                # Ensure per-team counters exist
                for team in teams:
                    if team not in team_climb_counts:
                        team_climb_counts[team] = {
                            "auto": 0,
                            "level1": 0,
                            "level2": 0,
                            "level3": 0,
                        }

                # Auto: 15 points per robot that climbed in auto
                for idx, state in enumerate(auto_states):
                    if state != "None" and idx < len(teams):
                        team_key = teams[idx]
                        per_team_points[team_key] += 15
                        team_climb_counts[team_key]["auto"] += 1

                # Endgame: 10/20/30 for Level1/2/3 climbs
                endgame_point_map = {
                    "Level1": ("level1", 10),
                    "Level2": ("level2", 20),
                    "Level3": ("level3", 30),
                }
                for idx, state in enumerate(endgame_states):
                    if idx < len(teams) and state in endgame_point_map:
                        bucket, pts = endgame_point_map[state]
                        team_key = teams[idx]
                        per_team_points[team_key] += pts
                        team_climb_counts[team_key][bucket] += 1

                total_climb_points = sum(per_team_points.values())

                # Skip if no robot climbed in auto or endgame
                if total_climb_points == 0:
                    continue

                auto_points = sum(15 for state in auto_states if state != "None")
                endgame_points = sum(
                    endgame_point_map[state][1] for state in endgame_states if state in endgame_point_map
                )

                traversal_flag = " [TRAVERSAL RP]" if traversal_achieved else ""
                event_code = event_key
                match_id = match_key
                desc = (
                    f"match={match_id} {color.upper()} teams={','.join(teams)} – "
                    f"auto tower {auto_points} (R1={auto_states[0]}, R2={auto_states[1]}, R3={auto_states[2]}), "
                    f"endgame tower {endgame_points} (R1={endgame_states[0]}, R2={endgame_states[1]}, R3={endgame_states[2]})"
                    f"{traversal_flag}"
                )
                match_climb_descriptions.append(
                    (
                        traversal_achieved,
                        total_climb_points,
                        event_code,
                        match_id,
                        color,
                        ",".join(teams),
                        auto_points,
                        endgame_points,
                        desc,
                    )
                )

                for team, points in per_team_points.items():
                    if points != 0:
                        team_climb_totals[team] = team_climb_totals.get(team, 0) + points

    # Sort match descriptions: traversal RP first, then by total climb points (descending)
    match_climb_descriptions.sort(key=lambda item: (not item[0], -item[1]))

    print("\nMatch climb breakdowns (Traversal RP first, highest climb points first):")
    for (
        traversal_achieved,
        total_climb_points,
        event_code,
        match_id,
        color,
        teams_csv,
        auto_points,
        endgame_points,
        line,
    ) in match_climb_descriptions:
        if traversal_achieved:
            print(line)

    # Sort teams by total points descending
    sorted_teams = sorted(team_climb_totals.items(), key=lambda item: item[1], reverse=True)

    print(f"\n{'Rank':<5} | {'Team':<10} | {'Total Robot Climb Points'}")
    print("-" * 45)
    for rank, (team, total) in enumerate(sorted_teams[:10], 1):
        # Format team key (frc1234 -> 1234)
        print(f"{rank:<5} | {team[3:]:<10} | {total}")

    # Write CSV with match-level results
    with open("match_climbs.csv", "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "traversal_achieved",
                "total_climb_points",
                "event",
                "match",
                "alliance_color",
                "teams",
                "auto_points",
                "endgame_points",
                "description",
            ]
        )
        for row in match_climb_descriptions:
            writer.writerow(row)

    # Write CSV with team-level aggregate results, including climb type counts
    with open("team_climbs.csv", "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "rank",
                "team_key",
                "team_number",
                "total_climb_points",
                "auto_climbs",
                "endgame_level1_climbs",
                "endgame_level2_climbs",
                "endgame_level3_climbs",
            ]
        )
        for rank, (team, total) in enumerate(sorted_teams, 1):
            counts = team_climb_counts.get(
                team,
                {
                    "auto": 0,
                    "level1": 0,
                    "level2": 0,
                    "level3": 0,
                },
            )
            writer.writerow(
                [
                    rank,
                    team,
                    team[3:],
                    total,
                    counts["auto"],
                    counts["level1"],
                    counts["level2"],
                    counts["level3"],
                ]
            )


if __name__ == "__main__":
    get_2026_rankings()