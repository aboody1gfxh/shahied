import io
import asyncio
import sys
import subprocess
import unicodedata
import os

from PIL import Image, ImageDraw, ImageFont

from telethon import TelegramClient, events, Button
from telethon.tl.types import InputMediaUploadedPhoto


# =========================================================
# 🔐 معلومات الاتصال — أبقِ معلوماتك الحالية كما هي
# =========================================================

API_ID = 32361464
API_HASH = "efa6fd8d917173938f503ec3659122cd"
BOT_TOKEN = "8877046448:AAELBYOfn-XVEUffWjog3Csee2_TrbfyGfc"
SESSION_NAME = "certificate_bot"


# =========================================================
# ⚙️ إعدادات الشهادات
# =========================================================

BATCH_SIZE = 10

NAME_X = 0.50

# 🔹 الاسم أعلى شوية
NAME_Y = 0.465

# 🔹 الاسم أصغر شوية
FONT_SIZE_RATIO = 0.060

MIN_FONT_SIZE = 20


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

users = {}


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
# 🗂️ خطوط الجهاز
# =========================================================

FONT_PATHS = [

    # =====================================================
    # 🇸🇦 Arabic
    # =====================================================

    "/system/fonts/NotoNaskhArabic-Medium.ttf",
    "/system/fonts/NotoNaskhArabic-Regular.ttf",

    "/system/fonts/NotoSansArabic-Medium.ttf",
    "/system/fonts/NotoSansArabic-Regular.ttf",

    "/system/fonts/NotoSansArabicUI-Medium.ttf",
    "/system/fonts/NotoSansArabicUI-Regular.ttf",

    "/system/fonts/NotoKufiArabic-Regular.ttf",
    "/system/fonts/NotoSansArabic-UI-Regular.ttf",

    # احتياط
    "/system/fonts/NotoNaskhArabic-Bold.ttf",
    "/system/fonts/NotoSansArabic-Bold.ttf",
    "/system/fonts/NotoSansArabicUI-Bold.ttf",
    "/system/fonts/NotoKufiArabic-Bold.ttf",

    # =====================================================
    # ✨ Mathematical
    # =====================================================

    "/system/fonts/NotoSansMath-Regular.ttf",
    "/system/fonts/NotoSansMath-Bold.ttf",

    # =====================================================
    # 🇬🇧 Latin
    # =====================================================

    "/system/fonts/NotoSans-Medium.ttf",
    "/system/fonts/NotoSans-Regular.ttf",

    "/system/fonts/NotoSansDisplay-Medium.ttf",
    "/system/fonts/NotoSansDisplay-Regular.ttf",

    "/system/fonts/Roboto-Medium.ttf",
    "/system/fonts/Roboto-Regular.ttf",

    # =====================================================
    # 🔣 Symbols
    # =====================================================

    "/system/fonts/NotoSansSymbols-Regular.ttf",
    "/system/fonts/NotoSansSymbols2-Regular.ttf",
    "/system/fonts/NotoSansSymbols-Bold.ttf",

    # =====================================================
    # 😀 Emoji
    # =====================================================

    "/system/fonts/NotoColorEmoji.ttf",

    # =====================================================
    # 🌍 لغات أخرى
    # =====================================================

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

    # =====================================================
    # 🐧 Linux / Pydroid
    # =====================================================

    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",

    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",

    # =====================================================
    # 🪟 Generic
    # =====================================================

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

        return ImageFont.truetype(
            path,
            size
        )

    except Exception:

        return None


# =========================================================
# 🔤 تحميل الخطوط
# =========================================================

def get_available_fonts(image_width):

    font_size = max(
        MIN_FONT_SIZE,
        int(
            image_width *
            FONT_SIZE_RATIO
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
        f"🔤 عدد الخطوط المتوفرة: {len(fonts)}"
    )

    for path, font in fonts:

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
# 🇬🇧 Latin — Medium أولاً
# =========================================================

def get_latin_font(fonts):

    preferred = [

        "NotoSans-Medium.ttf",
        "NotoSansDisplay-Medium.ttf",
        "Roboto-Medium.ttf",

        "NotoSans-Regular.ttf",
        "NotoSansDisplay-Regular.ttf",
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
# 🇸🇦 Arabic — Medium أولاً
# =========================================================

def get_arabic_font(fonts):

    preferred = [

        "NotoNaskhArabic-Medium.ttf",
        "NotoSansArabic-Medium.ttf",
        "NotoSansArabicUI-Medium.ttf",

        "NotoNaskhArabic-Regular.ttf",
        "NotoSansArabic-Regular.ttf",
        "NotoSansArabicUI-Regular.ttf",

        "NotoKufiArabic-Regular.ttf",
        "NotoSansArabic-UI-Regular.ttf"

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

    return get_latin_font(
        fonts
    )


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

    return get_latin_font(
        fonts
    )


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

    return get_symbol_font(
        fonts
    )


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

            return get_arabic_font(
                fonts
            )

        return get_latin_font(
            fonts
        )

    if is_arabic_char(char):

        return get_arabic_font(
            fonts
        )

    if is_math_decorated_char(char):

        return get_math_font(
            fonts
        )

    if is_decorated_latin(char):

        return get_math_font(
            fonts
        )

    if is_latin_char(char):

        return get_latin_font(
            fonts
        )

    if is_number_char(char):

        return get_latin_font(
            fonts
        )

    if is_emoji_char(char):

        return get_emoji_font(
            fonts
        )

    if is_symbol_char(char):

        return get_symbol_font(
            fonts
        )

    special = get_special_language_font(
        char,
        fonts
    )

    if special:

        return special

    if ord(char) < 128:

        return get_latin_font(
            fonts
        )

    generic = find_font_by_keywords(

        fonts,

        [
            "NotoSans-Medium.ttf",
            "NotoSans-Regular.ttf",
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

        print(
            "⚠️ مكتبات RTL غير متوفرة."
        )

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

    except Exception as e:

        print(
            "❌ خطأ أثناء معالجة العربية:"
        )

        print(e)

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

        width = (
            bbox[2] -
            bbox[0]
        )

        height = (
            bbox[3] -
            bbox[1]
        )

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

            width = (
                bbox[2] -
                bbox[0]
            )

            height = (
                bbox[3] -
                bbox[1]
            )

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
# ✍️ رسم الاسم
# =========================================================

def draw_certificate_name(
    image,
    original_name,
    color,
    fonts
):

    draw = ImageDraw.Draw(
        image
    )

    width = image.width
    height = image.height

    original_text = preserve_name(
        original_name
    )

    if not original_text:

        print(
            "⚠️ الاسم فارغ."
        )

        return

    render_text = prepare_text_for_display(
        original_text
    )

    print(
        "----------------------------------------"
    )

    print(
        f"📝 الاسم الأصلي:"
        f" {repr(original_text)}"
    )

    print(
        f"🔄 النص للرسم:"
        f" {repr(render_text)}"
    )

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

            print(
                f"⚠️ لا يوجد خط للحرف:"
                f" {repr(char)}"
            )

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

    if not segments:

        print(
            "❌ لم يتم إنشاء أي جزء للنص."
        )

        return

    # =====================================================
    # 📏 قياس
    # =====================================================

    measured_segments = []

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

        measured_segments.append(
            (
                segment_text,
                font,
                path,
                bbox,
                segment_width,
                segment_height
            )
        )

    # =====================================================
    # 📍 مكان الاسم
    # =====================================================

    center_x = int(
        width *
        NAME_X
    )

    baseline_y = int(
        height *
        NAME_Y
    )

    start_x = (
        center_x -
        total_width / 2
    )

    current_x = start_x

    # =====================================================
    # ✍️ الرسم
    # =====================================================

    for (
        segment_text,
        font,
        path,
        bbox,
        segment_width,
        segment_height
    ) in measured_segments:

        try:

            draw.text(

                (
                    current_x -
                    bbox[0],

                    baseline_y
                ),

                segment_text,

                font=font,

                fill=color,

                anchor="ls"

            )

            print(
                f"   🔤 {repr(segment_text)}"
                f" → {path}"
            )

        except Exception as e:

            print(
                "⚠️ خطأ رسم جزء:"
            )

            print(
                type(e).__name__,
                e
            )

        current_x += segment_width

    print(
        "✅ تم رسم الاسم"
    )

    print(
        "----------------------------------------"
    )


# =========================================================
# 🖼️ إنشاء شهادة
# =========================================================

def create_certificate(
    template_bytes,
    name,
    color_key
):

    # =====================================================
    # 📄 استخدام نموذج المستخدم فقط
    # =====================================================

    image = Image.open(
        io.BytesIO(
            template_bytes
        )
    )

    image.load()

    print(
        f"📐 نموذج المستخدم:"
        f" {image.width} × {image.height}"
    )

    # =====================================================
    # لا يوجد نموذج ثابت
    # لا يوجد حذف للاسم
    # لا يوجد مسح للخلفية
    # =====================================================

    if image.mode not in (
        "RGB",
        "RGBA"
    ):

        image = image.convert(
            "RGBA"
        )

    else:

        image = image.copy()

    # =====================================================
    # 🔤 الخطوط
    # =====================================================

    fonts = get_available_fonts(
        image.width
    )

    if not fonts:

        raise RuntimeError(
            "لم يتم العثور على أي خط صالح."
        )

    # =====================================================
    # 🎨 اللون
    # =====================================================

    if color_key in COLORS:

        color = COLORS[
            color_key
        ]["rgb"]

    else:

        color = COLORS[
            DEFAULT_COLOR
        ]["rgb"]

    # =====================================================
    # ✍️ كتابة الاسم
    # =====================================================

    draw_certificate_name(

        image,

        name,

        color,

        fonts

    )

    # =====================================================
    # 💾 حفظ
    # =====================================================

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
    template_bytes,
    names,
    color_key
):

    certificates = []

    total = len(
        names
    )

    print(
        "========================================"
    )

    print(
        f"⚙️ إنشاء {total} شهادة"
    )

    print(
        "📄 المصدر: نموذج المستخدم"
    )

    print(
        f"🎨 اللون:"
        f" {COLORS[color_key]['name']}"
    )

    print(
        "========================================"
    )

    for index, name in enumerate(
        names,
        1
    ):

        try:

            certificate = await asyncio.to_thread(

                create_certificate,

                template_bytes,

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
                f"✅ {index}/{total}:"
                f" {repr(name)}"
            )

        except Exception as e:

            print(
                f"❌ فشل إنشاء شهادة:"
                f" {repr(name)}"
            )

            print(
                type(e).__name__,
                e
            )

    return certificates


# =========================================================
# 📥 تحميل نموذج المستخدم
# =========================================================

async def download_template(event):

    try:

        print(
            "📥 جاري تحميل نموذج المستخدم..."
        )

        data = await event.download_media(
            file=bytes
        )

        if not data:

            return None

        image = Image.open(
            io.BytesIO(data)
        )

        image.load()

        print(
            "========================================"
        )

        print(
            "✅ تم تحميل نموذج المستخدم"
        )

        print(
            f"📐 الأبعاد:"
            f" {image.width} × {image.height}"
        )

        print(
            f"🖼️ النوع:"
            f" {image.format}"
        )

        print(
            "📄 سيتم استخدام هذا النموذج فقط."
        )

        print(
            "========================================"
        )

        return data

    except Exception as e:

        print(
            "❌ خطأ تحميل النموذج:"
        )

        print(
            type(e).__name__,
            e
        )

        return None


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

    await event.edit(

        f"🎨 تم اختيار اللون:"
        f" {COLORS[color_key]['name']}\n\n"

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
            "waiting_template",

        "template":
            None,

        "color":
            DEFAULT_COLOR

    }

    await event.respond(

        "🎓 أهلاً بك في بوت الشهادات التقديرية!\n\n"

        "📄 أرسل نموذج الشهادة أولاً.\n\n"

        "النموذج الذي ترسله هنا هو الذي سأستخدمه "
        "لإنشاء الشهادات.\n\n"

        "يفضل إرساله كـ Document للحفاظ على الجودة."

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

        users[
            chat_id
        ] = {

            "state":
                "waiting_template",

            "template":
                None,

            "color":
                DEFAULT_COLOR

        }

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

    # =====================================================
    # 📄 انتظار النموذج
    # =====================================================

    if state == "waiting_template":

        if not event.media:

            await event.respond(
                "📄 أرسل نموذج الشهادة كصورة أو Document."
            )

            return

        template_bytes = await download_template(
            event
        )

        if not template_bytes:

            await event.respond(
                "❌ ما گدرت أقرأ النموذج."
            )

            return

        user[
            "template"
        ] = template_bytes

        user[
            "state"
        ] = "waiting_color"

        await event.respond(

            "✅ تم استلام نموذجك.\n\n"

            "📄 هذا النموذج هو المصدر الوحيد "
            "الذي راح أستخدمه.\n\n"

            "🎨 اختار لون الاسم:",

            buttons=color_buttons()

        )

        return

    # =====================================================
    # 🎨 انتظار اللون
    # =====================================================

    if state == "waiting_color":

        await event.respond(
            "🎨 اختار لون الاسم من الأزرار."
        )

        return

    # =====================================================
    # ✍️ انتظار الأسماء
    # =====================================================

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

        user[
            "state"
        ] = "processing"

        template_bytes = user[
            "template"
        ]

        color_key = user.get(
            "color",
            DEFAULT_COLOR
        )

        total = len(
            names
        )

        await event.respond(

            f"⚙️ جاري إنشاء {total} شهادة...\n\n"

            "📄 باستخدام نموذجك المرسل.\n"

            f"🎨 اللون:"
            f" {COLORS[color_key]['name']}\n\n"

            "⏳ انتظر..."

        )

        certificates = await generate_certificates(

            template_bytes,

            names,

            color_key

        )

        if len(certificates) != total:

            user[
                "state"
            ] = "waiting_names"

            await event.respond(

                "❌ حدث خطأ أثناء إنشاء "
                "بعض الشهادات."

            )

            return

        # =================================================
        # 📦 الدفعات
        # =================================================

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

                print(

                    f"✅ تم إرسال الدفعة "
                    f"{batch_number}/"
                    f"{total_batches} كصور"

                )

            except Exception as e:

                print(
                    "❌ خطأ أثناء إرسال الصور:"
                )

                print(
                    type(e).__name__,
                    e
                )

                user[
                    "state"
                ] = "waiting_names"

                await event.respond(

                    "❌ حدث خطأ أثناء إرسال الصور."

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

            "يمكنك إرسال أسماء جديدة مباشرة."

        )

        return


# =========================================================
# 🚀 تشغيل البوت
# =========================================================

async def main():

    print(
        "========================================"
    )

    print(
        "🚀 بدء تشغيل بوت الشهادات"
    )

    print(
        "========================================"
    )

    print(
        "📡 نظام الاتصال: Telethon"
    )

    print(
        "🤖 النظام: Telegram MTProto"
    )

    print(
        "========================================"
    )

    load_arabic_libraries()

    print(
        "========================================"
    )

    print(
        "🌍 نظام اللغات جاهز"
    )

    print(
        "🇮🇶 العربية: RTL"
    )

    print(
        "🇬🇧 الإنجليزية: LTR"
    )

    print(
        "✨ English Fancy Unicode: مدعوم"
    )

    print(
        "✨ Arabic Unicode: مدعوم"
    )

    print(
        "🔢 الأرقام: مدعومة"
    )

    print(
        "🔣 الرموز: مدعومة"
    )

    print(
        "😀 Emoji: مدعومة حسب الخط"
    )

    print(
        "📄 النموذج: يعتمد على نموذج المستخدم"
    )

    print(
        "========================================"
    )

    await client.start(
        bot_token=BOT_TOKEN
    )

    me = await client.get_me()

    print(
        "========================================"
    )

    print(
        "✅ تم الاتصال بـ Telegram بنجاح!"
    )

    print(
        f"🤖 اسم البوت: {me.first_name}"
    )

    print(
        f"🔗 Username: @{me.username}"
    )

    print(
        "========================================"
    )

    print(
        "🟢 البوت جاهز لاستقبال الطلبات."
    )

    print(
        "========================================"
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
            "\n🛑 تم إيقاف البوت بأمان."
        )

    except Exception as e:

        print(
            "\n❌ خطأ رئيسي:"
        )

        print(
            type(e).__name__,
            e
)
