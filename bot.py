#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🍎 Blox Fruits Stock Bot — всё в одном файле.

Установка:   python -m pip install "aiogram>=3.7" aiohttp
Запуск:      python fruit_stock_bot.py

╔══════════════════════════════════════════════════════════════╗
║  ВСЁ, ЧТО МОЖНО МЕНЯТЬ, ЛЕЖИТ В 4 БЛОКАХ ВВЕРХУ ФАЙЛА:      ║
║    1. НАСТРОЙКИ  — токен, админы, ссылка на API, интервалы   ║
║    2. ТЕКСТЫ     — все сообщения для пользователей           ║
║    3. КНОПКИ     — подписи кнопок (для юзеров и админки)     ║
║    4. ФРУКТЫ     — список фруктов, редкости, иконки          ║
║  Ниже линии «ДАЛЬШЕ КОД» ничего трогать не нужно.            ║
╚══════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════
# 1. НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════
# 🔐 СЕКРЕТЫ НЕ ХРАНЯТСЯ В КОДЕ.
# На Render задай их в Environment Variables:
#   BOT_TOKEN       = токен от @BotFather
#   ADMIN_IDS       = ID админов через запятую, например 123456789,987654321
#   STOCK_API_KEYS  = API-ключи через запятую
#
# Локально можно задать эти же переменные окружения перед запуском.
BOT_TOKEN = ""
ADMIN_IDS = set()
STOCK_API_KEYS = []
STOCK_URLS = [                # источники стока: бот пробует их по очереди, пока один не ответит
    "https://api.parse.bot/scraper/e534d388-6640-4c19-b9b6-b2ba12930793/get_stock",
    # "https://другой-api.example.com/stock",   ← запасные источники добавляй сюда
]                             # (ссылку, заданную в админке, бот пробует первой)
CHECK_INTERVAL = 120        # как часто (сек) проверять смену стока для уведомлений
CACHE_SECONDS = 90          # сколько секунд держать полученный сток в кэше
NOTIFY_BY_DEFAULT = True    # автоуведомления включены с самого начала (потом переключаются в админке)
SHOW_PRICES = True          # показывать цены, если API их отдаёт
DB_PATH = "fruitstock.db"   # файл базы данных

# ── защита от спама (админов не касается) ──
STOCK_COOLDOWN = 5          # сек между открытиями стока одним пользователем
REFRESH_COOLDOWN = 30       # сек между нажатиями «Обновить» одним пользователем
SUB_COOLDOWN = 2            # сек между переключениями уведомлений

# ═══════════════════════════════════════════════════════════════
# 2. ТЕКСТЫ  (поддерживается HTML: <b>жирный</b>, <i>курсив</i>, <code>код</code>)
#    Приветствие потом можно поменять и из админки — оно главнее этого.
#    Приветствие держи до ~1000 символов (оно идёт подписью к картинке).
# ═══════════════════════════════════════════════════════════════
TEXTS = {
    "welcome": (
        "🍎 <b>Blox Fruits Stock</b>\n\n"
        "В этом боте вы можете посмотреть сток фруктов в Blox Fruits — "
        "обычный сток дилера и Mirage Island.\n\n"
        "Выбери действие 👇"
    ),
    "about": (
        "ℹ️ <b>О боте</b>\n\n"
        "Показываю актуальный сток Blox Fruits: обычный сток дилера и Mirage Island.\n"
        "Включи уведомления — и я напишу, как только сток обновится.\n\n"
        "<i>Данные берутся из сторонних источников и могут немного запаздывать.</i>"
    ),
    "stock_title": "🍎 <b>Сток фруктов</b>",
    "notify_title": "🔔 <b>Сток обновился!</b>",
    "section_normal": "Обычный сток",
    "section_mirage": "Mirage-сток",
    "section_normal_icon": "🛒",
    "section_mirage_icon": "🏝",
    "price_format": "💰 {price}",                       # {price} — цена
    "robux_format": " · {robux} R$",                   # добавляется к цене, если API отдаёт Robux
    "next_reset": "⏳ <i>Следующая смена через {left}</i>",  # {left} — сколько осталось
    "updated": "🕒 Обновлено: {time} UTC",              # {time} — время
    "stale": "⚠️ Источник не отвечает — показаны сохранённые данные",
    "no_data": "😔 Не удалось получить данные. Попробуй чуть позже.",
    "loading": "⏳ Загружаю сток…",
    "cooldown": "⏳ Не так быстро! Подожди {sec} сек.",   # {sec} — сколько осталось ждать
    "sub_on": "🔔 Уведомления включены",
    "sub_off": "🔕 Уведомления выключены",
    "banned": "🚫 Доступ ограничен",
    "admin_only": "⛔ Только для администратора",
    "admin_stale_button": "Кнопка устарела — открой /admin заново",
    "admin_home": "⚙️ <b>Админ-панель</b>\n\nВсё, что меняешь здесь, сразу видят пользователи.",
}

# ═══════════════════════════════════════════════════════════════
# 3. КНОПКИ
# ═══════════════════════════════════════════════════════════════
BUTTONS = {            # для пользователей
    "stock": "🍎 Сток фруктов",
    "notif_on": "🔔 Уведомления: ВКЛ",
    "notif_off": "🔕 Уведомления: ВЫКЛ",
    "about": "ℹ️ О боте",
    "admin": "⚙️ Админ-панель",
    "menu": "⬅️ В меню",
    "refresh": "🔄 Обновить",
    "open_stock": "🍎 Открыть сток",
}
ADMIN_BUTTONS = {      # для админ-панели
    "menu_img": "🖼 Картинка меню",
    "emoji": "🎨 Эмодзи фруктов",
    "broadcast": "📣 Рассылка",
    "welcome": "✏️ Приветствие",
    "source": "🔗 Источник стока",
    "notify": "🔔 Автоуведомления: {state}",   # {state} → ВКЛ / ВЫКЛ
    "stats": "📊 Статистика",
    "users": "👥 Пользователи",
    "ban": "🚫 Бан / разбан",
    "back": "⬅️ Назад",
    "to_admin": "⬅️ В админку",
    "done": "✅ Готово",
}

