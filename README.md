# URL Shortener With QR Code Generator

## Overview

This is an advanced URL shortener application built using Python, Tkinter, SQLite, and various libraries like `qrcode`, `pyperclip`, and `PIL`. The application allows users to shorten long URLs, customize short codes, generate QR codes, view URL history, and analyze usage statistics.

## Features

- **Shorten URLs**: Input a long URL and generate a custom or random short URL.
- **Generate QR Code**: Create a QR code for the shortened URL.
- **URL History**: View a list of previously shortened URLs, along with their creation dates and click count.
- **Analytics**: View statistics such as total URLs, total clicks, and average clicks for all shortened URLs.
- **Settings**: Adjust the short URL length.

## Requirements

Before running the application, ensure you have the following libraries installed:

- `tkinter`
- `sqlite3`
- `qrcode`
- `pyperclip`
- `PIL` (Pillow)
- `requests`

Install these dependencies using `pip`:

```bash
pip install qrcode[pil] pyperclip pillow requests
```

## Usage

1. **Shorten a URL**:
   - Enter a long URL into the text field.
   - Optionally, check the box to provide a custom short code.
   - Click "Shorten URL" to generate a shortened URL.
   - The shortened URL will appear in the result section and can be copied with a single click.

2. **Generate a QR Code**:
   - After shortening a URL, click the "Generate QR Code" button to create a scannable QR code for the shortened URL.

3. **View URL History**:
   - Navigate to the "URL History" tab to view all previously shortened URLs along with their creation timestamps and click counts.
   - You can search through your history, copy URLs, or delete them.

4. **Analytics**:
   - The "Analytics" tab displays statistics about the total number of URLs shortened, the total number of clicks, and the average number of clicks for all shortened URLs.

5. **Settings**:
   - In the "Settings" tab, you can configure the length of the short codes.

## Database

The application uses an SQLite database (`url_shortener.db`) to store URL records, including the long URL, short code, creation date, and click count.
