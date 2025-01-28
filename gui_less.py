# OpenAi Vectore Storage GUI in Python 
# DON’T. STEAL. MY. CODE. You think copying someone else's work and slapping your name on it makes you clever? No, Morty, it makes you a colossal asshole!
# Respect Credits of developers! 
# Copyright 208-2025 Volkan Kücükbudak
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from gui_less import VectorStoreClient
import os
import threading
from dotenv import load_dotenv

load_dotenv()  # load .env

class VectorStoreGUI:
    def __init__(self, root):
        self.root = root
        self.client = VectorStoreClient(api_key=os.getenv("OPENAI_API_KEY"))
        
        self.setup_ui()
        self.refresh_stores()
        
    def setup_ui(self):
        self.root.title("OpenAI Vector Store Manager")
        self.root.geometry("800x600")
        
        # Notebook für Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')
        
        # Vector Store Tab
        self.store_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.store_tab, text="Vector Stores")
        
        # File Operations Tab
        self.file_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.file_tab, text="Dateien")
        
        self.setup_store_tab()
        self.setup_file_tab()
        self.setup_log_panel()
        
    def setup_store_tab(self):
        # Linke Seite: Liste der Stores
        store_list_frame = ttk.LabelFrame(self.store_tab, text="Vector Stores")
        store_list_frame.pack(side=tk.LEFT, fill='y', padx=5, pady=5)
        
        self.store_list = tk.Listbox(store_list_frame, width=30)
        self.store_list.pack(fill='both', expand=True)
        
        btn_frame = ttk.Frame(store_list_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_stores).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Neu", command=self.show_create_dialog).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Löschen", command=self.delete_store).grid(row=0, column=2, padx=2)
        
        # Rechte Seite: Store Details
        detail_frame = ttk.LabelFrame(self.store_tab, text="Details")
        detail_frame.pack(side=tk.RIGHT, fill='both', expand=True, padx=5, pady=5)
        
        self.detail_text = scrolledtext.ScrolledText(detail_frame, height=15)
        self.detail_text.pack(fill='both', expand=True)
        
        ttk.Button(detail_frame, text="Status prüfen", command=self.check_status).pack(pady=5)
        
    def setup_file_tab(self):
        # Datei Upload Bereich
        upload_frame = ttk.LabelFrame(self.file_tab, text="Datei Upload")
        upload_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(upload_frame, text="Datei auswählen", command=self.select_file).grid(row=0, column=0, padx=2)
        self.file_label = ttk.Label(upload_frame, text="Keine Datei ausgewählt")
        self.file_label.grid(row=0, column=1, padx=2)
        
        ttk.Button(upload_frame, text="Hochladen", command=self.upload_file).grid(row=0, column=2, padx=2)
        
        # Dateiliste
        self.file_list = ttk.Treeview(self.file_tab, columns=('id', 'status'), show='headings')
        self.file_list.heading('id', text='Datei ID')
        self.file_list.heading('status', text='Status')
        self.file_list.pack(fill='both', expand=True, padx=5, pady=5)
        
    def setup_log_panel(self):
        # Log Bereich
        log_frame = ttk.LabelFrame(self.root, text="Logs")
        log_frame.pack(fill='x', padx=5, pady=5)
        
        self.log = scrolledtext.ScrolledText(log_frame, height=8)
        self.log.pack(fill='x')
        
    def refresh_stores(self):
        self.store_list.delete(0, tk.END)
        try:
            stores = self.client.list_vector_stores()
            for store in stores:
                self.store_list.insert(tk.END, f"{store['name']} ({store['id']})")
        except Exception as e:
            self.log_message(f"Fehler: {str(e)}")
            
    def show_create_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Neuer Vector Store")
        
        ttk.Label(dialog, text="Name:").grid(row=0, column=0)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1)
        
        ttk.Button(dialog, text="Erstellen", command=lambda: self.create_store(
            name_entry.get(),
            dialog
        )).grid(row=1, columnspan=2)
        
    def create_store(self, name, dialog):
        try:
            self.client.create_vector_store(name=name)
            self.refresh_stores()
            dialog.destroy()
            self.log_message(f"Store '{name}' erstellt")
        except Exception as e:
            self.log_message(f"Fehler: {str(e)}")
            
    def delete_store(self):
        selection = self.store_list.curselection()
        if not selection:
            return
            
        store_id = self.store_list.get(selection[0]).split("(")[-1].strip(")")
        try:
            self.client.delete_vector_store(store_id)
            self.refresh_stores()
            self.log_message(f"Store {store_id} gelöscht")
        except Exception as e:
            self.log_message(f"Fehler: {str(e)}")
            
    def check_status(self):
        selection = self.store_list.curselection()
        if not selection:
            return
            
        store_id = self.store_list.get(selection[0]).split("(")[-1].strip(")")
        try:
            status = self.client.poll_until_ready(store_id)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, str(status))
        except Exception as e:
            self.log_message(f"Fehler: {str(e)}")
            
    def select_file(self):
        self.selected_file = filedialog.askopenfilename()
        self.file_label.config(text=self.selected_file)
        
    def upload_file(self):
        if not hasattr(self, 'selected_file'):
            return
            
        selection = self.store_list.curselection()
        if not selection:
            return
            
        store_id = self.store_list.get(selection[0]).split("(")[-1].strip(")")
        
        def upload():
            try:
                result = self.client.upload_file(store_id, self.selected_file)
                self.log_message(f"Datei {self.selected_file} hochgeladen: {result['id']}")
                self.update_file_list(store_id)
            except Exception as e:
                self.log_message(f"Fehler: {str(e)}")
                
        threading.Thread(target=upload).start()
        
    def update_file_list(self, store_id):
        try:
            files = self.client.list_files(store_id)
            self.file_list.delete(*self.file_list.get_children())
            for file in files:
                self.file_list.insert('', 'end', values=(file['id'], file['status']))
        except Exception as e:
            self.log_message(f"Fehler: {str(e)}")
            
    def log_message(self, message):
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = VectorStoreGUI(root)
    root.mainloop()
