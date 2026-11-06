import requests, json, os, sys
from urllib.parse import urljoin
from bs4 import BeautifulSoup

URL = "https://cfc.scenecinemas.com/home"
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FILE = "seen.json"

html = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")

movies = {}
for a in soup.select('a[href*="/movie-details/"]'):
    name = a.get("title") or a.get_text(strip=True)
    if name:
        movies[a["href"]] = name

print(len(movies), "فيلم")

if not movies:
    print("لم يتم العثور على أي أفلام.")
    sys.exit()

# قراءة الملف القديم لو موجود
seen_movies = {}
if os.path.exists(FILE):
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            seen_movies = json.load(f)
    except Exception:
        seen_movies = {}

new_movies = {url: name for url, name in movies.items() if url not in seen_movies}

if new_movies:
    for url, name in new_movies.items():
        # رابط الفيلم الكامل
        full_url = urljoin(URL, url)
        message = f"🎬 فيلم جديد في سينما كايرو فستيفال:\n{name}\n🔗 {full_url}"
        
        # إرسال الإشعار عبر تليجرام
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
        requests.post(telegram_url, json=payload)

    # تحديث ملف الأفلام المشاهدة/المرسلة
    seen_movies.update(new_movies)
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(seen_movies, f, ensure_ascii=False, indent=4)
    print(f"تم إرسال {len(new_movies)} فيلم جديد.")
else:
    print("لا توجد أفلام جديدة.")
