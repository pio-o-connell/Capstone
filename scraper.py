# scraper.py
import os
import django
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# ----------------------------
# CONFIG — Edit these
# ----------------------------
DJANGO_SETTINGS_MODULE = "config.settings"  # <- change if your settings path is different
APP_NAME = "blog"                           # <- change to the app that contains Post and Comment
REQUEST_DELAY = 2                           # seconds between requests
USER_FOR_UNKNOWN_COMMENTS = "scraperbot"    # username for comments when no author found
MAX_CONTENT_CHARS = 100000                  # safety cap for content length

# ----------------------------
# Setup Django env
# ----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction

# Import models from your app
try:
    models_module = __import__(f"{APP_NAME}.models", fromlist=["Post", "Comment"])
    Post = getattr(models_module, "Post")
    Comment = getattr(models_module, "Comment")
except Exception as e:
    raise ImportError(f"Cannot import Post/Comment from app '{APP_NAME}': {e}")

# ----------------------------
# Utility helpers
# ----------------------------
def slugify_username(name: str) -> str:
    """Create a safe username from an author name."""
    name = (name or "anon").strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^\w\-\.]", "", name)
    # truncate to reasonable username length
    return name[:150] or "anon"

def get_or_create_user_for_author(author_name: str):
    """Return a Django User for a scraped author name (create if necessary)."""
    if not author_name:
        u, _ = User.objects.get_or_create(username=USER_FOR_UNKNOWN_COMMENTS)
        return u
    username = slugify_username(author_name)
    # ensure uniqueness: append numbers until unique if necessary
    base = username
    i = 0
    while True:
        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(username=username)
                if created:
                    # mark unusable password (we're not using these accounts for login)
                    user.set_unusable_password()
                    user.save()
                return user
        except IntegrityError:
            i += 1
            username = f"{base[:140]}{i}"

# ----------------------------
# Sites & selectors (15 sites)
# Note: selectors are best-effort. Use browser inspector to refine as needed.
# ----------------------------
scraping_rules = {
    # Irish / local
    "https://www.botanicgardens.ie/blog/": {
        "post_selector": "article, div.blog-item, div.post",
        "title_selector": "h2.entry-title a, h2 a, header h1 a",
        "content_selector": "div.entry-content, div.post-content, .content",
        "pagination_selector": "a.next, a[rel='next']",
    },
    "https://fruit-hill-farm.com/": {
        "post_selector": "article.post, article",
        "title_selector": "h2.entry-title a, h1.entry-title a, .post-title a",
        "content_selector": "div.entry-content, .post-content",
        "pagination_selector": "a.next, .pagination a.next",
    },
    "https://www.betterplants.ie/blog/": {
        "post_selector": "article.post, article",
        "title_selector": "h1.post-title a, h2.entry-title a",
        "content_selector": "div.post-content, .entry-content",
    },
    # placeholder sites (replace if you have real URLs)
    "https://master-my-garden.example.com/": {
        "post_selector": "article.post, article",
        "title_selector": "h2.title a, h1 a",
        "content_selector": "div.content, .post-body",
    },
    "https://littlegreengrowers.example.com/": {
        "post_selector": "article",
        "title_selector": "h1 a, h2 a",
        "content_selector": "div.post-body, .entry-content",
    },

    # UK / broader
    "https://gardenista.com/": {
        "post_selector": "article.post, div.single-post, article",
        "title_selector": "h1.post-title, h1.entry-title",
        "content_selector": "div.post-content, .entry-content",
        "pagination_selector": ".pagination a.next, a.next",
    },
    "https://themiddlesizedgarden.co.uk/": {
        "post_selector": "article.post, div.post",
        "title_selector": "h2.entry-title a, h1.entry-title a",
        "content_selector": "div.entry-content, .post-content",
    },
    "https://www.gardenstone.co.uk/": {
        "post_selector": "article.post, .post",
        "title_selector": "h2.entry-title a, h1.entry-title a",
        "content_selector": "div.entry-content, .post-content",
    },
    "https://awaytogarden.com/": {
        "post_selector": "article, div.post, .post",
        "title_selector": "h2.title a, h1 a",
        "content_selector": "div.post-body, .entry-content",
    },
    "https://www.epicgardening.com/": {
        "post_selector": "article, div.post, .post",
        "title_selector": "h1.entry-title, h1.post-title",
        "content_selector": "div.post-content, .entry-content",
    },
    "https://gardenology.org/": {
        "post_selector": "div.page, article",
        "title_selector": "h1",
        "content_selector": "div#content, .content",
    },
    "https://englishgardenmag.co.uk/": {
        "post_selector": "article.post, article",
        "title_selector": "h1.entry-title, h1.post-title",
        "content_selector": "div.entry-content, .post-content",
    },
    "https://www.gardeningetc.com/": {
        "post_selector": "div.post, article",
        "title_selector": "h2.post-title a, h1 a",
        "content_selector": "div.post-body, .entry-content",
    },
    "https://www.gardenersworld.com/": {
        "post_selector": "article.article-card, article",
        "title_selector": "h2.article-title a, h1 a",
        "content_selector": "div.article-body, .post-content",
        "pagination_selector": ".pagination a.next, a.next",
    },
    "https://www.finegardening.com/": {
        "post_selector": "div.post-card, article, .post",
        "title_selector": "h2.post-title a, h1 a",
        "content_selector": "div.post-content, .entry-content",
    },
}

