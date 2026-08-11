import webbrowser
from urllib.parse import quote_plus


def open_website(target):
    target = target.strip()

    if not target:
        return False

    if target.startswith("http://") or target.startswith("https://"):
        url = target

    elif "." in target:
        url = f"https://{target}"

    else:
        return False

    webbrowser.open(url)

    return True


def search_google(query):
    query = query.strip()

    if not query:
        return False

    encoded_query = quote_plus(query)

    url = f"https://www.google.com/search?q={encoded_query}"

    webbrowser.open(url)

    return True