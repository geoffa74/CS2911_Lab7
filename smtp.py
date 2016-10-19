#: ## Lab 7 ##
#:
#: CS-2911 Network Protocols
#: Dr. Yoder
#: Fall quarter 2016-2017
#:
#: | Team members (username) |
#: |:------------------------|
#: | Jon Sonderman (sondermajj)  |
#: | Geoff Appelbaum (appelbaumgl)   |
#:
#: Thanks to Trip Horbinski from the Fall 2015 class for providing the password-entering functionality.

# GUI library for password entry
import tkinter as tk

# Socket library
import socket

import time

# SSL/TLS library
import ssl

# base-64 encode/decode
import base64

# Python date/time and timezone modules
import datetime
import time
import pytz
import tzlocal

# Module for reading password from console without echoing it
import getpass

# Modules for some file operations
import os
import mimetypes

# Host name for MSOE (hosted) SMTP server
SMTP_SERVER = 'smtp.office365.com'

# The default port for STARTTLS SMTP servers is 587
SMTP_PORT = 587

# SMTP domain name
SMTP_DOMAINNAME = 'msoe.edu'


def main():
    """Main test method to send an SMTP email message.

    Modify data as needed/desired to test your code,
    but keep the same interface for the smtp_send
    method.
    """
    (username, password) = login_gui()

    message_info = {}
    message_info['To'] = 'sondermanjj@msoe.edu'
    message_info['From'] = username
    message_info['Subject'] = 'Yet another test message'
    message_info['Date'] = 'Thu, 9 Oct 2014 23:56:09 +0000'
    message_info['Date'] = get_formatted_date()

    print("message_info =", message_info)
    print()

    message_info['Text'] = 'Test message_info number 6\r\n\r\nAnother line.'

    smtp_send(password, message_info)


def login_gui():
    """Creates a graphical user interface for secure user authorization.

    Returns:
        username_value -- The username as a string.
        password_value -- The password as a string.

    Author: Tripp Horbinski
    """
    gui = tk.Tk()
    gui.title("MSOE Email Client")
    center_gui_on_screen(gui, 370, 120)

    tk.Label(gui, text="Please enter your MSOE credentials below:") \
        .grid(row=0, columnspan=2)
    tk.Label(gui, text="Email Address: ").grid(row=1)
    tk.Label(gui, text="Password:         ").grid(row=2)

    username = tk.StringVar()
    username_input = tk.Entry(gui, textvariable=username)
    username_input.grid(row=1, column=1)

    password = tk.StringVar()
    password_input = tk.Entry(gui, textvariable=password, show='*')
    password_input.grid(row=2, column=1)

    auth_button = tk.Button(gui, text="Authenticate", width=25, command=gui.destroy)
    auth_button.grid(row=3, column=1)

    gui.mainloop()

    username_value = username.get()
    password_value = password.get()

    return username_value, password_value


def center_gui_on_screen(gui, gui_width, gui_height):
    """Centers the graphical user interface on the screen.

    Args:
        gui: The graphical user interface to be centered.
        gui_width: The width of the graphical user interface.
        gui_height: The height of the graphical user interface.

    Returns:
        The graphical user interface coordinates for the center of the screen.

    Author: Tripp Horbinski
    """
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    x_coord = (screen_width / 2) - (gui_width / 2)
    y_coord = (screen_height / 2) - (gui_height / 2)

    return gui.geometry('%dx%d+%d+%d' % (gui_width, gui_height, x_coord, y_coord))


# *** Do not modify code above this line ***

def smtp_send(password, message_info):
    """Send a message via SMTP.

    Args:
        password: String containing user password.
        message_info: Dictionary with string values for the following keys:
                'To': Recipient address (only one recipient required)
                'From': Sender address
                'Date': Date string for current date/time in SMTP format
                'Subject': Email subject
            Other keys can be added to support other email headers, etc.
    """
    #Initial handshake
    smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    smtp_socket.connect((SMTP_SERVER, SMTP_PORT))
    print(read_line(smtp_socket))
    smtp_socket.send(b'EHLO ' + SMTP_DOMAINNAME.encode() + b'\r\n')
    print()
    read_lines(smtp_socket, 9)


    smtp_socket.send(b'STARTTLS\r\n')
    print()
    print(read_line(smtp_socket))

    context = ssl.create_default_context()
    wrapped_socket = context.wrap_socket(smtp_socket, server_hostname=SMTP_SERVER)

    authentication(message_info, wrapped_socket, password)

    # sends the actual information
    send_data(message_info, wrapped_socket)
    print()
    print(read_line(wrapped_socket))
    wrapped_socket.send(b'QUIT\r\n')
    print()
    print(read_line(wrapped_socket))

