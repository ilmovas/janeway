## دليل التثبيت — Sibar / Janeway

### المتطلبات الأساسية (Prerequisites)
- **Janeway 1.7.0+** (تم اختبار البلوقن على Janeway **1.8.0**).
- القدرة على تشغيل `manage.py` (ضمن الحاوية أو على الخادوم).
- الحصول على:
  - **Sibar API Base URL**
  - **Sibar API Key**

---

### STEP 1 — وضع البلوقن (Place the plugin)
انسخ مجلد البلوقن `sibar/` إلى مسار:

- `src/plugins/sibar/`

ضمن تثبيت Janeway في الجامعة.

---

### STEP 2 — تثبيت الاعتماديات (Install dependencies)
يعتمد البلوقن على:
- `weasyprint==69.0` (مذكور في `src/plugins/sibar/requirements.txt`)

**على إعداد Janeway القياسي عبر Docker**: يتم تثبيت متطلبات جميع البلوقنز تلقائياً أثناء البناء من ملفات `*requirements.txt` داخل `src/plugins/`.

**على إعدادات مخصصة/بدون Docker**:
- ثبّت الحزمة:
  - `pip install weasyprint==69.0`
- وتأكد من توفر مكتبات النظام التي يحتاجها WeasyPrint:
  - **pango**, **cairo**, **gdk-pixbuf**

---

### STEP 3 — تسجيل البلوقن (Register the plugin)
شغّل:

- `python src/manage.py install_plugins sibar`

---

### STEP 4 — تطبيق migrations (Apply migrations)
شغّل:

- `python src/manage.py migrate sibar`

---

### STEP 5 — إضافة مرحلة سير العمل (MANUAL) (Add the workflow stage)
هذه الخطوة **يدوية**: وظيفة `install()` في البلوقن لا تُنشئ عنصر الـ workflow تلقائياً.

**الخيار A (موصى به — عبر واجهة المدير)**:
- ادخل إلى: Journal Manager → Workflow
- أضف عنصر سير العمل باسم:
  - **`sibar_plugin`**
- **الموضع الموصى به**: أول عنصر في سير العمل (قبل `review`).

**الخيار B (عبر سكربت المساعدة)**:
- استخدم السكربت `setup_sibar.py` (انظر القسم الخاص به أدناه) لإضافة العنصر بشكل آمن ومتكرر (idempotent).

---

### STEP 6 — ضبط الإعدادات (Configure settings)
من إعدادات البلوقن/المدير، ضمن مجموعة الإعدادات:
- **`plugin:sibar`**

قم بضبط:
- **Sibar API Base URL** (`sibar_api_url`)
  - القيمة الافتراضية: `https://sibar.ilmovas.com`
- **Sibar API Key** (`sibar_api_key`)
  - أدخل مفتاح API الخاص بالمجلة (لا يتم وضعه داخل ملفات المشروع).

---

### STEP 7 — التحقق (Verify)
- افتح مقالاً في مرحلة **`sibar_plugin`**.
- شغّل فحص سِبار وتأكد من ظهور النتائج وإمكانية توليد تقرير PDF.

---

## استخدام سكربت المساعدة `setup_sibar.py`
السكربت يقوم بـ:
- إضافة عنصر سير العمل **`sibar_plugin`** لمجلة محددة بترتيب **0** (ويُزحزح العناصر الأخرى).
- يعمل بشكل **idempotent** (لن يكرر الإضافة إذا كانت موجودة).
- يمكنه اختيارياً ضبط **API URL** (بدون أي مفاتيح سرية).
- لا يضبط `sibar_api_key` (سيطبع تعليمات لضبطه عبر واجهة المدير).

**تشغيل عبر manage.py shell** (مثال):
- `python src/manage.py shell < src/plugins/sibar/setup_sibar.py -- <JOURNAL_CODE_OR_ID> [--api-url https://sibar.ilmovas.com]`

> ملاحظة: يتم تمرير الوسائط بعد `--` لتصل إلى السكربت.

---

## استكشاف الأخطاء وإصلاحها (Troubleshooting)
- **التقرير يظهر مربعات بدل العربية**:
  - تأكد من وجود خطوط Tajawal داخل البلوقن:
    - `src/plugins/sibar/assets/fonts/tajawal-400.ttf`
    - `src/plugins/sibar/assets/fonts/tajawal-700.ttf`
- **رابط البلوقن 404 بعد التثبيت**:
  - أعد تشغيل عملية الويب/الحاوية حتى تُحمَّل URLs والبلوقنز.
- **ظهور "Sibar_plugin" في لوحة التحكم**:
  - هذا **سلوك قياسي في Janeway** لتسميات مراحل البلوقنز (مثل `Typesetting_plugin`). العلامة التجارية هي **Sibar**.

---

## English install guide (same steps)

### Prerequisites
- **Janeway 1.7.0+** (plugin tested on Janeway **1.8.0**)
- Ability to run `manage.py`
- A valid **Sibar API Base URL** and **Sibar API Key**

### STEP 1 — Place the plugin
Copy the `sibar/` plugin folder into:
- `src/plugins/sibar/`

### STEP 2 — Install dependencies
The plugin depends on:
- `weasyprint==69.0` (declared in `src/plugins/sibar/requirements.txt`)

**Standard Janeway Docker builds** install plugin requirements automatically from `*requirements.txt` files under `src/plugins/`.

**Custom / non-Docker installs**:
- `pip install weasyprint==69.0`
- Ensure WeasyPrint system libs are installed: **pango**, **cairo**, **gdk-pixbuf**

### STEP 3 — Register the plugin
- `python src/manage.py install_plugins sibar`

### STEP 4 — Apply migrations
- `python src/manage.py migrate sibar`

### STEP 5 — Add the workflow stage (MANUAL)
This is **manual**: the plugin’s `install()` does not create the workflow element.

Option A (recommended): Journal Manager → Workflow → add element **`sibar_plugin`** (recommended first, before `review`).

Option B: run the helper script `setup_sibar.py` (see below).

### STEP 6 — Configure settings
Under settings group **`plugin:sibar`**, set:
- `sibar_api_url` (default `https://sibar.ilmovas.com`)
- `sibar_api_key` (enter the journal’s key via the UI; do not store secrets in code)

### STEP 7 — Verify
Open an article in stage `sibar_plugin` and run a check; confirm results and PDF generation.

### Troubleshooting
- PDF shows boxes instead of Arabic: confirm Tajawal font files exist under `assets/fonts/`.
- Plugin URL is 404 after install: restart the web process/container so routes load.
- Dashboard label shows `Sibar_plugin`: this is Janeway’s standard workflow-stage label format (e.g. `Typesetting_plugin`).
