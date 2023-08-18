import sys
import keyboard
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListWidget, QPushButton, QCheckBox, QComboBox, QDialog, QLabel
from spellchecker import SpellChecker
import time
import string
import os

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

#class that saves the words lists to variables
class WordList:
    def __init__(self, name, file):
        self.name = name
        self.file = file
        self.words = []
        self.trie = None
        self.dir = os.path.join(script_dir, file)
    
    def get_name(self):
        return self.name
    
    def get_file(self):
        return self.file
    
    def get_words(self):
        return self.words
    
    def set_words(self, words):
        self.words = words
    
    def get_trie(self):
        return self.trie
    
    def set_trie(self, trie):
        self.trie = trie

    def get_dir(self):
        return self.dir
    
    def set_dir(self, dir):
        self.dir = dir

unnoticable = WordList("Unnoticable", "unnoticable.txt")
risky = WordList("Risky", "risky.txt")
babyhacker = WordList("Baby Hacker", "BABYHACKER.txt")
extremehacker = WordList("Extreme Hacker", "EXTREMEHACKER.txt")
los = WordList("Los", "los.txt")
custom = WordList("Custom", "Custom.txt")

class Settings:
    def __init__(self):
        self.auto_correct_enabled = True
        self.auto_complete_enabled = True
        self.autocomplete_key = "tab"

settings = Settings()

# Add a new global variable
suggestion_list_active = False

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, reverse=False):
        node = self.root
        if reverse:
            word = word[::-1]

        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()
            node = node.children[letter]
        node.is_word = True

    def search(self, prefix, reverse=False, max_suggestions=None):
        suggestions = []
        node = self.root

        if reverse:
            prefix = prefix[::-1]

        for letter in prefix:
            if letter in node.children:
                node = node.children[letter]
            else:
                return []

        def search_helper(node, current_word):
            nonlocal suggestions, max_suggestions
            if max_suggestions is not None and len(suggestions) >= max_suggestions:
                return

            if node.is_word:
                suggestions.append(current_word)

            for letter, child_node in node.children.items():
                search_helper(child_node, current_word + letter)

        search_helper(node, prefix)
        return suggestions

    def search_containing(self, substring):
        suggestions = []

        def search_helper(node, current_word):
            nonlocal suggestions
            if node.is_word and substring in current_word:
                suggestions.append(current_word)

            for letter, child_node in node.children.items():
                search_helper(child_node, current_word + letter)

        search_helper(self.root, "")
        return suggestions

class AutocompleteWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Autocomplete Suggestions")
        self.list_widget = QListWidget(self)
        self.setCentralWidget(self.list_widget)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def update_suggestions(self, suggestions):
        self.list_widget.clear()
        for suggestion in suggestions:
            self.list_widget.addItem(suggestion)
    
    def mousePressEvent(self, event):
        global suggestion_list_active, current_word
        suggestion_list_active = False
        current_word = ""
        self.list_widget.clear()

    def open_settings(self):
        settings_dialog = SettingsDialog(self, settings)
        settings_dialog.exec_()
        self.settings_dialog = settings_dialog

class SettingsDialog(QDialog):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")

        layout = QVBoxLayout()

        self.auto_correct_checkbox = QCheckBox("Enable Auto Correct")
        self.auto_correct_checkbox.setChecked(self.settings.auto_correct_enabled)
        layout.addWidget(self.auto_correct_checkbox)

        self.auto_complete_checkbox = QCheckBox("Enable Auto Complete")
        self.auto_complete_checkbox.setChecked(self.settings.auto_complete_enabled)
        layout.addWidget(self.auto_complete_checkbox)

        self.autocomplete_key_combobox = QComboBox()
        self.autocomplete_key_combobox.addItems(["enter", "tab"])
        self.autocomplete_key_combobox.setCurrentText(self.settings.autocomplete_key)
        layout.addWidget(self.autocomplete_key_combobox)

        self.word_list_combobox = QComboBox()
        
        self.word_list_combobox.addItems(["unnoticable.txt", "risky.txt", "BABYHACKER.txt", "EXTREMEHACKER.txt", "los.txt", "Custom.txt"])  # Add your word list file names here        
        #self.word_list_combobox.setCurrentText("risky.txt")  # Set the default word list
        layout.addWidget(self.word_list_combobox)
        button = QPushButton("Close")
        button.clicked.connect(self.save_and_close)
        layout.addWidget(button)

        self.setLayout(layout)

    def save_and_close(self):
        # set the new words list and trie based on the selected word list in the combobox 
        self.settings.auto_correct_enabled = self.auto_correct_checkbox.isChecked()
        self.settings.auto_complete_enabled = self.auto_complete_checkbox.isChecked()
        self.settings.autocomplete_key = self.autocomplete_key_combobox.currentText()

        word_lists = ["unnoticable.txt", "risky.txt", "BABYHACKER.txt", "EXTREMEHACKER.txt", "los.txt", "Custom.txt"]
        selected_word_list = word_lists[self.word_list_combobox.currentIndex()]

        global trie_start, trie_end
        trie_start, trie_end = load_word_list(selected_word_list)
        self.close()    

app = QApplication(sys.argv)
autocomplete_window = AutocompleteWindow()

# Create the settings button
settings_button = QPushButton("Settings")
settings_button.clicked.connect(autocomplete_window.open_settings)

