# 3D reels (2026-11-01 dan asosiy uslub)

Foydalanuvchi blueprint chizmalarini takrorlanuvchi deb topdi va boshqa uslub so'radi. Endi har reels:
**Blender 3D sahna (stilizatsiyalangan, rangli, kesimlar) + jonli ovoz (stability 0 + [teglar]) + so'zma-so'z subtitr**.
Eski `engine/reel.py` (blueprint) faqat zaxira: 3D ishlamay qolsa.

## Fayllar
- `engine3d/make3d.py` — ovoz -> kadr vaqtlari -> Blender -> musiqa + subtitr (ASS) -> mp4.
- `engine3d/b3d.py` — Blender yordamchilari: `setup`, `mat`, `key_input`, `prim`, `lathe`, `camera`, `shot`, `visible`, `flicker`, `arrow`, `light`, `render`.
- `engine3d/scenes/<nom>.py` — har mavzuga bitta sahna skripti. Namuna: `scenes/tandir.py`.
- `scripts/NNN-slug.json` — `"style": "3d"`, `"scene": "<nom>"`, sahnalar faqat `say` (+ 1-sahnada hook `text`, oxirgisida end-card `text`).

## Buyruqlar (repo ildizida, bash)
```
export REEL_FONT_DIR="C:/Users/User/fonts/inter"
python engine3d/make3d.py scripts/NNN-slug.json out/NNN-slug.mp4 --preview   # har kadr o'rtasidan 1 ta kichik rasm -> out/NNN-slug_preview.png (~20 s)
python engine3d/make3d.py scripts/NNN-slug.json out/NNN-slug.mp4             # to'liq render
```
Blender: `C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe` (5.2, EEVEE). Xato bo'lsa `out/NNN-slug_work/blender.log`.

## Ssenariy
- 6-7 sahna, 24-30 s. **22 s dan qisqa QILMA** (2026-11-06: <=20.5 s bo'lgan 6 reelsdan 4 tasi deyarli 0 ko'rish oldi, 22 s+ hech biri). Har sahna = bitta kamera kadri (sahna skriptida `shot(...)`).
- `say`: tabiiy og'zaki o'zbekcha, raqamlar so'z bilan. ElevenLabs v4 teglari ingliz tilida, kvadrat qavsda, gap boshida:
  `[curious]` savol, `[whispers]` sir/qiziqtirish, `[excited]` ochilish va oxirgi chaqiriq, `[surprised]`, `[laughs]` kamdan-kam.
  Har sahnada ko'pi bilan 1-2 teg. Teglar subtitrga chiqmaydi.
- 1-sahna `text`: tepada katta hook (`|` qator, `*so'z*` sariq). Oxirgi sahna `text`: `*OBUNA* BO'LING|KEYINGISI:|...`, `say`: `[excited] Obuna bo'ling! Keyingi videoda: ...` (2026-11-04: maqsad obunachi, 9492 ko'rishga 20 obunachi edi).
- `"follow_pill": true` (2026-11-05 dan har yangi reelsda): 2-sahnadan 1 s keyin 4 s davomida tepada ovozsiz '+ OBUNA BO'LING' yozuvi, chunki o'rtacha tomosha 8-13 s va ko'pchilik end-cardga yetmaydi.
- Ovoz sozlamasi standart (`reel.VOICE`): stability 0.0, similarity 0.8 — foydalanuvchi tanlagan jonli variant.

## Sahna skripti qoidalari
- Uslub: soddalashtirilgan, yumaloq, rangli 3D (o'yinchoq/claymation hissi), qorong'i ko'k osmon, iliq yorug'lik.
  Rang filtri `Standard` (AgX olov va emissiyani oqartiradi). Emissiya kuchi 2-6, nuqta chiroq 100-300 W atrofida — undan ortig'i oqarib ketadi.
- Kadrlar xilma-xil bo'lsin: tashqi ko'rinish, **kesim (cutaway, Boolean)**, yaqin plan, harakatlanuvchi qism, oxirida orqaga uzoqlashish.
  Kamera har kadrda sekin harakatlansin (`shot` a->b). Kesimda kamera tomonidagi (kesib tashlangan) obyektlarni yashir (`visible`).
- Subtitr pastki uchdan birda (y ~1450), hook tepada (y ~210-450): asosiy obyekt kadrning o'rtasida bo'lsin.
- Har mavzu uchun mexanizmni ko'rsat: oqim (sharchalar yo'l bo'ylab), strelkalar (`arrow`, emissiya), rang o'zgarishi (`key_input`), miltillash (`flicker`).
- Odam/hayvon modellarini noldan yasama (yomon chiqadi). Kerak bo'lsa qo'l/odamni ko'rsatmasdan harakat bilan tushuntir.
- Avval `--preview`, rasmni ko'r: qorong'i/oqarib ketgan kadr, havoda osilgan qism, devor ichiga kirgan obyekt, bo'sh kadr yo'qligini tekshir. Keyin to'liq render.
- To'liq renderdan keyin 4-6 kadrni ffmpeg bilan olib, subtitr kesilmaganini va imloni tekshir.
