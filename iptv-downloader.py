import requests
import tkinter as tk
from tkinter import messagebox, Listbox, ttk
import threading
import json

# IPTV credentials
USERNAME = 'ahmadismael92'
PASSWORD = '648840449'
BASE_URL = 'http://lionzhd.com:8080'
PLAYER_API = f'{BASE_URL}/player_api.php?username={USERNAME}&password={PASSWORD}'

# Global variables to hold all movies
all_movies = []
search_movie_indices = []  # To store indices of movies displayed in search
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
def download_movie(selected_movie):
    stream_id = selected_movie['stream_id']
    movie_name = selected_movie['name']
    container_extension = selected_movie['container_extension']

    movie_url = f'{BASE_URL}/movie/{USERNAME}/{PASSWORD}/{stream_id}.{container_extension}'
    response = requests.get(movie_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    if total_size == 0:
        messagebox.showerror("Error", "Failed to download movie")
        return

    with open(f'{movie_name}.{container_extension}', 'wb') as file:
        progress_bar['value'] = 0  # Reset progress bar for download
        progress_bar['maximum'] = total_size
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                progress_bar['value'] += len(chunk)
                root.update_idletasks()

    messagebox.showinfo("Download Complete", f"{movie_name} has been downloaded!")


# Function to search and display movies
def search_movies():
    global search_movie_indices
    query = search_entry.get().lower()
    search_results.delete(0, tk.END)
    search_movie_indices = []  # Clear previous search result indices

    for i, movie in enumerate(all_movies):
        if query in movie['name'].lower():
            search_results.insert(tk.END, movie['name'])
            search_movie_indices.append(i)  # Store the index of the movie in all_movies

    search_results.bind('<<ListboxSelect>>', on_movie_select)


# Function to display the selected movie details
def on_movie_select(event):
    global selected_movie
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        selected_movie = all_movies[search_movie_indices[index]]  # Get movie using the correct index

        # Update download button and enable it
        download_button.pack()


# Function to fetch all movies and update progress bar
def fetch_movies():
    global all_movies
    all_movies.clear()  # Reset the list of movies to avoid duplication
    categories = get_categories()
    total_categories = len(categories)
    progress['maximum'] = total_categories

    for i, category in enumerate(categories):
        category_id = category['category_id']
        movies = get_movies(category_id)
        all_movies.extend(movies)
        progress['value'] = i + 1
        root.update_idletasks()

    # Save all_movies into a JSON file
    with open('movies_data.json', 'w') as json_file:
        json.dump(all_movies, json_file, indent=4)

    # Hide progress bar and show search UI
    progress.pack_forget()
    search_label.pack(pady=10)
    search_entry.pack()
    search_button.pack(pady=5)
    search_results.pack()


# Function to start the download process
def start_download():
    if selected_movie:
        progress_bar.pack(pady=10)

        # Run the download in a separate thread to prevent UI freezing
        threading.Thread(target=download_movie, args=(selected_movie,), daemon=True).start()


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

# Download button
download_button = tk.Button(root, text="Download", command=start_download)

# Progress bar for downloading
progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')

# Fetch movies in the background after the app starts
root.after(100, fetch_movies)

root.mainloop()