# ═══════════════════════════════════════════════════════════════
# 4. ФРУКТЫ
#    Новые фрукты из стока добавляются в базу автоматически.
#    Эмодзи любого фрукта меняется в админке (🎨 Эмодзи фруктов) по ID.
#    Редкость: common / uncommon / rare / legendary / mythical
# ═══════════════════════════════════════════════════════════════
RARITY_ICON = {"common": "⚪", "uncommon": "🟢", "rare": "🔵", "legendary": "🟣", "mythical": "🔴"}
DEFAULT_ICON = "🍏"    # для фруктов без известной редкости

DEFAULT_FRUITS = [
    ("Rocket", "common"), ("Spin", "common"), ("Blade", "common"), ("Spring", "common"),
    ("Bomb", "common"), ("Smoke", "common"), ("Spike", "common"),
    ("Flame", "uncommon"), ("Ice", "uncommon"), ("Sand", "uncommon"), ("Dark", "uncommon"),
    ("Eagle", "uncommon"), ("Diamond", "uncommon"),
    ("Light", "rare"), ("Rubber", "rare"), ("Ghost", "rare"), ("Magma", "rare"),
    ("Quake", "legendary"), ("Buddha", "legendary"), ("Love", "legendary"),
    ("Creation", "legendary"), ("Spider", "legendary"), ("Sound", "legendary"),
    ("Phoenix", "legendary"), ("Portal", "legendary"), ("Lightning", "legendary"),
    ("Pain", "legendary"), ("Blizzard", "legendary"),
    ("Gravity", "mythical"), ("Mammoth", "mythical"), ("T-Rex", "mythical"),
    ("Dough", "mythical"), ("Shadow", "mythical"), ("Venom", "mythical"),
    ("Control", "mythical"), ("Spirit", "mythical"), ("Dragon", "mythical"),
    ("Leopard", "mythical"), ("Kitsune", "mythical"), ("Yeti", "mythical"), ("Gas", "mythical"),
]
ALIASES = {"rumble": "lightning"}   # «другое имя» → «имя в списке выше» (в нижнем регистре, без пробелов)

# ═══════════════════════════════════════════════════════════════
# ─────────────────  ДАЛЬШЕ КОД, ТРОГАТЬ НЕ НУЖНО  ─────────────
# ═══════════════════════════════════════════════════════════════
import asyncio
import html
import json
import logging
import math
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone

import aiohttp
from aiogram import BaseMiddleware, Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

T, B, AB = TEXTS, BUTTONS, ADMIN_BUTTONS
NORMAL, MIRAGE = T["section_normal"], T["section_mirage"]

# переменные окружения (если заданы) главнее значений из настроек
BOT_TOKEN = str(os.getenv("BOT_TOKEN") or BOT_TOKEN).strip()
if os.getenv("ADMIN_IDS"):
    ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS").replace(" ", "").split(",") if x}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("fruitbot")

# ═══════════════════════════ БАЗА ДАННЫХ ═══════════════════════════
db = sqlite3.connect(DB_PATH, check_same_thread=False)
db.row_factory = sqlite3.Row


def esc(s) -> str:
    return html.escape(str(s))


def fkey(name) -> str:
    """Нормализованный ключ фрукта: 'Dragon-Dragon', 'dragon fruit' -> 'dragon'."""
    n = re.sub(r"fruit", "", str(name).lower())
    halves = [h.strip() for h in n.split("-")]
    if len(halves) == 2 and halves[0] and halves[0] == halves[1]:
        n = halves[0]
    k = re.sub(r"[^a-z0-9]", "", n)
    return ALIASES.get(k, k) or "x"