# Create the toggle button
toggle_button = QPushButton("Toggle ON/OFF")
toggle_button.setCheckable(True)
toggle_button.setChecked(True)

# Create the layout
layout = QVBoxLayout()
layout.addWidget(autocomplete_window.list_widget)
layout.addWidget(toggle_button)
layout.addWidget(settings_button)

# Create the main widget and set the layout
main_widget = QWidget()
main_widget.setLayout(layout)
autocomplete_window.setCentralWidget(main_widget)

autocomplete_window.show()

trie_start = Trie()
trie_end = Trie()

current_word = ""
spell = SpellChecker()

# Flag to check if the program is enabled or disabled
program_enabled = True

def load_word_list(word_list):
    trie_start = Trie()
    trie_end = Trie()
    word_list = WordList(word_list, word_list)
    with open(word_list.get_dir(), "r") as f:
        for word in f:
            word = word.strip()
            trie_start.insert(word)
            trie_end.insert(word, reverse=True)
    return trie_start, trie_end

#trie_start, trie_end = load_word_list(unnoticable)

# Function to toggle the program ON/OFF
def toggle_program():
    global program_enabled
    program_enabled = not program_enabled
    toggle_button.setText("Toggle ON" if program_enabled else "Toggle OFF")
    autocomplete_window.list_widget.clear()

# Connect the toggle button to the function
toggle_button.clicked.connect(toggle_program)

def get_suggestions(current_word):
    suggestions_start = trie_start.search(current_word, max_suggestions=5)
    suggestions_end = trie_end.search(current_word, reverse=True, max_suggestions=3)
    
    existing_suggestions = set(suggestions_start + [word[::-1] for word in suggestions_end])
    all_suggestions = trie_start.search_containing(current_word)
    suggestions_containing = [
        word for word in all_suggestions 
        if word not in existing_suggestions
        and not word.startswith(current_word)
        and not word.endswith(current_word)
    ][:2]

    suggestions = suggestions_start[:]
    for word in suggestions_end:
        reversed_word = word[::-1]
        if reversed_word not in suggestions_start:
            suggestions.append(reversed_word)
    for word in suggestions_containing:
        if word not in suggestions_start and word not in suggestions_end:
            suggestions.append(word)
    
    suggestions.sort(key=len)
    return suggestions

# Process key function
def process_key(e, settings):
    global current_word, autocomplete_window, program_enabled

    # If the program is disabled, return immediately
    if not program_enabled:
        return
    
    if settings.autocomplete_key == e.name:
        if e.event_type == "down":
            autocomplete_and_replace(current_word)
    elif e.name == "backspace":
        if e.event_type == "down":
            if current_word := current_word[:-1]:
                suggestions = get_suggestions(current_word)
                autocomplete_window.update_suggestions(suggestions)
            else:
                autocomplete_window.list_widget.clear()
    elif len(e.name) == 1:
        if e.event_type == "down":
            current_word += e.name
            suggestions = get_suggestions(current_word)
            suggestion_list_active = bool(suggestions)
            autocomplete_window.update_suggestions(suggestions)

    # Perform auto-correction on spacebar or backspace press
    if settings.auto_correct_enabled and e.name in ['space'] and e.event_type == "down":
        auto_correct(current_word)

    # Clear the suggestions when spacebar, enter, or tab is pressed
    if e.name in ['space', 'enter', 'tab'] and e.event_type == 'down':
        current_word = ""
        autocomplete_window.list_widget.clear()

def current_to_corrected(current_word, corrected_word):
    keyboard.press('ctrl+backspace')
    time.sleep(0.05)
    keyboard.release('ctrl+backspace')
    keyboard.write(f'{corrected_word} ')

    # if settings.autocomplete_key == "enter" temporarily block the enter key or else block the tab key
    if settings.autocomplete_key == "enter":
        temp_key_block('enter')
    else:
        temp_key_block('tab')

# TODO Rename this here and in `_extracted_from_process_key_8`
def temp_key_block(arg0):
    keyboard.block_key(arg0)
    time.sleep(0.05)
    keyboard.unblock_key(arg0)

# Update the function call in auto_correct()
def auto_correct(current_word):
    # if auto correct checkbox is unchecked, return immediately
    if not settings.auto_correct_enabled:
        return
    
    if not current_word or current_word[-1] in string.punctuation:
        return

    if misspelled := spell.unknown([current_word]):
        corrected_word = spell.correction(list(misspelled)[0])

        if corrected_word and corrected_word != current_word:
            current_to_corrected(current_word, corrected_word)
            autocomplete_window.list_widget.clear()  # Clear the suggestions

# Update the function call in autocomplete_and_replace()
def autocomplete_and_replace(current_word):

    if not current_word or current_word[-1] in string.punctuation:
        return

    suggestions = get_suggestions(current_word)
    corrected_word = suggestions[0] if suggestions else current_word

    # if autocomplete checkbox is unchecked, return immediately
    if not settings.auto_complete_enabled:
        return

    if corrected_word and corrected_word != current_word:
        current_to_corrected(current_word, corrected_word)
        autocomplete_window.list_widget.clear()  # Clear the suggestions

# Listen for key presses
keyboard.hook(lambda e: process_key(e, settings))
sys.exit(app.exec_())