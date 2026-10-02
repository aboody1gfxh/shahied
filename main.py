import io
import asyncio
import sys
import subprocess
import unicodedata
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

from telethon import TelegramClient, events, Button
from telethon.tl.types import InputMediaUploadedPhoto


# =========================================================
# 🔐 معلومات الاتصال — لم يتم تغييرها
# =========================================================

API_ID = 32361464
API_HASH = "efa6fd8d917173938f503ec3659122cd"
BOT_TOKEN = "8877046448:AAELBYOfn-XVEUffWjog3Csee2_TrbfyGfc"
SESSION_NAME = "certificate_bot"


# =========================================================
# 📁 مسارات المشروع
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ACADEMY_TEMPLATE = os.path.join(
    BASE_DIR,
    "academy.jpg"
)

KATIBA_TEMPLATE = os.path.join(
    BASE_DIR,
    "katiba.jpg"
)

FONTS_DIR = os.path.join(
    BASE_DIR,
    "fonts"
)

os.makedirs(
    FONTS_DIR,
    exist_ok=True
)


# =========================================================
# ⚙️ إعدادات النماذج
# =========================================================

TEMPLATES = {

    "academy": {
        "name": "🏆 نموذج الأكاديمية الأساسي",
        "path": ACADEMY_TEMPLATE,
        "name_x": 0.500,
        "name_y": 0.468,
        "font_ratio": 0.055,
        "max_width_ratio": 0.60
    },

    "katiba": {
        "name": "🎖️ نموذج الكتيبة الأساسي",
        "path": KATIBA_TEMPLATE,
        "name_x": 0.500,
        "name_y": 0.600,
        "font_ratio": 0.052,
        "max_width_ratio": 0.57
    }
}


# =========================================================
# 📦 حجم الدفعة
# =========================================================

BATCH_SIZE = 10

MIN_FONT_SIZE = 20


# =========================================================
# ✍️ سمك الخط
# =========================================================

STROKE_WIDTH = 2


# =========================================================
# 🎨 الألوان
# =========================================================

COLORS = {

    "black": {
        "name": "⚫ أسود",
        "rgb": (0, 0, 0)
    },

    "white": {
        "name": "⚪ أبيض",
        "rgb": (255, 255, 255)
    },

    "gold": {
        "name": "🟡 ذهبي",
        "rgb": (212, 175, 55)
    },

    "blue": {
        "name": "🔵 أزرق",
        "rgb": (20, 80, 180)
    },

    "red": {
        "name": "🔴 أحمر",
        "rgb": (190, 30, 30)
    },

    "green": {
        "name": "🟢 أخضر",
        "rgb": (20, 120, 60)
    }
}


DEFAULT_COLOR = "black"


# =========================================================
# 📡 Telethon
# =========================================================

client = TelegramClient(
    SESSION_NAME,
    API_ID,
    API_HASH
)


# =========================================================
# 👤 بيانات المستخدمين
# =========================================================

users = {}


# =========================================================
# 🖼️ ذاكرة مؤقتة للنماذج
# =========================================================

TEMPLATE_CACHE = {}


# =========================================================
# 📦 تثبيت المكتبات
# =========================================================

def install_package(package_name, version=None):

    try:

        package = package_name

        if version:
            package = f"{package_name}=={version}"

        print(
            f"📦 جاري تثبيت {package}..."
        )

        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            package
        ])

        return True

    except Exception as e:

        print(
            f"❌ فشل تثبيت {package_name}:"
        )

        print(e)

        return False


# =========================================================
# 🔤 تحميل الخطوط تلقائياً
# =========================================================

def download_font(filename, url):

    path = os.path.join(
        FONTS_DIR,
        filename
    )

    if os.path.exists(path):

        print(
            f"✅ الخط موجود: {filename}"
        )

        return path

    print(
        f"📥 جاري تنزيل الخط: {filename}"
    )

    try:

        urllib.request.urlretrieve(
            url,
            path
        )

        if os.path.exists(path):

            size = os.path.getsize(path)

            if size > 1000:

                print(
                    f"✅ تم تنزيل الخط: {filename}"
                )

                return path

        print(
            f"❌ ملف الخط غير صالح: {filename}"
        )

        return None

    except Exception as error:

        print(
            f"❌ فشل تنزيل الخط {filename}:"
        )

        print(error)

        return None


