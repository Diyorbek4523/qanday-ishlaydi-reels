# Kunlik reels: ish tartibi (har kuni avtomatik sessiya bajaradi)

Sahifa: Instagram @qanday_ishlaydi.uz (o'zbekcha, yuzsiz "Qanday ishlaydi?" reels). Til: o'zbek (lotin).
Maqsad: kuniga 3 ta reels, Toshkent vaqti 12:00, 18:00, 21:00.

1. Repo: `git clone https://github.com/Diyorbek4523/qanday-ishlaydi-reels` (yo'q bo'lsa add_repo, access push).
2. Metricool brand blogId 7647264, timezone Asia/Tashkent. getScheduledPosts bilan bugun (yoki soat 20:00 dan keyin bo'lsa ertaga)
   12:00/18:00/21:00 slotlaridan qaysilari bo'sh ekanini aniqlang. Faqat bo'sh slotlar uchun reels yasang (ko'pi bilan 3 ta).
3. TOPICS.md dagi birinchi ochiq mavzularni oling. Har biri uchun `scripts/NNN-slug.json` yozing (001 namunasi kabi):
   6-7 sahna, jami 22-30 s; 1-sahna = katta savol hook; oxirgi sahna = "*SAQLAB* QO'YING|KEYINGISI: ...".
   "text" = ekrandagi KATTA HARFLI qisqa matn (*so'z* = sariq), "say" = tabiiy og'zaki o'zbekcha (raqamlar so'z bilan).
   Faktlar to'g'ri bo'lsin (shubhali raqamni yozmang). Kerakli chizma yo'q bo'lsa engine/reel.py ga yangi draw funksiya
   qo'shing (mavjudlari uslubida: chiziq bilan chiziladi, CX/CY markazda, matn zonasiga (y<650) chiqmaydi) va DRAW ro'yxatiga kiriting.
4. Render: `python3 engine/reel.py scripts/NNN-slug.json out/NNN-slug.mp4` (ELEVENLABS_API_KEY kerak; ovoz Davronbek, eleven_v4, uz).
   Ovoz ishlamasa `--no-voice` bilan matnli versiya chiqaring va buni hisobotda ayting.
5. Tekshiring: 4-6 kadrni ffmpeg bilan olib, ko'z bilan qarang: matn kesilmagan, chizma matnga tegmaydi, imlo to'g'ri.
6. Videoni `reels/NNN-slug.mp4` ga ko'chiring, TOPICS.md da [x] qiling, commit + `git push origin main`.
7. Metricool createScheduledPost: instagram REEL, media = `https://raw.githubusercontent.com/Diyorbek4523/qanday-ishlaydi-reels/main/reels/NNN-slug.mp4`,
   isAiGenerated true, autoPublish true. Caption: savol + 2 jumla javob + "Bilmagan do'stingizga yuboring 👇" + "Keyingisi: ..." + 8-10 heshteg
   (#qandayishlaydi #bilasizmi #qiziqarli #fan #texnologiya #uzbekistan + mavzuga oid).
8. Hisobot (o'zbekcha, qisqa): qaysi reelslar qaysi vaqtga qo'yildi, plannerUrl'lar, muammo bo'lsa nima.
