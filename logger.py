import datetime

class CustomLogger:
    def __init__(self, filename="simulation_log.txt"):
        self.log_entries = []
        self.filename = filename

    def log_sound(self, sound):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"{timestamp}: Sound played - {sound}"
        self.log_entries.append(entry)
        self.write_to_file(entry)

    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"{timestamp}: {message}"
        print(entry)
        self.log_entries.append(entry)
        self.write_to_file(entry)

    def display_log(self):
        for entry in self.log_entries:
            print(entry)

    def write_to_file(self, entry):
        with open(self.filename, "a") as file:
            file.write(entry + "\n")

    def save_log(self):
        with open(self.filename, "w") as file:
            for entry in self.log_entries:
                file.write(entry + "\n")