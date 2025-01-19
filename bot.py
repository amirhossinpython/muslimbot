import subprocess
import sys


def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


required_packages = [
    'rubpy',
    'requests',
    'aiohttp',
    'deep_translator',
  
]


for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        install_package(package)


from rubpy import Client, filters
from rubpy.types import Updates
import requests
import random
import urllib.parse
import aiohttp
from deep_translator import GoogleTranslator
bot = Client(name='islamic')
BASE_API_URL = "http://api.alquran.cloud/v1/surah"
API_BASE_URL = "http://api.alquran.cloud/v1/juz"
BASE_API_URL_S = "http://api.alquran.cloud/v1/search"
def get_response_from_api(user_input):
    url = "https://api.api-code.ir/gpt-4/"
    payload = {"text": user_input}

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()  # بررسی وضعیت پاسخ

        data = response.json()
        return data['result']  # فقط نتیجه را برمی‌گرداند

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}"
    except Exception as e:
        return f"An error occurred: {e}"
def get_edition(language):
    """
    تابعی برای انتخاب edition مناسب بر اساس زبان
    """
    if language == "fa":
        return "fa"  # ترجمه فارسی
    else:
        return "en"  # پیش‌فرض: ترجمه انگلیسی

def get_prayer_times(city):
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=IR"
    response = requests.get(url)
    
    if response.status_code == 200:
        timings = response.json()['data']['timings']
        return timings
    else:
        return None

async def get_random_surah_with_audio():
    try:
        # دریافت لیست سوره‌ها
        response = requests.get(BASE_API_URL)
        response.raise_for_status()
        surahs = response.json().get('data', [])
        
        # انتخاب تصادفی یک سوره
        random_surah = random.choice(surahs)
        surah_id = random_surah['number']  # شماره سوره
        
        # دریافت اطلاعات سوره همراه با صوت
        audio_response = requests.get(f"{BASE_API_URL}/{surah_id}/ar.alafasy")
        audio_response.raise_for_status()
        
        audio_data = audio_response.json().get('data', {})
        
        # ساخت متن و لینک صوت کامل سوره
        surah_info = {
            "surah_number": surah_id,
            "surah_name_arabic": random_surah['name'],
            "surah_name_english": random_surah['englishName'],
            "total_ayahs": random_surah['numberOfAyahs'],
            "audio_link": audio_data['ayahs'][0]['audioSecondary'][0],  # لینک صوت کل سوره
            "ayahs_text": [ayah['text'] for ayah in audio_data['ayahs']]  # متن آیات
        }
        return surah_info
    except requests.exceptions.RequestException as e:
        return {"error": "Failed to fetch data from API", "details": str(e)}
async def get_random_page_data():
    try:
        # انتخاب صفحه تصادفی
        random_page = random.randint(1, 604)
        
        # دریافت داده صفحه
        response = requests.get(f"{BASE_API_URL}/{random_page}/quran-uthmani")
        response.raise_for_status()
        page_data = response.json().get('data', {})
        
        # استخراج اطلاعات
        ayahs = page_data['ayahs']
        surah_name = ayahs[0]['surah']['name']  # نام سوره در صفحه
        audio_links = [ayah['audio'] for ayah in ayahs if 'audio' in ayah]  # لینک صوت
        
        # متن صفحه
        page_text = "\n".join([f"{ayah['numberInSurah']}. {ayah['text']}" for ayah in ayahs])
        
        return {
            "page_number": random_page,
            "surah_name": surah_name,
            "page_text": page_text,
            "audio_links": audio_links
        }
    except requests.exceptions.RequestException as e:
        return {"error": "Failed to fetch data from API", "details": str(e)}

def get_random_ayah():
    reference = random.randint(1, 6236)
    editions = ["en.asad", "fa.salehi", "ar.alafasy"]
    editions_str = ",".join(editions)
    
    url = f"http://api.alquran.cloud/v1/ayah/{reference}/editions/{editions_str}"
    response = requests.get(url)
    
    if response.status_code == 200:
        ayah_data = response.json()['data']
        return reference, ayah_data
    else:
        return None, None
def get_translation(text, target_lang="en"):
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        return f"Error during translation: {e}"

@bot.on_message_updates(filters.is_private, filters.Commands(["start"]))
async def start_bot(update: Updates):
    info = """
    🌟 **به ربات مسلمان و قاری قرآن خوش آمدید!** 🌟
    
    این ربات قابلیت‌های متنوعی برای دسترسی به قرآن کریم دارد. لیست دستورات به شرح زیر است:
    
    🟢 **شروع ربات**:
    - `/start` 
    
    📖 **ارسال یک سوره از قرآن**:
    - /سوره
    - /سوره قرآن
    
    🕋 **ارسال یک آیه از قرآن**:
    - /آیه
    - /آیه قرآن
    
    📜 **ارسال صفحه‌ای از قرآن**:
    - /صفحه
    - `/صفحه قرآن`
    
    🟠 **ارسال یک جزء از قرآن**:
    - /جزء
    - /جز
    
    🕌 **نمایش اوقات شرعی**:
    - /sharia [نام شهر]
    - مثال: /sharia مشهد
    🔍 **جستجوی آیات قرآن**:
    - /search [کلمه یا عبارت مورد نظر]
    - مثال: /search رحمت` جستجو برای کلمه "رحمت" در قرآن
    🤖 **چت با هوش مصنوعی**:
    - برای چت با هوش مصنوعی، سوال خود را با علامت+ شروع کنید.
    - مثال: +سلام، چطور می‌توانم موفق باشم؟
   
    

    ✨ **نکته**: برای هر کدام از این دستورات، اطلاعات مرتبط به صورت دقیق و زیبا ارسال خواهد شد.
    
    💖 **التماس دعا!**
    """
    await update.reply(info)


    