def authentication(message_info, wrapped_socket, password):
    """Authenticates information from the wrapped socket

         Args:
             smtp_socket: Socket that we are reading the information from
             message_info: Email information that we're sending to the server
         """
    wrapped_socket.send(b'EHLO ' + SMTP_DOMAINNAME.encode())
    wrapped_socket.send(b'\r\n')

    print()
    read_lines(wrapped_socket, 9)

    wrapped_socket.send(b'AUTH LOGIN\r\n')
    print()
    print(read_line(wrapped_socket))
    wrapped_socket.send(base64.b64encode(message_info['From'].encode()) + b'\r\n')
    print()
    print(read_line(wrapped_socket))
    wrapped_socket.send(base64.b64encode(password.encode()) + b'\r\n')
    print()

    # Checks the sender/recipient for good emails.
    print(read_line(wrapped_socket))
    wrapped_socket.send(b'MAIL FROM:<' + message_info['From'].encode() + b'>\r\n')
    print()
    print(read_line(wrapped_socket))
    wrapped_socket.send(b'RCPT TO:<' + message_info['To'].encode() + b'>\r\n')
    print()
    print(read_line(wrapped_socket))
    wrapped_socket.send(b'DATA\r\n')
    print()
    print(read_line(wrapped_socket))

def send_data(message_info, wrapped_socket):
    """Sends the message info chunk to the server

        Args:
            smtp_socket: Socket that we are reading the information from
            message_info: Email information that we're sending to the server
        """
    wrapped_socket.send(b'From: ' + message_info['From'].encode() + b'\r\n')
    wrapped_socket.send(b'To: ' + message_info['To'].encode() + b'\r\n')
    wrapped_socket.send(b'Date: ' + message_info['Date'].encode() + b'\r\n')
    wrapped_socket.send(b'Subject: ' + message_info['Subject'].encode() + b'\r\n')
    wrapped_socket.send(b'\r\n')
    wrapped_socket.send(b'Subject: ' + message_info['Text'].encode() + b'\r\n')
    wrapped_socket.send(b'\r\n.\r\n')


def read_lines(smtp_socket, number):
    """reads a specificed number of lines of a reply from the server

        Args:
            smtp_socket: Socket that we are reading the information from
            number: number of lines to read
        """
    for x in range(0, number):
        print(read_line(smtp_socket))


def read_line(smtp_socket):
    """read a single line of a reply from the server

        Args:
            smtp_socket: Socket that we are reading the information from
        """
    bytes = b''
    next_byte = b''
    exit_bytes = b''
    while exit_bytes != b'\r\n':
        next_byte = smtp_socket.recv(1)
        if next_byte == b'\r' or next_byte == b'\n':
            exit_bytes += next_byte
        else:
            bytes += next_byte
    return bytes.decode()


# ** Do not modify code below this line. **

# Utility functions
# You may use these functions to simplify your code.


def get_formatted_date():
    """Get the current date and time, in a format suitable for an email date header.

    The constant TIMEZONE_NAME should be one of the standard pytz timezone names.
    If you really want to see them all, call the print_all_timezones function.

    tzlocal suggested by http://stackoverflow.com/a/3168394/1048186

    See RFC 5322 for details about what the timezone should be
    https://tools.ietf.org/html/rfc5322

    Returns:
         Formatted current date/time value, as a string.
    """
    zone = tzlocal.get_localzone()
    print("zone =", zone)
    timestamp = datetime.datetime.now(zone)
    timestring = timestamp.strftime('%a, %d %b %Y %H:%M:%S %z')  # Sun, 06 Nov 1994 08:49:37 +0000
    return timestring


def print_all_timezones():
    """Print all pytz timezone strings.
    """
    for tz in pytz.all_timezones:
        print(tz)


# You probably won't need the following methods, unless you decide to
# try to handle email attachments or send multi-part messages.
# These advanced capabilities are not required for the lab assignment.

def get_mime_type(file_path):
    """Try to guess the MIME type of a file (resource), given its path (primarily its file extension)

    Args:
        file_path: String containing path to (resource) file, such as './abc.jpg'

    Returns:
        If successful in guessing the MIME type, a string representing the content
          type, such as 'image/jpeg'
        Otherwise, None
    """
    mime_type_and_encoding = mimetypes.guess_type(file_path)
    mime_type = mime_type_and_encoding[0]
    return mime_type


def get_file_size(file_path):
    """Try to get the size of a file (resource) in bytes, given its path

    Args:
        file_path -- String containing path to (resource) file, such as './abc.html'

    Returns:
        If file_path designates a normal file, an integer value representing the the file size in bytes
        Otherwise (no such file, or path is not a file), None
    """
    # Initially, assume file does not exist
    file_size = None
    if os.path.isfile(file_path):
        file_size = os.stat(file_path).st_size
    return file_size


main()