def prepare_fonts():

    print(
        "\n"
        "========================================\n"
        "🔤 تجهيز الخطوط\n"
        "========================================"
    )

    # خط عربي
    arabic_url = (
        "https://raw.githubusercontent.com/"
        "notofonts/arabic/main/"
        "fonts/ttf/NotoNaskhArabic/"
        "NotoNaskhArabic-Regular.ttf"
    )

    # خط لاتيني وأرقام
    latin_url = (
        "https://raw.githubusercontent.com/"
        "notofonts/latin/main/"
        "googlefonts/ttf/"
        "NotoSans/NotoSans-Regular.ttf"
    )

    # خط احتياطي
    arabic_path = download_font(
        "NotoNaskhArabic-Regular.ttf",
        arabic_url
    )

    latin_path = download_font(
        "NotoSans-Regular.ttf",
        latin_url
    )

    print(
        "========================================\n"
    )

    return (
        arabic_path,
        latin_path
    )


# =========================================================
# 🌍 مكتبات العربية
# =========================================================

arabic_reshaper = None
bidi_get_display = None


def load_arabic_libraries():

    global arabic_reshaper
    global bidi_get_display

    # -----------------------------------------------------
    # Arabic Reshaper
    # -----------------------------------------------------

    try:

        import arabic_reshaper

        print(
            "✅ arabic_reshaper موجود"
        )

    except ImportError:

        print(
            "📦 arabic_reshaper غير موجود..."
        )

        installed = install_package(
            "arabic-reshaper"
        )

        if installed:

            try:

                import arabic_reshaper

                print(
                    "✅ تم تثبيت arabic-reshaper"
                )

            except Exception as e:

                print(
                    "❌ تعذر تحميل arabic_reshaper:"
                )

                print(e)

                arabic_reshaper = None

        else:

            arabic_reshaper = None

    # -----------------------------------------------------
    # Python Bidi
    # -----------------------------------------------------

    try:

        from bidi.algorithm import get_display

        bidi_get_display = get_display

        print(
            "✅ python-bidi موجود"
        )

    except ImportError:

        print(
            "📦 python-bidi غير موجود..."
        )

        print(
            "📦 سيتم استخدام النسخة 0.4.2"
        )

        installed = install_package(
            "python-bidi",
            "0.4.2"
        )

        if installed:

            try:

                from bidi.algorithm import get_display

                bidi_get_display = get_display

                print(
                    "✅ تم تحميل python-bidi 0.4.2"
                )

            except Exception as e:

                print(
                    "❌ تعذر تحميل python-bidi:"
                )

                print(e)

                bidi_get_display = None

        else:

            bidi_get_display = None


# =========================================================
# 📝 الحفاظ على الاسم
# =========================================================

def preserve_name(name):

    if name is None:
        return ""

    return str(name)


# =========================================================
# 🇸🇦 العربية
# =========================================================

def is_arabic_char(char):

    code = ord(char)

    return (

        0x0600 <= code <= 0x06FF

        or

        0x0750 <= code <= 0x077F

        or

        0x08A0 <= code <= 0x08FF

        or

        0xFB50 <= code <= 0xFDFF

        or

        0xFE70 <= code <= 0xFEFF

        or

        0x1EE00 <= code <= 0x1EEFF

    )


def contains_arabic(text):

    for char in text:

        if is_arabic_char(char):

            return True

    return False


# =========================================================
# 🇬🇧 Latin
# =========================================================

def is_latin_char(char):

    code = ord(char)

    return (

        0x0041 <= code <= 0x005A

        or

        0x0061 <= code <= 0x007A

        or

        0x00C0 <= code <= 0x024F

        or

        0x1E00 <= code <= 0x1EFF

    )


# =========================================================
# ✨ English Mathematical / Fancy
# =========================================================

def is_math_decorated_char(char):

    code = ord(char)

    return (
        0x1D400 <= code <= 0x1D7FF
    )


# =========================================================
# ✨ زخارف وأشكال Latin
# =========================================================

def is_decorated_latin(char):

    code = ord(char)

    return (

        0x1D400 <= code <= 0x1D7FF

        or

        0x2100 <= code <= 0x214F

        or

        0x2150 <= code <= 0x218F

        or

        0x2460 <= code <= 0x24FF

        or

        0xFF00 <= code <= 0xFFEF

    )


# =========================================================
# 🔢 الأرقام
# =========================================================

def is_number_char(char):

    return char.isdigit()


# =========================================================
# 😀 Emoji
# =========================================================

def is_emoji_char(char):

    code = ord(char)

    return (

        0x1F000 <= code <= 0x1FAFF

        or

        0x1FC00 <= code <= 0x1FFFF

        or

        0x2600 <= code <= 0x27BF

        or

        0x2300 <= code <= 0x23FF

        or

        0x2B00 <= code <= 0x2BFF

    )


# =========================================================
# 🔣 Symbols
# =========================================================

def is_symbol_char(char):

    try:

        name = unicodedata.name(
            char,
            ""
        )

    except Exception:

        name = ""

    return any(

        word in name

        for word in (

            "SYMBOL",
            "ARROW",
            "DINGBAT",
            "ORNAMENT",
            "MATH",
            "GEOMETRIC",
            "TECHNICAL"

        )

    )


