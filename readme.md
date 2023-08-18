# Autocomplete and Spellchecker
This program provides autocomplete and spellchecking functionality as you type in any application. It uses a trie-based data structure to efficiently search for word suggestions and the `pyspellchecker` library to check for spelling errors.

## Features

- Autocomplete suggestions based on the words in a provided text file
- Spellchecking to correct misspelled words
- Customizable settings to enable/disable autocomplete and spellchecking
- Toggle the program ON/OFF while running
- Accessible settings dialog to change preferences

## Requirements

- Python 3.7 or higher
- PyQt5
- keyboard
- pyspellchecker
-
## Installation

1. Install the required packages:

    pip install PyQt5 keyboard pyspellchecker

2. Download the program files and place them in a folder on your computer.

3. Make sure the `new_words.txt` file is in the same folder as the main script.

4. Run the script:
    
        python newautocorrect4.py

## Usage

1. Run the script as described in the Installation section.

2. A small window will appear with a list of autocomplete suggestions and buttons to access settings and toggle the program ON/OFF.

3. As you type in any application, the program will provide autocomplete suggestions and correct misspelled words.

4. Use the settings dialog to enable/disable autocomplete and spellchecking, and to change the key for accepting autocomplete suggestions.

5. Toggle the program ON/OFF using the "Toggle ON/OFF" button.

## Creating an Executable

To create an executable, follow the instructions provided in this conversation to use `pyinstaller`. Make sure to include the `new_words.txt` file with the resulting executable when distributing it.

## License

This program is provided under the MIT License. See the LICENSE file for more information.