def db_init():
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS fruits(
            key TEXT PRIMARY KEY, name TEXT NOT NULL, rarity TEXT DEFAULT '', photo TEXT, emoji TEXT);
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, username TEXT, name TEXT, joined TEXT,
            subscribed INTEGER DEFAULT 0, banned INTEGER DEFAULT 0, last_seen TEXT);
        """
    )
    # миграция старой базы: колонка с эмодзи
    cols = {r["name"] for r in db.execute("PRAGMA table_info(fruits)")}
    if "emoji" not in cols:
        db.execute("ALTER TABLE fruits ADD COLUMN emoji TEXT")
    ucols = {r["name"] for r in db.execute("PRAGMA table_info(users)")}
    if "last_seen" not in ucols:
        db.execute("ALTER TABLE users ADD COLUMN last_seen TEXT")
    for name, rarity in DEFAULT_FRUITS:
        db.execute("INSERT OR IGNORE INTO fruits(key,name,rarity) VALUES(?,?,?)", (fkey(name), name, rarity))
    db.commit()


def get_setting(key, default=None):
    r = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return r["value"] if r else default


def set_setting(key, value):
    db.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
    db.commit()


def del_setting(key):
    db.execute("DELETE FROM settings WHERE key=?", (key,))
    db.commit()


def notify_enabled() -> bool:
    return get_setting("notify", "1" if NOTIFY_BY_DEFAULT else "0") == "1"


def get_fruit(key):
    return db.execute("SELECT rowid AS id, * FROM fruits WHERE key=?", (key,)).fetchone()


def get_fruit_by_id(fid):
    return db.execute("SELECT rowid AS id, * FROM fruits WHERE rowid=?", (fid,)).fetchone()


def ensure_fruit(name):
    name = name.strip()
    key = fkey(name)
    if get_fruit(key):
        return key, False
    db.execute("INSERT INTO fruits(key,name) VALUES(?,?)", (key, name.title() if name.islower() else name))
    db.commit()
    return key, True


def set_fruit_emoji(fid, emoji):
    db.execute("UPDATE fruits SET emoji=? WHERE rowid=?", (emoji, fid))
    db.commit()


def upsert_user(u):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    db.execute(
        "INSERT INTO users(id,username,name,joined,last_seen) VALUES(?,?,?,?,?) "
        "ON CONFLICT(id) DO UPDATE SET username=excluded.username, name=excluded.name, last_seen=excluded.last_seen",
        (u.id, u.username or "", u.full_name, now, now),
    )
    db.commit()


def user_flag(uid, col):
    r = db.execute(f"SELECT {col} FROM users WHERE id=?", (uid,)).fetchone()
    return bool(r and r[col])


def set_user_flag(uid, col, val):
    db.execute(f"UPDATE users SET {col}=? WHERE id=?", (int(val), uid))
    db.commit()


# ═══════════════════════════ ЗАЩИТА ОТ СПАМА ═══════════════════════════
_cd = {}


def cooldown_left(uid, kind, seconds):
    """0 — можно (и время запоминается); иначе сколько секунд ещё ждать. Админы без ограничений."""
    if uid in ADMIN_IDS:
        return 0
    now = time.time()
    if len(_cd) > 5000:
        for k in [k for k, v in _cd.items() if now - v > 300]:
            del _cd[k]
    left = _cd.get((uid, kind), 0) + seconds - now
    if left > 0:
        return left
    _cd[(uid, kind)] = now
    return 0


# ═══════════════════════════ ПОЛУЧЕНИЕ СТОКА ═══════════════════════════
_cache = {"sections": {}, "resets": {}, "ts": 0.0}
_fetch_lock = asyncio.Lock()
# ключи: переменная окружения STOCK_API_KEYS (через запятую) главнее списка из настроек
if os.getenv("STOCK_API_KEYS") or os.getenv("STOCK_API_KEY"):
    STOCK_API_KEYS = (os.getenv("STOCK_API_KEYS") or os.getenv("STOCK_API_KEY")).split(",")
STOCK_API_KEYS = [k.strip() for k in STOCK_API_KEYS if k and k.strip() and not k.strip().startswith("pmx_PASTE")]
_good_key = {"i": 0}   # какой ключ работал в последний раз — с него и начинаем


def mask_key(k):
    return (k[:7] + "…" + k[-4:]) if k and len(k) > 12 else (k or "без ключа")


def key_attempts(url):
    """Какие ключи пробовать для этой ссылки. Ключи отправляем только на parse.bot, чужим сайтам не светим."""
    if "parse.bot" not in url or not STOCK_API_KEYS:
        return [None]
    n = len(STOCK_API_KEYS)
    start = _good_key["i"] % n
    return [STOCK_API_KEYS[(start + i) % n] for i in range(n)]


def headers_for(url, key=None):
    h = {"User-Agent": "Mozilla/5.0 (FruitStockBot)"}
    if key:
        h["X-API-Key"] = key
    return h


def parse_stock(raw, resets=None) -> dict:
    """Терпимый разбор JSON разных API → {NORMAL: [{name, price, robux}], MIRAGE: [...]}.
    Если передан словарь resets — в него кладутся времена следующей смены стока."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return {}
    sections, seen = {}, set()

    def add(title, items):
        for it in items:
            name = price = robux = None
            if isinstance(it, str):
                name = it
            elif isinstance(it, dict):
                name = next((it[k] for k in ("name", "fruit", "fruitName", "title") if it.get(k)), None)
                price = next((it[k] for k in ("price_beli", "price", "beliPrice", "belly", "cost")
                              if isinstance(it.get(k), (int, float, str)) and it.get(k) != ""), None)
                robux = it.get("price_robux") if isinstance(it.get("price_robux"), (int, float)) else None
            if not isinstance(name, str) or not name.strip() or len(name) > 30:
                continue
            k = (title, fkey(name))
            if k in seen:
                continue
            seen.add(k)
            sections.setdefault(title, []).append({"name": name.strip(), "price": price, "robux": robux})

    def walk(node, title):
        if isinstance(node, list):
            add(title, node)
        elif isinstance(node, dict):
            for k, v in node.items():
                lk = str(k).lower()
                sec = MIRAGE if "mirage" in lk else NORMAL if "normal" in lk else title
                if "next_reset" in lk:
                    if resets is not None and isinstance(v, dict) and v.get("reset_at"):
                        resets[sec] = str(v["reset_at"])
                    continue
                walk(v, sec)

    walk(raw, NORMAL)
    return sections


