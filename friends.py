from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from gamification import add_xp
import globals

db = Database("tg_bot.db")

def show_friends_menu(update, context):
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] or 1
    
    bot_username = context.bot.username
    invite_link = f"https://t.me/{bot_username}?start=ref_{chat_id}"
    
    title = globals.MENU_FRIENDS.get(lang_id, globals.MENU_FRIENDS[1])
    
    text = {
        1: f"👥 <b>Do'stlar bo'limi</b>\n\nSizning taklif havolangiz:\n{invite_link}\n\n<i>Do'stlaringizni taklif qiling va har bir yangi do'st uchun XP oling!</i>",
        2: f"👥 <b>Раздел друзей</b>\n\nВаша реферальная ссылка:\n{invite_link}\n\n<i>Приглашайте друзей и получайте XP за каждого нового друга!</i>",
        3: f"👥 <b>Friends Section</b>\n\nYour invite link:\n{invite_link}\n\n<i>Invite friends and get XP for each new friend!</i>"
    }[lang_id]
    
    btn_list = {
        1: "📝 Do'stlarim ro'yxati",
        2: "📝 Мои друзья",
        3: "📝 My Friends List"
    }[lang_id]
    
    kb = [[InlineKeyboardButton(text=btn_list, callback_data="friends_list")]]
    
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kb)
    )

def handle_friends_callback(update, context):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_user.id
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] or 1
    
    if data == "friends_list":
        friends = db.get_friends(chat_id)
        if not friends:
            msg = {
                1: "Sizda hozircha do'stlar yo'q.",
                2: "У вас пока нет друзей.",
                3: "You have no friends yet."
            }[lang_id]
            
            back_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='home')]
            ])
            query.message.edit_text(msg, reply_markup=back_kb)
            return
            
        text = {
            1: "👥 <b>Do'stlaringiz:</b>\n\n",
            2: "👥 <b>Ваши друзья:</b>\n\n",
            3: "👥 <b>Your Friends:</b>\n\n"
        }[lang_id]
        
        for idx, friend_id in enumerate(friends, 1):
            f_user = db.get_user_by_chat_id(friend_id)
            if f_user:
                name = f"{f_user.get('first_name', '')} {f_user.get('last_name', '')}".strip()
                lvl = f_user.get('level', 1)
                text += f"{idx}. {name} (Lvl {lvl})\n"
                
        back_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(globals.BTN_BACK[lang_id], callback_data='home')]
        ])
        query.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb)

def process_referral(update, context, data):
    chat_id = update.effective_user.id
    inviter_id = data.replace("ref_", "")
    
    if not inviter_id.isdigit():
        return
        
    inviter_id = int(inviter_id)
    if inviter_id == chat_id:
        return # Can't invite self
        
    # Check if already friends
    friends = db.get_friends(chat_id)
    if inviter_id in friends:
        return
        
    db.add_friend(inviter_id, chat_id)
    
    # Give XP
    add_xp(inviter_id, 50)
    add_xp(chat_id, 50)
    
    # Notify inviter
    inviter_user = db.get_user_by_chat_id(inviter_id)
    if inviter_user:
        lang_id = inviter_user["lang_id"] or 1
        msg = {
            1: "🎉 Yangi do'st qo'shildi! +50 XP",
            2: "🎉 Добавлен новый друг! +50 XP",
            3: "🎉 New friend added! +50 XP"
        }[lang_id]
        try:
            context.bot.send_message(chat_id=inviter_id, text=msg)
        except Exception:
            pass
            
    # Notify joined user
    user = db.get_user_by_chat_id(chat_id)
    lang_id = user["lang_id"] or 1
    msg2 = {
        1: "🤝 Siz do'stingizning taklifi bilan kirdingiz! +50 XP",
        2: "🤝 Вы присоединились по приглашению друга! +50 XP",
        3: "🤝 You joined via friend's invite! +50 XP"
    }[lang_id]
    context.bot.send_message(chat_id=chat_id, text=msg2)
