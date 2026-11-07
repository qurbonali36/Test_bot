from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from methods import send_main_menu
from database import Database
import globals
import random
import time
import html
import urllib.parse
import traceback

db = Database("tg_bot.db")

LOG_FILE = "debug.txt"

def _log(msg):
    """Debug log yozish."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    except:
        pass


def send_polls(context, point=1):
    """Test savollarini ketma-ket yuboradi (poll formatida)."""
    _log("send_polls called")

    # ── Ma'lumotlarni olish ──
    try:
        if context.job:
            _log("  via job")
            xalta = context.job.context["xalta"]
            chat_id = context.job.context["chat_id"]
            point = context.job.context.get("point", 1)
        else:
            _log("  via direct (user_data)")
            xalta = context.user_data
            if "chat_id" not in xalta:
                _log(f"  ERROR: chat_id missing! keys={list(xalta.keys())}")
                return
            chat_id = xalta["chat_id"]
    except Exception as e:
        _log(f"  CRITICAL init error: {e}")
        return

    chat_id = int(chat_id)

    # ── Test to'xtatilgan? ──
    if xalta.get("test_toxtatildi"):
        xalta["test_toxtatildi"] = False
        xalta.pop("test_time_limit", None)
        _log("  test was stopped")
        return

    current_quest = xalta.get("current_quest", 0)
    correct_ans = xalta.get("correct_ans", 0)
    question = xalta.get("savollar_bazasi", [])
    amount_quests = xalta.get("amount_quest", 0)
    name = xalta.get("name_link", "Foydalanuvchi")

    _log(f"  current={current_quest}, total={amount_quests}, correct={correct_ans}")

    # ── Asosiy ma'lumotlar ──
    test_id = xalta.get("test_id", "Nomalum")
    db_user = db.get_user_by_chat_id(chat_id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1

    meta = db.get_test_meta(test_id)
    if meta and meta.get("point_per_q"):
        try:
            point = int(meta["point_per_q"])
        except (ValueError, TypeError):
            point = 1

    # ════════════════════════════════════════════════
    #  TEST TUGADI — NATIJA CHIQARISH
    # ════════════════════════════════════════════════
    if current_quest == amount_quests and amount_quests > 0:
        _log("  === TEST COMPLETED ===")
        _send_result(context, xalta, chat_id, lang_id, test_id, meta, 
                     current_quest, correct_ans, amount_quests, name, point)
        return

    # ════════════════════════════════════════════════
    #  KEYINGI SAVOLNI YUBORISH
    # ════════════════════════════════════════════════
    if current_quest >= len(question):
        _log(f"  ERROR: current_quest={current_quest} >= len(question)={len(question)}")
        return

    answers = []
    for options in question[current_quest]["variantlar"].values():
        answers.append(options)

    answer = question[current_quest]['javob']
    cor_answ_sent = question[current_quest]['variantlar'][answer]
    random.shuffle(answers)
    correct_ans_ind = answers.index(cor_answ_sent)
    xalta["correct_ans_ind"] = correct_ans_ind

    question_poll = f"[{current_quest + 1}/{amount_quests}]  {question[current_quest]['savol']}⁉"

    time_limit = xalta.get("test_time_limit")
    if not time_limit:
        time_limit = meta.get("time_per_q", 10) if meta else 10
    time_limit = max(5, min(600, int(time_limit)))

    try:
        msg = context.bot.send_poll(
            chat_id=chat_id, type='quiz',
            question=question_poll, options=answers,
            correct_option_id=correct_ans_ind,
            open_period=time_limit, is_anonymous=False
        )
    except Exception as e:
        _log(f"  ERROR sending poll: {e}")
        return

    xalta["question_start_time"] = time.time()
    if current_quest == 0:
        xalta["test_start_time"] = time.time()

    if msg and msg.poll:
        xalta["poll_id"] = msg.poll.id
        context.bot_data[msg.poll.id] = {
            "chat_id": chat_id,
            "correct_ans_ind": correct_ans_ind,
            "test_id": test_id,
            "options": answers,
            "question": question[current_quest]['savol'],
            "time_limit": time_limit,
            "explanation": question[current_quest].get('explanation')
        }

    xalta["current_quest"] = current_quest + 1
    job = context.job_queue.run_once(
        send_polls, time_limit + 0.5,
        context={"xalta": xalta, "chat_id": chat_id, "point": point}
    )
    xalta["poll_job"] = job


def _send_result(context, xalta, chat_id, lang_id, test_id, meta,
                 current_quest, correct_ans, amount_quests, name, point):
    """Test natijasini xavfsiz yuborish — har qanday xatolikda ham foydalanuvchiga xabar boradi."""
    _log("  _send_result started")

    # ── Guruh rejimi ──
    if chat_id < 0:
        _log("  Group mode")
        try:
            turnir_key = f"turnir_{chat_id}_{test_id}"
            jadval = context.bot_data.get(turnir_key, {})

            test_title = html.escape(str(meta.get("title", test_id) if meta else test_id))

            if not jadval:
                text = (
                    "📊 <b>TEST YAKUNLANDI!</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📌 <b>Test:</b> <i>{test_title}</i>\n"
                    f"📊 <b>Savollar:</b> <i>{amount_quests} ta</i>\n\n"
                    "<i>Afsuski, guruhdan hech kim javob bermadi.</i>"
                )
                inline_btn = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="🔄 Qaytadan boshlash", callback_data=f"groupstart_{meta.get('chat_id', '')}_{test_id}" if meta else "home")]
                ])
            else:
                sorted_users = sorted(jadval.values(), key=lambda x: x["correct"], reverse=True)[:10]
                medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

                # G'olibning natijalari
                top_user = sorted_users[0]
                top_percent = round((top_user['correct'] / amount_quests) * 100, 1) if amount_quests > 0 else 0
                filled = int(top_percent / 10)
                bar = "🟩" * filled + "⬜" * (10 - filled)

                text = (
                    "🏆 <b>GURUH TEST NATIJALARI</b> 🏆\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📌 <b>Test:</b> <i>{test_title}</i>\n"
                    f"📊 <b>Savollar soni:</b> <i>{amount_quests} ta</i>\n"
                    f"💎 <b>Ball:</b> <i>har savol {point} ball</i>\n"
                    f"👥 <b>Ishtirokchilar:</b> <i>{len(sorted_users)} ta</i>\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "       📋 <b>NATIJALAR JADVALI</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                )
                for i, u_data in enumerate(sorted_users):
                    medal = medals[i] if i < len(medals) else "🏅"
                    u_correct = u_data['correct']
                    u_wrong = amount_quests - u_correct
                    u_percent = round((u_correct / amount_quests) * 100, 1) if amount_quests > 0 else 0
                    u_score = u_correct * point

                    text += (
                        f"{medal} <b>{u_data['name']}</b>\n"
                        f"    ├ ✅ <i>{u_correct} to'g'ri</i> │ ❌ <i>{u_wrong} xato</i>\n"
                        f"    ├ 🏅 <i>{u_score} ball</i> │ 📈 <i>{u_percent}%</i>\n"
                        f"    └ {'🟩' * int(u_percent / 20)}{'⬜' * (5 - int(u_percent / 20))}\n\n"
                    )

                text += (
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"  🎊 <b>G'olib:</b> <i>{top_user['name']}</i> — <b>{top_percent}%</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "<blockquote>💡 Testni qayta ishlash uchun quyidagi tugmani bosing!</blockquote>"
                )

                # Guruh uchun inline tugmalar
                try:
                    bot_username = context.bot.username
                    creator_id = meta.get("chat_id", "") if meta else ""
                    share_link = f"https://t.me/{bot_username}?start={creator_id}_{test_id}"
                    share_text_encoded = urllib.parse.quote("🎯 Guruhda test ishladik! Sen ham sinab ko'r!")
                    share_url = f"https://t.me/share/url?url={share_link}&text={share_text_encoded}"
                except Exception:
                    share_url = None

                buttons = [
                    [InlineKeyboardButton(text="🔄 Qaytadan boshlash", callback_data=f"groupstart_{meta.get('chat_id', '')}_{test_id}" if meta else "home")]
                ]
                if share_url:
                    buttons.append([InlineKeyboardButton(text="📤 Do'stlarga ulashish", url=share_url)])
                inline_btn = InlineKeyboardMarkup(buttons)

            context.bot.send_message(text=text, chat_id=chat_id, parse_mode="HTML", reply_markup=inline_btn)
            if turnir_key in context.bot_data:
                del context.bot_data[turnir_key]
        except Exception as e:
            _log(f"  Group result error: {e}")
        return

    # ════════════════════════════════
    #  SHAXSIY CHAT — NATIJA
    # ════════════════════════════════
    _log("  Private chat mode")

    wrong_ans = amount_quests - correct_ans
    precent = (correct_ans / amount_quests) * 100 if amount_quests > 0 else 0
    precent_corr_ans = round(precent, 1)
    speed_bonus = xalta.get("speed_bonus", 0)
    user_point = correct_ans * point + speed_bonus

    _log(f"  correct={correct_ans}, wrong={wrong_ans}, point={point}, user_point={user_point}")

    # ── DB ga saqlash ──
    try:
        if not db.check_first_attempt(chat_id, test_id):
            db.insert_stats_users(chat_id, user_point, precent_corr_ans, test_id)
            _log("  Stats saved to DB")
    except Exception as e:
        _log(f"  DB save error: {e}")

    # ── Gamification ──
    try:
        from gamification import process_test_completion
        process_test_completion(chat_id, correct_ans, amount_quests, test_id, context)
        _log("  Gamification done")
    except Exception as e:
        _log(f"  Gamification error: {e}")

    # ── Kundalik streak ──
    if xalta.get('is_daily'):
        try:
            from daily_challenge import process_daily_completion
            process_daily_completion(chat_id, context)
        except Exception as e:
            _log(f"  Daily streak error: {e}")
        xalta['is_daily'] = False

    # ── Duel ──
    if 'active_duel_id' in xalta:
        _log("  Duel active")
        _handle_duel_completion(context, xalta, chat_id, lang_id, test_id, meta,
                                correct_ans, amount_quests, user_point, precent_corr_ans, point)
        return

    # ── Vaqtni hisoblash ──
    test_end_time = time.time()
    test_start = xalta.get("test_start_time", test_end_time)
    time_taken_sec = round(test_end_time - test_start, 1)
    _log(f"  Time taken: {time_taken_sec}s")

    # ── Test nomi ──
    test_title = html.escape(str(meta.get("title", test_id) if meta else test_id))

    # ── Yaratuvchi ──
    creator_name = "Noma'lum"
    if meta:
        try:
            creator_db = db.get_user_by_chat_id(meta.get("chat_id"))
            if creator_db:
                fname = html.escape(str(creator_db.get("first_name", "")))
                lname = html.escape(str(creator_db.get("last_name", "")))
                creator_name = f'<a href="tg://user?id={meta.get("chat_id")}">{fname} {lname}</a>'
        except Exception as e:
            _log(f"  Creator name error: {e}")

    # ── Missions Update ──
    try:
        from missions import trigger_mission
        trigger_mission(chat_id, "play_test", 1)
        if correct_ans > 0:
            trigger_mission(chat_id, "correct_answers", correct_ans)
    except Exception as e:
        _log(f"  Missions error: {e}")

    # ── Tournament Update ──
    if "active_tournament_id" in xalta:
        try:
            t_id = xalta["active_tournament_id"]
            db.update_tournament_score(t_id, chat_id, user_point, time_taken_sec)
        except Exception as e:
            _log(f"  Tournament update error: {e}")

    # ── Reyting ──
    try:
        users_count = db.count_test_users(test_id)
        user_place = db.get_place_user(test_id, user_point)
    except Exception as e:
        _log(f"  Rating error: {e}")
        users_count = 1
        user_place = 1

    _log("  Building result text")

    # ── NATIJA MATNINI TAYYORLASH ──
    try:
        text = globals.get_premium_result_text(
            lang_id, name, test_id, correct_ans, wrong_ans,
            point, user_point, precent_corr_ans,
            users_count, user_place,
            speed_bonus, time_taken_sec, amount_quests, creator_name, test_title
        )
    except Exception as e:
        _log(f"  get_premium_result_text error: {e}")
        # Fallback oddiy natija matni
        text = (
            f"📊 <b>Test yakunlandi!</b>\n\n"
            f"✅ To'g'ri: {correct_ans} / {amount_quests}\n"
            f"❌ Noto'g'ri: {wrong_ans} / {amount_quests}\n"
            f"🏅 Ball: {user_point}\n"
            f"⏱ Vaqt: {time_taken_sec} sek\n"
            f"⚡ Tezlik bonusi: +{speed_bonus}\n"
            f"📍 O'rin: {user_place} / {users_count}\n"
        )

    # ── INLINE TUGMALAR (Senior Level) ──
    try:
        creator_id = meta.get("chat_id", "unknown") if meta else "unknown"
        bot_username = context.bot.username
        guruh_linki = f"https://t.me/{bot_username}?startgroup={creator_id}_{test_id}"
        share_link = f"https://t.me/{bot_username}?start={creator_id}_{test_id}"
        share_text_encoded = urllib.parse.quote(globals.get_share_result_text(lang_id))
        share_url = f"https://t.me/share/url?url={share_link}&text={share_text_encoded}"

        buttons = [
            [InlineKeyboardButton(text=globals.BTN_WORK_AGAIN[lang_id], callback_data=f"WORK_AGAIN_{test_id}")],
            [
                InlineKeyboardButton(text=globals.BTN_SHARE_RESULT[lang_id], url=share_url),
                InlineKeyboardButton(text=globals.BTN_WORK_GROUP[lang_id], url=guruh_linki)
            ],
        ]
        # Xatolar bo'lsa — "Xatolarimni ko'rish" tugmasi
        if wrong_ans > 0:
            buttons.append([InlineKeyboardButton(text=globals.BTN_VIEW_MISTAKES[lang_id], callback_data="wrong_ans")])
        buttons.append([
            InlineKeyboardButton(text=globals.BTN_LEADERBOARD_RESULT[lang_id], callback_data="lb_menu"),
            InlineKeyboardButton(text=globals.BTN_BOOKMARK_TEST[lang_id], callback_data=f"bm_toggle_{test_id}")
        ])
        buttons.append([InlineKeyboardButton(text=globals.BTN_HOME[lang_id], callback_data="home")])

        inline_button = InlineKeyboardMarkup(buttons)
    except Exception as e:
        _log(f"  Inline button error: {e}")
        inline_button = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=globals.BTN_WORK_AGAIN.get(lang_id, "🔄"), callback_data=f"WORK_AGAIN_{test_id}")],
            [InlineKeyboardButton(text="🏠 Bosh sahifa", callback_data="home")]
        ])

    # ════════════════════════════════
    #  NATIJANI YUBORISH
    # ════════════════════════════════
    _log("  Sending result message...")
    sent = False

    # 1-urinish: HTML bilan
    try:
        context.bot.send_message(
            text=text, chat_id=chat_id,
            parse_mode="HTML", reply_markup=inline_button
        )
        sent = True
        _log("  ✅ Result sent with HTML!")
    except Exception as e:
        _log(f"  HTML send error: {e}")

    # 2-urinish: HTML'siz
    if not sent:
        try:
            import re
            clean = re.sub(r'<[^>]+>', '', text)
            context.bot.send_message(
                text=clean, chat_id=chat_id,
                reply_markup=inline_button
            )
            sent = True
            _log("  ✅ Result sent without HTML!")
        except Exception as e:
            _log(f"  Plain send error: {e}")

    # 3-urinish: minimal matn
    if not sent:
        try:
            minimal = (
                f"📊 Test yakunlandi!\n"
                f"✅ {correct_ans}/{amount_quests} to'g'ri\n"
                f"🏅 {user_point} ball"
            )
            context.bot.send_message(text=minimal, chat_id=chat_id, reply_markup=inline_button)
            sent = True
            _log("  ✅ Minimal result sent!")
        except Exception as e:
            _log(f"  CRITICAL: Even minimal send failed: {e}")

    # ── Sertifikat ──
    try:
        from certificate import send_certificate
        send_certificate(context, chat_id, test_id, correct_ans, amount_quests, user_point, precent_corr_ans, lang_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        _log(f"  Certificate error: {e}")

    # ── Tozalash ──
    xalta.pop("speed_bonus", None)
    xalta.pop("test_time_limit", None)
    xalta.pop("test_start_time", None)
    _log("  _send_result completed")


def _handle_duel_completion(context, xalta, chat_id, lang_id, test_id, meta,
                             correct_ans, amount_quests, user_point, precent_corr_ans, point):
    """Duel natijasini yuborish — Senior Level UI."""
    try:
        duel_id = xalta['active_duel_id']
        db.update_duel_score(duel_id, chat_id, correct_ans, amount_quests)
        duel = db.get_duel(duel_id)

        if duel and duel['challenger_total'] > 0 and duel['opponent_total'] > 0 and duel['status'] != 'completed':
            db.complete_duel(duel_id)
            ch_score = duel['challenger_score']
            op_score = duel['opponent_score']

            u1 = db.get_user_by_chat_id(duel['challenger_id'])
            ch_name = f"{u1.get('first_name', '')} {u1.get('last_name', '')}".strip() if u1 else "Challenger"
            ch_lang = u1.get('lang_id', 1) if u1 else 1

            u2 = db.get_user_by_chat_id(duel['opponent_id'])
            op_name = f"{u2.get('first_name', '')} {u2.get('last_name', '')}".strip() if u2 else "Opponent"
            op_lang = u2.get('lang_id', 1) if u2 else 1

            ch_percent = round((ch_score / duel['challenger_total']) * 100, 1) if duel['challenger_total'] > 0 else 0
            op_percent = round((op_score / duel['opponent_total']) * 100, 1) if duel['opponent_total'] > 0 else 0
            test_title = html.escape(str(meta.get('title', test_id) if meta else test_id))

            ch_bar = "🟩" * int(ch_percent / 20) + "⬜" * (5 - int(ch_percent / 20))
            op_bar = "🟩" * int(op_percent / 20) + "⬜" * (5 - int(op_percent / 20))

            ch_points = ch_score * point
            op_points = op_score * point

            def get_winner_str(lang):
                if ch_score > op_score: return ch_name
                elif op_score > ch_score: return op_name
                else: return globals.TEXT_DUEL_DRAW.get(lang, globals.TEXT_DUEL_DRAW[1])

            def build_duel_result(lang):
                if lang == 1:
                    return (
                        "⚔️ <b>DUEL YAKUNLANDI!</b> ⚔️\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📌 <b>Test:</b> <i>{test_title}</i>\n"
                        f"📊 <b>Savollar:</b> <i>{duel['challenger_total']} ta</i>\n\n"
                        f"🏆 <b>G'OLIB:</b> <i>{get_winner_str(1)}</i>\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"👤 <b>{ch_name}</b>\n"
                        f"  ├ ✅ To'g'ri: <i>{ch_score}</i>\n"
                        f"  ├ 🏅 Ball: <i>{ch_points}</i>\n"
                        f"  ├ 📈 Aniqlik: <i>{ch_percent}%</i>\n"
                        f"  └ {ch_bar}\n\n"
                        "🆚 <b>VS</b>\n\n"
                        f"👤 <b>{op_name}</b>\n"
                        f"  ├ ✅ To'g'ri: <i>{op_score}</i>\n"
                        f"  ├ 🏅 Ball: <i>{op_points}</i>\n"
                        f"  ├ 📈 Aniqlik: <i>{op_percent}%</i>\n"
                        f"  └ {op_bar}\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "<blockquote>⚔️ Yangi duelga tayyormisiz? Qayta bellashing!</blockquote>"
                    )
                elif lang == 2:
                    return (
                        "⚔️ <b>ДУЭЛЬ ЗАВЕРШЕНА!</b> ⚔️\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📌 <b>Тест:</b> <i>{test_title}</i>\n"
                        f"📊 <b>Вопросов:</b> <i>{duel['challenger_total']}</i>\n\n"
                        f"🏆 <b>ПОБЕДИТЕЛЬ:</b> <i>{get_winner_str(2)}</i>\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"👤 <b>{ch_name}</b>\n"
                        f"  ├ ✅ Правильно: <i>{ch_score}</i>\n"
                        f"  ├ 🏅 Баллы: <i>{ch_points}</i>\n"
                        f"  ├ 📈 Точность: <i>{ch_percent}%</i>\n"
                        f"  └ {ch_bar}\n\n"
                        "🆚 <b>VS</b>\n\n"
                        f"👤 <b>{op_name}</b>\n"
                        f"  ├ ✅ Правильно: <i>{op_score}</i>\n"
                        f"  ├ 🏅 Баллы: <i>{op_points}</i>\n"
                        f"  ├ 📈 Точность: <i>{op_percent}%</i>\n"
                        f"  └ {op_bar}\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "<blockquote>⚔️ Готовы к реваншу? Сразитесь снова!</blockquote>"
                    )
                else:
                    return (
                        "⚔️ <b>DUEL COMPLETED!</b> ⚔️\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📌 <b>Test:</b> <i>{test_title}</i>\n"
                        f"📊 <b>Questions:</b> <i>{duel['challenger_total']}</i>\n\n"
                        f"🏆 <b>WINNER:</b> <i>{get_winner_str(3)}</i>\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"👤 <b>{ch_name}</b>\n"
                        f"  ├ ✅ Correct: <i>{ch_score}</i>\n"
                        f"  ├ 🏅 Score: <i>{ch_points}</i>\n"
                        f"  ├ 📈 Accuracy: <i>{ch_percent}%</i>\n"
                        f"  └ {ch_bar}\n\n"
                        "🆚 <b>VS</b>\n\n"
                        f"👤 <b>{op_name}</b>\n"
                        f"  ├ ✅ Correct: <i>{op_score}</i>\n"
                        f"  ├ 🏅 Score: <i>{op_points}</i>\n"
                        f"  ├ 📈 Accuracy: <i>{op_percent}%</i>\n"
                        f"  └ {op_bar}\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "<blockquote>⚔️ Ready for a rematch? Challenge again!</blockquote>"
                    )

            try:
                # Challenger uchun inline tugmalar
                kb_ch = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="⚔️ Qayta bellashish" if ch_lang == 1 else ("⚔️ Реванш" if ch_lang == 2 else "⚔️ Rematch"), callback_data=f"duel_test_{test_id}")],
                    [InlineKeyboardButton(text=globals.BTN_HOME.get(ch_lang, globals.BTN_HOME[1]), callback_data="home")]
                ])
                context.bot.send_message(chat_id=duel['challenger_id'], text=build_duel_result(ch_lang), parse_mode='HTML', reply_markup=kb_ch)

                # Opponent uchun inline tugmalar
                kb_op = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="⚔️ Qayta bellashish" if op_lang == 1 else ("⚔️ Реванш" if op_lang == 2 else "⚔️ Rematch"), callback_data=f"duel_test_{test_id}")],
                    [InlineKeyboardButton(text=globals.BTN_HOME.get(op_lang, globals.BTN_HOME[1]), callback_data="home")]
                ])
                context.bot.send_message(chat_id=duel['opponent_id'], text=build_duel_result(op_lang), parse_mode='HTML', reply_markup=kb_op)
                
                # ── Missions Update ──
                try:
                    from missions import trigger_mission
                    trigger_mission(duel['challenger_id'], "play_duel", 1)
                    trigger_mission(duel['opponent_id'], "play_duel", 1)
                except Exception as e:
                    _log(f"  Duel missions error: {e}")
                    
            except Exception as e:
                _log(f"  Duel result send error: {e}")
        else:
            # Hali raqib tugatmagan
            waiting_text = globals.TEXT_DUEL_WAITING.get(lang_id, globals.TEXT_DUEL_WAITING[1]).format(correct=correct_ans)
            inline_button = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=globals.BTN_HOME.get(lang_id, globals.BTN_HOME[1]), callback_data="home")]
            ])
            context.bot.send_message(chat_id=chat_id, text=waiting_text, parse_mode='HTML', reply_markup=inline_button)
    except Exception as e:
        _log(f"  Duel error: {e}")

    xalta.pop('active_duel_id', None)
    xalta.pop('active_tournament_id', None)
    xalta.pop("speed_bonus", None)
    xalta.pop("test_time_limit", None)

    try:
        from certificate import send_certificate
        send_certificate(context, chat_id, test_id, correct_ans, amount_quests, user_point, precent_corr_ans, lang_id)
    except Exception:
        pass


def cancel_test(update, context):
    """Test jarayonini to'xtatadi."""
    db_user = db.get_user_by_chat_id(update.effective_user.id)
    lang_id = db_user["lang_id"] if db_user and db_user.get("lang_id") else 1
    context.user_data["test_toxtatildi"] = True
    update.message.reply_text(globals.TEST_CANCELLED[lang_id], parse_mode="HTML")
    send_main_menu(context, update.effective_user.id, lang_id)


