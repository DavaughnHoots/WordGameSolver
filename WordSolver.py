
import contextlib
import sys
import time
import string
import os
import logging

import keyboard
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QListWidget, QPushButton, QCheckBox, QComboBox, 
                            QDialog, QHBoxLayout, QInputDialog, QMessageBox)
from spellchecker import SpellChecker
from functools import lru_cache
import json

import json

def export_cache():
    cache_dict = dict(word_list_manager.get_suggestions.cache_info().items())
    with open('cache_file.json', 'w') as f:
        json.dump(cache_dict, f)

def load_cache():
    with contextlib.suppress(FileNotFoundError):
        with open('cache_file.json', 'r') as f:
            cache_dict = json.load(f)
        word_list_manager.get_suggestions.cache_clear()
        for key, value in cache_dict.items():
            word_list_manager.get_suggestions.cache_update(key, value)

# Logging
logging.basicConfig(filename="WordSolver2.log", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

CUSTOM_WORD_LIST_FILENAME = "Custom.txt"
UNNOTICABLE_WORD_LIST_FILENAME = "unnoticable.txt"
RISKY_WORD_LIST_FILENAME = "risky.txt"
BABYHACKER_WORD_LIST_FILENAME = "Suspicious.txt"
BESTLIST_WORD_LIST_FILENAME = "BestList.txt"
EXTREMEHACKER_WORD_LIST_FILENAME = "Obvious.txt"

# Save the object to a file

class WordList:
    """
    A class for storing a list of words

    Attributes:
        name (str): The name of the word list
        file (str): The file containing the word list
        words (list): The list of words
        trie (Trie): The trie data structure used to store the words
        dir (str): The directory of the file

    Methods:
        get_name: Returns the name of the word list
        get_file: Returns the file containing the word list
        get_words: Returns the list of words
        set_words: Sets the list of words
        get_trie: Returns the trie data structure used to store the words
        set_trie: Sets the trie data structure used to store the words
        get_dir: Returns the directory of the file
        set_dir: Sets the directory of the file

    Args:
        name (str): The name of the word list
        file (str): The file containing the word list

    Returns:
        None

    Example:
        word_list = WordList("English", "english.txt")
    """
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

class CustomWordListEditor(QDialog):
    """
    A class for editing a custom word list

    Attributes:
        word_list (WordList): The word list to edit

    Methods:
        load_words: Loads the words from the word list
        add_word: Adds a word to the word list
        edit_word: Edits a word in the word list
        delete_word: Deletes a word from the word list
        save_changes: Saves the changes to the word list
        close_editor: Closes the editor

    Args:
        parent (QWidget): The parent widget
        word_list (WordList): The word list to edit

    Returns:
        None

    Example:
        editor = CustomWordListEditor(self, word_list)
    """

    def __init__(self, parent, word_list: WordList) -> None:
        super().__init__(parent)
        self.word_list = word_list
        self.setWindowTitle("Custom Word List Editor")

        # Create UI components
        self.list_widget = QListWidget(self)
        self.add_button = QPushButton("Add")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.save_button = QPushButton("Save")
        self.close_button = QPushButton("Close")

        # Connect buttons to functions
        self.add_button.clicked.connect(self.add_word)
        self.edit_button.clicked.connect(self.edit_word)
        self.delete_button.clicked.connect(self.delete_word)
        self.save_button.clicked.connect(self.save_changes)
        self.close_button.clicked.connect(self.close_editor)

        # Layout
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.close_button)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Load words
        self.load_words()

    def load_words(self) -> None:
        """
        Loads the words from the word list
        
        Args:
            None
            
        Returns:
            None
            
        Example:
            self.load_words()
            """
        # Clear existing items
        self.list_widget.clear()
        # Add words from the custom word list
        for word in self.word_list.get_words():
            self.list_widget.addItem(word)


    def add_word(self) -> None:
        """
        Adds a word to the word list

        Args:
            None

        Returns:
            None

        Example:
            self.add_word()
        """
        text, ok = QInputDialog.getText(self, "Add Word", "Enter the word:")
        if ok and text:
            self.list_widget.addItem(text)
            self.word_list.get_words().append(text)

    def edit_word(self):
        """
        Edits a word in the word list
        
        Args:
            None
            
        Returns:
            None
            
        Example:
            self.edit_word()
            """
        if selected_item := self.list_widget.currentItem():
            old_text = selected_item.text()
            new_text, ok = QInputDialog.getText(self, "Edit Word", "Edit the word:", text=old_text)
            if ok and new_text:
                selected_item.setText(new_text)
                self.word_list.get_words().remove(old_text)
                self.word_list.get_words().append(new_text)

    def delete_word(self):
        """
        Deletes a word from the word list

        Args:
            None

        Returns:
            None

        Example:
            self.delete_word()
        """
        if selected_item := self.list_widget.currentItem():
            self.word_list.get_words().remove(selected_item.text())
            self.list_widget.takeItem(self.list_widget.row(selected_item))


    def save_changes(self):
        """
        Saves the changes to the word list

        Args:
            None

        Returns:
            None

        Example:
            self.save_changes()
        """
        # Save the custom word list to a file
        with open(self.word_list.get_dir(), "w") as file:
            for word in self.word_list.get_words():
                file.write(word + "\n")
        QMessageBox.information(self, "Success", "Changes saved successfully!")

        # Update the trie
        trie_start, trie_end = self.word_list.get_trie()
        trie_start.root = TrieNode()  # Clear the trie
        trie_end.root = TrieNode()
        for word in self.word_list.get_words():
            trie_start.insert(word)
            trie_end.insert(word, reverse=True)

    def close_editor(self):
        self.close()

