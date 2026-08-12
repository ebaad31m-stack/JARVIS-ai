import json
import os

from core.paths import user_file


CONTACTS_FILE = user_file("contacts.json")


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
        print(
            "Contacts load error:",
            error
        )
        return {}


def save_contacts(contacts):
    folder = os.path.dirname(CONTACTS_FILE)

    os.makedirs(
        folder,
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

    save_contacts(
        contacts
    )

    return True


def remove_contact(name):
    contacts = load_contacts()

    name = name.lower().strip()

    if name not in contacts:
        return False

    del contacts[name]

    save_contacts(
        contacts
    )

    return True


def resolve_recipient(value):
    value = value.strip()

    if "@" in value:
        return value

    contacts = load_contacts()

    return contacts.get(
        value.lower()
    )