def get_poll_answers(update, context):
    """So'rovnoma javoblarini qayta ishlaydi."""
    answer = update.poll_answer
    poll_id = answer.poll_id
    if not answer.option_ids:
        return
    sel_opt = answer.option_ids[0]

    poll_data = context.bot_data.get(poll_id)
    if not poll_data:
        xalta = context.user_data
        if xalta.get("correct_ans_ind") is not None and sel_opt == xalta["correct_ans_ind"]:
            xalta["correct_ans"] = xalta.get("correct_ans", 0) + 1
        return

    chat_id = poll_data["chat_id"]
    correct_ans_ind = poll_data["correct_ans_ind"]
    test_id = poll_data["test_id"]
    user = answer.user

    # Guruh turnir jadvalini yangilash
    if chat_id < 0:
        turnir_key = f"turnir_{chat_id}_{test_id}"
        if turnir_key not in context.bot_data:
            context.bot_data[turnir_key] = {}
        if user.id not in context.bot_data[turnir_key]:
            context.bot_data[turnir_key][user.id] = {
                "name": f"{user.first_name} {user.last_name or ''}".strip(),
                "correct": 0
            }
        if sel_opt == correct_ans_ind:
            context.bot_data[turnir_key][user.id]["correct"] += 1

    # Shaxsiy chat hisobini yangilash
    xalta = context.user_data

    if "question_start_time" in xalta and "time_limit" in poll_data:
        time_taken = time.time() - xalta["question_start_time"]
        tl = poll_data["time_limit"]
        if time_taken <= tl / 2:
            xalta["speed_bonus"] = xalta.get("speed_bonus", 0) + 1

    if sel_opt == correct_ans_ind:
        xalta["correct_ans"] = min(xalta.get("correct_ans", 0) + 1, xalta.get("amount_quest", float('inf')))
    else:
        if "options" in poll_data and "question" in poll_data:
            try:
                db.save_wrong_answer(
                    user.id,
                    poll_data["question"],
                    poll_data["options"][correct_ans_ind],
                    poll_data["options"][sel_opt],
                    test_id
                )
            except Exception:
                pass
            # Tushuntirish yuborish
            explanation = poll_data.get("explanation")
            if explanation:
                try:
                    exp_text = f"💡 <b>Tushuntirish:</b>\n<i>{explanation}</i>"
                    context.bot.send_message(chat_id=user.id, text=exp_text, parse_mode='HTML')
                except Exception:
                    pass

    if chat_id > 0:
        if "poll_job" in xalta:
            try:
                xalta["poll_job"].schedule_removal()
                del xalta["poll_job"]
            except Exception:
                pass
        send_polls(context)