# =========================================================
# 🔤 Combining Marks
# =========================================================

def is_combining_char(char):

    try:

        return unicodedata.combining(char) != 0

    except Exception:

        return False


# =========================================================
# 🗂️ الخطوط
# =========================================================

FONT_PATHS = [

    # -----------------------------------------------------
    # الخطوط التي ننزلها داخل المشروع
    # -----------------------------------------------------

    os.path.join(
        FONTS_DIR,
        "NotoNaskhArabic-Regular.ttf"
    ),

    os.path.join(
        FONTS_DIR,
        "NotoSans-Regular.ttf"
    ),

    # -----------------------------------------------------
    # خطوط Linux الشائعة
    # -----------------------------------------------------

    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",

    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",

    # -----------------------------------------------------
    # خطوط Android القديمة — تبقى كاحتياط
    # -----------------------------------------------------

    "/system/fonts/NotoNaskhArabic-Medium.ttf",
    "/system/fonts/NotoNaskhArabic-Regular.ttf",

    "/system/fonts/NotoSansArabic-Medium.ttf",
    "/system/fonts/NotoSansArabic-Regular.ttf",

    "/system/fonts/NotoSansArabicUI-Medium.ttf",
    "/system/fonts/NotoSansArabicUI-Regular.ttf",

    "/system/fonts/NotoKufiArabic-Regular.ttf",

    "/system/fonts/NotoNaskhArabic-Bold.ttf",
    "/system/fonts/NotoSansArabic-Bold.ttf",

    "/system/fonts/NotoSansMath-Regular.ttf",
    "/system/fonts/NotoSansMath-Bold.ttf",

    "/system/fonts/NotoSans-Medium.ttf",
    "/system/fonts/NotoSans-Regular.ttf",

    "/system/fonts/NotoSansDisplay-Medium.ttf",
    "/system/fonts/NotoSansDisplay-Regular.ttf",

    "/system/fonts/Roboto-Medium.ttf",
    "/system/fonts/Roboto-Regular.ttf",

    "/system/fonts/NotoSansSymbols-Regular.ttf",
    "/system/fonts/NotoSansSymbols2-Regular.ttf",

    "/system/fonts/NotoColorEmoji.ttf",

    "/system/fonts/NotoSansHebrew-Regular.ttf",
    "/system/fonts/NotoSansThai-Regular.ttf",
    "/system/fonts/NotoSansDevanagari-Regular.ttf",
    "/system/fonts/NotoSansBengali-Regular.ttf",
    "/system/fonts/NotoSansTamil-Regular.ttf",
    "/system/fonts/NotoSansTelugu-Regular.ttf",
    "/system/fonts/NotoSansKannada-Regular.ttf",
    "/system/fonts/NotoSansMalayalam-Regular.ttf",
    "/system/fonts/NotoSansGujarati-Regular.ttf",
    "/system/fonts/NotoSansGurmukhi-Regular.ttf",

    "arial.ttf",
    "Arial.ttf",
    "arialbd.ttf",
    "Arial Bold.ttf"
]


# =========================================================
# 🔤 تحميل خط
# =========================================================

def load_font(path, size):

    try:

        if not os.path.exists(path):

            return None

        return ImageFont.truetype(
            path,
            size
        )

    except Exception:

        return None


# =========================================================
# 🔤 تحميل الخطوط
# =========================================================

def get_available_fonts(
    image_width,
    font_ratio
):

    font_size = max(
        MIN_FONT_SIZE,
        int(
            image_width *
            font_ratio
        )
    )

    fonts = []

    seen = set()

    for path in FONT_PATHS:

        if path in seen:
            continue

        seen.add(path)

        font = load_font(
            path,
            font_size
        )

        if font:

            fonts.append(
                (
                    path,
                    font
                )
            )

    print(
        f"🔤 عدد الخطوط المتاحة: {len(fonts)}"
    )

    for path, _ in fonts:

        print(
            f"   ✓ {path}"
        )

    return fonts


# =========================================================
# 🔎 البحث عن خط
# =========================================================

def find_font_by_keywords(
    fonts,
    keywords
):

    for keyword in keywords:

        for path, font in fonts:

            if keyword.lower() in path.lower():

                return (
                    path,
                    font
                )

    return None


# =========================================================
# 🇬🇧 Latin
# =========================================================

def get_latin_font(fonts):

    preferred = [

        "NotoSans-Regular.ttf",
        "NotoSans-Medium.ttf",

        "NotoSansDisplay-Regular.ttf",
        "NotoSansDisplay-Medium.ttf",

        "Roboto-Medium.ttf",
        "Roboto-Regular.ttf",

        "DejaVuSans.ttf",
        "FreeSans.ttf",

        "arial.ttf",
        "Arial.ttf"

    ]

    result = find_font_by_keywords(
        fonts,
        preferred
    )

    if result:
        return result

    if fonts:
        return fonts[0]

    return None