@bot.on_message_updates(filters.is_private, filters.Commands(["سوره", "سوره قرآن"]))
async def send_sorhe(update: Updates):
    try:
        await update.reply("درحال پردازش سوره و ارسال آن به کاربر...")
        
        surah_data = await get_random_surah_with_audio()
        
        if "error" not in surah_data:
            # متن کپشن
            caption = (
                f"📖 *سوره:* {surah_data['surah_name_arabic']} ({surah_data['surah_name_english']})\n"
                f"🔢 *شماره سوره:* {surah_data['surah_number']}\n"
                f"📜 *تعداد آیات:* {surah_data['total_ayahs']}\n\n"
                f"متن آیات:\n" + "\n".join(f"{i+1}. {ayah}" for i, ayah in enumerate(surah_data['ayahs_text']))
            )
            
            # تقسیم متن به بخش‌های کوچک‌تر (حداکثر 4000 کاراکتر برای هر پیام)
            max_length = 4000
            parts = [caption[i:i + max_length] for i in range(0, len(caption), max_length)]
            
            # ارسال هر بخش به ترتیب
            for part in parts:
                await update.reply(part)
            
            # ارسال فایل صوتی
            await update.reply_music(surah_data['audio_link'], caption="🎧 فایل صوتی کامل سوره")
        
        else:
            await update.reply("❌ خطا در دریافت اطلاعات. لطفاً دوباره تلاش کنید.")
    
    except Exception as e:
        await update.reply(f"❌ خطایی رخ داد: {str(e)}")


@bot.on_message_updates(filters.is_private,filters.Commands(['آیه قران','ایه قران','آیه']))
async def send_ayah(update: Updates):
    await update.reply('درحال  پردازش ایه از قران کریم')  # تایید دریافت پیام

    reference, ayah_data = get_random_ayah()
    try :
    
        if ayah_data:
            message_text = f"آیه تصادفی شماره {reference}:\n\n"
            
            # ارسال آیه و ترجمه‌ها
            for edition in ayah_data:
                version = edition['edition']['name']
                text = edition['text']
                
                if "fa" in version:
                    message_text += f"\n--- ترجمه فارسی ---\nVersion: {version}\nText: {text}\n"
                    # ترجمه فارسی به انگلیسی
                    translated_text = get_translation(text, target_lang="en")
                    message_text += f"\n--- ترجمه به انگلیسی ---\n{translated_text}\n"
                else:
                    message_text += f"\nVersion: {version}\nText: {text}\n"
            
            
            await update.reply(message_text)

            # ارسال صوت (ویس) همراه با کپشن
            audio_url = ayah_data[-1]['audio']  # گرفتن آدرس صوتی از تلاوت
            await update.reply_music(audio_url, caption=message_text)
            
        else:
            await update.reply("خطا در دریافت آیه.")
    except Exception as eror:
        await update.reply(f"eror:\n{eror}")
        
@bot.on_message_updates(filters.is_private, filters.Commands(['صفحه','صفحه قران']))
async def send_random_page(update: Updates):
    page_data = await get_random_page_data()
    await update.reply("درحال پردازش صفحه از قرآن ..")
    
    if "error" not in page_data:
        # متن کپشن
        caption = (
            f"📖 *صفحه شماره:* {page_data['page_number']}\n"
            f"🕌 *نام سوره:* {page_data['surah_name']}\n\n"
            f"متن آیات:\n{page_data['page_text']}"
        )
        
        # ارسال لینک صوت اول (می‌توانید همه صوت‌ها را ارسال کنید در صورت نیاز)
        if page_data['audio_links']:
            await update.reply_music(page_data['audio_links'][0], caption=caption)
        else:
            await update.reply(caption)
    else:
        await update.reply("❌ خطا در دریافت اطلاعات. لطفاً دوباره تلاش کنید.")     

