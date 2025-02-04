import os

dicoCorrespondance = {
    "R11": {"idRouter": "0cd5e6e8-a314-4976-9af0-73cee44fe070", "id": "i11"},
    "R12": {"idRouter": "805e7a1b-26e1-4e17-bde0-08089b23471b", "id": "i3"},
    "R13": {"idRouter": "63a70cc7-808d-44bf-9474-dcc3db5fba1d", "id": "i2"},
    "R14": {"idRouter": "250ff1dd-e98e-4993-a470-26f8e4764d19", "id": "i1"},
    "R15": {"idRouter": "dd178519-b796-4ab6-9650-05224036e5c7", "id": "i6"},
    "R16": {"idRouter": "af01ad7b-85a9-4d4c-8aeb-06dd90076d06", "id": "i5"},
    "R17": {"idRouter": "dcb179f0-d0eb-46d6-a640-d62464aaef15", "id": "i4"},
    "R21": {"idRouter": "e6389003-fc98-442b-86a9-863d32cd7748", "id": "i8"},
    "R22": {"idRouter": "8e0c8e39-237e-41b1-bbfe-577c0ab91c7b", "id": "i10"},
    "R23": {"idRouter": "32d9435a-d76e-4f14-b795-b2a0f8f901ff", "id": "i12"},
    "R24": {"idRouter": "aba60752-e158-4541-bd31-1fea77dd93b4", "id": "i14"},
    "R25": {"idRouter": "264d0e64-32f6-4c1d-8407-e36e5835d9fc", "id": "i13"},
    "R26": {"idRouter": "c7a642de-4fb0-471a-b951-55e818dda8b4", "id": "i7"},
    "R27": {"idRouter": "7b6bdd45-c3fc-4ae1-b1f9-3b8f51e3af9e", "id": "i9"},
}

def generateFolders(path):
    for router, data in dicoCorrespondance.items():
        folder_path = os.path.join(path, data["idRouter"])
        if os.path.exists(folder_path):
            os.rmdir(folder_path)
        os.makedirs(folder_path)

        
# def generateRouter():
# 	file = intentToConfig.generate_router_config

def dragAndDropRouter(router, path, config):
    if router in dicoCorrespondance:
        router_data = dicoCorrespondance[router]
        print(router_data["idRouter"])  
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, f"{router_data['id']}_startup-config.cfg")
        with open(file_path, "w") as file:
            file.write(config)

        
# generateFolders("C:/Users/etulyon1/Documents/INSA/TC3/GNS/GnsProjectCode")