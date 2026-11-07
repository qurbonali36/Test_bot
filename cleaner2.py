from PIL import Image
img = Image.open('Telegram Test Achievement Certificate.png').convert('RGB')
patch_name = img.crop((200, 320, 1300, 360)).resize((1100, 130)); img.paste(patch_name, (200, 435))
patch_course = img.crop((200, 580, 1300, 620)).resize((1100, 100)); img.paste(patch_course, (200, 660))
patch_date = img.crop((440, 1030, 680, 1050)).resize((240, 50)); img.paste(patch_date, (440, 1065))
patch_id = img.crop((1120, 1030, 1370, 1050)).resize((250, 50)); img.paste(patch_id, (1120, 1065))
patch_qr = img.crop((1400, 1040, 1550, 1050)).resize((150, 40)); img.paste(patch_qr, (1400, 1055))
img.save('template_clean.png')
