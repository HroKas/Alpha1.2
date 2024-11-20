import os
from docx import Document
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder

def load_dictionary(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл '{file_path}' не найден. Убедитесь, что он существует.")
    dictionary = {}
    doc = Document(file_path)
    for paragraph in doc.paragraphs:
        if ":" in paragraph.text:
            word, definition = paragraph.text.strip().split(":", 1)
            dictionary[word.strip()] = definition.strip()
    return dictionary

KV = """
<DictionaryScreen>:
    orientation: "vertical"
    spacing: 10

    BoxLayout:
        id: search_box
        size_hint_y: None
        height: "50dp"
        opacity: 1 if root.filtered_words else 0.5
        TextInput:
            id: search_input
            hint_text: "Ввод слова"
            multiline: False
            on_text: root.filter_words(self.text)
        Button:
            text: "Фильтр"
            size_hint_x: None
            width: "100dp"
            on_release: root.open_filter_window()

    BoxLayout:
        id: empty_placeholder
        size_hint_y: None
        height: root.height * 0.5 if not root.filtered_words else 0
        Label:
            text: "Введите слово или выберите фильтр"
            font_size: 18
            opacity: 1 if not root.filtered_words else 0

    ScrollView:
        id: scroll
        opacity: 1 if root.filtered_words else 0
        BoxLayout:
            id: word_list
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
"""

Builder.load_string(KV)

class DictionaryScreen(BoxLayout):
    def __init__(self, **kwargs):
        self.filtered_words = []
        super().__init__(**kwargs)
        try:
            self.dictionary = load_dictionary("dictionary.docx")
        except FileNotFoundError as e:
            self.dictionary = {}
            Popup(
                title="Ошибка",
                content=Label(text=str(e), size_hint_y=None, height="100dp"),
                size_hint=(0.8, 0.5),
            ).open()

    def update_word_list(self):
        word_list = self.ids.word_list
        word_list.clear_widgets()
        for word in self.filtered_words:
            btn = Button(
                text=word,
                size_hint_y=None,
                height="40dp",
                on_release=lambda instance: self.show_definition(instance.text),
            )
            word_list.add_widget(btn)

    def filter_words(self, query):
        query = query.lower()
        self.filtered_words = [
            word
            for word in self.dictionary.keys()
            if query in word.lower()
        ]
        self.update_word_list()
        self.adjust_ui()

    def show_definition(self, word):
        definition = self.dictionary.get(word, "Определение не найдено")
        scroll = ScrollView(size_hint=(1, 1))
        label = Label(text=definition, size_hint_y=None, padding=(10, 10), halign="left", valign="top")
        label.bind(size=label.setter("text_size"))
        scroll.add_widget(label)
        popup = Popup(
            title=word,
            content=scroll,
            size_hint=(0.8, 0.5),
        )
        popup.open()

    def open_filter_window(self):
        win = Popup(
            title="Фильтры",
            size_hint=(0.8, 0.5),
        )
        layout = BoxLayout(orientation="vertical", spacing=5, padding=10)
        label = Label(
            text="На какую букву будет начинаться слово?",
            size_hint_y=None,
            height="40dp",
        )
        layout.add_widget(label)
        scroll = ScrollView(size_hint=(1, 1))
        alphabet_layout = BoxLayout(
            orientation="vertical", size_hint_y=None, padding=5, spacing=5
        )
        alphabet_layout.bind(minimum_height=alphabet_layout.setter("height"))
        alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ"
        for letter in alphabet:
            btn = Button(
                text=letter,
                size_hint_y=None,
                height="40dp",
                on_release=lambda instance: self.filter_by_letter(instance.text),
            )
            alphabet_layout.add_widget(btn)
        scroll.add_widget(alphabet_layout)
        layout.add_widget(scroll)
        win.content = layout
        win.open()

    def filter_by_letter(self, letter):
        self.filtered_words = [
            word
            for word in self.dictionary.keys()
            if word.startswith(letter)
        ]
        self.update_word_list()
        self.adjust_ui()

    def adjust_ui(self):
        self.ids.empty_placeholder.height = 0 if self.filtered_words else self.height * 0.5
        self.ids.scroll.opacity = 1 if self.filtered_words else 0
        self.ids.search_box.opacity = 1 if self.filtered_words else 0.5

class DictionaryApp(App):
    def build(self):
        return DictionaryScreen()

if __name__ == "__main__":
    DictionaryApp().run()
