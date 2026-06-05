import json
from pathlib import Path
from datetime import datetime
import shutil


def get_root_folder():

    config_file = Path.home() / ".accident_logger_config.json"

    if config_file.exists():

        with open(config_file, "r") as f:
            config = json.load(f)

        saved_path = Path(config["root_folder"])
        if saved_path.exists():
            return saved_path

        print(
            "\nSaved accident folder no longer exists."
        )
        print("Please choose a new location.\n")

    default_parent = Path.home() / "Documents"

    folder = input(
        f"Enter parent folder for Accident storage [{default_parent}]: "
    ).strip()

    if not folder:
        parent_folder = default_parent
    else:
        parent_folder = Path(folder)

    # Ensure parent folder exists
    parent_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # Create Accidents folder inside parent folder
    root_folder = parent_folder / "Accidents"

    root_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(config_file, "w") as f:

        json.dump(
            {
                "root_folder": str(root_folder)
            },
            f,
            indent=4
        )

    return root_folder


root_folder= get_root_folder()
json_file = root_folder / "accidents.json"
root_folder.mkdir(exist_ok=True)


def load_accidents():

    if not json_file.exists():
        return []

    try:
        with open(json_file, "r") as f:
            return json.load(f)

    except json.JSONDecodeError:
        return []
    

def add_details():

    accident= {}
    accident["recorded_at"] = datetime.now().strftime(
    "%d/%m/%Y %H:%M:%S")
    
    # Get and validate accident date
    date = input("Date of Accident (DD-MM-YYYY): ")

    try:
        accident_date = datetime.strptime(date, "%d-%m-%Y")

        # Store as string because JSON cannot store datetime objects
        accident["date"] = accident_date.strftime("%d-%m-%Y")

    except ValueError:
        print("Invalid date format. Use DD-MM-YYYY.")
        return

    # Basic details
    accident["vehicle_number"] = input("Your Vehicle Number: ").strip().upper()
    accident["place"] = input("Place of Accident: ").strip() 
    accident["injuries"]= input("Any injuries? : ").strip()
    accident["damage"] = input("Vehicle Damage: ").strip()
    accident["wrong_by"] = input("Who was at fault? : ").strip()

    # Compensation amount
    compensation = input("Compensation received as Rs: $").strip()

    if compensation:
        try:
            accident["compensation"] = int(compensation)
        except ValueError:
            print("Invalid compensation amount. Stored as 0.")
            accident["compensation"] = 0
    else:
        accident["compensation"] = 0

    # Other vehicles involved
    other_vehicles = []

    try:
        count = int(input("How many other vehicles were involved? : "))
    except ValueError:
        print("Invalid number. Assuming 0 vehicles.")
        count = 0

    for i in range(count):
        print(f"\nOther Vehicle {i + 1}")

        vehicle = {
            "vehicle_number": input("Vehicle Number: ").strip().upper(),
            "vehicle_type": input("Vehicle Type (Car/Bike/Bus/etc): ").strip(),
            "other_details": input("Other details(like colour): ").strip()
        }

        other_vehicles.append(vehicle)

    accident["other_vehicles"] = other_vehicles

    # Description
    accident["description"] = input("Describe the accident: ").strip()
    return accident


def copy_media(accident_folder):
    media_files = []

    allowed_extensions = [
        ".jpeg", ".jpg", ".png", ".gif",
        ".mp4", ".mov", ".avi", ".mkv"
    ]

    while True:

        media = input(
            "Enter media path (folder or file). Blank to finish: "
        ).strip()

        if not media:
            break

        media = Path(media)

        if not media.exists():
            print("Path does not exist")
            continue

        if media.is_file():

            if media.suffix.lower() in allowed_extensions:

                media_files.append(media.name)
                shutil.copy(media, accident_folder)

            else:
                print("Unsupported file type")

        elif media.is_dir():

            for file in media.iterdir():

                if (
                    file.is_file()
                    and file.suffix.lower() in allowed_extensions
                ):

                    media_files.append(file.name)
                    shutil.copy(file, accident_folder)

    return media_files


