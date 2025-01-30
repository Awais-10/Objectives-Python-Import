import requests

# API tokens for the two workspaces
WORKSPACE_1_API_TOKEN = "97c8bd15-ae87-4587-ac01-ab12e87d60bb"
WORKSPACE_2_API_TOKEN = "d87e567e-7135-486e-a054-f22d5d06c55e"

# Base URLs for the API
BASE_URL = "https://api.app.shortcut.com/api/v3"

# Headers for API requests
HEADERS_WORKSPACE_1 = {
    "Shortcut-Token": WORKSPACE_1_API_TOKEN,
    "Content-Type": "application/json"
}
HEADERS_WORKSPACE_2 = {
    "Shortcut-Token": WORKSPACE_2_API_TOKEN,
    "Content-Type": "application/json"
}


def get_objectives():
    url = f"{BASE_URL}/objectives"
    response = requests.get(url, headers=HEADERS_WORKSPACE_1)
    response.raise_for_status()
    return response.json()


def get_epics_for_objective(objective_id):
    url = f"{BASE_URL}/objectives/{objective_id}/epics"
    response = requests.get(url, headers=HEADERS_WORKSPACE_1)
    response.raise_for_status()
    return response.json()


def get_stories_for_epic(epic_id):
    url = f"{BASE_URL}/epics/{epic_id}/stories"
    response = requests.get(url, headers=HEADERS_WORKSPACE_1)
    response.raise_for_status()
    return response.json()


def post_objectives(objective_data):
    url = f"{BASE_URL}/objectives"
    response = requests.post(url, json=objective_data, headers=HEADERS_WORKSPACE_2)
    response.raise_for_status()
    return response.json()


def post_epics(epic_data):
    url = f"{BASE_URL}/epics"
    response = requests.post(url, json=epic_data, headers=HEADERS_WORKSPACE_2)
    if response.status_code != 200:
        print("Error Response:", response.json())
    response.raise_for_status()
    return response.json()


def post_stories_bulk(stories_data):
    url = f"{BASE_URL}/stories/bulk"
    response = requests.post(url, json=stories_data, headers=HEADERS_WORKSPACE_2)
    response.raise_for_status()
    return response.json()


def main():
    # Part 1: Gather data from Workspace 1
    objectives = get_objectives()
    print("Fetched Objectives")

    objectives_mapping = {}
    epics_mapping = {}
    all_epics = {}

    # Fetch all epics for each objective
    for objective in objectives:
        objective_id = objective["id"]
        objectives_mapping[objective_id] = None  # Placeholder for new ID
        epics = get_epics_for_objective(objective_id)
        print(f"Fetched {len(epics)} epics for objective {objective_id}")
        for epic in epics:
            if epic["id"] not in all_epics:
                all_epics[epic["id"]] = epic  # Store unique epics

    print("All Epics:", all_epics)

    # Fetch all stories for each epic
    all_stories = {}
    for epic_id, epic in all_epics.items():
        stories = get_stories_for_epic(epic_id)
        print(f"Fetched {len(stories)} stories for epic {epic_id}")
        all_stories[epic_id] = stories

    # Part 2: Create entities in Workspace 2
    for objective in objectives:
        new_objective = {
            "name": objective["name"],
            "description": objective.get("description"),
            "state": objective["state"]
        }
        created_objective = post_objectives(new_objective)
        objectives_mapping[objective["id"]] = created_objective["id"]

    for epic_id, epic in all_epics.items():
        new_epic = {
            "name": epic["name"],
            "description": epic.get("description", ""),
            "objective_ids": [objectives_mapping[epic["objective_id"]]] if "objective_id" in epic else [],
            "created_at": epic["created_at"],
            "updated_at": epic["updated_at"],
            "planned_start_date": epic.get("planned_start_date"),
            "deadline": epic.get("deadline"),
        }
        print(f"Posting Epic: {new_epic}")  # Log the payload
        created_epic = post_epics(new_epic)
        epics_mapping[epic_id] = created_epic["id"]

    stories_bulk = []
    for epic_id, stories in all_stories.items():
        for story in stories:
            new_story = {
                "name": story["name"],
                "description": story.get("description"),
                "story_type": story["story_type"],
                "epic_id": epics_mapping[epic_id],
                "created_at": story["created_at"],
                "updated_at": story["updated_at"],
                "workflow_state_id": 500000007,
                "tasks": [{
                    "description": task["description"],
                    "complete": task["complete"]
                } for task in story.get("tasks", [])],
                "comments": [{
                    "text": comment["text"],
                    "created_at": comment["created_at"],
                    "updated_at": comment["updated_at"],
                    "parent_id": comment["parent_id"]
                } for comment in story.get("comments", [])]
            }
            stories_bulk.append(new_story)

    print(f"Posting {len(stories_bulk)} stories in bulk")
    post_stories_bulk({"stories": stories_bulk})


if __name__ == "__main__":
    main()
