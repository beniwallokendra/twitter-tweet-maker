#!/usr/bin/env python3
"""Conversation for deleting stored stickers."""
from typing import cast, List

from telegram import (
    Update,
    Message,
    PhotoSize,
)
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from bot.userdata import CCT, UserData
from bot.utils import TIMEOUT_HANDLER, FALLBACK_HANDLER

STATE = 42


def start(update: Update, _: CCT) -> int:
    """Starts the conversation and asks for the new picture..

    Args:
        update: The Telegram update.
        _: The callback context as provided by the dispatcher.

    Returns:
        int: The next state.
    """
    message = cast(Message, update.effective_message)
    message.reply_text(
        'Please send me the picture that you want to use as fallback. Make sure to send it as '
        'photo (compressed) instead of as document (uncompressed).\n\nNote that this photo will '
        "only be used if you don't have a profile picture or I can't see it due to your privacy "
        'settings.'
    )
    return STATE


def handle_picture(update: Update, context: CCT) -> int:
    """Handles the sticker input and deletes the sticker if possible.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the dispatcher.

    Returns:
        int: The next state.
    """
    user_data = cast(UserData, context.user_data)
    message = cast(Message, update.effective_message)
    if message.document:
        message.reply_text('Please send me the picture as compressed photo and not as document.')
        return STATE

    photos = cast(List[PhotoSize], message.photo)
    assert len(photos) > 0
    user_data.update_fallback_photo(photos[-1])
    message.reply_text('Fallback picture set.')

    return ConversationHandler.END


set_fallback_picture_conversation = ConversationHandler(
    entry_points=[CommandHandler('set_fallback_picture', start)],
    states={
        STATE: [MessageHandler(Filters.photo, handle_picture)],
        ConversationHandler.TIMEOUT: [TIMEOUT_HANDLER],
    },
    fallbacks=[FALLBACK_HANDLER],
    conversation_timeout=30,
    persistent=False,
    per_user=True,
    per_chat=True,
)