class Settings:
    """
    A class for storing the settings of the application

    Attributes:
        auto_correct_enabled (bool): Whether auto-correct is enabled
        auto_complete_enabled (bool): Whether auto-complete is enabled
        autocomplete_key (str): The key to press to auto-complete a word

    Methods:
        None

    Args:
        None

    Returns:
        None

    Example:
        settings = Settings()
    """
    def __init__(self):
        self.auto_correct_enabled = True
        self.auto_complete_enabled = True
        self.autocomplete_key = "tab"

class TrieNode:
    """
    A node in a trie data structure

    Attributes:
        children (dict): A dictionary of child nodes
        is_word (bool): Whether the node represents a word

    Methods:
        None

    Args:
        None

    Returns:
        None

    Example:
        node = TrieNode()
    """
    def __init__(self):
        self.children = {}
        self.is_word = False

class Trie:
    """
    A trie data structure for storing words and searching for words that start with a given prefix

    Attributes:
        root (TrieNode): The root node of the trie

    Methods:
        insert: Inserts a word into the trie
        search: Searches for words that start with a given prefix
        search_containing: Searches for words that contain a given substring

    Args:
        None

    Returns:
        None

    Example:
        trie = Trie()
        trie.insert("hello")
        trie.insert("world")
        trie.search("he") # Returns ["hello"]
        trie.search_containing("o") # Returns ["hello", "world"]
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, reverse=False):
        """
        Performs a depth-first search on a trie node to find all the words 
        that can be formed starting from the given node and current word. 
        The search stops when the maximum number of suggestions is reached.

        Args:
            node (TrieNode): The current node in the trie.
            current_word (str): The word formed so far.

        Behaviour:
            - Updates the suggestions list with the current word if the node represents a word.
            - Recursively calls the search_helper function for each child node, passing the child node and the updated current word.

        Returns:
            None

        Example:
            trie = Trie()
            suggestions = []
            max_suggestions = 5
            search_helper(trie.root, "")
            logger.info(suggestions)
        """
        node = self.root
        if reverse:
            word = word[::-1]

        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()
            node = node.children[letter]
        node.is_word = True

    def search(self, prefix, reverse=False, max_suggestions=None):
        """
        Updates the suggestions in the list_widget by clearing the existing items and adding the new suggestions.

        Args:
            suggestions (list): The list of suggestions to be displayed.

        Behaviour:
        - Clears the list_widget.
        - Adds each suggestion from the suggestions list as a new item in the list_widget.

        Returns:
            None

        Example:
            widget = SuggestionsWidget()
            suggestions = ["apple", "banana", "cherry"]
            widget.update_suggestions(suggestions)
        """        
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
            """
            Helps the search function to recursively search for words that start with a given prefix.

            Args:
                node (TrieNode): The current node in the trie.
                current_word (str): The word formed so far.

            Behaviour:
                - Adds the current word to the suggestions list if the node represents a word.
                - Recursively calls the search_helper function for each child node, 
                passing the child node and the updated current word.

            Returns:
                None

            Example:
                trie = Trie()
                suggestions = []
                max_suggestions = 5
                search_helper(trie.root, "")
                print(suggestions)
            """
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
        """
        Searches for words that contain a given substring

        Args:
            substring (str): The substring to search for

        Returns:
            suggestions (list): The list of suggestions

            Behaviour:
            - Updates the suggestions list with the current word if the node represents a word.
            - Recursively calls the search_helper function for each child node, 
            passing the child node and the updated current word.

        Example:
            trie = Trie()
            trie.insert("hello")
            trie.insert("world")
            trie.search_containing("o") # Returns ["hello", "world"]
        """
        suggestions = []

        def search_helper(node, current_word):
            """
            Performs a depth-first search on a trie node to find all the words
            that can be formed starting from the given node and current word.
            The search stops when the maximum number of suggestions is reached.
            
            Args:
                node (TrieNode): The current node in the trie.
                current_word (str): The word formed so far.
            
            Returns:
                None
                
            Example:
                trie = Trie()
                suggestions = []
                max_suggestions = 5
                search_helper(trie.root, "")
                print(suggestions)
            """
            nonlocal suggestions
            if node.is_word and substring in current_word:
                suggestions.append(current_word)

            for letter, child_node in node.children.items():
                search_helper(child_node, current_word + letter)

        search_helper(self.root, "")
        return suggestions

class AutocompleteWindow(QMainWindow):
    """
    A window that displays autocomplete suggestions

    Attributes:
        list_widget (QListWidget): The list widget that displays the suggestions

    Methods:
        update_suggestions: Updates the suggestions in the list widget
        mousePressEvent: Hides the window when the user clicks outside of it
        open_settings: Opens the settings dialog

    Args:
        parent (QWidget): The parent widget of this window

    Returns:
        None

    Example:
        autocomplete_window = AutocompleteWindow(self)
        autocomplete_window.show()
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Autocomplete Suggestions")
        self.list_widget = QListWidget(self)
        self.setCentralWidget(self.list_widget)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def update_suggestions(self, suggestions):
        """
        Updates the suggestions in the list widget
        
        Args:
            suggestions (list): The list of suggestions to display
            
        Returns
            None

        Calls:
            None

        Called by:
            process_key(key)

        Example:
            autocomplete_window.update_suggestions(["hello", "world"])
        """

        self.list_widget.clear()
        for suggestion in suggestions:
            self.list_widget.addItem(suggestion)
    
    def mousePressEvent(self, event):
        """
        A function that is called when the user clicks on the window

        Args:
            event (QEvent): The event that triggered this function

        Returns:
            None

        Calls:
            None

        Called by:
            None

        Example:
            None
        """

        global suggestion_list_active, current_word
        suggestion_list_active = False
        current_word = ""
        self.list_widget.clear()

    def open_settings(self):
        """
        Opens the settings dialog

        Args:
            None

        Returns:
            None

        Calls:
            None

        Called by:
            
        settings_button.clicked.connect(autocomplete_window.open_settings)      

        Example:
            
        settings_button.clicked.connect(autocomplete_window.open_settings)
        """
        settings_dialog = SettingsDialog(self, settings, word_list_manager)
        settings_dialog.exec_()
        self.settings_dialog = settings_dialog

    def open_custom_word_list_editor(self):
        custom_word_list = word_list_manager.get_word_list("Custom")
        editor = CustomWordListEditor(None, custom_word_list)
        editor.exec_()