# ----------------------------
# Scrape logic
# ----------------------------
def extract_text_safely(elem):
    if not elem:
        return ""
    txt = elem.get_text(separator="\n", strip=True)
    if len(txt) > MAX_CONTENT_CHARS:
        return txt[:MAX_CONTENT_CHARS]
    return txt

def find_title_and_url(post_html, title_selector, base_url):
    # try to find the element matching title_selector; prefer <a href>
    t_elem = None
    if title_selector:
        t_elem = post_html.select_one(title_selector)
    # fallback to common tags
    if not t_elem:
        t_elem = post_html.find(["h1", "h2", "h3", "a"])
    title = extract_text_safely(t_elem)
    # attempt to find href
    href = None
    if t_elem:
        if t_elem.name == "a" and t_elem.has_attr("href"):
            href = t_elem["href"]
        else:
            a = t_elem.find("a")
            if a and a.has_attr("href"):
                href = a["href"]
    if href:
        href = urljoin(base_url, href)
    return title, href

def scrape_site(site_url, rules):
    print("\n=== Scraping site:", site_url)
    page_url = site_url
    visited_pages = set()

    while page_url:
        if page_url in visited_pages:
            print("Already visited page, stopping pagination loop:", page_url)
            break
        visited_pages.add(page_url)

        print("Fetching:", page_url)
        try:
            resp = requests.get(page_url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (compatible; scraperbot/1.0)"})
            resp.raise_for_status()
        except Exception as e:
            print("  Failed to fetch page:", e)
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        selector = rules.get("post_selector", "article")
        posts_html = soup.select(selector)
        print(f"  Found {len(posts_html)} candidate post elements using selector '{selector}'")

        for idx, post_html in enumerate(posts_html, start=1):
            title, post_href = find_title_and_url(post_html, rules.get("title_selector"), page_url)
            content_elem = post_html.select_one(rules.get("content_selector", "div"))
            content = extract_text_safely(content_elem)

            if not title:
                print(f"    [{idx}] Skipped: no title found")
                continue
            # Show short preview
            print(f"    [{idx}] Title: {title[:80]!s}")

            # Save post (dedupe by title)
            post_obj, created = Post.objects.get_or_create(
                title=title,
                defaults={"content": content}
            )
            if created:
                print("      -> Created Post:", post_obj.title)
            else:
                # update content if missing or empty
                if not post_obj.content and content:
                    post_obj.content = content
                    post_obj.save(update_fields=["content"])
                    print("      -> Updated missing content for existing Post")
                else:
                    print("      -> Post already exists (by title)")

            # Optional: scrape comments if page contains comment elements within post_html
            comment_selector = rules.get("comment_selector")  # if provided in rules
            if comment_selector:
                comment_elements = post_html.select(comment_selector)
                print(f"      Found {len(comment_elements)} comment elements (selector '{comment_selector}')")
                for cidx, ce in enumerate(comment_elements, start=1):
                    author_elem = ce.select_one(rules.get("comment_author_selector", "")) if rules.get("comment_author_selector") else None
                    comment_author = author_elem.get_text(strip=True) if author_elem else None
                    comment_text = extract_text_safely(ce)
                    if not comment_text:
                        continue
                    user_obj = get_or_create_user_for_author(comment_author)
                    # avoid duplicate identical comments for the same post/author/content
                    comment_obj, c_created = Comment.objects.get_or_create(
                        post=post_obj,
                        author=user_obj,
                        content=comment_text
                    )
                    if c_created:
                        print(f"        -> Created comment #{cidx} by {user_obj.username}")
                    else:
                        print(f"        -> Comment #{cidx} already exists")
            # Small delay between processing posts to be polite
            time.sleep(0.1)

        # Pagination handling
        next_elem = soup.select_one(rules.get("pagination_selector", "a.next, a[rel='next']"))
        if next_elem and next_elem.get("href"):
            next_href = urljoin(page_url, next_elem.get("href"))
            if next_href == page_url:
                print("  Pagination next points to same page; stopping")
                break
            page_url = next_href
            print("  Following pagination to:", page_url)
            time.sleep(REQUEST_DELAY)
        else:
            print("  No pagination link found; finished site-level scraping.")
            break

    print("=== Finished site:", site_url)

# ----------------------------
# Entry point
# ----------------------------
def main():
    # ensure default user exists
    User.objects.get_or_create(username=USER_FOR_UNKNOWN_COMMENTS)
    for site, rules in scraping_rules.items():
        try:
            scrape_site(site, rules)
        except Exception as e:
            print(f"Error scraping {site}: {e}")

if __name__ == "__main__":
    main()