@bot.on_message_updates(filters.is_private, filters.Commands(['جزء','جزع قرآن','juz','جز']))       
async def send_juz(update: Updates):
    
    try:
        
        
        # انتخاب تصادفی یک جزء از 1 تا 30
        juz_number = random.randint(1, 30)
        edition = "quran-uthmani"  # نسخه پیش‌فرض (می‌توانید تغییر دهید)
        
        # درخواست به API برای جزء تصادفی
        async with aiohttp.ClientSession() as session:
            
            async with session.get(f"{API_BASE_URL}/{juz_number}/{edition}") as response:
                if response.status == 200:
                    data = await response.json()
                    ayahs = data["data"]["ayahs"]  # لیست آیات
                    
                    # انتخاب تصادفی یک آیه از جزء
                    random_ayah = random.choice(ayahs)
                    ayah_text = random_ayah['text']
                    
                    surah_name = random_ayah['surah']['name']
                    ayah_number = random_ayah['numberInSurah']
                    
                    # آماده‌سازی و ارسال پیام
                    message = f"📖 جزء {juz_number} از قرآن کریم:\n\n{ayah_text}\n\n📍سوره: {surah_name} - آیه: {ayah_number}"
                    await update.reply(message)
                    
                else:
                    await update.reply(f"خطا در دریافت اطلاعات. کد وضعیت: {response.status}")
    except Exception as e:
        await update.reply(f"خطایی رخ داد: {e}")
    

@bot.on_message_updates(filters.is_private , filters.Commands(["sharia","شرعی"]))
async def fetch_prayer_times(update: Updates):
    
    """
    دستور /sharia برای دریافت اوقات شرعی شهر
    """
    try:
        city = update.text.split(" ", 1)[1]  # استخراج نام شهر از دستور
        if not city:
            await update.reply("❗ لطفاً نام شهر را وارد کنید. مثال: `/sharia مشهد`")
            return
        await update.reply(f"درحال  پردازش اوقات شرعی شهر:\n{city}")
        
        timings = get_prayer_times(city)
        if timings:
            # تنظیم پیام اوقات شرعی
            result_shia = f"🕌 **اوقات شرعی (شیعه) برای {city}:**\n\n"
            result_shia += f"🌅 صبح: {timings['Fajr']}\n"
            result_shia += f"🏞 ظهر و عصر: {timings['Dhuhr']}\n"
            result_shia += f"🌙 مغرب و عشا: {timings['Maghrib']}\n\n"
            
            result_sunni = f"🕌 **اوقات شرعی (سنی) برای {city}:**\n\n"
            result_sunni += f"🌅 صبح: {timings['Fajr']}\n"
            result_sunni += f"🏞 ظهر: {timings['Dhuhr']}\n"
            result_sunni += f"🌇 عصر: {timings['Asr']}\n"
            result_sunni += f"🌙 مغرب: {timings['Maghrib']}\n"
            result_sunni += f"🌌 عشا: {timings['Isha']}"
            
            # ارسال پیام
            await update.reply(result_shia + "\n" + result_sunni)
        else:
            await update.reply("❌ اطلاعاتی یافت نشد. لطفاً نام شهر را بررسی کنید.")
    except IndexError:
        await update.reply("❗ لطفاً نام شهر را وارد کنید. مثال: /sharia مشهد")
    except Exception as e:
        await update.reply(f"⚠️ خطایی رخ داد:\n{e}")  
@bot.on_message_updates(filters.is_private)
async def handle_search(update: Updates):
    message_text = update.text

    if message_text.startswith('/search '):  
        keyword = message_text[len('/search '):]  # کلمه کلیدی جستجو

        if not keyword:
            await update.reply("لطفاً یک کلمه کلیدی وارد کنید.")
            return

        # تشخیص زبان کلمه کلیدی
        language = "fa" if any('\u0600' <= c <= '\u06ff' for c in keyword) else "en"
        
       
        keyword_encoded = urllib.parse.quote(keyword)

       
        surah = "all"  
        edition = get_edition(language)

        # ساخت URL برای درخواست به API
        url = f"{BASE_API_URL_S}/{keyword_encoded}/{surah}/{edition}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # بررسی موفقیت‌آمیز بودن درخواست

            data = response.json()

            if data.get('status') != "OK":
                await update.reply(f"هیچ نتیجه‌ای برای کلمه '{keyword}' پیدا نشد.")
                return

           
            results = []
            for match in data.get('data', {}).get('matches', []):
                results.append(f"سوره: {match['surah']['englishName']} ({match['surah']['name']})\n"
                               f"آیه: {match['numberInSurah']}\n"
                               f"متن: {match['text']}\n")

            if results:
              
                if len(results) == 1:
                    await update.reply(results[0])
                else:
                    
                    chunk_size = 5  
                    chunk = "\n\n".join(results[:chunk_size])  
                    await update.reply(chunk)

            else:
                await update.reply("هیچ نتیجه‌ای پیدا نشد.")

        except requests.exceptions.RequestException as e:
            await update.reply(f"خطا در ارتباط با سرور: {str(e)}")

@bot.on_message_updates(filters.is_private)
async def chatbot(update: Updates):
    message_text = update.text

    
    if message_text.startswith("+"):
        await update.reply(f"درحال پردازش سوال شما :\n{message_text}")
        user_input = message_text[1:].strip() 

        if not user_input:
            await update.reply("لطفاً سوال خود را وارد کنید.")
            return

        # دریافت پاسخ از API
        response = get_response_from_api(user_input)
        await update.reply(response)

    
bot.run()