def time_left(iso):
    """'2026-09-27T02:00:00Z' → '1ч 58м' (или None, если время уже прошло / не распознано)."""
    try:
        left = (datetime.fromisoformat(iso.replace("Z", "+00:00")) - datetime.now(timezone.utc)).total_seconds()
    except Exception:
        return None
    if left <= 0:
        return None
    h, m = divmod(int(left) // 60, 60)
    return f"{h}ч {m}м" if h else f"{max(m, 1)}м"


def source_urls():
    urls = [get_setting("stock_url")] + list(STOCK_URLS)
    return [u for i, u in enumerate(urls) if u and u not in urls[:i]]


def seconds_to_reset():
    """Через сколько секунд ближайшая смена стока (по данным API) или None."""
    try:
        ts = [datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp() for v in _cache["resets"].values()]
    except Exception:
        return None
    return (min(ts) - time.time()) if ts else None


def cache_fresh(max_age):
    if not _cache["sections"]:
        return False
    if time.time() - _cache["ts"] < max_age:
        return True
    # сток меняется только по таймеру: пока смены не было, лишний раз API не дёргаем
    left = seconds_to_reset()
    return left is not None and left > 0


async def fetch_stock(max_age=None):
    """→ (sections, error|None, timestamp). Пробует источники по очереди; при полном сбое отдаёт сохранённое."""
    max_age = CACHE_SECONDS if max_age is None else max_age
    async with _fetch_lock:
        if cache_fresh(max_age):
            return _cache["sections"], None, _cache["ts"]
        errors = []
        for url in source_urls():
            for key in key_attempts(url):
                try:
                    async with aiohttp.ClientSession(headers=headers_for(url, key)) as s:
                        async with s.get(url, timeout=aiohttp.ClientTimeout(total=45)) as r:
                            r.raise_for_status()
                            raw = await r.json(content_type=None)
                    resets = {}
                    sections = parse_stock(raw, resets)
                    if not sections:
                        raise ValueError("не удалось распознать ответ API")
                    for items in sections.values():      # новые фрукты получают ID, чтобы им можно было задать эмодзи
                        for it in items:
                            ensure_fruit(it["name"])
                    if key in STOCK_API_KEYS:
                        _good_key["i"] = STOCK_API_KEYS.index(key)
                    _cache.update(sections=sections, resets=resets, ts=time.time())
                    return sections, None, _cache["ts"]
                except Exception as e:
                    log.warning("Источник %s (ключ: %s) не сработал: %s", url, mask_key(key), e)
                    errors.append(f"{url} [{mask_key(key)}]: {e}")
        return _cache["sections"], "; ".join(errors) or "нет источников", _cache["ts"]


async def probe(url, chars=500):
    notes = []
    for key in key_attempts(url):
        label = f"🔑 {esc(mask_key(key))}\n" if key else ""
        try:
            async with aiohttp.ClientSession(headers=headers_for(url, key)) as s:
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=45)) as r:
                    status, body = r.status, await r.text()
            try:
                sections = parse_stock(json.loads(body))
            except Exception:
                sections = {}
            n = sum(len(v) for v in sections.values())
            res = f"{label}HTTP {status}\nРаспознано фруктов: <b>{n}</b>\n\n<code>{esc(body[:chars])}</code>"
            if status == 200 and n:
                return res
            notes.append(res)
        except Exception as e:
            notes.append(f"{label}❌ Ошибка: {esc(e)}")
    return "\n\n".join(notes)


def fmt_price(p):
    try:
        return f"{int(float(str(p).replace(',', '').replace(' ', ''))):,}".replace(",", " ")
    except Exception:
        return esc(p)


def icon_of_row(row):
    """Эмодзи фрукта: своё (из админки) → по редкости → стандартное."""
    return row["emoji"] or RARITY_ICON.get(row["rarity"], DEFAULT_ICON)


def fruit_icon(name):
    row = get_fruit(fkey(name))
    return icon_of_row(row) if row else DEFAULT_ICON


def display_name(name):
    row = get_fruit(fkey(name))
    return row["name"] if row else name


def stock_text(sections, err, ts, title=None):
    title = title or T["stock_title"]
    if not sections:
        return f"{title}\n\n{T['no_data']}"
    parts = [title]
    for sec, icon in ((NORMAL, T["section_normal_icon"]), (MIRAGE, T["section_mirage_icon"])):
        items = sections.get(sec)
        if not items:
            continue
        parts.append(f"\n{icon} <b>{sec}</b>")
        for it in items:
            line = f"{esc(fruit_icon(it['name']))} <b>{esc(display_name(it['name']))}</b>"
            if SHOW_PRICES and it.get("price"):
                line += " — " + T["price_format"].format(price=fmt_price(it["price"]))
                if it.get("robux"):
                    line += T["robux_format"].format(robux=fmt_price(it["robux"]))
            parts.append(line)
        left = time_left(_cache["resets"].get(sec, ""))
        if left:
            parts.append(T["next_reset"].format(left=left))
    parts.append("\n" + T["updated"].format(time=datetime.fromtimestamp(ts, timezone.utc).strftime("%H:%M")))
    if err:
        parts.append(T["stale"])
    return "\n".join(parts)


# ═══════════════════════════ УТИЛИТЫ TELEGRAM ═══════════════════════════
async def tg(fn, *a, **kw):
    """Вызов с переживанием флуд-лимитов."""
    for _ in range(3):
        try:
            return await fn(*a, **kw)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
    return await fn(*a, **kw)


def kb(*rows):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d) for t, d in row] for row in rows]
    )


async def show(target, text, markup=None, photo=None):
    """Показать экран: старое сообщение удаляется, новое (с картинкой или без) отправляется."""
    if isinstance(target, CallbackQuery):
        msg = target.message
        try:
            await msg.delete()
        except TelegramBadRequest:
            pass
    else:
        msg = target
    if photo:
        try:
            return await msg.answer_photo(photo, caption=text, reply_markup=markup)
        except TelegramBadRequest:
            pass  # битый file_id или слишком длинная подпись — покажем текстом
    return await msg.answer(text, reply_markup=markup)


class ImgError(Exception):
    pass


async def to_photo_id(bot, m: Message) -> str:
    """Принимает фото ИЛИ картинку-файл; возвращает file_id фото."""
    if m.photo:
        return m.photo[-1].file_id
    d = m.document
    if not d or not (d.mime_type or "").startswith("image/"):
        raise ImgError("это не картинка — пришли фото или файл PNG/JPG/WEBP")
    try:
        buf = await bot.download(d)
        sent = await tg(bot.send_photo, m.chat.id, BufferedInputFile(buf.read(), d.file_name or "image.png"),
                        disable_notification=True)
    except TelegramBadRequest:
        raise ImgError("Telegram не принял файл (слишком большой — лимит 10 МБ — или странные пропорции)")
    fid = sent.photo[-1].file_id
    try:
        await sent.delete()
    except Exception:
        pass
    return fid