# =========================================================
# 🇸🇦 Arabic
# =========================================================

def get_arabic_font(fonts):

    preferred = [

        "NotoNaskhArabic-Regular.ttf",
        "NotoNaskhArabic-Medium.ttf",

        "NotoSansArabic-Medium.ttf",
        "NotoSansArabic-Regular.ttf",

        "NotoSansArabicUI-Medium.ttf",
        "NotoSansArabicUI-Regular.ttf",

        "NotoKufiArabic-Regular.ttf",

        "DejaVuSans.ttf",
        "FreeSans.ttf"

    ]

    result = find_font_by_keywords(
        fonts,
        preferred
    )

    if result:
        return result

    if fonts:
        return fonts[0]

    return None


# =========================================================
# ✨ Math
# =========================================================

def get_math_font(fonts):

    preferred = [

        "NotoSansMath-Regular.ttf",
        "NotoSans-Regular.ttf",
        "NotoSansDisplay-Regular.ttf",
        "DejaVuSans.ttf"

    ]

    result = find_font_by_keywords(
        fonts,
        preferred
    )

    if result:
        return result

    return get_latin_font(fonts)


# =========================================================
# 🔣 Symbols
# =========================================================

def get_symbol_font(fonts):

    preferred = [

        "NotoSansSymbols2-Regular.ttf",
        "NotoSansSymbols-Regular.ttf",
        "DejaVuSans.ttf",
        "FreeSans.ttf"

    ]

    result = find_font_by_keywords(
        fonts,
        preferred
    )

    if result:
        return result

    return get_latin_font(fonts)


# =========================================================
# 😀 Emoji
# =========================================================

def get_emoji_font(fonts):

    result = find_font_by_keywords(
        fonts,
        [
            "NotoColorEmoji.ttf"
        ]
    )

    if result:
        return result

    return get_symbol_font(fonts)


# =========================================================
# 🌍 لغات خاصة
# =========================================================

def get_special_language_font(
    char,
    fonts
):

    try:

        unicode_name = unicodedata.name(
            char,
            ""
        )

    except Exception:

        unicode_name = ""

    language_map = {

        "HEBREW": [
            "NotoSansHebrew"
        ],

        "THAI": [
            "NotoSansThai"
        ],

        "DEVANAGARI": [
            "NotoSansDevanagari"
        ],

        "BENGALI": [
            "NotoSansBengali"
        ],

        "TAMIL": [
            "NotoSansTamil"
        ],

        "TELUGU": [
            "NotoSansTelugu"
        ],

        "KANNADA": [
            "NotoSansKannada"
        ],

        "MALAYALAM": [
            "NotoSansMalayalam"
        ],

        "GUJARATI": [
            "NotoSansGujarati"
        ],

        "GURMUKHI": [
            "NotoSansGurmukhi"
        ]

    }

    for language, keywords in language_map.items():

        if language in unicode_name:

            result = find_font_by_keywords(
                fonts,
                keywords
            )

            if result:
                return result

    return None


# =========================================================
# 🔤 اختيار الخط للحرف
# =========================================================

def find_font_for_char(
    char,
    fonts,
    previous_font=None
):

    if is_combining_char(char):

        if previous_font:
            return previous_font

        if is_arabic_char(char):
            return get_arabic_font(fonts)

        return get_latin_font(fonts)

    if is_arabic_char(char):
        return get_arabic_font(fonts)

    if is_math_decorated_char(char):
        return get_math_font(fonts)

    if is_decorated_latin(char):
        return get_math_font(fonts)

    if is_latin_char(char):
        return get_latin_font(fonts)

    if is_number_char(char):
        return get_latin_font(fonts)

    if is_emoji_char(char):
        return get_emoji_font(fonts)

    if is_symbol_char(char):
        return get_symbol_font(fonts)

    special = get_special_language_font(
        char,
        fonts
    )

    if special:
        return special

    if ord(char) < 128:
        return get_latin_font(fonts)

    generic = find_font_by_keywords(
        fonts,
        [
            "NotoSans-Regular.ttf",
            "NotoSans-Medium.ttf",
            "Roboto-Medium.ttf",
            "Roboto-Regular.ttf",
            "DejaVuSans.ttf",
            "FreeSans.ttf"
        ]
    )

    if generic:
        return generic

    if fonts:
        return fonts[0]

    return None


# =========================================================
# 📝 معالجة العربية
# =========================================================

