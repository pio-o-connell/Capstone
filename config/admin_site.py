# config/admin_site.py

from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from users.models import BloggerRequest, CustomUser
from blog.models import Comment
from bookings.models import Booking
from django.utils.timezone import now, timedelta


class CustomAdminSite(AdminSite):
    site_header = "Capstone Admin Dashboard"
    site_title = "Capstone Admin"
    index_title = "SuperUser Control Panel"

    def each_context(self, request):
        context = super().each_context(request)

        # --- Dashboard cards ---
        pending_bloggers = BloggerRequest.objects.filter(approved=False).count()
        unapproved_comments = Comment.objects.filter(approved=False).count()
        total_users = CustomUser.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()

        blogger_request_url = (
            f"{reverse('admin:users_bloggerrequest_changelist')}?approved__exact=0"
        )
        comment_review_url = (
            f"{reverse('admin:blog_comment_changelist')}?approved__exact=0"
        )
        pending_booking_url = (
            f"{reverse('admin:bookings_booking_changelist')}?status__exact=pending"
        )

        card_configs = [
            {
                'title': '👥 Number of Users',
                'value': total_users,
                'url': reverse('admin:users_customuser_changelist'),
                'link_label': 'View Users',
                'bg': '#6f42c1',
                'text': 'white',
                'link_color': 'white',
            },
            {
                'title': '📝 Pending Blogger Requests',
                'value': pending_bloggers,
                'url': blogger_request_url,
                'link_label': 'View Details',
                'bg': '#007bff',
                'text': 'white',
                'link_color': 'white',
            },
            {
                'title': '💬 Unapproved Comments',
                'value': unapproved_comments,
                'url': comment_review_url,
                'link_label': 'View Details',
                'bg': '#ffc107',
                'text': 'black',
                'link_color': 'black',
            },
            {
                'title': '📅 Pending Bookings',
                'value': pending_bookings,
                'url': pending_booking_url,
                'link_label': 'View Details',
                'bg': '#28a745',
                'text': 'white',
                'link_color': 'white',
            },
            {
                'title': '📝 All Posts with Comments',
                'value': None,
                'url': reverse('blog_with_comments'),
                'link_label': 'View Posts & Comments',
                'bg': '#17a2b8',
                'text': 'white',
                'link_color': 'white',
                'show_value': False,
            },
        ]

        def _card_html(card):
            base_style = (
                "padding:20px; background:{bg}; color:{text}; border-radius:10px; "
                "flex:1; box-shadow:0 4px 6px rgba(0,0,0,0.1); "
                "transition: transform 0.2s;"
            ).format(bg=card['bg'], text=card['text'])

            value_block = ''
            if card.get('show_value', True):
                value_block = format_html(
                    '<p style="font-size:28px; font-weight:bold;">{}</p>',
                    card['value'],
                )

            return format_html(
                (
                    '<div style="{style}">'
                    '<h3>{title}</h3>'
                    '{value_block}'
                    '<a href="{url}" '
                    'style="color:{link_color}; text-decoration:underline;">'
                    '{link_label}</a>'
                    '</div>'
                ),
                style=base_style,
                title=card['title'],
                value_block=value_block,
                url=card['url'],
                link_color=card['link_color'],
                link_label=card['link_label'],
            )

        cards_markup = format_html_join(
            '',
            '{}',
            ((_card_html(card),) for card in card_configs),
        )

        context['dashboard_cards'] = format_html(
            '<div style="{style}">{cards}</div>',
            style='display:flex; gap:20px; flex-wrap:wrap; margin-bottom:20px;',
            cards=cards_markup,
        )

        # --- Recent items panels ---
        recent_bloggers = BloggerRequest.objects.order_by('-created_at')[:5]
        recent_comments = Comment.objects.order_by('-created_at')[:5]
        recent_bookings = Booking.objects.order_by('-created_at')[:5]

        def status_label(approved):
            color = 'green' if approved else 'red'
            label = 'Approved' if approved else 'Pending'
            return format_html(
                '<span style="color:{0}; font-weight:bold;">{1}</span>',
                color,
                label,
            )

        def booking_status_label(status):
            booking_colors = {
                'pending': 'orange',
                'approved': 'green',
                'rejected': 'red',
                'cancelled': 'gray',
            }
            color = booking_colors.get(status, 'black')
            return format_html(
                '<span style="color:{0}; font-weight:bold;">{1}</span>',
                color,
                status.capitalize(),
            )

        def booking_service_label(booking):
            if booking and booking.service and getattr(booking.service, 'name', None):
                return booking.service.name
            return 'Unknown service'

        item_style = 'padding:5px 0;'
        list_style = 'list-style:none; padding-left:0;'
        section_style = (
            'flex:1; background:#f8f9fa; padding:15px; border-radius:10px; '
            'box-shadow:0 2px 4px rgba(0,0,0,0.1);'
        )

        blogger_items = format_html_join(
            '',
            (
                '<li style="{0}">{1} - <a href="{2}">{3}</a> '
                '[{4}]</li>'
            ),
            (
                (
                    item_style,
                    r.user.username if r.user else 'Unknown',
                    reverse('admin:users_bloggerrequest_change', args=[r.id]),
                    r.reason[:40],
                    status_label(r.approved),
                )
                for r in recent_bloggers
            ),
        )

        comment_items = format_html_join(
            '',
            (
                '<li style="{0}">{1} - <a href="{2}">{3}</a> '
                '[{4}]</li>'
            ),
            (
                (
                    item_style,
                    c.author.username if c.author else 'Anonymous',
                    reverse('admin:blog_comment_change', args=[c.id]),
                    c.content[:40],
                    status_label(c.approved),
                )
                for c in recent_comments
            ),
        )

        booking_items = format_html_join(
            '',
            (
                '<li style="{0}">{1} - <a href="{2}">{3}</a> '
                '[{4}]</li>'
            ),
            (
                (
                    item_style,
                    b.user.username if b.user else 'Unknown',
                    reverse('admin:bookings_booking_change', args=[b.id]),
                    booking_service_label(b),
                    booking_status_label(b.status),
                )
                for b in recent_bookings
            ),
        )

        context['recent_items'] = format_html(
            (
                '<div style="display:flex; gap:20px; margin-top:20px; flex-wrap:wrap;">'
                '<div style="{section_style}">'
                '<h4>Recent Blogger Requests</h4>'
                '<ul style="{list_style}">{blogger_items}</ul>'
                '</div>'
                '<div style="{section_style}">'
                '<h4>Recent Comments</h4>'
                '<ul style="{list_style}">{comment_items}</ul>'
                '</div>'
                '<div style="{section_style}">'
                '<h4>Recent Bookings</h4>'
                '<ul style="{list_style}">{booking_items}</ul>'
                '</div>'
                '</div>'
            ),
            section_style=section_style,
            list_style=list_style,
            blogger_items=blogger_items,
            comment_items=comment_items,
            booking_items=booking_items,
        )

        # --- Charts data ---
        today = now().date()
        dates = [today - timedelta(days=delta) for delta in range(6, -1, -1)]
        labels = [day.strftime('%b %d') for day in dates]

        context['charts_data'] = {
            'labels': labels,
            'bookings': [
                Booking.objects.filter(created_at__date=day).count()
                for day in dates
            ],
            'blogger_requests': [
                BloggerRequest.objects.filter(created_at__date=day).count()
                for day in dates
            ],
            'comments': [
                Comment.objects.filter(created_at__date=day).count()
                for day in dates
            ],
        }

        return context
