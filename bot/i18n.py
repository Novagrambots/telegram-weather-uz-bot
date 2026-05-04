"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="ru", name="Иван")
"""

from bot.emojis import E

TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['search']} Я покажу тебе прогноз погоды для любого города.\n\n"
            f"{E['pin']} <b>Как пользоваться:</b>\n"
            "Отправь название города или свою геолокацию — "
            f"и я покажу актуальную погоду! {E['plane']}\n\n"
            "Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['search']} Istalgan shahar uchun ob-havo ma'lumotini ko'rsataman.\n\n"
            f"{E['pin']} <b>Qanday foydalanish:</b>\n"
            "Shahar nomini yoki geolokatsiyangizni yuboring — "
            f"men sizga hozirgi ob-havoni ko'rsataman! {E['plane']}\n\n"
            "Quyidagi tugmalardan birini tanlang:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['search']} I'll show you weather forecasts for any city.\n\n"
            f"{E['pin']} <b>How to use:</b>\n"
            "Send a city name or your location — "
            f"and I'll show you the current weather! {E['plane']}\n\n"
            "Choose an action below:"
        ),
    },

    # === Кнопки главного меню ===
    "btn.weather": {
        "ru": "Погода",
        "uz": "Ob-havo",
        "en": "Weather",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
    "btn.settings": {
        "ru": "Настройки",
        "uz": "Sozlamalar",
        "en": "Settings",
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['gear']} Единицы: {{units}}\n"
            f"{E['clock']} Часовой пояс: {{timezone}}\n"
        ),
        "uz": (
            f"{E['profile']} <b>Sizning profilingiz</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['gear']} Birliklar: {{units}}\n"
            f"{E['clock']} Vaqt zonasi: {{timezone}}\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['gear']} Units: {{units}}\n"
            f"{E['clock']} Timezone: {{timezone}}\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['star']} Отправь название города — получишь текущую погоду\n"
            f"{E['star']} Или отправь геолокацию\n"
            f"{E['star']} Поддерживается прогноз на несколько дней\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['star']} Shahar nomini yuboring — hozirgi ob-havoni oling\n"
            f"{E['star']} Yoki geolokatsiyangizni yuboring\n"
            f"{E['star']} Bir necha kunlik ob-havo bashorati qo'llab-quvvatlanadi\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['star']} Send a city name — get current weather\n"
            f"{E['star']} Or send your location\n"
            f"{E['star']} Multi-day forecast is supported\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['search']} Этот бот показывает прогноз погоды — быстро и бесплатно!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['search']} Bu bot ob-havo ma'lumotini ko'rsatadi — tez va bepul!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            f"Obuna bo'lgandan keyin «{E['check']} Obunani tekshirish» tugmasini bosing"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['search']} This bot shows weather forecasts — fast and free!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Siz hali barcha kanallarga obuna bo'lmadingiz:</b>\n\n"
            f"Obuna bo'ling va «{E['check']} Obunani tekshirish» tugmasini qayta bosing."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['plane']}\n\n"
            "Отправь название города для получения погоды."
        ),
        "uz": (
            f"{E['check']} <b>Ajoyib, {{name}}!</b>\n\n"
            f"Endi siz botdan foydalanishingiz mumkin! {E['plane']}\n\n"
            "Ob-havo olish uchun shahar nomini yuboring."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['plane']}\n\n"
            "Send a city name to get weather."
        ),
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },
    "sub.check_alert_fail": {
        "ru": f"{E['cross']} Подпишись на все каналы!",
        "uz": f"{E['cross']} Barcha kanallarga obuna bo'ling!",
        "en": f"{E['cross']} Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": f"{E['check']} Подписка подтверждена!",
        "uz": f"{E['check']} Obuna tasdiqlandi!",
        "en": f"{E['check']} Subscription confirmed!",
    },
    "sub.not_required": {
        "ru": f"{E['check']} Подписка не требуется!",
        "uz": f"{E['check']} Obuna talab qilinmaydi!",
        "en": f"{E['check']} No subscription required!",
    },

    # === Ошибки ===
    "error.generic": {
        "ru": f"{E['cross']} <b>Произошла ошибка</b>\n\nПопробуй позже.",
        "uz": f"{E['cross']} <b>Xatolik yuz berdi</b>\n\nKeyinroq urinib ko'ring.",
        "en": f"{E['cross']} <b>An error occurred</b>\n\nPlease try again later.",
    },
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kuting va qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },
    "error.city_not_found": {
        "ru": f"{E['cross']} <b>Город не найден</b>\n\nПроверь название и попробуй снова.",
        "uz": f"{E['cross']} <b>Shahar topilmadi</b>\n\nNomni tekshiring va qayta urinib ko'ring.",
        "en": f"{E['cross']} <b>City not found</b>\n\nCheck the name and try again.",
    },
    "error.api_unavailable": {
        "ru": f"{E['warning']} <b>Сервис временно недоступен</b>\n\nПопробуй позже.",
        "uz": f"{E['warning']} <b>Xizmat vaqtincha mavjud emas</b>\n\nKeyinroq urinib ko'ring.",
        "en": f"{E['warning']} <b>Service temporarily unavailable</b>\n\nPlease try again later.",
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Погода ===
    "weather.menu_title": {
        "ru": f"{E['search']} <b>Меню погоды</b>\n\nВыбери действие:",
        "uz": f"{E['search']} <b>Ob-havo menyusi</b>\n\nAmalni tanlang:",
        "en": f"{E['search']} <b>Weather menu</b>\n\nChoose an action:",
    },
    "weather.ask_city": {
        "ru": f"{E['search']} <b>Введи название города</b>\n\nНапример: <i>Ташкент</i>, <i>Samarqand</i>, <i>London</i>",
        "uz": f"{E['search']} <b>Shahar nomini kiriting</b>\n\nMasalan: <i>Toshkent</i>, <i>Samarqand</i>, <i>London</i>",
        "en": f"{E['search']} <b>Enter a city name</b>\n\nFor example: <i>Tashkent</i>, <i>Samarkand</i>, <i>London</i>",
    },
    "weather.send_location": {
        "ru": (
            f"{E['pin']} <b>Отправь свою геолокацию</b>\n\n"
            "На мобильном — нажми кнопку ниже.\n"
            "На десктопе — скрепка 📎 → <i>Геопозиция</i>."
        ),
        "uz": (
            f"{E['pin']} <b>Geolokatsiyangizni yuboring</b>\n\n"
            "Mobil qurilmada — quyidagi tugmani bosing.\n"
            "Desktopda — qisqich 📎 → <i>Joylashuv</i>."
        ),
        "en": (
            f"{E['pin']} <b>Share your location</b>\n\n"
            "On mobile — tap the button below.\n"
            "On desktop — paperclip 📎 → <i>Location</i>."
        ),
    },
    "weather.location_manual_hint": {
        "ru": (
            f"{E['warning']} На этом клиенте кнопка геолокации не сработала.\n\n"
            "Пришли локацию вручную: скрепка 📎 → <i>Геопозиция</i>."
        ),
        "uz": (
            f"{E['warning']} Bu klientda geolokatsiya tugmasi ishlamadi.\n\n"
            "Joylashuvni qo'lda yuboring: qisqich 📎 → <i>Joylashuv</i>."
        ),
        "en": (
            f"{E['warning']} The location button doesn't work on this client.\n\n"
            "Send location manually: paperclip 📎 → <i>Location</i>."
        ),
    },
    "weather.uz_cities_title": {
        "ru": f"{E['pin']} <b>Города Узбекистана</b>\n\nВыбери город:",
        "uz": f"{E['pin']} <b>O'zbekiston shaharlari</b>\n\nShaharni tanlang:",
        "en": f"{E['pin']} <b>Uzbekistan cities</b>\n\nChoose a city:",
    },
    "weather.no_favorites": {
        "ru": f"{E['star']} У тебя пока нет избранных городов.\n\nДобавь их кнопкой ⭐ при просмотре погоды.",
        "uz": f"{E['star']} Sevimli shaharlaringiz hali yo'q.\n\nOb-havoni ko'rishda ⭐ tugmasi orqali qo'shing.",
        "en": f"{E['star']} You have no favorite cities yet.\n\nAdd them with the ⭐ button on a weather card.",
    },
    "weather.favorites_title": {
        "ru": f"{E['star']} <b>Избранные города</b>",
        "uz": f"{E['star']} <b>Sevimli shaharlar</b>",
        "en": f"{E['star']} <b>Favorite cities</b>",
    },
    "weather.fav_added": {"ru": "⭐ Добавлено в избранное!", "uz": "⭐ Sevimlilarga qo'shildi!", "en": "⭐ Added to favorites!"},
    "weather.fav_exists": {"ru": "⭐ Уже в избранном", "uz": "⭐ Allaqachon sevimlilarda", "en": "⭐ Already in favorites"},
    "weather.fav_removed": {"ru": "❌ Удалено из избранного", "uz": "❌ Sevimlilardan o'chirildi", "en": "❌ Removed from favorites"},
    "weather.units_choose": {
        "ru": f"{E['gear']} Выбери единицы измерения:",
        "uz": f"{E['gear']} O'lchov birliklarini tanlang:",
        "en": f"{E['gear']} Choose measurement units:",
    },
    "weather.units_bad": {
        "ru": f"{E['cross']} Использование: /units metric или /units imperial",
        "uz": f"{E['cross']} Foydalanish: /units metric yoki /units imperial",
        "en": f"{E['cross']} Usage: /units metric or /units imperial",
    },
    "weather.units_set": {
        "ru": f"{E['check']} Единицы изменены: <b>{{units}}</b>",
        "uz": f"{E['check']} Birliklar o'zgartirildi: <b>{{units}}</b>",
        "en": f"{E['check']} Units changed: <b>{{units}}</b>",
    },

    # === Кнопки погоды ===
    "btn.weather.now":      {"ru": "Сейчас", "uz": "Hozir", "en": "Now"},
    "btn.weather.forecast": {"ru": "Прогноз", "uz": "Bashorat", "en": "Forecast"},
    "btn.weather.location": {"ru": "По геолокации", "uz": "Geolokatsiya", "en": "By location"},
    "btn.weather.uz_cities":{"ru": "Города UZ", "uz": "UZ shaharlari", "en": "UZ cities"},
    "btn.weather.favorites":{"ru": "Избранные", "uz": "Sevimlilar", "en": "Favorites"},
    "btn.weather.air":      {"ru": "Воздух", "uz": "Havo", "en": "Air"},
    "btn.weather.clothes":  {"ru": "Одежда", "uz": "Kiyim", "en": "Clothes"},
    "btn.weather.fav_add":  {"ru": "В избранное", "uz": "Sevimlilarga", "en": "Add favorite"},
    "btn.weather.fav_remove":{"ru": "Из избранного", "uz": "O'chirish", "en": "Remove favorite"},

    # === Описания доменных команд ===
    "cmd.forecast":    {"ru": "Прогноз на 5 дней", "uz": "5 kunlik bashorat", "en": "5-day forecast"},
    "cmd.tomorrow":    {"ru": "Прогноз на завтра", "uz": "Ertangi bashorat", "en": "Tomorrow's forecast"},
    "cmd.location":    {"ru": "Погода по геолокации", "uz": "Geolokatsiya bo'yicha", "en": "Weather by location"},
    "cmd.favorites":   {"ru": "Избранные города", "uz": "Sevimli shaharlar", "en": "Favorite cities"},
    "cmd.clothes":     {"ru": "Что надеть", "uz": "Nima kiyish", "en": "What to wear"},
    "cmd.air":         {"ru": "Качество воздуха", "uz": "Havo sifati", "en": "Air quality"},
    "cmd.map":         {"ru": "Карта города", "uz": "Shahar xaritasi", "en": "City map"},
    "cmd.units":       {"ru": "Единицы измерения", "uz": "O'lchov birliklari", "en": "Measurement units"},

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": f"{E['lock']} У тебя нет доступа к админке.",
        "uz": f"{E['lock']} Sizda admin panelga kirish huquqi yo'q.",
        "en": f"{E['lock']} You don't have access to admin panel.",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            "Отправь <b>ID канала</b> (например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            "<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            "Send the <b>channel ID</b> (e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b>:",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring:",
        "en": f"{E['edit']} Now send the <b>channel name</b>:",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            "Принимаю любой формат:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            "Istalgan formatda:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            "Any format accepted:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysizmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },

    # === Кнопки админки ===
    "btn.admin_stats": {"ru": "Статистика", "uz": "Statistika", "en": "Statistics"},
    "btn.admin_channels": {"ru": "Каналы", "uz": "Kanallar", "en": "Channels"},
    "btn.admin_home": {"ru": "Главное меню", "uz": "Bosh menyu", "en": "Main menu"},
    "btn.admin_add": {"ru": "Добавить канал", "uz": "Kanal qo'shish", "en": "Add channel"},
    "btn.admin_back": {"ru": "Назад", "uz": "Orqaga", "en": "Back"},
    "btn.admin_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_confirm_del": {"ru": "Да, удалить", "uz": "Ha, o'chirish", "en": "Yes, delete"},
    "btn.admin_cancel_del": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_panel": {"ru": "Админ-панель", "uz": "Admin panel", "en": "Admin panel"},
    "btn.admin_broadcast": {"ru": "Рассылка", "uz": "Xabar yuborish", "en": "Broadcast"},

    # === Рассылка ===
    "admin.broadcast_prompt": {
        "ru": f"{E['plane']} <b>Массовая рассылка</b>\n\nОтправь текст/фото/видео для рассылки.\nПоддерживается HTML.",
        "uz": f"{E['plane']} <b>Ommaviy xabar</b>\n\nYuborish uchun matn/rasm/video yuboring.\nHTML qo'llab-quvvatlanadi.",
        "en": f"{E['plane']} <b>Mass broadcast</b>\n\nSend text/photo/video to broadcast.\nHTML supported.",
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysizmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {"ru": "Да, отправить", "uz": "Ha, yuborish", "en": "Yes, send"},
    "admin.broadcast_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": f"{E['chart']} <b>Рассылка завершена!</b>\n\n{E['check']} Доставлено: <b>{{success}}</b>\n{E['cross']} Ошибок: <b>{{failed}}</b>\n{E['users']} Всего: <b>{{total}}</b>",
        "uz": f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n{E['check']} Yetkazildi: <b>{{success}}</b>\n{E['cross']} Xatolar: <b>{{failed}}</b>\n{E['users']} Jami: <b>{{total}}</b>",
        "en": f"{E['chart']} <b>Broadcast complete!</b>\n\n{E['check']} Delivered: <b>{{success}}</b>\n{E['cross']} Failed: <b>{{failed}}</b>\n{E['users']} Total: <b>{{total}}</b>",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Asosiy menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
    "cmd.weather": {
        "ru": "Узнать погоду",
        "uz": "Ob-havoni bilish",
        "en": "Get weather",
    },

    # === Дополнительные ключи погоды ===

    # Ошибка превышения квоты API
    "error.api_quota": {
        "ru": f"{E['warning']} <b>Превышен лимит запросов</b>\n\nСервис временно перегружен. Попробуй позже.",
        "uz": f"{E['warning']} <b>So'rovlar limiti oshib ketdi</b>\n\nXizmat vaqtincha band. Keyinroq urinib ko'ring.",
        "en": f"{E['warning']} <b>API quota exceeded</b>\n\nService is temporarily overloaded. Please try again later.",
    },

    # Заголовок утреннего дайджеста
    "weather.digest_header": {
        "ru": "🌅 <b>Доброе утро!</b> Сводка погоды:",
        "uz": "🌅 <b>Xayrli tong!</b> Ob-havo sharhi:",
        "en": "🌅 <b>Good morning!</b> Weather digest:",
    },

    # Единицы видимости
    "weather.unit_km": {
        "ru": "км",
        "uz": "km",
        "en": "km",
    },

    # Единицы скорости ветра
    "weather.unit_ms": {
        "ru": "м/с",
        "uz": "m/s",
        "en": "m/s",
    },
    "weather.unit_mph": {
        "ru": "миль/ч",
        "uz": "mil/soat",
        "en": "mph",
    },
    "weather.unit_kmh": {
        "ru": "км/ч",
        "uz": "km/soat",
        "en": "km/h",
    },

    # Единицы мкг/м³ (качество воздуха)
    "weather.unit_ugm3": {
        "ru": "мкг/м³",
        "uz": "mkg/m³",
        "en": "μg/m³",
    },

    # WeatherAPI fallback — метки для format_current_weatherapi
    "weather.feels_like_short": {
        "ru": "ощущается",
        "uz": "his etiladi",
        "en": "feels like",
    },
    "weather.humidity_label": {
        "ru": "Влажность",
        "uz": "Namlik",
        "en": "Humidity",
    },
    "weather.wind_label": {
        "ru": "Ветер",
        "uz": "Shamol",
        "en": "Wind",
    },


    # Нет данных прогноза
    "weather.no_forecast_data": {
        "ru": "⚠️ Нет данных прогноза для {city}",
        "uz": "⚠️ {city} uchun bashorat ma'lumotlari yo'q",
        "en": "⚠️ No forecast data for {city}",
    },

    # Нет данных качества воздуха
    "weather.no_air_data": {
        "ru": "⚠️ Нет данных по качеству воздуха для {city}",
        "uz": "⚠️ {city} uchun havo sifati ma'lumotlari yo'q",
        "en": "⚠️ No air quality data for {city}",
    },

    # Inline — город не найден (switch_pm_text)
    "weather.inline_city_not_found": {
        "ru": "Город не найден",
        "uz": "Shahar topilmadi",
        "en": "City not found",
    },

    # Единицы измерения — метки для профиля
    "units.metric_label": {
        "ru": "Метрические (°C)",
        "uz": "Metrik (°C)",
        "en": "Metric (°C)",
    },
    "units.imperial_label": {
        "ru": "Имперские (°F)",
        "uz": "Imperial (°F)",
        "en": "Imperial (°F)",
    },
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("ru", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → русский"""
    if not language_code:
        return "ru"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    if language_code.startswith("en"):
        return "en"
    return "ru"
