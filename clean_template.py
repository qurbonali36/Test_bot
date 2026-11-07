from PIL import Image
img = Image.open('Telegram Test Achievement Certificate.png').convert('RGB')
patch_name = img.crop((200, 440, 1300, 450)).resize((1100, 95)); img.paste(patch_name, (200, 460))
patch_course = img.crop((200, 660, 1300, 670)).resize((1100, 80)); img.paste(patch_course, (200, 675))
patch_date = img.crop((440, 1050, 680, 1055)).resize((240, 50)); img.paste(patch_date, (440, 1065))
patch_id = img.crop((1120, 1050, 1370, 1055)).resize((250, 50)); img.paste(patch_id, (1120, 1065))
patch_score = img.crop((1400, 720, 1530, 725)).resize((130, 75)); img.paste(patch_score, (1400, 745))
patch_qr = img.crop((1400, 1040, 1550, 1045)).resize((150, 40)); img.paste(patch_qr, (1400, 1055))
img.save('template_clean.png')
