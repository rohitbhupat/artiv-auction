import logging

import boto3

from django.conf import settings


logger = logging.getLogger(__name__)


ses_client = boto3.client(
    "sesv2",
    region_name=settings.AWS_SES_REGION,
)


def send_email(
    recipient,
    subject,
    text_body,
    html_body=None,
):
    """
    Send a transactional email through Amazon SES.
    """

    if not recipient:
        logger.warning(
            "Email not sent because recipient is empty."
        )
        return None

    body = {
        "Text": {
            "Data": text_body,
            "Charset": "UTF-8",
        }
    }

    if html_body:
        body["Html"] = {
            "Data": html_body,
            "Charset": "UTF-8",
        }

    response = ses_client.send_email(
        FromEmailAddress=settings.AWS_SES_FROM_EMAIL,

        Destination={
            "ToAddresses": [recipient],
        },

        Content={
            "Simple": {
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8",
                },

                "Body": body,
            }
        },
    )

    logger.info(
        f"SES email accepted for {recipient}. "
        f"Message ID: {response.get('MessageId')}"
    )

    return response


def send_outbid_email(
    user,
    artwork,
    new_bid_amount,
):
    """
    Notify the previous highest bidder that
    someone has placed a higher bid.
    """

    if not user.email:
        return None

    name = (
        user.get_full_name()
        or user.username
        or "there"
    )

    subject = (
        f"You've been outbid on "
        f"'{artwork.product_name}'"
    )

    text_body = f"""
    Hello {name},

    You've been outbid on "{artwork.product_name}".

    The new highest bid is ₹{new_bid_amount}.

    The auction is still active, so you can return to Artiv
    and place a higher bid if you wish.

    Auction ends:
    {artwork.end_date.strftime('%d %B %Y, %I:%M %p')}

    Regards,
    Artiv Team
    """

    html_body = f"""
    <html>
    <body>
        <h2>You've been outbid!</h2>

        <p>
            Hello {name},
        </p>

        <p>
            You've been outbid on
            <strong>{artwork.product_name}</strong>.
        </p>

        <p>
            New highest bid:
            <strong>₹{new_bid_amount}</strong>
        </p>

        <p>
            The auction is still active, so you can return
            to Artiv and place a higher bid.
        </p>

        <p>
            Auction ends:
            <strong>
                {artwork.end_date.strftime('%d %B %Y, %I:%M %p')}
            </strong>
        </p>

        <p>
            Regards,<br>
            Artiv Team
        </p>
    </body>
    </html>
    """

    return send_email(
        recipient=user.email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )
    
def send_auction_ending_email(
    user,
    artwork,
    current_bid,
):
    """
    Notify a bidder that an auction will end
    within approximately 6 hours.
    """

    if not user.email:
        return None

    name = (
        user.get_full_name()
        or user.username
        or "there"
    )

    subject = (
        f"Only 6 hours left: "
        f"'{artwork.product_name}'"
    )

    text_body = f"""
    Hello {name},
    
    The auction for "{artwork.product_name}"
    will end in approximately 6 hours.
    
    Current highest bid:
    ₹{current_bid}
    
    Auction ends:
    {artwork.end_date.strftime('%d %B %Y, %I:%M %p')}
    
    If you want to continue bidding, visit Artiv before
    the auction ends.
    
    Regards,
    Artiv Team
    """

    html_body = f"""
    <html>
    <body>
        <h2>Auction ending soon</h2>

        <p>Hello {name},</p>

        <p>
            The auction for
            <strong>{artwork.product_name}</strong>
            will end in approximately
            <strong>6 hours</strong>.
        </p>

        <p>
            Current highest bid:
            <strong>₹{current_bid}</strong>
        </p>

        <p>
            Auction ends:
            <strong>
                {artwork.end_date.strftime('%d %B %Y, %I:%M %p')}
            </strong>
        </p>

        <p>
            Don't miss your chance to win this artwork.
        </p>

        <p>
            Regards,<br>
            Artiv Team
        </p>
    </body>
    </html>
    """

    return send_email(
        recipient=user.email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )
    
def send_auction_winner_email(
    user,
    artwork,
    winning_bid,
):
    """
    Notify the highest bidder that they won the auction.
    """

    if not user.email:
        return None

    name = (
        user.get_full_name()
        or user.username
        or "there"
    )

    deadline = artwork.response_deadline.strftime(
        "%d %B %Y, %I:%M %p"
    )

    purchase_url = (
        f"https://www.artiv.co.in"
        f"/confirm_purchase/{artwork.id}/"
        f"?response=yes"
    )

    decline_url = (
        f"https://www.artiv.co.in"
        f"/confirm_purchase/{artwork.id}/"
        f"?response=no"
    )

    subject = (
        f"Congratulations! You won "
        f"'{artwork.product_name}'"
    )

    text_body = f"""
    Congratulations {name}!

    You have won the auction for
    "{artwork.product_name}".

    Winning bid:
    ₹{winning_bid}

    You have 24 hours to complete your purchase.

    Purchase deadline:
    {deadline}

    Confirm your purchase:
    {purchase_url}

    If you do not want to purchase the artwork:
    {decline_url}

    If you do not complete the purchase within 24 hours,
    the artwork will be marked as unsold.

    Regards,
    Artiv Team
    """

    html_body = f"""
    <html>
    <body>

        <h2>Congratulations! 🎉</h2>

        <p>
            Hello {name},
        </p>

        <p>
            You have won the auction for
            <strong>{artwork.product_name}</strong>.
        </p>

        <p>
            Winning bid:
            <strong>₹{winning_bid}</strong>
        </p>

        <p>
            You have
            <strong>24 hours</strong>
            to complete your purchase.
        </p>

        <p>
            Purchase deadline:
            <strong>{deadline}</strong>
        </p>

        <p>
            <a href="{purchase_url}">
                Confirm your purchase
            </a>
        </p>

        <p>
            <a href="{decline_url}">
                I don't want to purchase this artwork
            </a>
        </p>

        <p>
            If you do not complete the purchase within
            24 hours, the artwork will be marked as unsold.
        </p>

        <p>
            Regards,<br>
            Artiv Team
        </p>

    </body>
    </html>
    """

    return send_email(
        recipient=user.email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )
    