def prepare_text_for_display(text):

    if not contains_arabic(text):
        return text

    if (
        arabic_reshaper is None
        or
        bidi_get_display is None
    ):

        return text

    try:

        reshaped = arabic_reshaper.reshape(
            text
        )

        visual = bidi_get_display(
            reshaped,
            base_dir="R"
        )

        return visual

    except Exception:

        return text


# =========================================================
# 📏 قياس النص
# =========================================================

def measure_segment(
    draw,
    text,
    font
):

    try:

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font,
            anchor="ls"
        )

        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        return (
            bbox,
            width,
            height
        )

    except Exception:

        try:

            bbox = draw.textbbox(
                (0, 0),
                text,
                font=font
            )

            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]

            return (
                bbox,
                width,
                height
            )

        except Exception:

            return (
                (0, 0, 0, 0),
                0,
                0
            )


# =========================================================
# 🧩 إنشاء أجزاء الاسم
# =========================================================

def build_segments(
    draw,
    render_text,
    fonts
):

    segments = []

    current_text = ""
    current_font = None
    current_path = None

    previous_font = None

    for char in render_text:

        font_data = find_font_for_char(
            char,
            fonts,
            previous_font
        )

        if font_data is None:

            continue

        path, font = font_data

        previous_font = font_data

        if (
            current_font is not None
            and
            current_path == path
        ):

            current_text += char

        else:

            if current_text:

                segments.append(
                    (
                        current_text,
                        current_font,
                        current_path
                    )
                )

            current_text = char
            current_font = font
            current_path = path

    if current_text:

        segments.append(
            (
                current_text,
                current_font,
                current_path
            )
        )

    measured = []

    total_width = 0

    for (
        segment_text,
        font,
        path
    ) in segments:

        (
            bbox,
            segment_width,
            segment_height
        ) = measure_segment(
            draw,
            segment_text,
            font
        )

        total_width += segment_width

        measured.append(
            (
                segment_text,
                font,
                path,
                bbox,
                segment_width,
                segment_height
            )
        )

    return measured, total_width


# =========================================================
# ✍️ رسم الاسم على الشهادة
# =========================================================

def draw_certificate_name(
    image,
    original_name,
    color,
    template_key
):

    if template_key not in TEMPLATES:

        raise ValueError(
            f"النموذج غير موجود: {template_key}"
        )

    config = TEMPLATES[
        template_key
    ]

    original_text = preserve_name(
        original_name
    ).strip()

    if not original_text:

        raise ValueError(
            "الاسم فارغ."
        )

    draw = ImageDraw.Draw(
        image
    )

    width = image.width
    height = image.height

    center_x = int(
        width *
        float(config["name_x"])
    )

    baseline_y = int(
        height *
        float(config["name_y"])
    )

    render_text = prepare_text_for_display(
        original_text
    )

    current_font_ratio = float(
        config["font_ratio"]
    )

    max_width = int(
        width *
        float(config["max_width_ratio"])
    )

    fonts = get_available_fonts(
        width,
        current_font_ratio
    )

    if not fonts:

        raise RuntimeError(
            "لم يتم العثور على خط صالح."
        )

    measured_segments, total_width = build_segments(
        draw,
        render_text,
        fonts
    )

    if not measured_segments:

        raise RuntimeError(
            f"تعذر تجهيز الاسم للرسم: {original_text}"
        )

    attempts = 0

    while (
        total_width > max_width
        and
        current_font_ratio > 0.025
        and
        attempts < 20
    ):

        current_font_ratio -= 0.0025

        fonts = get_available_fonts(
            width,
            current_font_ratio
        )

        measured_segments, total_width = build_segments(
            draw,
            render_text,
            fonts
        )

        attempts += 1

    start_x = (
        center_x -
        (total_width / 2)
    )

    current_x = start_x

    for (
        segment_text,
        font,
        path,
        bbox,
        segment_width,
        segment_height
    ) in measured_segments:

        if not segment_text:
            continue

        try:

            draw.text(

                (
                    current_x,
                    baseline_y
                ),

                segment_text,

                font=font,

                fill=color,

                anchor="ls",

                stroke_width=STROKE_WIDTH,

                stroke_fill=color

            )

        except Exception as error:

            raise RuntimeError(

                "فشل رسم الاسم على الشهادة.\n"
                f"النموذج: {template_key}\n"
                f"الاسم: {original_text}\n"
                f"الخط: {path}\n"
                f"الخطأ: {error}"

            ) from error

        current_x += segment_width

    if total_width <= 0:

        raise RuntimeError(
            f"عرض الاسم أصبح صفراً: {original_text}"
        )

    print(
        "\n"
        "========================================\n"
        "✍️ تم رسم الاسم\n"
        f"📄 النموذج: {template_key}\n"
        f"👤 الاسم: {original_text}\n"
        f"📍 X: {center_x}\n"
        f"📍 Y: {baseline_y}\n"
        f"📏 العرض: {total_width}\n"
        f"🔤 Font Ratio: {current_font_ratio}\n"
        f"✍️ Stroke Width: {STROKE_WIDTH}\n"
        "========================================\n"
    )

    return True


