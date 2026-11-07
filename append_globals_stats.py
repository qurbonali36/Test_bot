import os

content = """
# ── Statistics Senior Design ──
def get_user_stats_text(lang_id, first_name, last_name, stats):
    total_tests = len(stats)
    total_score = sum(s.get('point_test', 0) for s in stats)
    avg_accuracy = sum(s.get('precent_corr_ans', 0) for s in stats) / total_tests if total_tests > 0 else 0
    avg_accuracy = round(avg_accuracy, 1)
    
    name = f"{first_name} {last_name or ''}".strip()
    
    if lang_id == 2:
        text = (
            f"<b>📊 Персональный отчет по статистике</b>\\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            f"👤 <b>Имя:</b> {name}\\n"
            f"🏆 <b>Общий балл:</b> {total_score} баллов\\n"
            f"📈 <b>Средняя точность:</b> {avg_accuracy}%\\n"
            f"📝 <b>Всего пройдено тестов:</b> {total_tests}\\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            f"<b>📋 Последние пройденные тесты:</b>\\n\\n"
        )
    elif lang_id == 3:
        text = (
            f"<b>📊 Personal Statistics Report</b>\\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            f"👤 <b>Name:</b> {name}\\n"
            f"🏆 <b>Total Score:</b> {total_score} points\\n"
            f"📈 <b>Avg Accuracy:</b> {avg_accuracy}%\\n"
            f"📝 <b>Total tests taken:</b> {total_tests}\\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            f"<b>📋 Recently taken tests:</b>\\n\\n"
        )
    else:
        text = (
            f"<b>📊 Shaxsiy Statistika Hisoboti</b>\\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            f"👤 <b>Ism:</b> {name}\\n"
            f"🏆 <b>Umumiy to'plangan ball:</b> {total_score} ball\\n"
            f"📈 <b>O'rtacha aniqlik:</b> {avg_accuracy}%\\n"
            f"📝 <b>Jami ishlangan testlar:</b> {total_tests} ta\\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            f"<b>📋 Oxirgi ishlangan testlar:</b>\\n\\n"
        )
        
    medals = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    for i, stat in enumerate(stats[:5]):
        title = stat.get('title')
        if not title:
            title = "Noma'lum" if lang_id == 1 else ('Неизвестно' if lang_id == 2 else 'Unknown')
        point = stat.get('point_test', 0)
        percent = stat.get('precent_corr_ans', 0)
        
        icon = medals[i] if i < len(medals) else f"{i+1}️⃣"
        
        if lang_id == 2:
            text += f"{icon} <b>Тест:</b> <i>{title}</i>\\n├ 🎯 <b>Балл:</b> <i>{point}</i>\\n└ 📈 <b>Точность:</b> <i>{percent}%</i>\\n\\n"
        elif lang_id == 3:
            text += f"{icon} <b>Test:</b> <i>{title}</i>\\n├ 🎯 <b>Score:</b> <i>{point}</i>\\n└ 📈 <b>Accuracy:</b> <i>{percent}%</i>\\n\\n"
        else:
            text += f"{icon} <b>Test:</b> <i>{title}</i>\\n├ 🎯 <b>Ball:</b> <i>{point}</i>\\n└ 📈 <b>Aniqlik:</b> <i>{percent}%</i>\\n\\n"
            
    return text

BTN_SETTINGS_BACK = {1: "⬅️ Sozlamalarga qaytish", 2: "⬅️ Вернуться в настройки", 3: "⬅️ Back to settings"}
"""

with open('globals.py', 'a', encoding='utf-8') as f:
    f.write(content)
print('Done appending to globals.py')
