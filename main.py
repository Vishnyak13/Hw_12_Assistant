from collections import UserDict
from typing import List, Tuple
from datetime import date, datetime
import re
import pickle, csv


class Field:
    def __init__(self, value) -> None:
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):
    @Field.value.setter
    def value(self, name: str):
        if not isinstance(name, str):
            raise TypeError('The name must be a string!')
        if not re.match(r"^[a-zA-Z]{1,16}$", name):
            raise ValueError('The name must contain only letters up to 16 characters long!')
        self._value = name


class Phone(Field):
    @Field.value.setter
    def value(self, phone: str):
        if not isinstance(phone, str):
            raise TypeError('The phone must be a string!')
        if not re.match(r'^[0-9]{10}$', phone):
            raise ValueError('Phone number must be 10 digits!')
        self._value = phone


class Birthday(Field):
    @Field.value.setter
    def value(self, value: str):
        try:
            self._value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError('Incorrect date format, try format: DD.MM.YYYY')

    def __repr__(self):
        return f"{self.value}"


class Record:
    def __init__(self, name: Name, phones: List[Phone] = [], birthday: Birthday = None) -> None:
        self.name = name
        self.phones = phones
        self.birthday = birthday

    def add_phone(self, phone: Phone) -> Phone | None:
        if phone.value not in [ph.value for ph in self.phones]:
            self.phones.append(phone)
            return phone

    def del_phone(self, phone: Phone) -> None:
        for ph in self.phones:
            if ph.value == phone.value:
                self.phones.remove(ph)
                return ph

    def change_phone(self, phone, new_phone) -> Tuple[Phone, Phone] | None:
        if self.del_phone(phone):
            self.add_phone(new_phone)
            return phone, new_phone

    def add_birthday(self, birthday: Birthday):
        if birthday:
            self.birthday = birthday

    def days_to_birthday(self):
        date_now = date.today()
        birth_day = date(date_now.year, self.birthday.value.month, self.birthday.value.day)
        if birth_day < date_now:
            birth_day = date(date_now.year + 1, self.birthday.value.month, self.birthday.value.day)
        return (birth_day - date_now).days

    def __repr__(self):
        if self.birthday:
            return f'{", ".join([ph.value for ph in self.phones])} Birthday: {self.birthday}'
        return f'{", ".join([ph.value for ph in self.phones])}'


class AddressBook(UserDict):
    def add_record(self, record: Record) -> Record | None:
        if not self.data.get(record.name.value):
            self.data[record.name.value] = record
            return record

    def del_record(self, key: str) -> Record | None:
        rec_del = self.data.get(key)
        if rec_del:
            self.data.pop(key)
            return rec_del

    def iterator(self, n=2):
        step = 0
        result = '_' * 20 + '\n'
        for k, v in self.data.items():
            result += f'{k} {v}\n'
            step += 1
            if step >= n:
                yield result
                result = '_' * 20 + '\n'
                step = 0
        yield result

    def to_find(self, value):
        result = []
        for k, v in self.data.items():
            v = str(v)
            [result.append(f'{k.title()} {v}') for i in value if i in v]
        return result

    def save_file(self):
        with open('my_AddressBook', 'wb') as f:
            pickle.dump(self, f)
        with open('my_AddressBook.csv', 'w') as f:
            writer = csv.writer(f)
            for k, v in self.data.items():
                writer.writerow([k, v])

    def load_file(self):
        try:
            with open('my_AddressBook', "rb") as f:
                self.data = pickle.load(f)
            with open('my_AddressBook.csv', 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    return row
        except FileNotFoundError:
            return 'File not found!'


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Please enter the contact in the format:\nName: phone number"
        # except ValueError:
        #     return "Incorrectly entered command!"
        except KeyError:
            return "Contact not found"

    return inner


def unknown_command(*args):
    return "Unknown command, try again or write 'help'!"


def greeting(*args):
    return "Hello! How can I help you?"


def to_exit(*args):
    return "Good bye!"


contact_dict = AddressBook()


@input_error
def add_contact(*args):
    rec = Record(Name(args[0]), [Phone(args[1])])
    contact_dict.add_record(rec)
    try:
        rec.add_birthday(Birthday(args[2]))
    except IndexError:
        birthday = None
    return f"Contact {rec.name.value} has added successfully."


@input_error
def change_phone(*args):
    rec = contact_dict.get(args[0])
    if rec:
        rec.change_phone(Phone(args[1]), Phone(args[2]))
        return f'Contact {rec.name.value} has changed successfully.'
    return f'Contact, with name {args[0]} not in contacts list.'


@input_error
def remove_contact(*args):
    rec = contact_dict.get(args[0])
    if rec:
        rec.del_phone(Phone(args[1]))
        return f'Contact {args[1]} has deleted successfully from contact {rec.name.value}.'
    return f'Contact, with name {args[0]} not in contacts list.'


@input_error
def print_phone(*args):
    return contact_dict[args[0]]


def show_all(*args):
    # return "\n".join([f"{key.title()}: {value}" for key, value in contact_dict.items()]) if len(
    #     contact_dict) > 0 else 'Contacts are empty'
    if not contact_dict:
        return 'Contacts are empty'
    result = "List of contacts:\n"
    print_result = contact_dict.iterator()
    for line in print_result:
        result += line
    return result


@input_error
def find(*args):
    print_str = ''
    for i in contact_dict.to_find(args):
        print_str += f'{i}\n'
    return print_str[:-1] if print_str else 'Sorry, nothing found!'


@input_error
def days_to_births(*args):
    rec = contact_dict.get(args[0])
    if rec:
        return f'Contact {rec.name.value.title()} has {rec.days_to_birthday()} days to birthday.'
    return f'Contact {args[0]} not in notebook.'


def help():
    return """
Enter "hello", "hi" for greeting
Enter "add", "new" for add new contact
Enter "change", "replace" for change phone
Enter "phone", "number" for find phone
Enter "show all", "show" for show all contacts
Enter "good bye", "close", "exit", ".", "bye", "stop" for exit exit the program
Enter "del", "delete", "remove" for delete contact
Enter "birth", "show birth", "days" to display a list of contacts with birthdays
Enter "find", "search" for find contact
Enter "help" to open a list of all commands
"""


commands = {
    greeting: ["hello", "hi"],
    add_contact: ["add", "new"],
    change_phone: ["change", "replace"],
    print_phone: ["phone", "number"],
    days_to_births: ["birth", "show birth", "days"],
    show_all: ["show all", "show"],
    to_exit: ["good bye", "close", "exit", ".", "bye", "stop"],
    remove_contact: ["del", "delete", "remove"],
    find: ["find", "search"],
    help: ["help"]
}


def input_parser(user_input):
    for key, values in commands.items():
        for i in values:
            if user_input.lower().startswith(i.lower()):
                return key, user_input[len(i):].strip().split()
    return unknown_command, []


def main():
    contact_dict.load_file()
    while True:
        user_input = input('Waiting your command:>>> ')
        command, parser_data = input_parser(user_input)
        print(command(*parser_data))
        if command is to_exit:
            contact_dict.save_file()
            break


if __name__ == "__main__":
    main()