def save_accident():
    accident= add_details()
    accidents = load_accidents()
    if accident is None:
        return 
    
    # Generate accident ID
    accident["id"] = len(accidents) + 1

    accident_folder=root_folder / f"Accident_{accident['id']}_{accident['date']}"
    accident_folder.mkdir(parents=True, exist_ok=True)
    media_files = copy_media(accident_folder)
    
    accident["folder"]=accident_folder.name
    accident["media_files"]= media_files
    accident["media_count"]= len(media_files)

    detail_file=accident_folder / "details.txt"
    with open(detail_file,"w") as f:
        for key, value in accident.items():
            f.write(f"{key}: {value}\n")

    # Add accident to list
    accidents.append(accident)

    # Save updated list
    with open(json_file, "w") as f:
        json.dump(accidents, f, indent=4)

    print("\nAccident record saved successfully.")
    print(f"Accident ID: {accident['id']}")


def show_details():
    accidents = load_accidents()

    if not accidents:
        print("-" * 50)
        print("No accident records found.")
        return

    print()
    print()
    print(f"{'ID':<5}{'Date':<12}{'Vehicle':<15}{'Injuries':<20}{'Damage':<20}{'Place'}")


    print("-" * 80)

    for accident in accidents:
        print(
            f"{accident['id']:<5}"
            f"{accident['date']:<12}"
            f"{accident['vehicle_number']:<15}"
            f"{accident['injuries']:<20}"
            f"{accident['damage']:<20}"
            f"{accident['place']}"
        )


def display_accident(found):

    print("\n" + "=" * 50)
    print("ACCIDENT DETAILS")
    print("=" * 50)

    print(f"ID              : {found['id']}")
    print(f"Recorded At     : {found['recorded_at']}")
    print(f"Date            : {found['date']}")
    print(f"Vehicle Number  : {found['vehicle_number']}")
    print(f"Place           : {found['place']}")
    print(f"Injuries        : {found['injuries']}")
    print(f"Damage          : {found['damage']}")
    print(f"Wrong By        : {found['wrong_by']}")
    print(f"Compensation    : {found['compensation']}")
    print(f"Description     : {found['description']}")

    print("\nOTHER VEHICLES")
    print("-" * 50)

    if found["other_vehicles"]:

        for i, vehicle in enumerate(
            found["other_vehicles"],
            start=1
        ):

            print(f"\nVehicle {i}")
            print(
                f"Number : "
                f"{vehicle['vehicle_number']}"
            )
            print(
                f"Type   : "
                f"{vehicle['vehicle_type']}"
            )
            print(
                f"Details: "
                f"{vehicle['other_details']}"
            )

    else:
        print("None")

    print("\nMEDIA FILES")
    print("-" * 50)

    if found["media_files"]:

        for media in found["media_files"]:
            print(media)

    else:
        print("No media files")

    print("\nFOLDER")
    print("-" * 50)
    print(found["folder"])


def search_accident():

    accidents = load_accidents()

    result = []
    criteria = {}

    id_input = input(
        "Search by Accident ID (leave blank to skip): "
    ).strip()

    if id_input:
        criteria["id"] = int(id_input)

    vehicle = input(
        "Vehicle Number (leave blank to skip): "
    ).strip().upper()

    if vehicle:
        criteria["vehicle_number"] = vehicle

    place = input(
        "Place (leave blank to skip): "
    ).strip()

    if place:
        criteria["place"] = place.lower()

    injuries = input(
        "Injuries keyword (leave blank to skip): "
    ).strip()

    if injuries:
        criteria["injuries"] = injuries.lower()

    damage = input(
        "Damage keyword (leave blank to skip): "
    ).strip()

    if damage:
        criteria["damage"] = damage.lower()

    for accident in accidents:

        match = True

        for key, value in criteria.items():

            if key == "id":

                if accident["id"] != value:
                    match = False
                    break

            elif key in (
                "place",
                "injuries",
                "damage"
            ):

                if (
                    value.lower()
                    not in accident[key].lower()
                ):
                    match = False
                    break

            else:

                if accident[key] != value:
                    match = False
                    break

        if match:
            result.append(accident)

    if not result:
        print("\nNo matching accidents found.")
        print()
        return

    print(
        f"\nFound {len(result)} matching accident(s).\n"
    )

    for accident in result:
        display_accident(accident)


def menu():

    while True:
        
        show_details()

        print("\n=== ACCIDENT LOGGER ===")
        print("1. Add Accident")
        print("2. Search Accident")
        print("3. Exit")

        choice = input("Choice: ")
        print()

        if choice == "1":
            save_accident()

        elif choice == "2":
            search_accident()

        elif choice == "3":
            break

        else:
            print("Invalid choice")


menu()