# =========================================================
# 📄 تحميل نموذج ثابت
# =========================================================

def load_template(template_key):

    if template_key not in TEMPLATES:

        raise ValueError(
            "نموذج غير معروف."
        )

    if template_key in TEMPLATE_CACHE:

        return TEMPLATE_CACHE[
            template_key
        ]

    path = TEMPLATES[
        template_key
    ]["path"]

    if not os.path.exists(path):

        raise FileNotFoundError(
            f"لم يتم العثور على ملف النموذج:\n{path}"
        )

    with open(
        path,
        "rb"
    ) as file:

        data = file.read()

    image = Image.open(
        io.BytesIO(data)
    )

    image.load()

    TEMPLATE_CACHE[
        template_key
    ] = data

    return data


# =========================================================
# 🖼️ إنشاء شهادة
# =========================================================

def create_certificate(
    template_key,
    name,
    color_key
):

    if template_key not in TEMPLATES:

        raise ValueError(
            f"النموذج غير موجود: {template_key}"
        )

    template_bytes = load_template(
        template_key
    )

    image = Image.open(
        io.BytesIO(
            template_bytes
        )
    )

    image.load()

    if image.mode not in (
        "RGB",
        "RGBA"
    ):

        image = image.convert(
            "RGBA"
        )

    else:

        image = image.copy()

    if color_key in COLORS:

        color = COLORS[
            color_key
        ]["rgb"]

    else:

        color = COLORS[
            DEFAULT_COLOR
        ]["rgb"]

    result = draw_certificate_name(

        image=image,

        original_name=name,

        color=color,

        template_key=template_key

    )

    if result is not True:

        raise RuntimeError(
            "لم يتم تأكيد رسم الاسم."
        )

    output = io.BytesIO()

    image.save(
        output,
        format="PNG"
    )

    output.seek(0)

    return output


# =========================================================
# ⚙️ إنشاء الشهادات
# =========================================================

async def generate_certificates(
    template_key,
    names,
    color_key
):

    certificates = []

    total = len(names)

    for index, name in enumerate(
        names,
        1
    ):

        try:

            certificate = await asyncio.to_thread(

                create_certificate,

                template_key,

                name,

                color_key

            )

            certificates.append(
                (
                    certificate,
                    name
                )
            )

            print(
                f"✅ تم إنشاء الشهادة "
                f"{index}/{total}: {name}"
            )

        except Exception as error:

            print(
                "\n"
                "========================================\n"
                "❌ فشل إنشاء شهادة\n"
                f"📄 النموذج: {template_key}\n"
                f"👤 الاسم: {name}\n"
                f"❌ الخطأ: {error}\n"
                "========================================\n"
            )

            raise RuntimeError(

                f"فشل إنشاء شهادة الاسم:\n"
                f"{name}\n\n"
                f"النموذج:\n"
                f"{TEMPLATES[template_key]['name']}\n\n"
                f"التفاصيل:\n"
                f"{error}"

            ) from error

    return certificates


# =========================================================
# 📄 أزرار النماذج
# =========================================================

def template_buttons():

    return [

        [
            Button.inline(
                "🏆 نموذج الأكاديمية الأساسي",
                b"template_academy"
            )
        ],

        [
            Button.inline(
                "🎖️ نموذج الكتيبة الأساسي",
                b"template_katiba"
            )
        ],

        [
            Button.inline(
                "❌ إلغاء",
                b"cancel_operation"
            )
        ]

    ]


# =========================================================
# 🎨 أزرار الألوان
# =========================================================

def color_buttons():

    return [

        [
            Button.inline(
                "⚫ أسود",
                b"color_black"
            ),

            Button.inline(
                "⚪ أبيض",
                b"color_white"
            )
        ],

        [
            Button.inline(
                "🟡 ذهبي",
                b"color_gold"
            ),

            Button.inline(
                "🔵 أزرق",
                b"color_blue"
            )
        ],

        [
            Button.inline(
                "🔴 أحمر",
                b"color_red"
            ),

            Button.inline(
                "🟢 أخضر",
                b"color_green"
            )
        ],

        [
            Button.inline(
                "❌ إلغاء",
                b"cancel_operation"
            )
        ]

    ]


# =========================================================
# 📄 اختيار النموذج
# =========================================================