# ═══════════════════════════ MIDDLEWARE ═══════════════════════════
class UserMW(BaseMiddleware):
    async def __call__(self, handler, event, data):
        u = data.get("event_from_user")
        if u and not u.is_bot:
            upsert_user(u)
            if user_flag(u.id, "banned") and u.id not in ADMIN_IDS:
                if isinstance(event, CallbackQuery):
                    await event.answer(T["banned"], show_alert=True)
                return
        return await handler(event, data)


# ═══════════════════════════ ПОЛЬЗОВАТЕЛЬСКАЯ ЧАСТЬ ═══════════════════════════
user = Router()


def sub_label(uid):
    return B["notif_on"] if user_flag(uid, "subscribed") else B["notif_off"]


def main_kb(uid):
    rows = [
        [(B["stock"], "stock")],
        [(sub_label(uid), "sub:menu")],
        [(B["about"], "about")],
    ]
    if uid in ADMIN_IDS:
        rows.append([(B["admin"], "adm")])
    return kb(*rows)


async def show_menu(target, uid):
    await show(target, get_setting("welcome_text") or T["welcome"], main_kb(uid), get_setting("menu_photo"))


def stock_kb(uid):
    return kb(
        [(B["refresh"], "stock_refresh")],
        [(sub_label(uid), "sub:stock")],
        [(B["menu"], "menu")],
    )


async def render_stock(target, uid, force=False, answer=True):
    left = cooldown_left(uid, "refresh" if force else "stock", REFRESH_COOLDOWN if force else STOCK_COOLDOWN)
    if left:
        txt = T["cooldown"].format(sec=math.ceil(left))
        if isinstance(target, CallbackQuery):
            return await target.answer(txt)
        if not cooldown_left(uid, "warn", STOCK_COOLDOWN):   # предупреждаем не чаще раза в кулдаун
            await target.answer(txt)
        return
    if answer and isinstance(target, CallbackQuery):
        await target.answer(T["loading"])
    sections, err, ts = await fetch_stock(max_age=15 if force else None)
    await show(target, stock_text(sections, err, ts), stock_kb(uid))


@user.message(CommandStart())
async def cmd_start(m: Message, state: FSMContext):
    await state.clear()
    await show_menu(m, m.from_user.id)


@user.message(Command("stock"))
async def cmd_stock(m: Message):
    await render_stock(m, m.from_user.id)


@user.callback_query(F.data == "menu")
async def cb_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await show_menu(cb, cb.from_user.id)


@user.callback_query(F.data == "stock")
async def cb_stock(cb: CallbackQuery):
    await render_stock(cb, cb.from_user.id)


@user.callback_query(F.data == "stock_refresh")
async def cb_stock_refresh(cb: CallbackQuery):
    await render_stock(cb, cb.from_user.id, force=True)


@user.callback_query(F.data.startswith("sub:"))
async def cb_sub(cb: CallbackQuery):
    uid = cb.from_user.id
    left = cooldown_left(uid, "sub", SUB_COOLDOWN)
    if left:
        return await cb.answer(T["cooldown"].format(sec=math.ceil(left)))
    new = not user_flag(uid, "subscribed")
    set_user_flag(uid, "subscribed", new)
    await cb.answer(T["sub_on"] if new else T["sub_off"])
    if cb.data.endswith("stock"):
        await render_stock(cb, uid, answer=False)
    else:
        await show_menu(cb, uid)


@user.callback_query(F.data == "about")
async def cb_about(cb: CallbackQuery):
    await cb.answer()
    await show(cb, T["about"], kb([(B["menu"], "menu")]))


@user.callback_query(F.data == "noop")
async def cb_noop(cb: CallbackQuery):
    await cb.answer()


@user.callback_query(F.data.startswith("adm"))
async def cb_adm_fallback(cb: CallbackQuery):
    if cb.from_user.id in ADMIN_IDS:
        await cb.answer(T["admin_stale_button"], show_alert=True)
    else:
        await cb.answer(T["admin_only"], show_alert=True)


# ═══════════════════════════ АДМИН-ПАНЕЛЬ ═══════════════════════════
admin = Router()
admin.message.filter(F.from_user.id.in_(ADMIN_IDS))
admin.callback_query.filter(F.from_user.id.in_(ADMIN_IDS))


class A(StatesGroup):
    menu_img = State()
    emoji = State()
    bc_wait = State()
    bc_confirm = State()
    url = State()
    welcome = State()
    ban = State()


def admin_kb():
    state = "ВКЛ" if notify_enabled() else "ВЫКЛ"
    return kb(
        [(AB["menu_img"], "adm:menuimg"), (AB["emoji"], "adm:emoji")],
        [(AB["users"], "adm:users:0"), (AB["stats"], "adm:stats")],
        [(AB["broadcast"], "adm:bc"), (AB["welcome"], "adm:welcome")],
        [(AB["source"], "adm:url"), (AB["notify"].format(state=state), "adm:notif")],
        [(AB["ban"], "adm:ban")],
        [(B["menu"], "menu")],
    )


async def admin_home(target, state: FSMContext):
    await state.clear()
    await show(target, T["admin_home"], admin_kb())


@admin.message(Command("admin"))
async def cmd_admin(m: Message, state: FSMContext):
    await admin_home(m, state)


