import sys
import pathlib
import random
import argparse
from datetime import timedelta

# Ensure project root is on PYTHONPATH so `config` is importable
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
from django.utils import timezone

django.setup()

from django.contrib.auth import get_user_model
from blog.models import Post, Comment

User = get_user_model()

# Titles and shorter mapping (use existing mapping where available)
POST_TITLES = [
    "How to Start a Simple Vegetable Garden",
    "The Secret to Perfect Tomato Plants",
    "Beginner’s Guide to Composting at Home",
    "10 Low-Maintenance Plants for Busy Gardeners",
    "How to Improve Soil Quality Naturally",
    "Best Spring Planting Tips for Irish Gardens",
    "Common Gardening Mistakes and How to Fix Them",
    "A Complete Guide to Raised Beds",
    "How to Grow Herbs Indoors All Year",
    "Organic Pest Control That Really Works",
]

# Minimal BLOG_POSTS mapping (use the long content for first two titles; others will be generated)
BLOG_POSTS = {
    "How to Start a Simple Vegetable Garden": """
Starting a vegetable garden is one of the most rewarding activities you can undertake... (truncated for brevity)
""",
    "The Secret to Perfect Tomato Plants": """
Growing perfect tomatoes is the dream of every gardener... (truncated for brevity)
""",
}

COMMENTS = [
    "Great post — I learned a lot from this!",
    "Thanks for sharing these tips, very helpful.",
    "This really cleared up a lot of questions I had.",
    "Brilliant advice, I’m definitely trying this in my garden.",
    "Love this! Your posts are always so informative.",
]


def generate_long_content(title):
    base = BLOG_POSTS.get(title, "")
    tips = [
        "Remember to water plants deeply but infrequently to encourage root growth.",
        "Use mulch to retain soil moisture and prevent weeds.",
        "Rotate crops annually to maintain healthy soil.",
        "Choose native plants to attract beneficial insects.",
        "Composting kitchen waste is a great way to enrich your soil.",
    ]

    parts = []
    if base:
        parts.append(base.strip())

    target = random.randint(300, 500)

    def word_count(text):
        return len(text.split())

    current = sum(word_count(p) for p in parts)

    while current < target:
        parts.append(random.choice(tips))
        current = sum(word_count(p) for p in parts)

    full = "\n\n".join(parts)
    words = full.split()
    if len(words) > 500:
        full = " ".join(words[:500])
    return full


def main(posts_per_blogger=1, min_comments=5, max_comments=5):
    now = timezone.now()

    bloggers = list(User.objects.filter(is_blogger=True))
    if not bloggers:
        print("No bloggers found; aborting.")
        return

    admins = list(User.objects.filter(is_superuser=True))
    registered_non_bloggers = list(User.objects.filter(is_customer=True, is_blogger=False))
    guests = list(User.objects.filter(is_customer=False, is_blogger=False))
    pool_all = list(User.objects.all())

    created_posts = 0
    created_comments = 0

    title_iter = iter(POST_TITLES)
    for b in bloggers:
        for pidx in range(posts_per_blogger):
            try:
                title = next(title_iter)
            except StopIteration:
                base_title = random.choice(POST_TITLES)
                title = f"{base_title} (Part {pidx + 1})"

            author = b
            content = generate_long_content(title)
            excerpt = " ".join(content.split()[:40])

            post = Post.objects.create(
                author=author,
                title=title,
                content=content,
                excerpt=excerpt,
                status='published',
            )

            created_posts += 1

            num_comments = random.randint(min_comments, max_comments)

            authors_pool = []
            if admins:
                authors_pool.append(random.choice(admins))
            if guests:
                authors_pool.append(random.choice(guests))
            if registered_non_bloggers:
                authors_pool.append(random.choice(registered_non_bloggers))
            other_bloggers = [x for x in bloggers if x.pk != author.pk]
            if other_bloggers:
                authors_pool.append(random.choice(other_bloggers))

            remaining_pool = [u for u in pool_all if u.pk not in {a.pk for a in authors_pool}]
            while len(authors_pool) < num_comments and remaining_pool:
                pick = random.choice(remaining_pool)
                authors_pool.append(pick)
                remaining_pool = [u for u in remaining_pool if u.pk != pick.pk]

            while len(authors_pool) < num_comments:
                authors_pool.append(random.choice(pool_all))

            for author_user in authors_pool[:num_comments]:
                comment_text = random.choice(COMMENTS)
                approved = random.choice([True, True, True, False])
                c = Comment.objects.create(
                    post=post,
                    author=author_user,
                    content=comment_text,
                    approved=approved,
                    name=author_user.username if author_user else None,
                    email=getattr(author_user, 'email', None) if author_user else None,
                )
                Comment.objects.filter(pk=c.pk).update(created_at=now)
                created_comments += 1

            print(f"Created post '{title}' by {author.username} with {num_comments} comments")

    print("--- Summary ---")
    print(f"Posts created: {created_posts}")
    print(f"Comments created: {created_comments}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create posts and comments for bloggers')
    parser.add_argument('--posts-per-blogger', type=int, default=1, help='Number of posts to create per blogger')
    parser.add_argument('--min-comments', type=int, default=5, help='Minimum comments per post')
    parser.add_argument('--max-comments', type=int, default=5, help='Maximum comments per post')
    args = parser.parse_args()
    main(args.posts_per_blogger, args.min_comments, args.max_comments)
