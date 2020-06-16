from colorama import Fore, Style


def colour(colour, message):
    colours = {"green": Fore.GREEN, "blue": Fore.BLUE, "red": Fore.RED, "yellow": Fore.YELLOW}
    return colours[colour] + str(message) + Style.RESET_ALL