class SettingsDialog(QDialog):
    """
    A dialog to change the settings of the program

    Attributes:
        settings (Settings): The settings object to modify
        auto_correct_checkbox (QCheckBox): The checkbox for enabling/disabling auto correct
        auto_complete_checkbox (QCheckBox): The checkbox for enabling/disabling auto complete
        autocomplete_key_combobox (QComboBox): The combobox for selecting the autocomplete key
        word_list_combobox (QComboBox): The combobox for selecting the word list

    Methods:
        save_and_close: Saves the settings and closes the dialog

    Args:
        parent (QWidget): The parent widget of this dialog
        settings (Settings): The settings object to modify

    Returns:
        None

    Example:
        settings_dialog = SettingsDialog(self, settings, word_list_manager)
        settings_dialog.exec_
    """
    def __init__(self, parent, settings, word_list_manager):
        super().__init__(parent)
        self.settings = settings
        self.word_list_manager = word_list_manager
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
        
        self.word_list_combobox.addItems(["Unnoticable", "Risky", "BestList", "Suspicious", "Obvious", "Custom"])
        self.word_list_combobox.setCurrentText(self.word_list_manager.current_word_list.name)
        layout.addWidget(self.word_list_combobox)
        button = QPushButton("Close")
        button.clicked.connect(self.save_and_close)
        layout.addWidget(button)

        self.setLayout(layout)

    def save_and_close(self):
        """
        Saves the settings and closes the dialog

        Args:
            None

        Returns:
            None

        Calls:
             word_list_manager.get_word_list(selected_word_list_name)
             selected_word_list.get_trie()

        Called by:
            self.__init__
            
        Example:
            self.save_and_close()
        """
        logger.debug("Saving and closing settings...")

        # set the new words list and trie based on the selected word list in the combobox 
        self.settings.auto_correct_enabled = self.auto_correct_checkbox.isChecked()
        self.settings.auto_complete_enabled = self.auto_complete_checkbox.isChecked()
        self.settings.autocomplete_key = self.autocomplete_key_combobox.currentText()
        
        selected_word_list_name = self.word_list_combobox.currentText()
        selected_word_list = self.word_list_manager.get_word_list(selected_word_list_name)
        self.word_list_manager.current_word_list = selected_word_list
        if selected_word_list is None:
            logger.info(f"Word list with name {selected_word_list_name} not found.")
            return  # Return early if the word list is not found

        global trie_start, trie_end
        trie_start, trie_end = selected_word_list.get_trie()
        logger.debug(f"Settings saved: auto_correct_enabled={self.settings.auto_correct_enabled}, auto_complete_enabled={self.settings.auto_complete_enabled}, word_list_name={self.word_list_combobox.currentText()}")

        self.close()

