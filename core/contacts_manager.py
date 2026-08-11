import json
import os


CONTACTS_FILE = "data/contacts.json"


def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return {}

    try:
        with open(
            CONTACTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception as error:
        print("Contacts load error:", error)
        return {}


def save_contacts(contacts):
    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        CONTACTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            contacts,
            file,
            indent=4
        )


def add_contact(name, email):
    contacts = load_contacts()

    name = name.lower().strip()
    email = email.strip()

    contacts[name] = email

    save_contacts(contacts)

    return True


def remove_contact(name):
    contacts = load_contacts()

    name = name.lower().strip()

    if name not in contacts:
        return False

    del contacts[name]

    save_contacts(contacts)

    return True


def resolve_recipient(value):
    value = value.strip()

    # User typed an actual email address.
    if "@" in value:
        return value

    contacts = load_contacts()

    return contacts.get(
        value.lower()
    )