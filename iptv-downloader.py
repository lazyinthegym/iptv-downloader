import requests
import tkinter as tk
from tkinter import messagebox, Listbox, ttk
from PIL import Image, ImageTk
import io

# IPTV credentials
USERNAME = 'ahmadismael92'
PASSWORD = '648840449'
BASE_URL = 'http://lionzhd.com:8080'
PLAYER_API = f'{BASE_URL}/player_api.php?username={USERNAME}&password={PASSWORD}'

# Global variables to hold all movies
all_movies = []
selected_movie = None  # To keep track of the currently selected movie


# Function to get movie categories
def get_categories():
    response = requests.get(f'{PLAYER_API}&action=get_vod_categories')
    return response.json() if response.status_code == 200 else []


# Function to get movies in a category
def get_movies(category_id):
    response = requests.get(f'{PLAYER_API}&action=get_vod_streams&category_id={category_id}')
    return response.json() if response.status_code == 200 else []


# Function to download movie
def download_movie(stream_id, movie_name):
    movie_url = f'{BASE_URL}/movie/{USERNAME}/{PASSWORD}/{stream_id}.mkv'
    response = requests.get(movie_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    if total_size == 0:
        messagebox.showerror("Error", "Failed to download movie")
        return

    with open(f'{movie_name}.mkv', 'wb') as file:
        progress_bar['maximum'] = total_size
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                progress_bar['value'] += len(chunk)
                root.update_idletasks()

    messagebox.showinfo("Download Complete", f"{movie_name} has been downloaded!")


# Function to search and display movies
def search_movies():
    query = search_entry.get().lower()
    search_results.delete(0, tk.END)
    for movie in all_movies:
        if query in movie['name'].lower():
            search_results.insert(tk.END, movie['name'])
    search_results.bind('<<ListboxSelect>>', on_movie_select)


# Function to display the selected movie details
def on_movie_select(event):
    global selected_movie
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        selected_movie = all_movies[index]
        stream_id = selected_movie['stream_id']

        # Show the movie image
        load_movie_image(selected_movie['stream_icon'])

        # Update download button and enable it
        download_button.pack()


# Function to load the movie image
def load_movie_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_data = Image.open(io.BytesIO(response.content))
        image_data = image_data.resize((200, 300), Image.ANTIALIAS)  # Resize image
        movie_image = ImageTk.PhotoImage(image_data)

        movie_image_label.config(image=movie_image)
        movie_image_label.image = movie_image  # Keep a reference
        movie_image_label.pack()


# Function to fetch all movies and update progress bar
def fetch_movies():
    global all_movies
    categories = get_categories()
    total_categories = len(categories)
    progress['maximum'] = total_categories

    for i, category in enumerate(categories):
        category_id = category['category_id']
        movies = get_movies(category_id)
        all_movies.extend(movies)
        progress['value'] = i + 1
        root.update_idletasks()

    # Hide progress bar and show search UI
    progress.pack_forget()
    search_label.pack(pady=10)
    search_entry.pack()
    search_button.pack(pady=5)
    search_results.pack()


# Function to start the download process
def start_download():
    if selected_movie:
        stream_id = selected_movie['stream_id']
        movie_name = selected_movie['name']
        progress_bar.pack(pady=10)
        download_movie(stream_id, movie_name)


# GUI setup
root = tk.Tk()
root.title('IPTV Movie Downloader')

# Set window size and make it resizable
root.geometry('800x600')
root.resizable(True, True)

# Progress bar for fetching movies
progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress.pack(pady=20)

# Search UI
search_label = tk.Label(root, text="Search Movies")
search_entry = tk.Entry(root, width=50)
search_button = tk.Button(root, text="Search", command=search_movies)
search_results = Listbox(root, width=50, height=15)

# Movie image display
movie_image_label = tk.Label(root)
download_button = tk.Button(root, text="Download", command=start_download)

# Progress bar for downloading
progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')

# Fetch movies in the background after the app starts
root.after(100, fetch_movies)

root.mainloop()