class WordListManager:
    """
    Represents a WordListManager class that manages word lists. It provides functionality to load word lists from files and store them in a dictionary.

    Attributes:
        word_lists (dict): A dictionary to hold all the word lists.

    Methods:
        load_word_list(name, filename)
        get_word_list(name)
        validate_word_lists()
        get_suggestions(current_word)
        process_key(e, settings)

    Args:
        name (str): The name of the word list.
        filename (str): The filename of the file containing the words.

    Returns:
        WordList or None: The loaded WordList object if the file is found, None otherwise.

    Example:
        manager = WordListManager()
        word_list = manager.load_word_list("English", "english_words.txt")
        if word_list:
            logger.info(f"Word list '{word_list.name}' loaded successfully!")
        else:
            logger.info("Failed to load word list.")
    """

    def __init__(self):
        self.word_lists = {}  # A dictionary to hold all the word lists
        self.current_word_list = None  # The current word list
        self.suggestions_cache = self.load_cache()

    def load_cache(self):
        # Load cache from file if exists
        try:
            with open('suggestions_cache.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_cache(self):
        # Save cache to file
        with open('suggestions_cache.json', 'w') as file:
            json.dump(self.suggestions_cache, file)
    
    def get_word_list(self, name):
        """
        Returns the word list with the given name

        Args:
            name (str): The name of the word list

        Returns:
            WordList or None: The word list with the given name, or None if the word list is not found

        Example:
            word_list = manager.get_word_list("English")
        """
        return self.word_lists.get(name)
    
    def load_word_list(self, name, filename):
        """
        Loads the words from a file and creates a WordList object to store the words and associated trie. 
        The WordList object is then stored in the word_lists dictionary.

        Args:
            name (str): The name of the word list.
            filename (str): The filename of the file containing the words.

        Returns:
            WordList or None: The loaded WordList object if the file is found, None otherwise.

        Calls:
            WordList.set_words(words)
            WordList.set_trie((trie_start, trie_end))
            Trie.insert(word, reverse=False)
            Trie.insert(word, reverse=True)

        Called by:
            SettingsDialog.save_and_close()

        Example:
            manager = WordListManager()
            word_list = manager.load_word_list("English", "english_words.txt")
        """
        # Load the words from the file
        logger.debug(f"Loading words from {filename}...")

        words = []
        trie_start = Trie()
        trie_end = Trie()
        file_path = os.path.join(script_dir, filename)
        try:
            with open(file_path, "r") as f:
                if f.readable():
                    for word in f:
                        word = word.strip()
                        if not word.isalpha():  # Ensurglogg glogg e the word only contains letters
                            #logger.info(f"Invalid word found: {word}")
                            continue
                        words.append(word)
                        trie_start.insert(word)
                        trie_end.insert(word, reverse=True)
                else:
                    logger.info(f"File {filename} is not readable.")
                    return None
        except FileNotFoundError:
            logger.error(f"File {filename} not found.")
            return None
        except PermissionError:
            logger.error(f"Permission denied when accessing {filename}.")
            return None
        except IOError as e:
            logger.error(f"An I/O error occurred when reading {filename}: {str(e)}")
            return None

        # Create a WordList object and store it
        logger.info(f"Loaded {len(words)} words from {filename}.")
        word_list = WordList(name, filename)
        word_list.set_words(words)
        word_list.set_trie((trie_start, trie_end))
        self.word_lists[name] = word_list
        logger.info(f"Word list '{word_list.name}' loaded successfully!")
        self.current_word_list = word_list
        return word_list

    @lru_cache(maxsize=100000)
    def get_suggestions(self, current_word):
        logger.debug(f"Generating suggestions for word: {current_word}, word list: {self.current_word_list.name}")
        if cached_suggestions := self.suggestions_cache.get(current_word):
            return cached_suggestions

        selected_word_list = self.word_lists.get(self.current_word_list.name)
        if selected_word_list is None:
            logger.error(f"Word list with name {self.current_word_list.name} not found.")
            return []

        trie_start, trie_end = selected_word_list.get_trie()

        suggestions_start = trie_start.search(current_word, max_suggestions=5)
        suggestions_end = trie_end.search(current_word, reverse=True, max_suggestions=3)

        suggestions_containing = []  # Example: logic to find words containing the current word

        suggestions = suggestions_start[:]
        for word in suggestions_end:
            reversed_word = word[::-1]
            if reversed_word not in suggestions_start:
                suggestions.append(reversed_word)
        for word in suggestions_containing:
            if word not in suggestions_start and word not in suggestions_end:
                suggestions.append(word)

        logger.debug(f"Suggestions generated: {suggestions}")
        suggestions.sort(key=len)
        # Store suggestions in cache
        self.suggestions_cache[current_word] = suggestions

        return suggestions

    def process_key(self, e, settings):
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
                    suggestions = self.get_suggestions(current_word)
                    autocomplete_window.update_suggestions(suggestions)
                else:
                    autocomplete_window.list_widget.clear()
        elif len(e.name) == 1:
            if e.event_type == "down":
                current_word += e.name
                suggestions = self.get_suggestions(current_word)
                suggestion_list_active = bool(suggestions)
                autocomplete_window.update_suggestions(suggestions)

        # Perform auto-correction on spacebar or backspace press
        if settings.auto_correct_enabled and e.name in ['space'] and e.event_type == "down":
            auto_correct(current_word)
        
        # Clear the suggestions when spacebar, enter, or tab is pressed
        if e.name in ['space', 'enter', 'tab', 'ctrl', 'alt'] and e.event_type == 'down':
            current_word = ""
            autocomplete_window.list_widget.clear()
            
def toggle_program():
        """
        This function is called when the toggle button is pressed. It toggles the program_enabled variable,
        and changes the text of the button to reflect the new state of the program.

        Args:
            None

        Returns:
            None

        Calls:
            None

        Called by:
            toggle_button.clicked.connect(toggle_program())

        Example: 
            toggle_button.clicked.connect(toggle_program())
        """
        # This function is called when the button is pressed. The program_enabled variable is
        # toggled, and the text of the button is changed to reflect the new state of the program.
        global program_enabled
        program_enabled = not program_enabled
        toggle_button.setText("Toggle ON" if program_enabled else "Toggle OFF")
    
        # The list widget is cleared, so that it does not contain any suggestions from before
        autocomplete_window.list_widget.clear()

def current_to_corrected(current_word: str, corrected_word: str) -> None:
    """
    Executes the current_to_corrected function, which corrects a word by deleting the current word and 
    typing the corrected word using keyboard inputs. 
    If the autocomplete_key setting is set to "enter", the enter key is temporarily blocked during the execution of the function. 
    Otherwise, the tab key is temporarily blocked.

    Args:
        current_word (str): The word to be corrected.
        corrected_word (str): The corrected version of the word.

    Returns:
        None

    Calls:
        - temp_key_block(key)

    Called by:
        - autocomplete_and_replace(current_word, word_list_name)
        - auto_correct(current_word

    Example:
        current_to_corrected("current", "corrected")
    """

    # Press and release ctrl+backspace to delete the word
    keyboard.press('ctrl+backspace')
    time.sleep(0.05)
    keyboard.release('ctrl+backspace')

    # Type the corrected word and add a space
    keyboard.write(f'{corrected_word} ')

    # if settings.autocomplete_key == "enter" temporarily block the enter key or else block the tab key
    if settings.autocomplete_key == "enter":
        temp_key_block('enter')
    else:
        temp_key_block('tab')

def temp_key_block(arg0: str) -> None:
    """
    Executes the autocomplete_and_replace function, which performs autocomplete and replacement of a current word. 
    If the current word is empty or ends with punctuation, the function returns immediately. 
    It retrieves suggestions for the current word and selects the first suggestion as the corrected word. 
    If the autocomplete_enabled setting is True and the corrected word is different from the current word, 
    the function calls the current_to_corrected function to correct the word and clears the autocomplete window.

    Args:
        current_word (str): The word to be autocompleted and replaced.

    Returns:
        None

    Calls:
        - None

    Called by:
        - current_to_corrected(current_word, corrected_word): 

    Example:
        autocomplete_and_replace("current")
    """
    keyboard.block_key(arg0)
    time.sleep(0.05)
    keyboard.unblock_key(arg0)

def auto_correct(current_word: str) -> None:
    """
    Executes the auto_correct function, which performs auto-correction of a current word. 
    If the current word is empty or ends with punctuation, the function returns immediately. 
    It retrieves suggestions for the current word and selects the first suggestion as the corrected word. 
    If the auto_correct_enabled setting is True and the corrected word is different from the current word, 
    the function calls the current_to_corrected function to correct the word and clears the autocomplete window.
    
    Args:
        current_word (str): The word to be auto-corrected

    Returns:
        None

    Calls:
        - current_to_corrected(current_word, corrected_word):
        Corrects a word by deleting the current word and typing the corrected word using keyboard inputs.

    Called by:
        - process_key(e, settings):

    Example:
        auto_correct("current")   
    """
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

def autocomplete_and_replace(current_word):
    if not current_word or current_word[-1] in string.punctuation:
        return

    suggestions = word_list_manager.get_suggestions(current_word)
    corrected_word = suggestions[0] if suggestions else current_word

    # if autocomplete checkbox is unchecked, return immediately
    if not settings.auto_complete_enabled:
        return

    if corrected_word and corrected_word != current_word:
        current_to_corrected(current_word, corrected_word)
        autocomplete_window.list_widget.clear()  # Clear the suggestions

# load the cache
cache_filename = "cache.json"


settings = Settings()

suggestion_list_active = False
global word_list_manager
word_list_manager = WordListManager()

word_list_manager.load_word_list(name="Unnoticable", filename=UNNOTICABLE_WORD_LIST_FILENAME)
word_list_manager.load_word_list(name="Risky", filename=RISKY_WORD_LIST_FILENAME)
word_list_manager.load_word_list(name="BestList", filename=BESTLIST_WORD_LIST_FILENAME)
word_list_manager.load_word_list(name="Suspicious", filename=BABYHACKER_WORD_LIST_FILENAME)
word_list_manager.load_word_list(name="Obvious", filename=EXTREMEHACKER_WORD_LIST_FILENAME)
word_list_manager.load_word_list(name="Custom", filename=CUSTOM_WORD_LIST_FILENAME)

app = QApplication(sys.argv)
autocomplete_window = AutocompleteWindow()

# Create the settings button
settings_button = QPushButton("Settings")
settings_button.clicked.connect(autocomplete_window.open_settings)

# Create the toggle button
toggle_button = QPushButton("Toggle ON/OFF")
toggle_button.setCheckable(True)
toggle_button.setChecked(True)

# Create the button to open the custom word list editor
edit_custom_list_button = QPushButton("Edit Custom Word List")
edit_custom_list_button.clicked.connect(autocomplete_window.open_custom_word_list_editor)

# Create the layout
layout = QVBoxLayout()
layout.addWidget(autocomplete_window.list_widget)
layout.addWidget(toggle_button)
layout.addWidget(settings_button)
layout.addWidget(edit_custom_list_button)

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

# Connect the toggle button to the function
toggle_button.clicked.connect(toggle_program)

# Listen for key presses
keyboard.hook(lambda e: word_list_manager.process_key(e, settings))
sys.exit(app.exec_())
