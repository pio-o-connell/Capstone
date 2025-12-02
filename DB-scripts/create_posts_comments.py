import sys
import pathlib
import random
from datetime import timedelta
import argparse

import sys
import pathlib
import random
from datetime import timedelta
import argparse

# Ensure project root is on PYTHONPATH so `config` is importable
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
from django.utils import timezone

django.setup()

from django.contrib.auth import get_user_model
from blog.models import Post, Comment
from users.models import CustomUser

User = get_user_model()

# -----------------------------
# Sample Titles + provided text snippets
# -----------------------------
POST_TITLES = [
    "How to Start a Simple Vegetable Garden",
    "The Secret to Perfect Tomato Plants",
    "Beginner’s Guide to Composting at Home",
    "10 Low-Maintenance Plants for Busy Gardeners",
    # -----------------------------
    # Main: create posts & comments
    # -----------------------------

    def main(posts_per_blogger=1, min_comments=5, max_comments=5):
        now = timezone.now()

        bloggers = list(User.objects.filter(is_blogger=True))
        if not bloggers:
            print("No bloggers found in system; aborting.")
            return

        admins = list(User.objects.filter(is_superuser=True))
        registered_non_bloggers = list(User.objects.filter(is_customer=True, is_blogger=False))
        guests = list(User.objects.filter(is_customer=False, is_blogger=False))

        # If any category empty, try fallback by picking from general pool
        pool_all = list(User.objects.all())

        created_posts = 0
        created_comments = 0

        # If posts_per_blogger==1 and number of titles >= number bloggers, we'll use titles list
        # Otherwise we will generate titles per blogger by combining title + index

        title_iter = iter(POST_TITLES)
        for b in bloggers:
            for pidx in range(posts_per_blogger):
                try:
                    # Prefer to consume provided titles first
                    title = next(title_iter)
                except StopIteration:
                    # Reuse titles but add suffix to keep uniqueness
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

                # Determine number of comments for this post
                num_comments = random.randint(min_comments, max_comments)

                # Build comment authors list: try to pick diverse roles
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

                # Fill remaining authors from pool_all ensuring some diversity
                remaining_pool = [u for u in pool_all if u.pk not in {a.pk for a in authors_pool}]
                while len(authors_pool) < num_comments and remaining_pool:
                    pick = random.choice(remaining_pool)
                    authors_pool.append(pick)
                    remaining_pool = [u for u in remaining_pool if u.pk != pick.pk]

                # If still short, allow duplicates
                while len(authors_pool) < num_comments:
                    authors_pool.append(random.choice(pool_all))

                # Create comments
                for author_user in authors_pool[:num_comments]:
                    comment_text = random.choice(COMMENTS)
                    approved = random.choice([True, True, True, False])  # mostly approved

                    c = Comment.objects.create(
                        post=post,
                        author=author_user,
                        content=comment_text,
                        approved=approved,
                        name=author_user.username if author_user else None,
                        email=getattr(author_user, 'email', None) if author_user else None,
                    )

                    update_fields = {'created_at': now}
                    if hasattr(Comment, 'updated_on'):
                        update_fields['updated_on'] = now
                    if hasattr(Comment, 'updated_at'):
                        update_fields['updated_at'] = now

                    Comment.objects.filter(pk=c.pk).update(**update_fields)
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
        "Prune regularly to encourage healthy growth and flowering.",
        "Monitor for pests early to prevent infestations.",
        "Fertilize naturally using organic matter like compost or manure.",
        "Consider companion planting to naturally deter pests and enhance growth.",
        "Plan your garden layout to ensure proper sunlight for each plant.",
    ]

    # Start with the provided base if any
    parts = []
    if base:
        parts.append(base.strip())

    # target words between 300 and 500
    target = random.randint(300, 500)

    def word_count(text):
        return len(text.split())

    current = sum(word_count(p) for p in parts)

    # Add tips and repeat short sentences until target reached
    while current < target:
        to_add = random.choice(tips)
        parts.append(to_add)
        current = sum(word_count(p) for p in parts)

    # If over 500 words, trim
    full = "\n\n".join(parts)
    words = full.split()
    if len(words) > 500:
        full = " ".join(words[:500])

    return full


# -----------------------------
# Main: create posts & comments
# -----------------------------

def main():
    now = timezone.now()

    bloggers = list(User.objects.filter(is_blogger=True))
    if not bloggers:
        print("No bloggers found in system; aborting.")
        return
    def main(posts_per_blogger=1, min_comments=5, max_comments=5):
    admins = list(User.objects.filter(is_superuser=True))
    registered_non_bloggers = list(User.objects.filter(is_customer=True, is_blogger=False))
    guests = list(User.objects.filter(is_customer=False, is_blogger=False))
    other_users = list(User.objects.exclude(pk__in=[u.pk for u in bloggers + admins + registered_non_bloggers + guests]))

    # If any category empty, try fallback by picking from general pool
    pool_all = list(User.objects.all())

    created_posts = 0
    created_comments = 0

    for i, title in enumerate(POST_TITLES):
        # pick an author (rotate through bloggers)
        author = bloggers[i % len(bloggers)]

        content = generate_long_content(title)
        excerpt = " ".join(content.split()[:40])

        # If posts_per_blogger==1 and number of titles >= number bloggers, we'll use titles list
        # Otherwise we will generate titles per blogger by combining title + index

        title_iter = iter(POST_TITLES)
        for b in bloggers:
            for pidx in range(posts_per_blogger):
                try:
                    # Prefer to consume provided titles first
                    title = next(title_iter)
                except StopIteration:
                    # Reuse titles but add suffix to keep uniqueness
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

                # Determine number of comments for this post
                num_comments = random.randint(min_comments, max_comments)

                # Build comment authors list: try to pick diverse roles
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

                # Fill remaining authors from pool_all ensuring some diversity
                remaining_pool = [u for u in pool_all if u.pk not in {a.pk for a in authors_pool}]
                while len(authors_pool) < num_comments and remaining_pool:
                    pick = random.choice(remaining_pool)
                    authors_pool.append(pick)
                    remaining_pool = [u for u in remaining_pool if u.pk != pick.pk]

                # If still short, allow duplicates
                while len(authors_pool) < num_comments:
                    authors_pool.append(random.choice(pool_all))

                # Create comments
                for author_user in authors_pool[:num_comments]:
                    comment_text = random.choice(COMMENTS)
                    approved = random.choice([True, True, True, False])  # mostly approved

                    c = Comment.objects.create(
                        post=post,
                        author=author_user,
                        content=comment_text,
                        approved=approved,
                        name=author_user.username if author_user else None,
                        email=getattr(author_user, 'email', None) if author_user else None,
                    )

                    update_fields = {'created_at': now}
                    if hasattr(Comment, 'updated_on'):
                        update_fields['updated_on'] = now
                    if hasattr(Comment, 'updated_at'):
                        update_fields['updated_at'] = now

                    Comment.objects.filter(pk=c.pk).update(**update_fields)
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
