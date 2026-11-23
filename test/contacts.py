"""Contact Book — the Phase 11 mini-boss.

A small practice program for classes and `self`, built
before refactoring FRIDAY itself. Run it directly to try
it:  python contacts.py
"""


class Contact:
    """One person: a name plus optional phone and email."""

    def __init__(self, name, phone="", email=""):
        self.name = name
        self.phone = phone
        self.email = email

    def __str__(self):
        parts = [self.name]
        if self.phone:
            parts.append(f"phone {self.phone}")
        if self.email:
            parts.append(f"email {self.email}")
        return " — ".join(parts)


class ContactBook:
    """Holds contacts; add / search / delete by name."""

    def __init__(self):
        self.contacts = {}

    def add(self, name, phone="", email=""):
        self.contacts[name.lower()] = Contact(name, phone, email)
        return f"Saved {name}."

    def search(self, name):
        return self.contacts.get(name.lower())

    def delete(self, name):
        return self.contacts.pop(name.lower(), None)

    def list_all(self):
        if not self.contacts:
            return "No contacts yet."
        return "\n".join(str(contact) for contact in self.contacts.values())


if __name__ == "__main__":
    book = ContactBook()
    print("Contact Book — try: add, search, list, delete, quit")
    while True:
        try:
            choice = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not choice:
            continue
        low = choice.lower()
        if low == "quit":
            break
        elif low == "list":
            print(book.list_all())
        elif low.startswith("add "):
            parts = choice[4:].split()
            if not parts:
                print("Usage: add Name phone email")
            else:
                name = parts[0]
                phone = parts[1] if len(parts) > 1 else ""
                email = parts[2] if len(parts) > 2 else ""
                print(book.add(name, phone, email))
        elif low.startswith("search "):
            hit = book.search(choice[7:].strip())
            print(hit if hit else "Not found.")
        elif low.startswith("delete "):
            gone = book.delete(choice[7:].strip())
            print(f"Deleted {gone}." if gone else "Not found.")
        else:
            print("Commands: add, search, list, delete, quit")
