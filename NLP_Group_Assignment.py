import tkinter as tk
from nltk.tokenize import word_tokenize
from tkinter import PhotoImage
from PIL import Image, ImageTk
import json
import time

class SpellChecker:
    def __init__(self, word_dict):
        self.word_dict = word_dict
    
    def check_word(self, word):
        return word.lower() in self.word_dict
    
    def get_suggestions(self, word, num_suggestions=5):
        # Example: Provide all words in the dictionary as suggestions
        # Note: This is not practical for a real-world application with a large dictionary
        suggestions = sorted(self.word_dict.keys(), 
                             key=lambda x: self.levenshtein_distance(word, x))[:num_suggestions]
        return suggestions
    
    def levenshtein_distance(self, s1, s2):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]

class NLPGui:
    def __init__(self, master):
        self.master = master
        master.title("NLP Application")
        
        # Labels
        self.spell_check_label = tk.Label(master, text="Check Spelling:")
        self.spell_check_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.dictionary_label = tk.Label(master, text="Dictionary:")
        self.dictionary_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # Text Editors
        self.spell_check_text = tk.Text(master, height=15, width=40, wrap=tk.WORD)
        self.spell_check_text.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.search_text = tk.Text(master, height=1, width=40, wrap=tk.WORD)
        self.search_text.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.result_text = tk.Text(master, height=15, width=40, wrap=tk.WORD)
        self.result_text.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        # Word Count Label
        self.word_count_label = tk.Label(master, text="Words: 0/500")
        self.word_count_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Bind key release event
        self.spell_check_text.bind("<KeyRelease>", self.update_word_count)

        # Buttons
        self.check_spelling_button = tk.Button(master, text="Check Spelling", command=self.check_spelling)
        self.check_spelling_button.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        self.search_button = tk.Button(master, text="Search", command=self.search_word)
        self.search_button.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        self.close_button = tk.Button(master, text="Close", command=master.quit)
        self.close_button.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        # Load words from JSON file into dictionary
        self.word_dict = self.load_words_from_file('C:/Users/Atha/Downloads/NLP - Class/Dataset/data.json')
        self.spell_checker = SpellChecker(self.word_dict)
        
        # Configure tag for misspelled words
        self.spell_check_text.tag_configure("misspelled", foreground="red", underline=True)
        self.spell_check_text.bind("<Button-3>", self.suggest_correction)


    def load_words_from_file(self, filepath):
        try:
            with open(filepath, 'r') as file:
                words = json.load(file)
        except FileNotFoundError:
            print(f"No such file: '{filepath}'")
            words = {}
        except json.JSONDecodeError:
            print(f"Error reading JSON file: '{filepath}'")
            words = {}
        return words

    def check_spelling(self):
        self.spell_check_text.tag_remove("misspelled", "1.0", tk.END)
        text = self.spell_check_text.get("1.0",'end-1c')
        tokens = word_tokenize(text)
        misspelled_words = [word for word in tokens if not self.spell_checker.check_word(word)]
        for word in misspelled_words:
            start = "1.0"
            while True:
                start = self.spell_check_text.search(word, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(word)}c"
                self.spell_check_text.tag_add("misspelled", start, end)
                start = end

    def suggest_correction(self, event):
        index = self.spell_check_text.index(f"@{event.x},{event.y}")
        word_start = self.spell_check_text.index(f"{index} wordstart")
        word_end = self.spell_check_text.index(f"{index} wordend")
        word = self.spell_check_text.get(word_start, word_end)
    
        menu = tk.Menu(self.master, tearoff=0)
        suggestions = self.spell_checker.get_suggestions(word)
        for suggestion in suggestions:
            menu.add_command(label=suggestion, 
                         command=lambda s=suggestion: self.replace_word(word_start, word_end, s))
        menu.post(event.x_root, event.y_root)
    
    def replace_word(self, start, end, replacement):
        self.spell_check_text.delete(start, end)
        self.spell_check_text.insert(start, replacement)
        self.check_spelling()

    def open_dictionary(self):
        words_sorted = sorted(self.word_dict.keys())
        self.result_label.config(text=f"Words in Dictionary: {', '.join(words_sorted)}")
    
    def search_word(self):
        word_to_search = self.search_text.get("1.0",'end-1c').strip()
        definition = self.word_dict.get(word_to_search.lower(), 'Word not found in dictionary')
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"{word_to_search}: {definition}")

    def update_word_count(self, event=None):
        words = self.spell_check_text.get("1.0", 'end-1c').split()
        count = len(words)
        self.word_count_label.config(text=f"Words: {count}/500")

class LoadingScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)  # Hide the window border
        
        width = 1300
        height = 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # calculate position x and y coordinates
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))
        
        # Load and display the image
        image = Image.open("C:/Users/Atha/Downloads/nlp.jpeg")  # Update with your image path
        self.image = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(self, image=self.image)
        self.image_label.pack(pady=10)
        
        self.loading_label = tk.Label(self, text="Loading: 0%", font=("Arial", 16))
        self.loading_label.pack(pady=10)
        
        self.percentage = 0
        self.update_loading()

    def update_loading(self):
        self.loading_label.config(text=f"Loading: {self.percentage}%")
        self.percentage += 1
        if self.percentage <= 100:
            # Update the loading message after 50 milliseconds
            self.after(50, self.update_loading)
        else:
            # Close the loading screen once reaching 100%
            self.destroy()

# Show loading screen
loading_screen = LoadingScreen()
loading_screen.mainloop()

# Then show main app
root = tk.Tk()
app = NLPGui(root)
root.mainloop()