@client.on(
    events.CallbackQuery(
        pattern=b"template_"
    )
)
async def template_handler(event):

    chat_id = event.chat_id

    if chat_id not in users:

        await event.answer(
            "استخدم /start أولاً",
            alert=True
        )

        return

    data = event.data.decode(
        "utf-8"
    )

    template_key = data.replace(
        "template_",
        ""
    )

    if template_key not in TEMPLATES:

        await event.answer(
            "نموذج غير معروف",
            alert=True
        )

        return

    user = users[
        chat_id
    ]

    if user.get(
        "state"
    ) != "waiting_template_choice":

        await event.answer(
            "لا يوجد اختيار نموذج حالياً.",
            alert=True
        )

        return

    try:

        load_template(
            template_key
        )

    except Exception as error:

        await event.answer(
            "ملف النموذج غير موجود على السيرفر.",
            alert=True
        )

        print(
            f"❌ خطأ تحميل النموذج: {error}"
        )

        return

    user[
        "template"
    ] = template_key

    user[
        "state"
    ] = "waiting_color"

    print(
        f"📄 المستخدم {chat_id} اختار النموذج: "
        f"{template_key}"
    )

    await event.edit(

        f"✅ تم اختيار:\n"
        f"{TEMPLATES[template_key]['name']}\n\n"

        "🎨 هسه اختار لون الاسم:",

        buttons=color_buttons()

    )

    await event.answer(
        "✅ تم اختيار النموذج"
    )


# =========================================================
# 🎨 اختيار اللون
# =========================================================

@client.on(
    events.CallbackQuery(
        pattern=b"color_"
    )
)
async def color_handler(event):

    chat_id = event.chat_id

    if chat_id not in users:

        await event.answer(
            "استخدم /start أولاً",
            alert=True
        )

        return

    data = event.data.decode(
        "utf-8"
    )

    color_key = data.replace(
        "color_",
        ""
    )

    if color_key not in COLORS:

        await event.answer(
            "لون غير معروف",
            alert=True
        )

        return

    user = users[
        chat_id
    ]

    if user.get(
        "state"
    ) != "waiting_color":

        await event.answer(
            "لا يوجد اختيار لون حالياً.",
            alert=True
        )

        return

    user[
        "color"
    ] = color_key

    user[
        "state"
    ] = "waiting_names"

    template_key = user.get(
        "template"
    )

    await event.edit(

        f"🎨 تم اختيار اللون:"
        f" {COLORS[color_key]['name']}\n\n"

        f"📄 النموذج:"
        f" {TEMPLATES[template_key]['name']}\n\n"

        "✍️ هسه أرسل أسماء الأشخاص.\n\n"

        "كل اسم بسطر منفصل."

    )

    await event.answer(
        "✅ تم اختيار اللون"
    )


# =========================================================
# ❌ إلغاء العملية
# =========================================================

@client.on(
    events.CallbackQuery(
        pattern=b"cancel_operation"
    )
)
async def cancel_button_handler(event):

    chat_id = event.chat_id

    users.pop(
        chat_id,
        None
    )

    await event.edit(

        "❌ تم إلغاء العملية.\n\n"
        "استخدم /start للبدء من جديد."

    )

    await event.answer(
        "تم الإلغاء"
    )


# =========================================================
# 🚀 /start
# =========================================================

@client.on(
    events.NewMessage(
        pattern=r"^/start$"
    )
)
async def start_handler(event):

    chat_id = event.chat_id

    users[
        chat_id
    ] = {

        "state":
            "waiting_template_choice",

        "template":
            None,

        "color":
            DEFAULT_COLOR

    }

    await event.respond(

        "🎓 أهلاً بك في بوت الشهادات التقديرية!\n\n"

        "📄 اختار نموذج الشهادة الذي تريد استخدامه:\n\n"

        "🏆 نموذج الأكاديمية الأساسي\n"
        "🎖️ نموذج الكتيبة الأساسي\n\n"

        "بعد اختيار النموذج راح تختار لون الاسم "
        "وبعدين ترسل الأسماء.",

        buttons=template_buttons()

    )


# =========================================================
# ❌ /cancel
# =========================================================

@client.on(
    events.NewMessage(
        pattern=r"^/cancel$"
    )
)
async def cancel_handler(event):

    users.pop(
        event.chat_id,
        None
    )

    await event.respond(

        "❌ تم إلغاء العملية.\n\n"
        "استخدم /start للبدء من جديد."

    )


# =========================================================
# 💬 استقبال الرسائل
# =========================================================

