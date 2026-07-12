import random
import string

class IdentityGenerator:
    def __init__(self):
        self.adjectives = ["Swift", "Silent", "Shadow", "Neon", "Cyber", "Mystic", "Frost", "Blaze", "Iron", "Lunar", "Solar", "Void", "Ethereal", "Grim", "Radiant"]
        self.nouns = ["Hunter", "Ghost", "Rider", "Blade", "Wolf", "Raven", "Knight", "Storm", "Pulse", "Echo", "Titan", "Viper", "Dragon", "Phoenix", "Specter"]
        self.first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
        self.last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

    def generate_username(self, length=10, use_numbers=True, use_special=False):
        base = random.choice(self.adjectives) + random.choice(self.nouns)
        if len(base) > length: base = base[:length]
        chars = ""
        if use_numbers: chars += string.digits
        if use_special: chars += "!@#$%^&*"
        username = list(base)
        while len(username) < length:
            username.append(random.choice(chars if chars else string.ascii_lowercase))
        return "".join(username)

    def generate_name(self, max_length=15, include_middle=False):
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        middle = f" {random.choice(string.ascii_uppercase)}." if include_middle else ""
        full_name = f"{first}{middle} {last}"
        return full_name[:max_length]

if __name__ == "__main__":
    gen = IdentityGenerator()
    print(f"Username: {gen.generate_username(12)}")
    print(f"Name: {gen.generate_name(20, True)}")