@admin.callback_query(F.data == "adm")
async def cb_admin(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await admin_home(cb, state)


# ── Картинка главного меню ──
@admin.callback_query(F.data == "adm:menuimg")
async def adm_menuimg(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(A.menu_img)
    cur = get_setting("menu_photo")
    rows = ([[("🗑 Убрать картинку", "adm:menuimg_del")]] if cur else []) + [[(AB["back"], "adm")]]
    await show(
        cb,
        "🖼 <b>Картинка главного меню</b>\n\nПришли картинку — обычным фото или файлом (без сжатия)."
        + ("\n\nСейчас стоит картинка выше 👆" if cur else "\n\nСейчас картинки нет."),
        kb(*rows), cur,
    )


@admin.callback_query(F.data == "adm:menuimg_del")
async def adm_menuimg_del(cb: CallbackQuery, state: FSMContext):
    del_setting("menu_photo")
    await cb.answer("🗑 Картинка убрана")
    await admin_home(cb, state)


@admin.message(A.menu_img, F.photo | F.document)
async def got_menu_img(m: Message, state: FSMContext, bot: Bot):
    try:
        fid = await to_photo_id(bot, m)
    except ImgError as e:
        return await m.answer(f"⚠️ {e}")
    set_setting("menu_photo", fid)
    await state.clear()
    await m.answer("✅ Картинка главного меню обновлена!",
                   reply_markup=kb([("👀 Посмотреть меню", "menu")], [(AB["to_admin"], "adm")]))


@admin.message(A.menu_img)
async def menu_img_wrong(m: Message):
    await m.answer("Пришли именно картинку (фото или файл) 🙂")


# ── Эмодзи фруктов (по ID) ──
def emoji_screen():
    rows = db.execute("SELECT rowid AS id, * FROM fruits ORDER BY rowid").fetchall()
    lines = [f"<code>{r['id']}</code> · {esc(icon_of_row(r))} {esc(r['name'])}" for r in rows]
    text = (
        "🎨 <b>Эмодзи фруктов</b>\n\n"
        "Пришли <b>ID и эмодзи</b> через пробел, например:\n"
        "<code>12 🔥</code>\n"
        "Можно сразу несколько — каждый с новой строки.\n"
        "Чтобы вернуть стандартное (по редкости): <code>12 -</code>\n\n"
        + "\n".join(lines)
    )
    return text[:3900]


@admin.callback_query(F.data == "adm:emoji")
async def adm_emoji(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(A.emoji)
    await show(cb, emoji_screen(), kb([(AB["done"], "adm")]))


@admin.message(A.emoji, F.text)
async def got_emoji(m: Message):
    out = []
    for line in m.text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or not parts[0].isdigit():
            out.append(f"⚠️ «{esc(line[:30])}» — нужен формат: ID эмодзи")
            continue
        row = get_fruit_by_id(int(parts[0]))
        if not row:
            out.append(f"⚠️ Фрукта с ID {esc(parts[0])} нет")
            continue
        val = parts[1].strip()
        if val in ("-", "reset", "/reset"):
            set_fruit_emoji(row["id"], None)
            out.append(f"♻️ {esc(row['name'])}: стандартное {esc(RARITY_ICON.get(row['rarity'], DEFAULT_ICON))}")
        elif len(val) > 16 or re.search(r"[A-Za-z0-9]", val):
            out.append(f"⚠️ {esc(row['name'])}: «{esc(val[:20])}» — это не эмодзи")
        else:
            set_fruit_emoji(row["id"], val)
            out.append(f"✅ {esc(row['name'])}: {esc(val)}")
    await m.answer("\n".join(out) or "Пришли ID и эмодзи, например: <code>12 🔥</code>",
                   reply_markup=kb([("📋 Показать список", "adm:emoji")], [(AB["done"], "adm")]))


@admin.message(A.emoji)
async def emoji_wrong(m: Message):
    await m.answer("Пришли текстом: ID и эмодзи, например <code>12 🔥</code> 🙂")


# ── Рассылка ──
@admin.callback_query(F.data == "adm:bc")
async def adm_bc(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(A.bc_wait)
    await show(cb, "📣 <b>Рассылка</b>\n\nПришли сообщение (текст, фото, видео — что угодно). "
                   "Оно уйдёт всем пользователям в точности как есть.", kb([(AB["back"], "adm")]))


@admin.message(A.bc_wait)
async def bc_got(m: Message, state: FSMContext):
    await state.update_data(chat=m.chat.id, mid=m.message_id)
    await state.set_state(A.bc_confirm)
    n = db.execute("SELECT COUNT(*) FROM users WHERE banned=0").fetchone()[0]
    await m.reply(f"Разослать это сообщение <b>{n}</b> пользователям?",
                  reply_markup=kb([("✅ Отправить", "adm:bc_go"), ("❌ Отмена", "adm")]))


@admin.callback_query(A.bc_confirm, F.data == "adm:bc_go")
async def bc_go(cb: CallbackQuery, state: FSMContext, bot: Bot):
    d = await state.get_data()
    await state.clear()
    await cb.answer("Начинаю рассылку…")
    ids = [r["id"] for r in db.execute("SELECT id FROM users WHERE banned=0")]
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    status = await bot.send_message(cb.message.chat.id, f"📣 Рассылка… 0/{len(ids)}")
    ok = fail = 0
    for i, uid in enumerate(ids, 1):
        try:
            await tg(bot.copy_message, uid, d["chat"], d["mid"])
            ok += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.05)
        if i % 25 == 0:
            try:
                await status.edit_text(f"📣 Рассылка… {i}/{len(ids)}")
            except TelegramBadRequest:
                pass
    await status.edit_text(f"✅ <b>Рассылка завершена</b>\n\nДоставлено: {ok}\nНе доставлено: {fail}",
                           reply_markup=kb([(AB["to_admin"], "adm")]))


# ── Приветствие ──
@admin.callback_query(F.data == "adm:welcome")
async def adm_welcome(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(A.welcome)
    await show(cb, "✏️ <b>Текст приветствия</b>\n\nПришли новый текст главного меню. Можно использовать "
                   "форматирование Telegram (жирный, курсив, ссылки) и эмодзи. До 1000 символов.\n\n"
                   "Чтобы вернуть стандартный (из файла) — отправь <code>/reset</code>.",
               kb([(AB["back"], "adm")]))


@admin.message(A.welcome, F.text)
async def got_welcome(m: Message, state: FSMContext):
    if m.text.strip() == "/reset":
        del_setting("welcome_text")
        await state.clear()
        return await m.answer("✅ Вернул стандартное приветствие",
                              reply_markup=kb([("👀 Меню", "menu")], [(AB["to_admin"], "adm")]))
    txt = m.html_text
    if len(txt) > 1000:
        return await m.answer("⚠️ Слишком длинно (максимум ~1000 символов). Сократи и пришли снова.")
    set_setting("welcome_text", txt)
    await state.clear()
    await m.answer("✅ Приветствие обновлено!",
                   reply_markup=kb([("👀 Посмотреть меню", "menu")], [(AB["to_admin"], "adm")]))


# ── Источник стока ──
@admin.callback_query(F.data == "adm:url")
async def adm_url(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(A.url)
    cur = "\n".join(source_urls()) or "—"
    keys = "\n".join(f"{i}. <code>{esc(mask_key(k))}</code>" for i, k in enumerate(STOCK_API_KEYS, 1)) or "—"
    await show(
        cb,
        f"🔗 <b>Источники стока</b> (пробую по порядку):\n<code>{esc(cur)}</code>\n\n"
        f"🔑 <b>API-ключи</b> ({len(STOCK_API_KEYS)}), если один не работает — беру следующий:\n{keys}\n\n"
        "Пришли новую ссылку на JSON-API — я поставлю её первой и сразу проверю, что в ней нашёл.",
        kb([("🧪 Проверить текущий", "adm:url_test")], [("♻️ Сбросить на стандартный", "adm:url_reset")],
           [(AB["back"], "adm")]),
    )


@admin.callback_query(F.data == "adm:url_test")
async def adm_url_test(cb: CallbackQuery):
    await cb.answer("⏳ Проверяю…")
    res = "\n\n".join([f"<b>{esc(u)}</b>\n" + await probe(u, 250) for u in source_urls()])
    await cb.message.answer(res, reply_markup=kb([(AB["to_admin"], "adm")]))


@admin.callback_query(F.data == "adm:url_reset")
async def adm_url_reset(cb: CallbackQuery, state: FSMContext):
    del_setting("stock_url")
    _cache.update(sections={}, ts=0.0)
    await cb.answer("♻️ Сброшено")
    await admin_home(cb, state)


@admin.message(A.url, F.text)
async def got_url(m: Message, state: FSMContext):
    url = m.text.strip()
    if not re.match(r"^https?://\S+$", url):
        return await m.answer("⚠️ Нужна ссылка, начинающаяся с http:// или https://")
    set_setting("stock_url", url)
    _cache.update(sections={}, ts=0.0)
    await state.clear()
    wait = await m.answer("⏳ Проверяю…")
    res = await probe(url)
    await wait.edit_text("✅ Ссылка сохранена\n\n" + res, reply_markup=kb([(AB["to_admin"], "adm")]))


# ── Автоуведомления / статистика / бан ──
@admin.callback_query(F.data == "adm:notif")
async def adm_notif(cb: CallbackQuery, state: FSMContext):
    new = "0" if notify_enabled() else "1"
    set_setting("notify", new)
    await cb.answer("🔔 Включены" if new == "1" else "🔕 Выключены")
    await admin_home(cb, state)


@admin.callback_query(F.data == "adm:stats")
async def adm_stats(cb: CallbackQuery):
    await cb.answer()
    q = lambda sql: db.execute(sql).fetchone()[0]
    total, subs, banned = q("SELECT COUNT(*) FROM users"), q("SELECT COUNT(*) FROM users WHERE subscribed=1"), q("SELECT COUNT(*) FROM users WHERE banned=1")
    fr, fe = q("SELECT COUNT(*) FROM fruits"), q("SELECT COUNT(*) FROM fruits WHERE emoji IS NOT NULL")
    await show(
        cb,
        "📊 <b>Статистика</b>\n\n"
        f"👥 Пользователей: <b>{total}</b>\n🔔 Подписано на уведомления: <b>{subs}</b>\n🚫 В бане: <b>{banned}</b>\n\n"
        f"🍎 Фруктов в базе: <b>{fr}</b>, со своим эмодзи: <b>{fe}</b>\n"
        f"🖼 Картинка меню: {'есть' if get_setting('menu_photo') else 'нет'}\n"
        f"🔔 Автоуведомления: {'вкл' if notify_enabled() else 'выкл'}",
        kb([(AB["back"], "adm")]),
    )


USERS_PER_PAGE = 15


@admin.callback_query(F.data.startswith("adm:users:"))
async def adm_users(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    q = lambda sql, *a: db.execute(sql, a).fetchone()[0]
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat(timespec="seconds")
    total = q("SELECT COUNT(*) FROM users")
    subs = q("SELECT COUNT(*) FROM users WHERE subscribed=1")
    banned = q("SELECT COUNT(*) FROM users WHERE banned=1")
    new24 = q("SELECT COUNT(*) FROM users WHERE joined>=?", cutoff)
    act24 = q("SELECT COUNT(*) FROM users WHERE COALESCE(last_seen, joined)>=?", cutoff)
    pages = max(1, (total + USERS_PER_PAGE - 1) // USERS_PER_PAGE)
    page = max(0, min(int(cb.data.split(":")[2]), pages - 1))
    rows = db.execute(
        "SELECT * FROM users ORDER BY COALESCE(last_seen, joined) DESC LIMIT ? OFFSET ?",
        (USERS_PER_PAGE, page * USERS_PER_PAGE),
    ).fetchall()
    lines = []
    for i, r in enumerate(rows, page * USERS_PER_PAGE + 1):
        uname = f"@{esc(r['username'])}" if r["username"] else "без username"
        flags = (" 🔔" if r["subscribed"] else "") + (" 🚫" if r["banned"] else "")
        seen = (r["last_seen"] or r["joined"] or "")[5:16].replace("T", " ") or "—"
        joined = (r["joined"] or "")[:10] or "—"
        lines.append(
            f"{i}. <a href=\"tg://user?id={r['id']}\">{esc(r['name'] or '—')}</a> · {uname}{flags}\n"
            f"    🆔 <code>{r['id']}</code> · 📅 {joined} · 🕒 {seen}"
        )
    text = (
        "👥 <b>Пользователи бота</b>\n\n"
        f"Всего: <b>{total}</b> · 🔔 подписаны: <b>{subs}</b> · 🚫 в бане: <b>{banned}</b>\n"
        f"За 24 часа: новых <b>{new24}</b>, активных <b>{act24}</b>\n\n"
        + ("\n".join(lines) or "Пока никого нет.")
        + "\n\n<i>🕒 — последняя активность (UTC)</i>"
    )
    nav = []
    if page > 0:
        nav.append(("◀️", f"adm:users:{page - 1}"))
    nav.append((f"{page + 1}/{pages}", "noop"))
    if page < pages - 1:
        nav.append(("▶️", f"adm:users:{page + 1}"))
    await show(cb, text[:4000], kb(nav, [(AB["ban"], "adm:ban")], [(AB["back"], "adm")]))


@admin.callback_query(F.data == "adm:ban")
async def adm_ban(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(A.ban)
    await show(cb, "🚫 <b>Бан / разбан</b>\n\nПришли числовой ID пользователя — статус переключится.\n"
                   "(ID можно узнать через @userinfobot)", kb([(AB["back"], "adm")]))


@admin.message(A.ban, F.text)
async def got_ban(m: Message):
    if not m.text.strip().isdigit():
        return await m.answer("⚠️ Нужен числовой ID")
    uid = int(m.text.strip())
    if uid in ADMIN_IDS:
        return await m.answer("Админа банить нельзя 🙂")
    if not db.execute("SELECT 1 FROM users WHERE id=?", (uid,)).fetchone():
        return await m.answer("Такого пользователя нет в базе бота")
    new = not user_flag(uid, "banned")
    set_user_flag(uid, "banned", new)
    await m.answer(f"{'🚫 Забанен' if new else '✅ Разбанен'}: <code>{uid}</code>\n\nМожешь прислать ещё ID.")


# ═══════════════════════════ УВЕДОМЛЕНИЯ О СМЕНЕ СТОКА ═══════════════════════════
async def broadcast_stock(bot: Bot, sections):
    text = stock_text(sections, None, time.time(), title=T["notify_title"])
    ids = [r["id"] for r in db.execute("SELECT id FROM users WHERE subscribed=1 AND banned=0")]
    for uid in ids:
        try:
            await tg(bot.send_message, uid, text, reply_markup=kb([(B["open_stock"], "stock")]))
        except TelegramForbiddenError:
            set_user_flag(uid, "subscribed", False)
        except Exception as e:
            log.warning("уведомление %s не доставлено: %s", uid, e)
        await asyncio.sleep(0.05)


async def watcher(bot: Bot):
    await asyncio.sleep(5)
    while True:
        try:
            if notify_enabled():
                sections, err, _ = await fetch_stock(max_age=max(CHECK_INTERVAL - 5, 1))
                if sections and not err:
                    sig = json.dumps({k: sorted(fkey(i["name"]) for i in v) for k, v in sections.items()}, sort_keys=True)
                    last = get_setting("last_sig")
                    if sig != last:
                        set_setting("last_sig", sig)
                        if last:  # при самом первом запуске не рассылаем
                            await broadcast_stock(bot, sections)
        except Exception:
            log.exception("watcher error")
        delay = CHECK_INTERVAL
        left = seconds_to_reset()
        if left is not None and 0 < left < CHECK_INTERVAL:
            delay = left + 5  # проснуться сразу после смены стока
        await asyncio.sleep(delay)


# ═══════════════════════════ ЗАПУСК ═══════════════════════════
async def main():
    if not BOT_TOKEN:
        sys.exit("Не задан BOT_TOKEN. Добавь его в Environment Variables на Render.")
    if not ADMIN_IDS:
        sys.exit("Не задан ADMIN_IDS. Добавь Telegram ID администратора в Environment Variables на Render.")
    db_init()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.outer_middleware(UserMW())
    dp.callback_query.outer_middleware(UserMW())
    dp.include_router(admin)  # админка первой — у обычных пользователей она не сработает
    dp.include_router(user)
    watch_task = asyncio.create_task(watcher(bot))
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    log.info("Бот @%s запущен. Админы: %s", me.username, ", ".join(map(str, ADMIN_IDS)))
    try:
        await dp.start_polling(bot)
    finally:
        watch_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except SystemExit as e:
        if e.code:
            log.error("%s", e.code)
        raise
    except Exception:
        log.exception("Бот упал с ошибкой")
        raise