@client.on(
    events.NewMessage()
)
async def message_handler(event):

    text = event.raw_text or ""

    command_check = text.strip()

    if command_check in (
        "/start",
        "/cancel"
    ):

        return

    chat_id = event.chat_id

    if chat_id not in users:

        await event.respond(
            "🎓 استخدم /start للبدء."
        )

        return

    user = users[
        chat_id
    ]

    state = user[
        "state"
    ]

    if state == "processing":

        await event.respond(

            "⏳ بعدني أجهز الشهادات، "
            "انتظر شوي."

        )

        return

    if state == "waiting_template_choice":

        await event.respond(

            "📄 اختار أحد النموذجين من الأزرار أعلاه."

        )

        return

    if state == "waiting_color":

        await event.respond(

            "🎨 اختار لون الاسم من الأزرار."

        )

        return

    if state == "waiting_names":

        names = []

        for line in text.splitlines():

            if line.endswith("\r"):

                line = line[:-1]

            if line != "":

                names.append(
                    line
                )

        if not names:

            await event.respond(
                "❌ ماكو أسماء صالحة."
            )

            return

        template_key = user.get(
            "template"
        )

        color_key = user.get(
            "color",
            DEFAULT_COLOR
        )

        if template_key not in TEMPLATES:

            await event.respond(

                "❌ النموذج غير محدد.\n"
                "استخدم /start من جديد."

            )

            return

        user[
            "state"
        ] = "processing"

        total = len(
            names
        )

        await event.respond(

            f"⚙️ جاري إنشاء {total} شهادة...\n\n"

            f"📄 النموذج:\n"
            f"{TEMPLATES[template_key]['name']}\n\n"

            f"🎨 اللون:\n"
            f"{COLORS[color_key]['name']}\n\n"

            "⏳ انتظر..."

        )

        try:

            certificates = await generate_certificates(

                template_key,

                names,

                color_key

            )

        except Exception as error:

            user[
                "state"
            ] = "waiting_names"

            await event.respond(

                "❌ حدث خطأ أثناء إنشاء الشهادات.\n\n"

                f"📄 النموذج:\n"
                f"{TEMPLATES[template_key]['name']}\n\n"

                "👤 لم يتم إرسال الشهادات "
                "حتى لا تحصل على صور ناقصة.\n\n"

                f"🔧 التفاصيل:\n"
                f"{error}"

            )

            return

        if len(certificates) != total:

            user[
                "state"
            ] = "waiting_names"

            await event.respond(

                "❌ لم يتم إنشاء جميع الشهادات.\n"
                "تم إيقاف الإرسال."

            )

            return

        total_batches = (

            total +
            BATCH_SIZE -
            1

        ) // BATCH_SIZE

        for start in range(
            0,
            total,
            BATCH_SIZE
        ):

            batch = certificates[
                start:
                start + BATCH_SIZE
            ]

            batch_number = (

                start //
                BATCH_SIZE

            ) + 1

            await event.respond(

                f"📤 إرسال الدفعة "
                f"{batch_number}/{total_batches}..."

            )

            media = []

            try:

                for certificate, name in batch:

                    certificate.seek(
                        0
                    )

                    uploaded_file = (

                        await client.upload_file(

                            certificate,

                            file_name="certificate.png"

                        )

                    )

                    photo = InputMediaUploadedPhoto(
                        file=uploaded_file
                    )

                    media.append(
                        photo
                    )

                await client.send_file(

                    chat_id,

                    media,

                    force_document=False

                )

            except Exception as error:

                user[
                    "state"
                ] = "waiting_names"

                print(
                    f"❌ خطأ إرسال الصور: {error}"
                )

                await event.respond(

                    "❌ حدث خطأ أثناء إرسال الصور.\n\n"
                    f"🔧 التفاصيل:\n{error}"

                )

                return

            if (
                start + BATCH_SIZE
                < total
            ):

                await asyncio.sleep(
                    2
                )

        user[
            "state"
        ] = "waiting_names"

        await event.respond(

            f"🎉 تم إرسال {total} شهادة "
            "بنجاح كصور! 🖼️\n\n"

            f"📄 النموذج المستخدم:\n"
            f"{TEMPLATES[template_key]['name']}\n\n"

            "يمكنك إرسال أسماء جديدة مباشرة."

        )

        return


# =========================================================
# 🚀 تشغيل البوت
# =========================================================

async def main():

    print(
        "\n"
        "========================================\n"
        "🚀 بدء تشغيل بوت الشهادات\n"
        "========================================\n"
    )

    # تجهيز الخطوط قبل تشغيل البوت
    prepare_fonts()

    load_arabic_libraries()

    print(
        "📡 جاري الاتصال بتليجرام..."
    )

    await client.start(
        bot_token=BOT_TOKEN
    )

    print(
        "✅ البوت يعمل الآن\n"
    )

    await client.run_until_disconnected()


# =========================================================
# ▶️ تشغيل
# =========================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "\n🛑 تم إيقاف البوت."
        )

    except Exception as error:

        print(
            "\n"
            "========================================\n"
            "❌ حدث خطأ رئيسي\n"
            f"{error}\n"
            "========================================\n"
        )