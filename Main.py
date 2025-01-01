import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import string
import random
import re
from urllib.parse import urlparse
import webbrowser
import pyperclip
import datetime
import requests
from threading import Thread
import qrcode # type: ignore
from PIL import Image, ImageTk
import io

class URLShortenerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced URL Shortener")
        self.root.geometry("800x600")
        
        # Initialize the database
        self.shortener = URLShortener()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.create_shorten_tab()
        self.create_history_tab()
        self.create_analytics_tab()
        self.create_settings_tab()
        
        # Style configuration
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TLabel', padding=5)
        
    def create_shorten_tab(self):
        shorten_frame = ttk.Frame(self.notebook)
        self.notebook.add(shorten_frame, text='Shorten URL')
        
        # URL Entry
        url_frame = ttk.Frame(shorten_frame)
        url_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(url_frame, text="Enter Long URL:").pack(side='left')
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Custom Short Code Option
        custom_frame = ttk.Frame(shorten_frame)
        custom_frame.pack(fill='x', padx=10, pady=5)
        
        self.custom_var = tk.BooleanVar()
        ttk.Checkbutton(custom_frame, text="Use Custom Short Code", 
                       variable=self.custom_var, 
                       command=self.toggle_custom_entry).pack(side='left')
        
        self.custom_entry = ttk.Entry(custom_frame, state='disabled')
        self.custom_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(shorten_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Shorten URL", 
                  command=self.shorten_url).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Generate QR Code", 
                  command=self.generate_qr).pack(side='left', padx=5)
        
        # Result Frame
        self.result_frame = ttk.LabelFrame(shorten_frame, text="Result")
        self.result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.short_url_label = ttk.Label(self.result_frame, text="")
        self.short_url_label.pack(pady=5)
        
        self.qr_label = ttk.Label(self.result_frame)
        self.qr_label.pack(pady=5)
        
    def create_history_tab(self):
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text='URL History')
        
        # Search Frame
        search_frame = ttk.Frame(history_frame)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_urls)
        
        # Treeview for URL history
        columns = ('Long URL', 'Short Code', 'Created At', 'Clicks')
        self.tree = ttk.Treeview(history_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Copy URL", 
                  command=self.copy_url).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Selected", 
                  command=self.delete_url).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Refresh", 
                  command=self.refresh_history).pack(side='left', padx=5)
        
        self.refresh_history()
        
    def create_analytics_tab(self):
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text='Analytics')
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(analytics_frame, text="Statistics")
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.total_urls_label = ttk.Label(stats_frame, text="Total URLs: 0")
        self.total_urls_label.pack(pady=5)
        
        self.total_clicks_label = ttk.Label(stats_frame, text="Total Clicks: 0")
        self.total_clicks_label.pack(pady=5)
        
        self.avg_clicks_label = ttk.Label(stats_frame, text="Average Clicks: 0")
        self.avg_clicks_label.pack(pady=5)
        
        # Update statistics
        self.update_statistics()
        
    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text='Settings')
        
        # Short Code Length
        length_frame = ttk.Frame(settings_frame)
        length_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(length_frame, text="Short Code Length:").pack(side='left')
        self.length_var = tk.StringVar(value=str(self.shortener.short_length))
        length_spin = ttk.Spinbox(length_frame, from_=4, to=12, 
                                textvariable=self.length_var)
        length_spin.pack(side='left', padx=5)
        
        # Save Button
        ttk.Button(settings_frame, text="Save Settings", 
                  command=self.save_settings).pack(pady=10)
        
    def toggle_custom_entry(self):
        if self.custom_var.get():
            self.custom_entry.config(state='normal')
        else:
            self.custom_entry.config(state='disabled')
            
    def shorten_url(self):
        long_url = self.url_entry.get()
        custom_code = self.custom_entry.get() if self.custom_var.get() else None
        
        try:
            short_code = self.shortener.shorten_url(long_url, custom_code)
            short_url = f"domain.com/{short_code}"
            self.short_url_label.config(
                text=f"Shortened URL: {short_url}\nClick to copy!")
            self.short_url_label.bind('<Button-1>', 
                                    lambda e: pyperclip.copy(short_url))
            self.generate_qr(short_url)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            
    def generate_qr(self, url=None):
        if url is None:
            url = f"domain.com/{self.short_url_label.cget('text').split('/')[-1]}"
            
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_photo = ImageTk.PhotoImage(qr_image)
        
        self.qr_label.config(image=qr_photo)
        self.qr_label.image = qr_photo
        
    def refresh_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        urls = self.shortener.get_all_urls()
        for url in urls:
            self.tree.insert('', 'end', values=url)
            
    def search_urls(self, event=None):
        search_term = self.search_entry.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        urls = self.shortener.get_all_urls()
        for url in urls:
            if (search_term in url[0].lower() or 
                search_term in url[1].lower()):
                self.tree.insert('', 'end', values=url)
                
    def copy_url(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a URL to copy")
            return
            
        item = self.tree.item(selected[0])
        short_url = f"domain.com/{item['values'][1]}"
        pyperclip.copy(short_url)
        messagebox.showinfo("Success", "URL copied to clipboard!")
        
    def delete_url(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a URL to delete")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete?"):
            item = self.tree.item(selected[0])
            self.shortener.delete_url(item['values'][1])
            self.refresh_history()
            self.update_statistics()
            
    def update_statistics(self):
        stats = self.shortener.get_statistics()
        self.total_urls_label.config(text=f"Total URLs: {stats['total_urls']}")
        self.total_clicks_label.config(text=f"Total Clicks: {stats['total_clicks']}")
        self.avg_clicks_label.config(
            text=f"Average Clicks: {stats['avg_clicks']:.2f}")
        
    def save_settings(self):
        try:
            length = int(self.length_var.get())
            self.shortener.short_length = length
            messagebox.showinfo("Success", "Settings saved successfully!")
        except ValueError:
            messagebox.showerror("Error", "Invalid short code length")

class URLShortener:
    def __init__(self, db_name='url_shortener.db'):
        self.db_name = db_name
        self.short_length = 6
        self.initialize_db()
    
    def initialize_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             long_url TEXT NOT NULL,
             short_code TEXT NOT NULL UNIQUE,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             clicks INTEGER DEFAULT 0)
        ''')
        conn.commit()
        conn.close()
    
    def generate_short_code(self):
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) 
                         for _ in range(self.short_length))
            if not self.code_exists(code):
                return code
    
    def code_exists(self, code):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM urls WHERE short_code = ?', (code,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def shorten_url(self, long_url, custom_code=None):
        if not self.is_valid_url(long_url):
            raise ValueError("Invalid URL format. Please include http:// or https://")
        
        if custom_code and self.code_exists(custom_code):
            raise ValueError("Custom code already exists")
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT short_code FROM urls WHERE long_url = ?', 
                      (long_url,))
        result = cursor.fetchone()
        
        if result:
            short_code = result[0]
        else:
            short_code = custom_code if custom_code else self.generate_short_code()
            cursor.execute('''INSERT INTO urls (long_url, short_code) 
                            VALUES (?, ?)''', (long_url, short_code))
            conn.commit()
        
        conn.close()
        return short_code
    
    def get_long_url(self, short_code):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''UPDATE urls SET clicks = clicks + 1 
                         WHERE short_code = ?''', (short_code,))
        cursor.execute('SELECT long_url FROM urls WHERE short_code = ?', 
                      (short_code,))
        
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        
        if result:
            return result[0]
        raise ValueError("Short code not found")
    
    def get_all_urls(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT long_url, short_code, created_at, clicks 
                         FROM urls ORDER BY created_at DESC''')
        urls = cursor.fetchall()
        conn.close()
        return urls
    
    def delete_url(self, short_code):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM urls WHERE short_code = ?', (short_code,))
        conn.commit()
        conn.close()
    
    
    def get_statistics(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM urls')
        total_urls = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(clicks) FROM urls')
        total_clicks = cursor.fetchone()[0] or 0
        
        avg_clicks = total_clicks / total_urls if total_urls > 0 else 0
        
        conn.close()  # Fixed missing conn.close()
        
        return {
            'total_urls': total_urls,
            'total_clicks': total_clicks,
            'avg_clicks': avg_clicks
        }

# Main part to run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = URLShortenerGUI(root)
    root.mainloop()
